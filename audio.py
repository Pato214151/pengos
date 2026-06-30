import audioop
import io
import re
import sys
import threading
import time
import wave
from datetime import datetime, timedelta, timezone

import pyaudio
import pyperclip
import webrtcvad
from PyQt5.QtCore import QObject, pyqtSignal

from api import transcribe_audio, translate_en_to_es, translate_es_to_en
from aprendizaje import registrar_traduccion, traduccion_aprendida
from config import config, log
from filters import es_transcripcion_valida
from glosario import corregir_transcripcion, traduccion_directa
from historial import registrar


class AudioProcessor(QObject):
    sig_partial    = pyqtSignal(str)
    sig_final      = pyqtSignal(str, str, str)   # (original, translated, direction: "en2es"|"es2en")
    sig_status     = pyqtSignal(str)
    sig_ptt        = pyqtSignal(bool)
    sig_mic        = pyqtSignal(bool)
    sig_mic_result = pyqtSignal(str, str)
    sig_proc       = pyqtSignal(bool)

    SAMPLE_RATE  = 16000
    FRAME_BYTES  = 480
    MAX_BUFFER_S = 8.0   # default; configurable vía config["max_buffer_s"]

    # Corte suave: una vez que el segmento ya lleva _SOFT_BUFFER_S de voz, basta
    # una pausita de _SOFT_SILENCE_MS (entre palabras) para cortar ahí, en vez de
    # esperar el corte DURO por max_buffer (que parte a mitad de palabra). Esto
    # mantiene la latencia baja Y corta en límites naturales (no "scre-am").
    _SOFT_BUFFER_S   = 2.5
    _SOFT_SILENCE_MS = 150

    # Throttle ADAPTATIVO (gap compartido entre sys+mic; el rate limit de Groq
    # es de toda la cuenta, no por stream). Arranca rápido y se ensancha solo
    # al chocar un 429, volviendo al piso de a poco con cada éxito.
    _GAP_MIN   = 1.8   # piso: rápido pero con margen para no reventar el límite gratis
    _GAP_MAX   = 8.0   # techo cuando Groq nos está frenando duro
    _GAP_GROW  = 1.6   # multiplicador al recibir un 429 (back-off)
    _GAP_DECAY = 0.92  # se acerca al piso con cada llamada exitosa
    _DEDUP_WINDOW_S  = 8.0   # ignora la misma transcripción si ya salió en los últimos 8s
    # Códigos HTTP transitorios (reintentables). \b para no matchear "1500" → "500".
    _HTTP_RETRY_RE = re.compile(r"\b(?:500|502|503|504)\b")
    # Si el stream de audio falla esta cantidad de veces SEGUIDAS, se da por muerto
    # y se corta el loop (en vez de girar en seco quemando CPU para siempre).
    _MAX_READ_ERRORS = 100
    # Gate previo a la API: no transcribir segmentos demasiado cortos o de baja
    # energía (silencio/ruido). Ahorra llamadas (clave para no reventar el 429).
    _MIN_VOZ_S = 0.35   # duración mínima de voz para que valga la pena transcribir
    _RMS_MIN   = 300    # energía mínima (RMS int16); por debajo = silencio/ruido/TV de fondo

    def __init__(self):
        super().__init__()
        self.running      = True
        # Buffer máximo por segmento de voz: más alto = corta menos las frases
        # largas (conversación/RP), pero sube la latencia y el tamaño de cada
        # llamada. Configurable; se acota a un rango sano [3, 20] s.
        self.MAX_BUFFER_S = min(20.0, max(3.0, float(config.get("max_buffer_s", self.MAX_BUFFER_S))))
        self._ptt_active  = False
        self._mic_active  = False
        self._mic_processing = False   # True mientras el mic worker traduce una frase
        self._mic_stopped = threading.Event()
        self._proc_count  = 0
        self._proc_lock   = threading.Lock()
        self._sys_ts   = 0.0
        self._sys_lock = threading.Lock()
        self._mic_ts   = 0.0
        self._mic_lock = threading.Lock()
        self._gap      = self._GAP_MIN          # gap adaptativo actual (compartido)
        self._gap_lock = threading.Lock()
        # Language lock (F4/escucha): "auto" detecta idioma por audio; "en"/"es"
        # lo FIJAN — más preciso cuando ya sabés en qué idioma hablan tus amigos
        # (evita que Whisper auto-traduzca español→inglés en audio mezclado).
        _lang = str(config.get("idioma_entrada", "auto")).lower()
        self._listen_lock = _lang if _lang in ("en", "es") else None
        if self._listen_lock:
            log.info(f"[ESCUCHA] idioma fijado: {self._listen_lock} (lock)")
        else:
            log.info("[ESCUCHA] idioma: auto (detección por audio)")
        self._last_sys_text = ""
        self._last_sys_time = 0.0
        # Dedup compartido entre streams (sys+mic): si la misma voz entra por
        # ambos (p.ej. el mic se cuela en el audio de sistema), no traducir 2 veces.
        self._dedup_lock     = threading.Lock()
        self._last_out_text  = ""
        self._last_out_time  = 0.0
        # Despacho "último gana": en vez de lanzar un hilo por segmento (que se
        # apilaban en el throttle hasta CONGELAR la traducción bajo 429), cada
        # stream tiene UN solo slot pendiente. Si llega audio nuevo mientras el
        # worker está ocupado, sobrescribe el pendiente (descarta el viejo al
        # instante, sin gastar un turno de throttle). El worker procesa siempre
        # el más reciente → latencia acotada, nunca se forma una cola sin fin.
        self._pending_sys       = None
        self._pending_sys_lock  = threading.Lock()
        self._pending_sys_event = threading.Event()
        self._pending_mic       = None
        self._pending_mic_lock  = threading.Lock()
        self._pending_mic_event = threading.Event()
        # Rendición por límite DIARIO (RPD): al agotarse la cuota diaria de Groq,
        # no sirve seguir pidiendo hasta el reset (medianoche UTC). Guardamos hasta
        # cuándo rendirnos y cortamos TODO procesamiento (sin spam de 429).
        self._rpd_lock        = threading.Lock()
        self._rpd_until_utc   = None   # datetime UTC del reset, o None si activo
        self.p            = pyaudio.PyAudio()
        self._sample_size = self.p.get_sample_size(pyaudio.paInt16)
        self.stream_sys   = self._open_stream_sys()
        self.stream_mic   = self._open_mic()
        # Workers de despacho (uno por stream); viven hasta running=False.
        threading.Thread(target=self._sys_worker, daemon=True).start()
        threading.Thread(target=self._mic_worker, daemon=True).start()

    _STEREO_MIX_NAMES = [
        "stereo mix", "mezcla estéreo", "mezcla de sonido",
        "what u hear", "what you hear", "wave out mix",
        "loopback", "sum", "mix out",
    ]

    def _open_stream_sys(self):
        mode = config.get("audio_mode", "vbcable")
        if mode == "vbcable":
            return self._open_by_name(config["audio_device_name"])
        elif mode == "stereo_mix":
            return self._open_stereo_mix()
        elif mode == "auto":
            name = config.get("audio_device_name", "CABLE Output")
            if self._find_device_index(name) is not None:
                log.info("[AUTO] VB-CABLE encontrado — usando vbcable.")
                return self._open_by_name(name)
            log.warning("[AUTO] VB-CABLE no encontrado — intentando Stereo Mix.")
            try:
                return self._open_stereo_mix()
            except RuntimeError:
                log.error("[AUTO] Stereo Mix tampoco encontrado.")
                self._listar_dispositivos()
                sys.exit(1)
        else:
            log.error(f"audio_mode '{mode}' no reconocido. Valores válidos: vbcable, stereo_mix, auto")
            sys.exit(1)

    def _find_device_index(self, name: str) -> int | None:
        return next(
            (i for i in range(self.p.get_device_count())
             if name in self.p.get_device_info_by_index(i)["name"]
             and self.p.get_device_info_by_index(i)["maxInputChannels"] > 0),
            None,
        )

    def _open_by_name(self, name: str):
        index = self._find_device_index(name)
        if index is None:
            log.error(f"Dispositivo '{name}' no encontrado.")
            self._listar_dispositivos()
            sys.exit(1)
        log.info(f"[AUDIO] {self.p.get_device_info_by_index(index)['name']}")
        return self.p.open(
            format=pyaudio.paInt16, channels=1, rate=self.SAMPLE_RATE,
            input=True, input_device_index=index,
            frames_per_buffer=self.FRAME_BYTES,
        )

    def _open_stereo_mix(self):
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                name_l = info["name"].lower()
                if any(s in name_l for s in self._STEREO_MIX_NAMES):
                    log.info(f"[STEREO MIX] {info['name']}")
                    return self.p.open(
                        format=pyaudio.paInt16, channels=1, rate=self.SAMPLE_RATE,
                        input=True, input_device_index=i,
                        frames_per_buffer=self.FRAME_BYTES,
                    )
        raise RuntimeError(
            "Stereo Mix no encontrado. Activalo en: Panel de control → Sonido "
            "→ Grabación → clic derecho → Mostrar dispositivos deshabilitados."
        )

    def _listar_dispositivos(self):
        log.info("Dispositivos de entrada disponibles:")
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                log.info(f"  [{i}] {info['name']}")

    def _open_mic(self):
        mic_name = config.get("microphone_device_name", "")
        if mic_name:
            index = next(
                (i for i in range(self.p.get_device_count())
                 if mic_name in self.p.get_device_info_by_index(i)["name"]
                 and self.p.get_device_info_by_index(i)["maxInputChannels"] > 0),
                None
            )
            if index is not None:
                log.info(f"[MIC] {self.p.get_device_info_by_index(index)['name']}")
                return self.p.open(
                    format=pyaudio.paInt16, channels=1, rate=self.SAMPLE_RATE,
                    input=True, input_device_index=index,
                    frames_per_buffer=self.FRAME_BYTES,
                )
            log.warning(f"[MIC] '{mic_name}' no encontrado — usando default.")

        try:
            info = self.p.get_default_input_device_info()
            log.info(f"[MIC] (default) {info['name']}")
            return self.p.open(
                format=pyaudio.paInt16, channels=1, rate=self.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.FRAME_BYTES,
            )
        except Exception as e:
            log.warning(f"Sin micrófono — F5 deshabilitado. ({e})")
            return None

    def set_ptt(self, active: bool):
        self._ptt_active = active
        self.sig_ptt.emit(active)

    def set_mic(self, active: bool):
        if self.stream_mic is None:
            return
        self._mic_active = active
        self.sig_mic.emit(active)

    def run(self):
        frame_ms        = int(self.FRAME_BYTES / self.SAMPLE_RATE * 1000)  # 30 ms
        silencio_ms     = config.get("vad_silencio_ms", 600)
        silence_trigger = max(1, silencio_ms // frame_ms)
        pre_roll_frames = 10                                                # 300 ms
        max_frames      = int(self.MAX_BUFFER_S * 1000 / frame_ms)
        soft_frames     = int(self._SOFT_BUFFER_S * 1000 / frame_ms)
        soft_silence    = max(1, self._SOFT_SILENCE_MS // frame_ms)

        try:
            vad = webrtcvad.Vad(config.get("vad_sensibilidad", 2))
            vad_ok = True
        except Exception as e:
            log.warning(f"VAD no disponible ({e}) — modo buffer simple.")
            vad_ok = False

        voiced: list[bytes] = []
        ring:   list[bytes] = []
        silent_count = 0
        in_speech    = False
        was_ptt      = False

        log.info("Captura iniciada (F4=escuchar, F5=hablar).")

        read_errors = 0
        while self.running:
            try:
                frame = self.stream_sys.read(self.FRAME_BYTES, exception_on_overflow=False)
                read_errors = 0
            except Exception as e:
                read_errors += 1
                if read_errors >= self._MAX_READ_ERRORS:
                    log.error(f"[AUDIO] stream de sistema caído "
                              f"({read_errors} fallos seguidos): {e}")
                    self.sig_status.emit("red")
                    break
                time.sleep(0.05)
                continue

            # Frame vacío/corto (device muteado o devolviendo basura): no procesar
            # ni alimentar al VAD (evita el giro en seco y segmentos de basura).
            if len(frame) < self.FRAME_BYTES * self._sample_size:
                time.sleep(0.005)
                continue

            ptt = self._ptt_active

            if not ptt:
                if was_ptt and voiced:
                    voiced.append(frame)   # incluir el último frame (~30ms) al soltar
                    self._start_process_sys(b"".join(voiced))
                voiced.clear()
                ring.clear()
                silent_count = 0
                in_speech = False
                was_ptt = False
                continue

            was_ptt = True

            if not vad_ok:
                voiced.append(frame)
                if len(voiced) >= max_frames:
                    self._start_process_sys(b"".join(voiced))
                    voiced.clear()
                continue

            try:
                is_speech = vad.is_speech(frame, self.SAMPLE_RATE)
            except Exception:
                is_speech = True

            if is_speech:
                if not in_speech:
                    voiced = list(ring) + [frame]
                    in_speech = True
                else:
                    voiced.append(frame)
                silent_count = 0

                if len(voiced) >= max_frames:
                    self._start_process_sys(b"".join(voiced))
                    voiced.clear()
                    in_speech = False
            else:
                if in_speech:
                    voiced.append(frame)
                    silent_count += 1
                    # Corte normal (pausa larga) o suave (buffer ya largo + pausita
                    # corta entre palabras → corta en límite natural, no a la fuerza).
                    soft_cut = len(voiced) >= soft_frames and silent_count >= soft_silence
                    if silent_count >= silence_trigger or soft_cut:
                        self._start_process_sys(b"".join(voiced))
                        voiced.clear()
                        in_speech = False
                        silent_count = 0
                else:
                    ring.append(frame)
                    if len(ring) > pre_roll_frames:
                        ring.pop(0)

        if voiced:
            self._start_process_sys(b"".join(voiced))

        # Esperar a que run_mic() cierre su stream ANTES de terminar PyAudio.
        # _mic_stopped se setea recién DESPUÉS de stream_mic.close(), así que
        # esto garantiza que no llamemos p.terminate() con un stream vivo (crash).
        if not self._mic_stopped.wait(timeout=5.0):
            log.warning("[CIERRE] run_mic no confirmó cierre en 5s — terminando igual.")
        try:
            self.stream_sys.stop_stream()
            self.stream_sys.close()
        except Exception as e:
            log.warning(f"[CIERRE] error cerrando stream_sys: {e}")
        try:
            self.p.terminate()
        except Exception as e:
            log.warning(f"[CIERRE] error en p.terminate(): {e}")
        log.info("AudioProcessor cerrado.")

    def run_mic(self):
        if self.stream_mic is None:
            self._mic_stopped.set()
            return

        frame_ms        = int(self.FRAME_BYTES / self.SAMPLE_RATE * 1000)
        silencio_ms     = config.get("vad_silencio_ms", 600)
        silence_trigger = max(1, silencio_ms // frame_ms)
        pre_roll_frames = 5                                                 # 150 ms para mic
        max_frames      = int(self.MAX_BUFFER_S * 1000 / frame_ms)
        soft_frames     = int(self._SOFT_BUFFER_S * 1000 / frame_ms)
        soft_silence    = max(1, self._SOFT_SILENCE_MS // frame_ms)

        try:
            vad_level = max(0, config.get("vad_sensibilidad", 2) - 1)
            vad = webrtcvad.Vad(vad_level)
            vad_ok = True
        except Exception:
            vad_ok = False

        voiced: list[bytes] = []
        ring:   list[bytes] = []
        silent_count = 0
        in_speech    = False
        was_mic      = False

        read_errors = 0
        while self.running:
            try:
                frame = self.stream_mic.read(self.FRAME_BYTES, exception_on_overflow=False)
                read_errors = 0
            except Exception as e:
                read_errors += 1
                if read_errors >= self._MAX_READ_ERRORS:
                    log.error(f"[AUDIO] stream de micrófono caído "
                              f"({read_errors} fallos seguidos): {e}")
                    break
                time.sleep(0.05)
                continue

            # Frame vacío/corto (mic muteado/roto): no procesar ni alimentar al VAD.
            if len(frame) < self.FRAME_BYTES * self._sample_size:
                time.sleep(0.005)
                continue

            mic = self._mic_active

            if not mic:
                if was_mic and voiced:
                    voiced.append(frame)   # incluir el último frame (~30ms) al soltar
                    self._start_process_mic(b"".join(voiced))
                voiced.clear()
                ring.clear()
                silent_count = 0
                in_speech = False
                was_mic = False
                continue

            was_mic = True

            if not vad_ok:
                voiced.append(frame)
                if len(voiced) >= max_frames:
                    self._start_process_mic(b"".join(voiced))
                    voiced.clear()
                continue

            try:
                is_speech = vad.is_speech(frame, self.SAMPLE_RATE)
            except Exception:
                is_speech = True

            if is_speech:
                if not in_speech:
                    voiced = list(ring) + [frame]
                    in_speech = True
                else:
                    voiced.append(frame)
                silent_count = 0

                if len(voiced) >= max_frames:
                    self._start_process_mic(b"".join(voiced))
                    voiced.clear()
                    in_speech = False
            else:
                if in_speech:
                    voiced.append(frame)
                    silent_count += 1
                    soft_cut = len(voiced) >= soft_frames and silent_count >= soft_silence
                    if silent_count >= silence_trigger or soft_cut:
                        self._start_process_mic(b"".join(voiced))
                        voiced.clear()
                        in_speech = False
                        silent_count = 0
                else:
                    ring.append(frame)
                    if len(ring) > pre_roll_frames:
                        ring.pop(0)

        if voiced:
            self._start_process_mic(b"".join(voiced))

        self.stream_mic.stop_stream()
        self.stream_mic.close()
        self._mic_stopped.set()

    def _voz_util(self, pcm: bytes) -> bool:
        """True si el PCM tiene voz real (no silencio/ruido y dura lo suficiente).

        Filtra ANTES de llamar a la API: los segmentos cortísimos o de baja energía
        son casi siempre ruido/relleno que Whisper alucina ('you', 'Thank you', etc.).
        Cada uno de esos era una llamada desperdiciada que ayudaba a reventar el 429.
        """
        dur = len(pcm) / 2 / self.SAMPLE_RATE   # int16 → 2 bytes/muestra
        if dur < self._MIN_VOZ_S:
            return False
        try:
            if audioop.rms(pcm, 2) < self._RMS_MIN:
                return False
        except Exception:
            pass   # ante la duda, dejar pasar (mejor traducir que perder voz real)
        return True

    def _start_process_sys(self, pcm: bytes):
        # No procesa acá: deja el segmento como "pendiente más reciente". El worker
        # lo recoge. Si ya había uno sin empezar, se descarta (siempre el más nuevo)
        # → nunca se acumula una cola que congele la traducción.
        if not self._voz_util(pcm):
            return   # silencio/ruido/segmento muy corto → ni se manda a la API
        captured_at = time.time()
        with self._pending_sys_lock:
            habia = self._pending_sys is not None
            self._pending_sys = (self._pcm_to_wav(pcm), captured_at)
        if habia:
            log.info("[COALESCE] sys: segmento viejo descartado por uno más nuevo")
        self._pending_sys_event.set()

    def _start_process_mic(self, pcm: bytes):
        if not self._voz_util(pcm):
            return
        captured_at = time.time()
        with self._pending_mic_lock:
            habia = self._pending_mic is not None
            self._pending_mic = (self._pcm_to_wav(pcm), captured_at)
        if habia:
            log.info("[COALESCE] mic: segmento viejo descartado por uno más nuevo")
        self._pending_mic_event.set()

    def _ceder_a_mic(self, max_wait: float = 6.0):
        """Prioridad al micrófono (F5): mientras el usuario habla o su frase está
        en cola/proceso, el stream de SISTEMA (F4, escuchar) cede el paso. Lo que
        YO quiero decir es lo urgente; a los compañeros los traduzco después. Así
        el mic no pierde el cupo de la API contra la cháchara de fondo.

        max_wait acota la espera para que el sistema no se quede mudo si algo se
        traba con el micrófono.
        """
        t0 = time.time()
        while self.running and time.time() - t0 < max_wait:
            with self._pending_mic_lock:
                mic_pend = self._pending_mic is not None
            if self._mic_active or mic_pend or self._mic_processing:
                time.sleep(0.1)
            else:
                return

    def _sys_worker(self):
        """Procesa de a un segmento, siempre el más reciente disponible."""
        while self.running:
            if not self._pending_sys_event.wait(timeout=0.3):
                continue
            self._ceder_a_mic()   # prioridad al micrófono antes de tomar el turno
            self._pending_sys_event.clear()
            with self._pending_sys_lock:
                item = self._pending_sys
                self._pending_sys = None
            if item is None:
                continue
            wav, captured_at = item
            with self._proc_lock:
                self._proc_count += 1
                if self._proc_count == 1:
                    self.sig_proc.emit(True)
            try:
                self._process_sys(wav, captured_at)
            except Exception as e:
                log.error(f"[SYS] error inesperado: {e}")
            finally:
                with self._proc_lock:
                    self._proc_count -= 1
                    if self._proc_count == 0:
                        self.sig_proc.emit(False)

    def _mic_worker(self):
        """Idéntico al sys_worker pero para el micrófono (F5)."""
        while self.running:
            if not self._pending_mic_event.wait(timeout=0.3):
                continue
            self._pending_mic_event.clear()
            with self._pending_mic_lock:
                item = self._pending_mic
                self._pending_mic = None
            if item is None:
                continue
            wav, captured_at = item
            self._mic_processing = True   # avisa al sys worker que ceda el paso
            with self._proc_lock:
                self._proc_count += 1
                if self._proc_count == 1:
                    self.sig_proc.emit(True)
            try:
                self._process_mic(wav, captured_at)
            except Exception as e:
                log.error(f"[MIC] error inesperado: {e}")
            finally:
                self._mic_processing = False
                with self._proc_lock:
                    self._proc_count -= 1
                    if self._proc_count == 0:
                        self.sig_proc.emit(False)

    def _pcm_to_wav(self, pcm: bytes) -> bytes:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self._sample_size)
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(pcm)
        return buf.getvalue()

    def _activar_rendicion_rpd(self):
        """Marca que la cuota DIARIA se agotó: rendirse hasta medianoche UTC."""
        now_utc   = datetime.now(timezone.utc)
        reset_utc = (now_utc + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0)
        with self._rpd_lock:
            ya_estaba = self._rpd_until_utc is not None
            self._rpd_until_utc = reset_utc
        if not ya_estaba:
            falta = reset_utc - now_utc
            horas = falta.total_seconds() / 3600
            log.error("[CUOTA] Límite DIARIO de Groq agotado (RPD). "
                      f"Rindiendo hasta el reset (~{horas:.1f}h, medianoche UTC).")
        self.sig_status.emit("red")

    def _rpd_rendido(self) -> bool:
        """True si seguimos en rendición por RPD (cuota diaria sin resetear aún)."""
        with self._rpd_lock:
            until = self._rpd_until_utc
        if until is None:
            return False
        if datetime.now(timezone.utc) >= until:
            # Llegó el reset → reactivar.
            with self._rpd_lock:
                self._rpd_until_utc = None
            log.info("[CUOTA] Reset diario alcanzado — reanudando traducción.")
            self.sig_status.emit("green")
            return False
        return True

    def _es_duplicado_global(self, text: str) -> bool:
        """True si esta transcripción ya salió por cualquier stream hace poco.

        Evita que la misma voz, capturada por sys y mic a la vez, se traduzca
        (y se cobre) dos veces. Registra el texto como visto si es nuevo.
        """
        key = text.lower().strip()
        if not key:
            return False
        now = time.time()
        with self._dedup_lock:
            if key == self._last_out_text and now - self._last_out_time < self._DEDUP_WINDOW_S:
                return True
            self._last_out_text = key
            self._last_out_time = now
            return False

    def _current_gap(self) -> float:
        with self._gap_lock:
            return self._gap

    def _register_rate_limit(self):
        """Un 429 nos llegó: ensanchar el gap (back-off) para dejar respirar a Groq."""
        with self._gap_lock:
            self._gap = min(self._GAP_MAX, self._gap * self._GAP_GROW)
            log.info(f"[THROTTLE] 429 — subiendo gap a {self._gap:.1f}s")

    def _register_success(self):
        """Llamada exitosa: acercar el gap al piso de a poco."""
        with self._gap_lock:
            if self._gap > self._GAP_MIN:
                self._gap = max(self._GAP_MIN, self._gap * self._GAP_DECAY)

    def _throttle_sys(self):
        gap = self._current_gap()
        with self._sys_lock:
            now  = time.time()
            wait = gap - (now - self._sys_ts)
            if wait > 0:
                time.sleep(wait)
            self._sys_ts = time.time()

    def _throttle_mic(self):
        gap = self._current_gap()
        with self._mic_lock:
            now  = time.time()
            wait = gap - (now - self._mic_ts)
            if wait > 0:
                time.sleep(wait)
            self._mic_ts = time.time()

    def _evaluar_error_api(self, e: Exception, attempt: int, max_retries: int,
                           tag: str = "") -> str:
        """Clasifica un error de la API y, si toca reintentar, espera el back-off.

        Compartido por _process_sys y _process_mic para no duplicar la lógica.
        Devuelve uno de:
        - "rpd"   → límite DIARIO agotado: el caller debe rendirse hasta el reset.
        - "retry" → ya esperó el back-off; el caller debe `continue` el loop.
        - "stop"  → error final (o sin reintentos): abortar este segmento.
        tag: "" para el stream de sistema, "MIC-" para el de micrófono (solo logs).
        """
        msg = str(e)
        msg_l = msg.lower()
        is_429 = "429" in msg
        # Límite DIARIO (RPD): no sirve reintentar, no se libera hasta el reset.
        if is_429 and ("per day" in msg_l or "(rpd)" in msg_l):
            return "rpd"
        retryable = (
            is_429
            or self._HTTP_RETRY_RE.search(msg) is not None
            or "timeout" in msg_l
            or "connection" in msg_l
        )
        if is_429:
            self._register_rate_limit()   # back-off: ensanchar el gap
        if retryable and attempt < max_retries - 1:
            retry_after = 3.0
            m = re.search(r"try again in (\d+(?:\.\d+)?)s", msg)
            if m:
                retry_after = float(m.group(1)) + 0.5
            log.info(f"[{tag}RETRY] esperando {retry_after:.1f}s "
                     f"(intento {attempt+1}/{max_retries})")
            time.sleep(retry_after)
            return "retry"
        log.error(f"[{tag}ERROR] {msg[:200]}")
        return "stop"

    def _process_sys(self, wav_bytes: bytes, captured_at: float = None):
        if self._rpd_rendido():
            return   # cuota diaria agotada — no pedir hasta el reset
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            try:
                # El worker ya entrega SIEMPRE el segmento más reciente (el coalescing
                # del slot pendiente descarta el atraso solo). Así que acá no se salta
                # nada: se traduce lo que llegó. Bajo habla continua esto avanza de a un
                # segmento por ciclo (throttle+API), nunca se congela.
                self._throttle_sys()
                t0 = time.time()

                # Idioma: fijado por config (lock) o auto-detectado por audio.
                # Whisper devuelve (texto, idioma).
                raw, lang = transcribe_audio(wav_bytes, language=self._listen_lock)
                self._register_success()   # la transcripción pasó → relajar el gap
                # Verde recién acá: la llamada a Groq fue OK. Antes se ponía verde
                # ANTES de llamar, así que un fallo dejaba el indicador en verde.
                self.sig_status.emit("green")
                if not es_transcripcion_valida(raw):
                    log.info(f"[FILTRO] {repr(raw[:60])}")
                    return

                # Deduplicación: descartar si es la misma frase que ya mostramos hace poco
                now = time.time()
                raw_key = raw.lower().strip()
                if (raw_key == self._last_sys_text
                        and now - self._last_sys_time < self._DEDUP_WINDOW_S):
                    log.info(f"[DEDUP] ignorado (duplicado reciente): {repr(raw[:60])}")
                    return

                corregido = corregir_transcripcion(raw)
                if corregido != raw:
                    log.info(f"[GLOSARIO] {repr(raw[:50])} → {repr(corregido[:50])}")
                    raw = corregido

                if self._es_duplicado_global(raw):
                    log.info(f"[DEDUP-X] mic ya tradujo esto, omito sys: {repr(raw[:60])}")
                    return

                # Recién acá, tras pasar TODOS los filtros, marcamos esta frase como la
                # última procesada por el stream de sistema (antes se pisaba aunque el
                # dedup global la descartara, rompiendo el dedup de la frase siguiente).
                self._last_sys_text = raw_key
                self._last_sys_time = now

                self.sig_partial.emit(raw)

                if lang == "es":
                    # Español detectado → traducir a inglés
                    log.info(f"[ES] ({time.time()-t0:.1f}s) {raw[:70]}")
                    aprendida = traduccion_aprendida(raw, "es2en")
                    if aprendida:
                        log.info(f"[APRENDIDO] ({time.time()-t0:.1f}s): {aprendida[:70]}")
                        self.sig_final.emit(raw, aprendida, "es2en")
                        registrar("es2en", raw, aprendida)
                        return
                    translated = translate_es_to_en(raw)
                    log.info(f"[→EN] ({time.time()-t0:.1f}s) {translated[:70]}")
                    self.sig_final.emit(raw, translated, "es2en")
                    registrar("es2en", raw, translated)
                    registrar_traduccion("es2en", raw, translated)
                else:
                    # No es español → traducir a español (el usuario lee español).
                    # Lo normal es inglés (audio de los compañeros). Si Whisper detecta
                    # OTRO idioma (fr/de/…) lo logueamos para que no sea silencioso:
                    # Llama igual lo lleva a español, pero queda registro del caso raro.
                    if lang not in ("en", "es"):
                        log.warning(f"[IDIOMA] detectado '{lang}' (no en/es) → traduzco a español igual")
                    log.info(f"[EN] ({time.time()-t0:.1f}s) {raw[:70]}")
                    directa = traduccion_directa(raw)
                    if directa:
                        log.info(f"[GLOSARIO] directa ({time.time()-t0:.1f}s): {directa[:70]}")
                        self.sig_final.emit(raw, directa, "en2es")
                        registrar("en2es", raw, directa)
                        return
                    aprendida = traduccion_aprendida(raw, "en2es")
                    if aprendida:
                        log.info(f"[APRENDIDO] ({time.time()-t0:.1f}s): {aprendida[:70]}")
                        self.sig_final.emit(raw, aprendida, "en2es")
                        registrar("en2es", raw, aprendida)
                        return
                    translated = translate_en_to_es(raw)
                    log.info(f"[→ES] ({time.time()-t0:.1f}s) {translated[:70]}")
                    self.sig_final.emit(raw, translated, "en2es")
                    registrar("en2es", raw, translated)
                    registrar_traduccion("en2es", raw, translated)
                return

            except Exception as e:
                accion = self._evaluar_error_api(e, attempt, MAX_RETRIES, tag="")
                if accion == "rpd":
                    self._activar_rendicion_rpd()
                    return
                if accion == "retry":
                    continue
                self.sig_status.emit("red")   # error final
                return

    def _process_mic(self, wav_bytes: bytes, captured_at: float = None):
        if self._rpd_rendido():
            return   # cuota diaria agotada — no pedir hasta el reset
        MAX_RETRIES = 3
        ultimo_es = ""   # última transcripción ES (para avisar si la traducción falla)
        for attempt in range(MAX_RETRIES):
            try:
                # Igual que sys: el worker entrega el más reciente; no se salta nada.
                self._throttle_mic()
                t0 = time.time()

                es_raw, _ = transcribe_audio(wav_bytes, language="es")
                ultimo_es = es_raw or ultimo_es
                self._register_success()   # la transcripción pasó → relajar el gap
                if not es_raw or len(es_raw.strip()) < 2:
                    return
                if not es_transcripcion_valida(es_raw):
                    log.info(f"[MIC-FILTRO] {repr(es_raw[:60])}")
                    return

                corregido = corregir_transcripcion(es_raw)
                if corregido != es_raw:
                    es_raw = corregido

                if self._es_duplicado_global(es_raw):
                    log.info(f"[DEDUP-X] sys ya tradujo esto, omito mic: {repr(es_raw[:60])}")
                    return

                log.info(f"[MIC-ES] ({time.time()-t0:.1f}s) {es_raw[:70]}")
                aprendida = traduccion_aprendida(es_raw, "es2en")
                if aprendida:
                    log.info(f"[MIC-APRENDIDO] ({time.time()-t0:.1f}s): {aprendida[:70]}")
                    pyperclip.copy(aprendida)
                    self.sig_mic_result.emit(es_raw, aprendida)
                    registrar("mic", es_raw, aprendida)
                    return
                en_translated = translate_es_to_en(es_raw)
                log.info(f"[MIC-EN] ({time.time()-t0:.1f}s) {en_translated[:70]}")
                pyperclip.copy(en_translated)
                self.sig_mic_result.emit(es_raw, en_translated)
                registrar("mic", es_raw, en_translated)
                registrar_traduccion("es2en", es_raw, en_translated)
                return

            except Exception as e:
                accion = self._evaluar_error_api(e, attempt, MAX_RETRIES, tag="MIC-")
                if accion == "rpd":
                    self._activar_rendicion_rpd()
                    return
                if accion == "retry":
                    continue
                # Error final: avisar en el overlay en vez de quedarse mudo, así
                # sabés que tu mensaje NO se tradujo (antes fallaba en silencio).
                if ultimo_es.strip():
                    self.sig_mic_result.emit(ultimo_es, "⚠ no se pudo traducir — reintentá")
                else:
                    self.sig_mic_result.emit("", "⚠ no se pudo traducir tu voz — reintentá")
                return

    def stop(self):
        self.running = False

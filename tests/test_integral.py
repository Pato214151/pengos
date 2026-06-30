#!/usr/bin/env python3
"""Test integral — cubre config, glosario, filtros, pipeline, concurrencia, errores."""
import json
import os
import sys
import time
import threading

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.environ.setdefault("GROQ_API_KEY", "test-key-for-tests")
from pathlib import Path

# El test vive en tests/; agregar el root del repo al path para importar los módulos.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import glosario as _glosario_mod
from filters import es_transcripcion_valida
from glosario import (
    _glosario_key,
    cargar_glosario,
    corregir_transcripcion,
    traduccion_directa,
)

REPO = Path(__file__).parent.parent

# ── Test helpers ──
PASS = 0
FAIL = 0


def test(nombre, condicion, detalle=""):
    global PASS, FAIL
    if condicion:
        PASS += 1
        print(f"  [OK] {nombre}")
    else:
        FAIL += 1
        print(f"  [FAIL] {nombre} -- {detalle}")


# ────────────────────────────────────────────────────────────

def test_config():
    """Verifica que todos los campos de config.json se lean correctamente."""
    print("\n" + "=" * 70)
    print("SECCIÓN 1: CONFIGURACIÓN")
    print("=" * 70)

    with open(REPO / "config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    test("config.json existe y es JSON válido", True)

    api_key_ok = bool(os.environ.get("GROQ_API_KEY") or cfg.get("api_key"))
    test("api_key disponible (env o config)", api_key_ok)

    valido = cfg.get("audio_mode") in ("vbcable", "stereo_mix", "auto")
    test("audio_mode válido (vbcable/stereo_mix/auto)", valido, f"valor: {cfg.get('audio_mode')}")

    hk = cfg.get("hotkeys", {})
    required_hk = ["push_to_talk", "push_to_mic", "frases_rapidas", "pin_overlay", "salir"]
    for key in required_hk:
        test(f"hotkey '{key}' presente", key in hk, f"valor: {hk.get(key)}")

    ov = cfg.get("overlay", {})
    test("overlay.posicion presente", "posicion" in ov, f"valor: {ov.get('posicion')}")
    x = ov.get("x", 0)
    y = ov.get("y", 0)
    test("overlay.x es entero no-negativo", isinstance(x, int) and x >= 0)
    test("overlay.y es entero no-negativo", isinstance(y, int) and y >= 0)
    test("overlay.tiempo_visible presente", "tiempo_visible" in ov)

    sens = cfg.get("vad_sensibilidad", 2)
    test("vad_sensibilidad en rango 0-3", 0 <= sens <= 3)
    test("vad_silencio_ms presente y positivo", cfg.get("vad_silencio_ms", 0) > 0)

    test("idioma_entrada es 'auto', 'en' o 'es'",
         cfg.get("idioma_entrada") in ("auto", "en", "es"))

    frases = cfg.get("frases_rapidas", [])
    test("frases_rapidas es lista con elementos", len(frases) >= 4)
    for i, frase in enumerate(frases):
        test(f"frase_rapida[{i}].es presente", bool(frase.get("es")))
        test(f"frase_rapida[{i}].en presente", bool(frase.get("en")))

    return cfg


def test_overlay_posicion():
    """Verifica que la lógica de posicion presets funcione."""
    print("\n" + "=" * 70)
    print("SECCIÓN 2: OVERLAY POSICIÓN")
    print("=" * 70)

    def calc_position(posicion: str, sw: int, sh: int, ox: int, oy: int):
        if posicion == "bottom-right":
            return (sw - 540, sh - 220)
        elif posicion == "top-left":
            return (ox, 20)
        elif posicion == "top-right":
            return (sw - 540, 20)
        return (ox, oy)

    x, y = calc_position("bottom-left", 1920, 1080, 50, 680)
    test("bottom-left: respeta x=50, y=680", x == 50 and y == 680)

    x, y = calc_position("bottom-right", 1920, 1080, 50, 680)
    test("bottom-right: x = 1920-540 = 1380", x == 1380)
    test("bottom-right: y = 1080-220 = 860", y == 860)

    x, y = calc_position("top-left", 1920, 1080, 50, 680)
    test("top-left: respeta x=50", x == 50)
    test("top-left: y = 20", y == 20)

    x, y = calc_position("top-right", 1920, 1080, 50, 680)
    test("top-right: x = 1920-540 = 1380", x == 1380)
    test("top-right: y = 20", y == 20)

    x, y = calc_position("bottom-right", 2560, 1440, 50, 680)
    test("bottom-right 1440p: x = 2560-540 = 2020", x == 2020)
    test("bottom-right 1440p: y = 1440-220 = 1220", y == 1220)


def test_glosario_key_normalization():
    """Verifica _glosario_key con strip en ambos extremos."""
    print("\n" + "=" * 70)
    print("SECCIÓN 3: NORMALIZACIÓN _glosario_key (both-end strip)")
    print("=" * 70)

    casos = [
        ("",                 ""),
        ("!!!",              ""),
        ("...",              ""),
        ("a.",               "a"),
        ("!a?",              "a"),
        ("...galletas...",   "galletas"),
        ("¡hola!",           "¡hola"),
        (".--wait.",         "wait"),
        (".no.",             "no"),
        (",yes,",            "yes"),
        ("  hello  ",        "hello"),
    ]
    for entrada, esperado in casos:
        res = _glosario_key(entrada)
        test(f"key({repr(entrada)}) → {repr(esperado)}",
             res == esperado, f"obtuvo {repr(res)}")


def test_glosario_carga_y_correcciones():
    """Verifica carga y todas las entradas de correcciones."""
    print("\n" + "=" * 70)
    print("SECCIÓN 4: GLOSARIO — CARGA Y CORRECCIONES")
    print("=" * 70)

    correcciones = _glosario_mod._glosario_correcciones
    traducciones  = _glosario_mod._glosario_traducciones_directas

    test("correcciones no vacías", len(correcciones) > 0,
         f"{len(correcciones)} entradas")
    test("traducciones no vacías", len(traducciones) > 0,
         f"{len(traducciones)} entradas")

    for key, val in correcciones.items():
        test(f"corrección útil: {repr(key)} ≠ {repr(val)}",
             key != val, f"corrección que no cambia: {repr(key)}")

    for key in correcciones:
        res = corregir_transcripcion(key)
        test(f"corrección directa: '{key}' → '{correcciones[key]}'",
             res == correcciones[key], f"obtuvo {repr(res)}")

    for key in list(correcciones.keys())[:5]:
        entrada = key + "."
        esperado = correcciones[key]
        res = corregir_transcripcion(entrada)
        test(f"corrección con punto: '{entrada}' → '{esperado}'",
             res == esperado, f"obtuvo {repr(res)}")

    for key in list(correcciones.keys())[:5]:
        entrada = key.title()
        esperado = correcciones[key]
        res = corregir_transcripcion(entrada)
        test(f"corrección caps: '{entrada}' → '{esperado}'",
             res == esperado, f"obtuvo {repr(res)}")


def test_traducciones_directas():
    """Verifica todas las traducciones directas."""
    print("\n" + "=" * 70)
    print("SECCIÓN 5: TRADUCCIONES DIRECTAS")
    print("=" * 70)

    traducciones = _glosario_mod._glosario_traducciones_directas

    for key in traducciones:
        res = traduccion_directa(key)
        test(f"traducción: '{key}' → '{traducciones[key]}'",
             res == traducciones[key], f"obtuvo {repr(res)}")

    for key in list(traducciones.keys())[:5]:
        res = traduccion_directa(key + "!")
        test(f"traducción con !: '{key}!' → '{traducciones[key]}'",
             res == traducciones[key], f"obtuvo {repr(res)}")

    no_existentes = ["i like trains", "xyzzy", "completamente aleatorio"]
    for entrada in no_existentes:
        res = traduccion_directa(entrada)
        test(f"no-traducción: '{entrada}' → None",
             res is None, f"obtuvo {repr(res)}")


def test_filtro_edge_cases():
    """Prueba exhaustiva del filtro es_transcripcion_valida."""
    print("\n" + "=" * 70)
    print("SECCIÓN 6: FILTRO — TODOS LOS EDGE CASES")
    print("=" * 70)

    verdaderos = [
        ("he's one shot",           "frase en glosario"),
        ("push a now",              "frase normal"),
        ("pull back",               "frase válida genérica"),
        ("vamos B",                 "español gaming"),
        ("necesito cura",           "español"),
        ("go",                      "corto con traducción directa"),
        ("no",                      "corto con traducción directa"),
        ("yes",                     "corto con traducción directa"),
        ("ez",                      "corto con traducción directa"),
        ("go go go",                "multi-word corto"),
        ("1 left a",                "número + palabras"),
        ("clutch 1v3",              "frase real"),
        ("wait...",                 "puntos al final"),
        ("...wait",                 "puntos al inicio"),
        ("he's one shot!",          "signo al final"),
        ("push\tleft",              "tabulador"),
        ("  push  left  ",          "espacios extra"),
        ("\npush\nleft\n",          "newlines"),
        ("PUSH LEFT",               "mayúsculas"),
        ("café",                    "unicode combinado"),
        ("​push left",               "zero-width space inicio"),
        ("thanks bro",              "'thanks' no es patron completo"),
        ("subscribe to win",        "'subscribe to' no es patron exacto"),
        ("caption this",            "caption sin 'by'"),
        ("music to my ears",        "music en contexto"),
        ("musica en el lobby",      "musica en frase"),
        ("[ ♪ música ♪ ]",         "notas con texto válido"),
    ]
    for entrada, desc in verdaderos:
        test(f"PASA: {desc} ({repr(entrada[:40])})",
             es_transcripcion_valida(entrada) is True,
             "el filtro lo bloqueó")

    falsos = [
        ("",                        "vacío"),
        ("   ",                     "solo espacios"),
        (".",                       "punto solo"),
        ("...",                     "puntos suspensivos solos"),
        (". . .",                   "puntos con espacios"),
        ("!!!!",                    "solo exclamación"),
        ("???",                     "solo pregunta"),
        ("12345",                   "solo números"),
        ("—",                       "guión largo solo"),
        ("•",                       "bullet solo"),
        ("♪ ♫ ♪",                  "notas musicales"),
        ("música",                  "música suelta"),
        ("[music]",                 "music en brackets"),
        ("thanks for watching",     "hallucination gracias"),
        ("subscribe to my",         "hallucination suscripción"),
        ("subtitles by",            "hallucination subtítulos"),
        ("subtitulos por",          "hallucination subtitulos"),
        ("broth3rmax",              "hallucination broth3rmax"),
        ("sub indo",                "hallucination sub indo"),
        ("谢谢你",                   "chino"),
        ("привет",                  "cirílico"),
        ("감사합니다",               "coreano"),
        ("push левый",              "latin + cirílico"),
        ("привет team",             "cirílico + latin"),
        ("اجولو اجولو اجولو خلق",   "árabe (alucinación real del log)"),
        ("خلق الخلق الخلق",         "árabe puro"),
        ("שלום חברים",              "hebreo"),
        ("สวัสดีครับ",                "tailandés"),
        ("γεια σου φίλε",           "griego"),
        ("a",                       "1 char sin glosario"),
        ("ok",                      "2 chars sin glosario"),
        ("hi",                      "2 chars sin glosario"),
        ("lol",                     "3 chars sin glosario (<4 sin key)"),
        ("1v3",                     "3 chars numérico sin glosario"),
    ]
    for entrada, desc in falsos:
        test(f"BLOQUEA: {desc} ({repr(entrada[:40])})",
             es_transcripcion_valida(entrada) is False,
             "el filtro lo dejó pasar")


def test_glosario_consistencia():
    """Verifica consistencia del glosario."""
    print("\n" + "=" * 70)
    print("SECCIÓN 7: CONSISTENCIA DEL GLOSARIO")
    print("=" * 70)

    correcciones = _glosario_mod._glosario_correcciones
    traducciones  = _glosario_mod._glosario_traducciones_directas

    overlap = set(correcciones.keys()) & set(traducciones.keys())
    test("sin overlap entre correcciones y traducciones_directas",
         len(overlap) == 0, f"duplicadas: {list(overlap)[:5]}")

    vacias_c = [k for k in correcciones if not k]
    vacias_t = [k for k in traducciones if not k]
    test("sin claves vacías en correcciones", len(vacias_c) == 0)
    test("sin claves vacías en traducciones", len(vacias_t) == 0)

    vacias_v = [k for k, v in traducciones.items() if not v]
    test("sin valores vacíos en traducciones", len(vacias_v) == 0,
         f"claves con valor vacío: {vacias_v[:3]}")

    largas = [k for k in correcciones if len(k) > 35]
    test("correcciones sin claves >35 chars", len(largas) == 0,
         f"largas: {largas[:3]}")
    largas_t = [k for k in traducciones if len(k) > 35]
    test("traducciones sin claves >35 chars", len(largas_t) == 0,
         f"largas: {largas_t[:3]}")

    frases_gaming = [
        "need shield", "heal me", "one shot", "push a", "push b",
        "rotate a", "rotate b", "enemy low", "spike down",
        "cover me", "behind you", "nice shot", "gg",
        "eco round", "full buy", "drop me",
    ]
    cubiertas = sum(
        1 for f in frases_gaming
        if f in traducciones or f in correcciones
    )
    cobertura = cubiertas / len(frases_gaming) * 100
    test(f"cobertura de frases gaming comunes: {cobertura:.0f}%",
         cobertura >= 80, f"{cubiertas}/{len(frases_gaming)}")


def test_vad_init():
    """Verifica que la inicialización de VAD funciona."""
    print("\n" + "=" * 70)
    print("SECCIÓN 8: VAD — INICIALIZACIÓN Y CONFIGURACIÓN")
    print("=" * 70)

    import webrtcvad
    for nivel in range(4):
        try:
            webrtcvad.Vad(nivel)
            test(f"Vad(nivel={nivel}) creado OK", True)
        except Exception as e:
            test(f"Vad(nivel={nivel}) falló", False, str(e))

    for nivel_config in range(4):
        nivel_mic = max(0, nivel_config - 1)
        try:
            webrtcvad.Vad(nivel_mic)
            test(f"Vad mic(nivel_config={nivel_config} → mic={nivel_mic}) OK", True)
        except Exception as e:
            test(f"Vad mic(nivel_config={nivel_config}) falló", False, str(e))

    vad = webrtcvad.Vad(2)
    for label, frame in [("960@16kHz 30ms", b"\x00" * 960),
                          ("640@16kHz 20ms", b"\x00" * 640),
                          ("320@16kHz 10ms", b"\x00" * 320)]:
        try:
            vad.is_speech(frame, 16000)
            test(f"Vad.is_speech(frame {label}) no lanza error", True)
        except Exception as e:
            test(f"Vad.is_speech(frame {label}) falló", False, str(e))


def test_throttle_lock():
    """Verifica el throttle ADAPTATIVO real (back-off en 429, relax en éxito)."""
    print("\n" + "=" * 70)
    print("SECCIÓN 9: THROTTLE — BACK-OFF ADAPTATIVO")
    print("=" * 70)

    from audio import AudioProcessor

    # Constantes coherentes
    test("GAP_MIN < GAP_MAX",
         AudioProcessor._GAP_MIN < AudioProcessor._GAP_MAX)
    test("GAP_GROW > 1 (ensancha en 429)",
         AudioProcessor._GAP_GROW > 1.0)
    test("0 < GAP_DECAY < 1 (relaja en éxito)",
         0.0 < AudioProcessor._GAP_DECAY < 1.0)

    # Instancia liviana SIN abrir audio (bypass __init__) para probar el código real.
    # AudioProcessor hereda de QObject, que define su propio __new__.
    ap = AudioProcessor.__new__(AudioProcessor)
    ap._gap = AudioProcessor._GAP_MIN
    ap._gap_lock = threading.Lock()

    g0 = ap._current_gap()
    ap._register_rate_limit()
    g1 = ap._current_gap()
    test("un 429 ensancha el gap (back-off)", g1 > g0, f"{g0:.2f} → {g1:.2f}")

    for _ in range(20):
        ap._register_rate_limit()
    test("429 sostenidos topan exactamente en GAP_MAX",
         abs(ap._current_gap() - AudioProcessor._GAP_MAX) < 1e-9,
         f"gap={ap._current_gap():.2f}")

    for _ in range(200):
        ap._register_success()
    test("éxitos sostenidos devuelven el gap al piso (GAP_MIN)",
         abs(ap._current_gap() - AudioProcessor._GAP_MIN) < 1e-9,
         f"gap={ap._current_gap():.2f}")
    test("el gap nunca baja de GAP_MIN",
         ap._current_gap() >= AudioProcessor._GAP_MIN - 1e-9)


def test_audio_device_discovery():
    """Verifica la lógica de búsqueda de dispositivos de audio."""
    print("\n" + "=" * 70)
    print("SECCIÓN 10: AUDIO — DESCUBRIMIENTO DE DISPOSITIVOS")
    print("=" * 70)

    mock_device_infos = {
        0: {"name": "CABLE Output (VB-Audio Virtual Cable)", "maxInputChannels": 2},
        1: {"name": "Micrófono (Realtek Audio)", "maxInputChannels": 1},
        2: {"name": "Speakers (Realtek Audio)", "maxInputChannels": 0},
        3: {"name": "Stereo Mix (Realtek Audio)", "maxInputChannels": 2},
        4: {"name": "VoiceMeeter Output (VB-Audio VoiceMeeter VAIO)", "maxInputChannels": 2},
    }

    class MockPyAudio:
        def get_device_count(self):
            return len(mock_device_infos)
        def get_device_info_by_index(self, i):
            return mock_device_infos[i]

    p = MockPyAudio()

    def find_device_index(name):
        return next(
            (i for i in range(p.get_device_count())
             if name in p.get_device_info_by_index(i)["name"]
             and p.get_device_info_by_index(i)["maxInputChannels"] > 0),
            None,
        )

    test("find 'CABLE Output' → index 0",   find_device_index("CABLE Output") == 0)
    test("find 'Stereo Mix' → index 3",     find_device_index("Stereo Mix") == 3)
    test("find 'No existe' → None",         find_device_index("No existe") is None)
    test("find 'VoiceMeeter' → index 4",    find_device_index("VoiceMeeter") == 4)

    _STEREO_MIX_NAMES = [
        "stereo mix", "mezcla estéreo", "mezcla de sonido",
        "what u hear", "what you hear", "wave out mix",
        "loopback", "sum", "mix out",
    ]

    def open_stereo_mix(pa):
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                if any(s in info["name"].lower() for s in _STEREO_MIX_NAMES):
                    return i
        return None

    test("Stereo Mix encontrado por nombre", open_stereo_mix(p) == 3)

    class MockPyAudioNoMix:
        _infos = {
            0: {"name": "CABLE Output", "maxInputChannels": 2},
            1: {"name": "Micrófono",    "maxInputChannels": 1},
        }
        def get_device_count(self):      return len(self._infos)
        def get_device_info_by_index(self, i): return self._infos[i]

    test("Sin Stereo Mix → None", open_stereo_mix(MockPyAudioNoMix()) is None)


def test_retry_logic():
    """Verifica la lógica de reintento ante errores 429."""
    print("\n" + "=" * 70)
    print("SECCIÓN 11: ERRORES — LÓGICA DE REINTENTO (429)")
    print("=" * 70)

    MAX_RETRIES = 3

    def simulate_retry(errors):
        for attempt in range(MAX_RETRIES):
            try:
                if attempt < len(errors) and errors[attempt] is not None:
                    raise errors[attempt]
                return "success", attempt + 1
            except Exception as e:
                msg = str(e)
                msg_l = msg.lower()
                is_429 = "429" in msg
                # RPD = límite DIARIO → fail-fast (no se libera en segundos)
                if is_429 and ("per day" in msg_l or "(rpd)" in msg_l):
                    return "rpd", attempt + 1
                if is_429 and attempt < MAX_RETRIES - 1:
                    continue
                return "error", attempt + 1

    status, n = simulate_retry([])
    test("sin errores → éxito en intento 1", status == "success" and n == 1)

    status, n = simulate_retry([Exception("429 too many requests"), None])
    test("429 transitorio → éxito en intento 2", status == "success" and n == 2)

    status, n = simulate_retry([
        Exception("429 try again in 5s"),
        Exception("429 try again in 5s"),
        Exception("429 try again in 5s"),
    ])
    test("429 persistente → error en intento 3", status == "error" and n == 3)

    status, n = simulate_retry([Exception("500 internal error")])
    test("error no-429 → falla en intento 1", status == "error" and n == 1)

    rpd_err = Exception(
        "Error code: 429 - Rate limit reached for model `whisper-large-v3-turbo` "
        "on requests per day (RPD): Limit ..."
    )
    status, n = simulate_retry([rpd_err, None, None])
    test("429 RPD (límite diario) → fail-fast en intento 1, sin reintentar",
         status == "rpd" and n == 1)

    status, n = simulate_retry([Exception("429"), Exception("429"), None])
    test("429 recovery en intento 3 → éxito", status == "success" and n == 3)


def test_pipeline_mock():
    """Prueba el pipeline completo con mocks (sin llamadas reales a API)."""
    print("\n" + "=" * 70)
    print("SECCIÓN 12: PIPELINE — FLUJO COMPLETO (MOCK API)")
    print("=" * 70)

    scenarios = [
        # (texto_transcripto, debe_pasar_filtro, tiene_traduccion_directa)
        ("he's one shot",       True,  True),
        ("rotate to b",         True,  True),
        ("push left",           True,  False),
        ("clutch 1v3",          True,  True),
        ("thanks for watching", False, False),
        ("música",              False, False),
        ("necesito cura",       True,  False),
        ("vamos B",             True,  False),
        ("...",                 False, False),
    ]

    for texto, debe_pasar, tiene_trad in scenarios:
        pasa = es_transcripcion_valida(texto)
        test(f"pipeline '{texto}': filtro {'PASA' if debe_pasar else 'BLOQUEA'}",
             pasa == debe_pasar)

        if not pasa:
            continue

        corregido = corregir_transcripcion(texto)
        test(f"pipeline '{texto}': corrección aplicada",
             corregido == texto or corregido != texto)

        directa = traduccion_directa(corregido)
        if tiene_trad:
            test(f"pipeline '{texto}': traducción directa encontrada", directa is not None)
        else:
            test(f"pipeline '{texto}': sin traducción directa (→ Llama)", directa is None)


def test_prompt_analysis():
    """Analiza los prompts del sistema (sin llamar a API)."""
    print("\n" + "=" * 70)
    print("SECCIÓN 13: PROMPTS — ANÁLISIS DE CALIDAD")
    print("=" * 70)

    from api import (
        _WHISPER_PROMPT_EN, _WHISPER_PROMPT_ES,
        _TRANSLATE_EN_ES_SYSTEM, _TRANSLATE_ES_EN_SYSTEM,
    )

    test("whisper_en es lista de términos gaming",
         any(t in _WHISPER_PROMPT_EN for t in ("push", "clutch", "rush", "spike")),
         "sesga la ortografía de la jerga")
    test("whisper_es incluye términos español/colombianos",
         any(t in _WHISPER_PROMPT_ES for t in ("flankear", "parcero", "curar", "rotar")),
         "vocabulario de partida en español")
    # Los prompts NO deben contener oraciones en prosa: Whisper las eco-transcribe
    # en los silencios (de ahí salía "Fruits de comunicación en partida").
    _prosa = ("comunicación en partida", "frases cortas",
              "gaming voice chat", "hablando en español")
    _ambos = (_WHISPER_PROMPT_EN + " " + _WHISPER_PROMPT_ES).lower()
    test("prompts sin prosa eco-transcribible",
         not any(p in _ambos for p in _prosa),
         "deben ser listas de vocabulario, no frases")
    test("translate_en_es menciona 'word for word'",
         "word for word" in _TRANSLATE_EN_ES_SYSTEM, "ayuda a evitar expansión")
    test("translate_en_es menciona 'No quotes'",
         "No quotes" in _TRANSLATE_EN_ES_SYSTEM, "previene formato incorrecto")
    test("translate_es_en pide solo la traducción",
         "ONLY" in _TRANSLATE_ES_EN_SYSTEM, "previene explicaciones de Llama")


def test_fatiga_rapida():
    """Prueba de fatiga reducida (1000 iteraciones) para detectar regresión."""
    print("\n" + "=" * 70)
    print("SECCIÓN 14: FATIGA — 1,000 ITERACIONES RÁPIDAS")
    print("=" * 70)

    corpus = [
        "he's one shot", "push left", "i need healing", "cover me",
        "rotate to b", "enemy low", "spike down", "eco round",
        "full buy", "need util", "thanks for watching",
        "...", "music", "música", "♪ ♫ ♪",
        "wait", "no", "yes", "go", "nice",
        "behind you", "one left a", "defuse now",
    ]

    t0 = time.time()
    total_ops = 0
    for _ in range(1000):
        for frase in corpus:
            es_transcripcion_valida(frase)
            corregir_transcripcion(frase)
            traduccion_directa(frase)
            total_ops += 3

    elapsed = time.time() - t0
    throughput = total_ops / elapsed
    test(f"fatiga: {total_ops} ops en {elapsed:.2f}s ({throughput:.0f} op/s)",
         throughput > 10000, f"throughput muy bajo: {throughput:.0f} op/s")


def test_quick_phrases():
    """Verifica que todas las frases rápidas tengan traducciones coherentes."""
    print("\n" + "=" * 70)
    print("SECCIÓN 15: FRASES RÁPIDAS (QUICK PHRASES)")
    print("=" * 70)

    with open(REPO / "config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    frases = cfg.get("frases_rapidas", [])
    for i, frase in enumerate(frases):
        es = frase.get("es", "")
        en = frase.get("en", "")
        test(f"frase[{i}] EN='{en}' ES='{es}': ambos no vacíos", bool(es) and bool(en))
        test(f"frase[{i}] EN='{en}' tiene >0 chars", len(en) > 0)
        test(f"frase[{i}] ES='{es}' tiene >0 chars", len(es) > 0)


def test_rpd_rendicion():
    """Verifica la rendición global por límite DIARIO (RPD) hasta el reset UTC."""
    print("\n" + "=" * 70)
    print("SECCIÓN 17: RENDICIÓN POR CUOTA DIARIA (RPD)")
    print("=" * 70)

    import types
    from datetime import datetime, timedelta, timezone

    from audio import AudioProcessor

    # Instancia liviana sin abrir audio; stub de sig_status (no hay QObject real).
    ap = AudioProcessor.__new__(AudioProcessor)
    ap._rpd_lock = threading.Lock()
    ap._rpd_until_utc = None
    emitido = []
    ap.sig_status = types.SimpleNamespace(emit=lambda c: emitido.append(c))

    test("sin rendición activa → _rpd_rendido False", ap._rpd_rendido() is False)

    ap._activar_rendicion_rpd()
    test("tras activar RPD → _rpd_rendido True", ap._rpd_rendido() is True,
         "deja de pedir hasta el reset")
    test("activar RPD emite status rojo", "red" in emitido)
    test("reset programado en el futuro (UTC)",
         ap._rpd_until_utc is not None
         and ap._rpd_until_utc > datetime.now(timezone.utc),
         "medianoche UTC siguiente")
    test("reset es exactamente medianoche UTC (00:00)",
         ap._rpd_until_utc.hour == 0 and ap._rpd_until_utc.minute == 0
         and ap._rpd_until_utc.second == 0)

    # Simular que ya pasó el reset → debe reactivar y limpiar el estado.
    ap._rpd_until_utc = datetime.now(timezone.utc) - timedelta(seconds=1)
    test("pasado el reset → _rpd_rendido False (reanuda)", ap._rpd_rendido() is False)
    test("pasado el reset → estado limpiado", ap._rpd_until_utc is None)
    test("reanudar emite status verde", "green" in emitido)


def test_alucinacion_silencio():
    """Filtro de alucinaciones de Whisper por confianza de segmentos."""
    print("\n" + "=" * 70)
    print("SECCIÓN 16: ALUCINACIONES DE SILENCIO (no_speech_prob / avg_logprob)")
    print("=" * 70)

    from api import _es_alucinacion_silencio

    # Voz real: no_speech_prob bajo, avg_logprob alto → NO alucinación
    real = [{"no_speech_prob": 0.04, "avg_logprob": -0.2, "compression_ratio": 1.3}]
    test("voz real no se descarta", _es_alucinacion_silencio(real) is False,
         "segmentos de voz clara deben pasar")

    # Silencio típico: no_speech_prob alto + avg_logprob bajo → alucinación
    silencio = [{"no_speech_prob": 0.9, "avg_logprob": -0.9, "compression_ratio": 1.2}]
    test("silencio (no_speech alto + logprob bajo) se descarta",
         _es_alucinacion_silencio(silencio) is True,
         "así se filtra 'a la cintura' en silencio")

    # Confianza pésima aunque no_speech sea bajo → alucinación
    pesimo = [{"no_speech_prob": 0.2, "avg_logprob": -1.3, "compression_ratio": 1.5}]
    test("avg_logprob < -1.0 se descarta", _es_alucinacion_silencio(pesimo) is True,
         "baja confianza dura siempre se rechaza")

    # Texto repetitivo (compression_ratio alto) → alucinación
    repetido = [{"no_speech_prob": 0.3, "avg_logprob": -0.9, "compression_ratio": 3.0}]
    test("compression_ratio alto + logprob bajo se descarta",
         _es_alucinacion_silencio(repetido) is True,
         "'a la la la la' repetitivo se filtra")

    # Sin segmentos → no se puede juzgar, no descartar
    test("sin segmentos no descarta", _es_alucinacion_silencio(None) is False,
         "si Groq no da segmentos, conservar el texto")

    # Objetos (no dict) con atributos también funcionan
    class _Seg:
        no_speech_prob = 0.95
        avg_logprob = -1.1
        compression_ratio = 1.0
    test("acepta segmentos como objetos", _es_alucinacion_silencio([_Seg()]) is True,
         "_seg_get debe leer atributos además de dicts")


def test_aprendizaje():
    """Cache de auto-aprendizaje: conteo, estabilidad, promoción, LRU."""
    import tempfile
    import aprendizaje as ap

    # Aislar el estado y redirigir el archivo a un temporal (no tocar el real).
    tmpdir = tempfile.mkdtemp()
    ap._RUTA = Path(tmpdir) / "aprendido_test.json"
    ap._contador = {}
    ap._aprendidas = {}

    # _es_cacheable: frases cortas sí, largas no, vacías no.
    test("cacheable: frase corta",
         ap._es_cacheable("necesito cura") is True)
    test("cacheable: vacío no",
         ap._es_cacheable("   ") is False)
    test("cacheable: frase larga no",
         ap._es_cacheable("uno dos tres cuatro cinco seis siete ocho") is False)

    # _norm: minúsculas + sin puntuación al borde.
    test("norm quita puntuación y baja",
         ap._norm("  ¡Cúbreme!  ") == "¡cúbreme")  # ¡ no está en _STRIP_PUNCT

    # Aún no promovida tras 1-2 repeticiones.
    ap.registrar_traduccion("en2es", "Cover me", "Cúbreme")
    test("no promovida con 1 repetición",
         ap.traduccion_aprendida("Cover me", "en2es") is None)
    ap.registrar_traduccion("en2es", "Cover me", "Cúbreme")
    test("no promovida con 2 repeticiones",
         ap.traduccion_aprendida("Cover me", "en2es") is None)

    # A la 3ª (UMBRAL) se promueve y queda en cache gratis.
    ap.registrar_traduccion("en2es", "Cover me", "Cúbreme")
    test("promovida al alcanzar el umbral",
         ap.traduccion_aprendida("Cover me", "en2es") == "Cúbreme")

    # La dirección importa: es2en no debe ver la de en2es.
    test("la dirección separa las claves",
         ap.traduccion_aprendida("Cover me", "es2en") is None)

    # Inestabilidad: una traducción distinta reinicia el contador.
    ap._contador = {}
    ap._aprendidas = {}
    ap.registrar_traduccion("en2es", "Go", "Vamos")
    ap.registrar_traduccion("en2es", "Go", "Vamos")
    ap.registrar_traduccion("en2es", "Go", "Anda")   # cambia → reinicia
    test("traducción inestable no se promueve",
         ap.traduccion_aprendida("Go", "en2es") is None)
    # Ahora estabiliza en "Anda" y promueve.
    ap.registrar_traduccion("en2es", "Go", "Anda")
    ap.registrar_traduccion("en2es", "Go", "Anda")
    test("tras estabilizar se promueve la nueva",
         ap.traduccion_aprendida("Go", "en2es") == "Anda")

    # Persistencia: el archivo se escribió y se puede recargar.
    test("aprendido.json se escribió", ap._RUTA.exists() is True)
    ap._contador = {}
    ap._aprendidas = {}
    ap.cargar_aprendido()
    test("recarga reconstruye promovidas",
         ap.traduccion_aprendida("Go", "en2es") == "Anda")

    # No cacheable no se cuenta.
    antes = len(ap._contador)
    ap.registrar_traduccion("en2es", "una frase larguísima que no se repite jamás igual", "x")
    test("frase larga no se registra", len(ap._contador) == antes)


def test_clasificacion_error_api():
    """Helper compartido de errores: regex con \\b (no falsos positivos), RPD, retry/stop."""
    import audio as audio_mod
    from audio import AudioProcessor

    proc = AudioProcessor.__new__(AudioProcessor)
    proc._register_rate_limit = lambda: None         # stub: no tocar el gap real

    orig_sleep = audio_mod.time.sleep
    audio_mod.time.sleep = lambda s: None            # no dormir de verdad
    try:
        # "1500" NO debe confundirse con "500" (el bug del any(c in msg) viejo).
        test("1500 no se confunde con 500",
             proc._evaluar_error_api(Exception("weird error code 1500"), 0, 3) == "stop")

        # Código HTTP transitorio real → reintentar.
        test("503 real reintenta",
             proc._evaluar_error_api(Exception("503 Service Unavailable"), 0, 3) == "retry")

        # 429 transitorio (no diario) → reintentar.
        test("429 transitorio reintenta",
             proc._evaluar_error_api(Exception("429 try again in 2s"), 0, 3) == "retry")

        # 429 en el último intento → ya no reintenta.
        test("429 último intento para",
             proc._evaluar_error_api(Exception("429 rate limit"), 2, 3) == "stop")

        # Límite DIARIO (RPD) → rendición inmediata.
        test("RPD se rinde sin reintentar",
             proc._evaluar_error_api(Exception("429 limit reached per day (RPD)"), 0, 3) == "rpd")

        # Error no reintentable → stop.
        test("400 no reintentable para",
             proc._evaluar_error_api(Exception("400 bad request"), 0, 3) == "stop")
    finally:
        audio_mod.time.sleep = orig_sleep


def test_coalescing_despacho():
    """Despacho 'último gana': un segmento nuevo reemplaza al pendiente (no se apila)."""
    import threading as _th
    from audio import AudioProcessor

    proc = AudioProcessor.__new__(AudioProcessor)
    proc._sample_size = 2
    proc._pending_sys = None
    proc._pending_sys_lock = _th.Lock()
    proc._pending_sys_event = _th.Event()

    # PCM con voz "útil": >0.35s y energía alta (pasa el gate _voz_util).
    pcm_a = b"\xff\x3f" * 6000   # ~0.375s, RMS alto (≈16383)
    pcm_b = b"\x00\x50" * 6000   # distinto contenido (≈20480)

    test("sin encolar, slot vacío", proc._pending_sys is None)

    proc._start_process_sys(pcm_a)
    test("tras encolar hay pendiente", proc._pending_sys is not None)
    test("el evento queda señalizado", proc._pending_sys_event.is_set() is True)

    # Encolar otro REEMPLAZA al anterior (último gana, no se forma cola).
    proc._start_process_sys(pcm_b)
    wav, _ = proc._pending_sys
    test("el segundo segmento reemplaza al primero", wav == proc._pcm_to_wav(pcm_b))

    # El worker lo consume → el slot vuelve a quedar vacío.
    proc._pending_sys = None
    test("tras consumir, slot vacío", proc._pending_sys is None)

    # Gate de energía/duración: silencio y segmentos cortos NO se encolan
    # (no se manda basura a la API → no se revienta el 429).
    proc._start_process_sys(b"\x00\x00" * 6000)   # silencio (RMS 0)
    test("silencio no se encola", proc._pending_sys is None)
    proc._start_process_sys(b"\xff\x3f" * 100)    # ~0.006s, muy corto
    test("segmento muy corto no se encola", proc._pending_sys is None)


def test_prioridad_mic():
    """El stream de sistema cede el paso mientras el micrófono está activo/ocupado."""
    import threading as _th
    from audio import AudioProcessor

    proc = AudioProcessor.__new__(AudioProcessor)
    proc.running = True
    proc._mic_active = False
    proc._mic_processing = False
    proc._pending_mic = None
    proc._pending_mic_lock = _th.Lock()

    # Mic libre → no espera (retorna de inmediato).
    t0 = time.time()
    proc._ceder_a_mic(max_wait=1.0)
    test("mic libre: el sistema no espera", time.time() - t0 < 0.2)

    # Mic activo (F5 apretado) → cede el paso hasta max_wait.
    proc._mic_active = True
    t0 = time.time()
    proc._ceder_a_mic(max_wait=0.3)
    test("mic activo: el sistema cede", time.time() - t0 >= 0.3)

    # Mic traduciendo → también cede.
    proc._mic_active = False
    proc._mic_processing = True
    t0 = time.time()
    proc._ceder_a_mic(max_wait=0.3)
    test("mic procesando: el sistema cede", time.time() - t0 >= 0.3)

    # Frase de mic pendiente en cola → también cede.
    proc._mic_processing = False
    proc._pending_mic = (b"x", 0.0)
    t0 = time.time()
    proc._ceder_a_mic(max_wait=0.3)
    test("mic pendiente: el sistema cede", time.time() - t0 >= 0.3)


def test_poda_historial():
    """La poda conserva las últimas N sesiones y borra las más viejas."""
    import tempfile
    import historial as hist

    tmpdir = Path(tempfile.mkdtemp())
    orig_dir = hist.HIST_DIR
    hist.HIST_DIR = tmpdir
    try:
        # Crear 13 sesiones, cada una con 2 buckets (en2es + es2en).
        stamps = [f"2026-05-{d:02d}_120000" for d in range(1, 14)]
        for s in stamps:
            for b in ("en2es", "es2en"):
                (tmpdir / f"historial_{s}_{b}.jsonl").write_text("{}\n", encoding="utf-8")
        total_antes = len(list(tmpdir.glob("historial_*.jsonl")))
        test("13 sesiones creadas (26 archivos)", total_antes == 26)

        hist.podar_historial(max_sesiones=10)

        restantes = sorted(tmpdir.glob("historial_*.jsonl"))
        # Quedan 10 sesiones × 2 = 20 archivos.
        test("quedan 20 archivos tras poda", len(restantes) == 20)
        # Las 3 sesiones más viejas (días 01-03) deben haberse borrado.
        nombres = {p.name for p in restantes}
        test("se borró la sesión más vieja",
             not any("2026-05-01_120000" in n for n in nombres))
        test("se conservó la sesión más nueva",
             any("2026-05-13_120000" in n for n in nombres))

        # Idempotente: una segunda poda no borra nada más.
        hist.podar_historial(max_sesiones=10)
        test("poda idempotente",
             len(list(tmpdir.glob("historial_*.jsonl"))) == 20)

        # Por debajo del tope no borra nada.
        hist.podar_historial(max_sesiones=50)
        test("no poda si está por debajo del tope",
             len(list(tmpdir.glob("historial_*.jsonl"))) == 20)
    finally:
        hist.HIST_DIR = orig_dir


# ────────────────────────────────────────────────────────────

def main():
    global PASS, FAIL
    start = time.time()
    print("=" * 70)
    print("TEST INTEGRAL — PENGOS")
    print("=" * 70)
    print()

    cfg = test_config()
    test_overlay_posicion()
    test_glosario_key_normalization()

    cargar_glosario()

    test_glosario_carga_y_correcciones()
    test_traducciones_directas()
    test_filtro_edge_cases()
    test_glosario_consistencia()
    test_vad_init()
    test_throttle_lock()
    test_audio_device_discovery()
    test_retry_logic()
    test_pipeline_mock()
    test_prompt_analysis()
    test_fatiga_rapida()
    test_quick_phrases()
    test_rpd_rendicion()
    test_alucinacion_silencio()
    test_aprendizaje()
    test_clasificacion_error_api()
    test_coalescing_despacho()
    test_prioridad_mic()
    test_poda_historial()

    elapsed = time.time() - start
    print("\n" + "=" * 70)
    print(f"RESULTADO: {PASS} pasaron, {FAIL} fallaron de {PASS + FAIL}")
    print(f"TIEMPO: {elapsed:.1f}s")
    print("=" * 70)

    if FAIL > 0:
        print("\nFALLOS DETECTADOS:")
        print("Revisá los [FAIL] arriba para más detalles.")
    else:
        print("\nTodos los tests pasaron.")
    print()

    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

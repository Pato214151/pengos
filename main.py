#!/usr/bin/env python3
"""Pengos MVP — Overlay de traducción gamer en tiempo real."""

import signal
import sys
import threading

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from pynput import keyboard as kb

from aprendizaje import cargar_aprendido
from audio import AudioProcessor
from config import config, log
from glosario import cargar_glosario
from historial import podar_historial
from overlay import Overlay
from launcher import Launcher
from settings_panel import SettingsPanel
from tray import SystemTray

def _parse_key(s: str, key_map: dict):
    s = s.strip().lower()
    if s in key_map:
        return key_map[s]
    if len(s) == 1:
        return kb.KeyCode.from_char(s)
    return None

class PengosApp:
    def __init__(self, app):
        self.app = app
        self.processor = None
        self.overlay = None
        self.tray = None
        self.listener = None
        
    def start_pengos(self, launcher):
        launcher.hide()
        
        cargar_glosario()
        cargar_aprendido()
        podar_historial()

        self.overlay = Overlay()
        ov_cfg = config.get("overlay", {})
        screen = self.app.primaryScreen()
        sw = screen.geometry().width()  if screen else 1920
        sh = screen.geometry().height() if screen else 1080
        ox = ov_cfg.get("x", 50)
        oy = ov_cfg.get("y", 680)
        pos = ov_cfg.get("posicion", "bottom-left")
        if pos == "bottom-right":
            ox = sw - 540
            oy = sh - 220
        elif pos == "top-left":
            oy = 20
        elif pos == "top-right":
            ox = sw - 540
            oy = 20
        self.overlay.move(ox, oy)
        
        self.processor = AudioProcessor()
        self.processor.sig_partial.connect(self.overlay.show_partial,       Qt.QueuedConnection)
        self.processor.sig_final.connect(self.overlay.show_final,           Qt.QueuedConnection)
        self.processor.sig_status.connect(self.overlay.set_status,          Qt.QueuedConnection)
        self.processor.sig_ptt.connect(self.overlay.show_ptt,               Qt.QueuedConnection)
        self.processor.sig_mic.connect(self.overlay.show_mic,               Qt.QueuedConnection)
        self.processor.sig_mic_result.connect(self.overlay.show_mic_result, Qt.QueuedConnection)
        self.processor.sig_proc.connect(self.overlay.show_procesando,       Qt.QueuedConnection)

        self.tray = SystemTray()
        self.tray.sig_toggle_ptt.connect(self.processor.set_ptt, Qt.QueuedConnection)
        self.tray.sig_toggle_mic.connect(self.processor.set_mic, Qt.QueuedConnection)
        self.tray.sig_open_settings.connect(self._show_settings, Qt.QueuedConnection)
        self.tray.sig_show_overlay.connect(self.overlay.show, Qt.QueuedConnection)
        self.tray.sig_quit.connect(self.quit_app, Qt.QueuedConnection)
        
        self.processor.sig_status.connect(lambda s: self.tray.set_status('error' if s == 'red' else 'active'), Qt.QueuedConnection)
        
        audio_thread = threading.Thread(target=self.processor.run, daemon=True)
        audio_thread.start()
        if self.processor.stream_mic is not None:
            threading.Thread(target=self.processor.run_mic, daemon=True).start()
        else:
            self.processor._mic_stopped.set()

        modo_escucha = config.get("modo_escucha", "mantener")
        if modo_escucha == "siempre":
            self.processor.set_ptt(True)
            self.tray.set_ptt_state(True)
            self.tray.set_status('active')
        else:
            self.tray.set_status('waiting')

        signal.signal(signal.SIGINT, lambda *args: self.quit_app())

        self._setup_hotkeys()
        
        log.info("[OK] Pengos iniciado.")
        self.overlay.show()
        self.tray.show()

    def _setup_hotkeys(self):
        _KEY_MAP = {
            **{f"f{i}": getattr(kb.Key, f"f{i}") for i in range(1, 13)},
            "esc": kb.Key.esc, "tab": kb.Key.tab, "space": kb.Key.space,
            "insert": kb.Key.insert, "delete": kb.Key.delete,
            "home": kb.Key.home, "end": kb.Key.end,
            "up": kb.Key.up, "down": kb.Key.down,
            "left": kb.Key.left, "right": kb.Key.right,
        }

        hk = config.get("hotkeys", {})
        KEY_PTT = _parse_key(hk.get("push_to_talk", "f4"), _KEY_MAP)
        KEY_MIC = _parse_key(hk.get("push_to_mic", "f5"), _KEY_MAP)
        KEY_FRASES = _parse_key(hk.get("frases_rapidas", "f2"), _KEY_MAP)
        KEY_PIN = _parse_key(hk.get("pin_overlay", "f3"), _KEY_MAP)

        salir_parts = {p.strip().lower() for p in hk.get("salir", "ctrl+shift+q").split("+")}
        _SALIR_CHAR = next((p for p in salir_parts if p not in {"ctrl", "shift", "alt"}), "q")

        current_keys: set = set()
        _SHIFT = {kb.Key.shift, kb.Key.shift_l, kb.Key.shift_r}
        _CTRL  = {kb.Key.ctrl,  kb.Key.ctrl_l,  kb.Key.ctrl_r}
        
        modo_escucha = config.get("modo_escucha", "mantener")

        def on_press(key):
            ya_presionada = key in current_keys
            current_keys.add(key)
            try:
                if ya_presionada:
                    return
                if key == KEY_FRASES:
                    self.overlay.toggle_frases()
                if key == KEY_PIN:
                    self.overlay.toggle_pin()
                if key == KEY_PTT:
                    if modo_escucha == "siempre":
                        nuevo = not self.processor._ptt_active
                        self.processor.set_ptt(nuevo)
                        self.tray.set_ptt_state(nuevo)
                        log.info(f"[PTT] {'ON' if nuevo else 'OFF'} (toggle)")
                    else:
                        self.processor.set_ptt(True)
                        self.tray.set_ptt_state(True)
                        log.info("[PTT] ON")
                if key == KEY_MIC:
                    self.processor.set_mic(True)
                    self.tray.set_mic_state(True)
                    log.info("[MIC] ON")
                if hasattr(key, "char") and key.char in "1234":
                    self.overlay.select_frase(int(key.char) - 1)
                    
                ctrl  = bool(current_keys & _CTRL)
                shift = bool(current_keys & _SHIFT)
                char  = key.char.lower() if hasattr(key, "char") and key.char else ""
                need_ctrl  = "ctrl"  in salir_parts
                need_shift = "shift" in salir_parts
                
                if (not need_ctrl or ctrl) and (not need_shift or shift) and char == _SALIR_CHAR:
                    self.quit_app()
            except Exception:
                pass

        def on_release(key):
            current_keys.discard(key)
            if key == KEY_PTT and modo_escucha == "mantener":
                self.processor.set_ptt(False)
                self.tray.set_ptt_state(False)
                log.info("[PTT] OFF — procesando...")
            if key == KEY_MIC:
                self.processor.set_mic(False)
                self.tray.set_mic_state(False)
                log.info("[MIC] OFF — procesando...")

        self.listener = kb.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()

    def _show_settings(self):
        SettingsPanel().exec_()

    def quit_app(self):
        if self.processor:
            self.processor.stop()
        if self.listener:
            self.listener.stop()
        self.app.quit()

def _bajar_prioridad_proceso():
    """Baja la prioridad de CPU de Pengos en Windows para que el JUEGO mande.

    Pengos es una utilidad de fondo: no debe competir por CPU con el juego. Con
    BELOW_NORMAL, Windows le da el procesador al juego primero y a Pengos lo que
    sobra (sigue traduciendo bien, pero deja de causar lag/caída de FPS).
    """
    try:
        import ctypes
        from ctypes import wintypes
        BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
        # use_last_error + argtypes/restype explícitos: en Windows x64 el HANDLE es
        # de tamaño puntero (64 bits). Sin declararlo, ctypes lo trunca a 32 bits y
        # SetPriorityClass falla (era el caso del warning).
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        k32.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        k32.SetPriorityClass.restype = wintypes.BOOL
        if k32.SetPriorityClass(k32.GetCurrentProcess(), BELOW_NORMAL_PRIORITY_CLASS):
            log.info("[PERF] Prioridad del proceso bajada a BELOW_NORMAL (el juego manda).")
        else:
            err = ctypes.get_last_error()
            log.warning(f"[PERF] No se pudo bajar la prioridad del proceso (err={err}).")
    except Exception as e:
        log.warning(f"[PERF] No se pudo ajustar la prioridad del proceso: {e}")


def main():
    _bajar_prioridad_proceso()
    app = QApplication(sys.argv)

    pengos_app = PengosApp(app)
    
    launcher = Launcher()
    launcher.sig_start.connect(lambda: pengos_app.start_pengos(launcher))
    launcher.sig_settings.connect(lambda: SettingsPanel().exec_())
    launcher.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

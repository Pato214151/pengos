"""
Icono en la bandeja del sistema (junto al reloj de Windows).
Menú con: activar escucha/micrófono, abrir ajustes, mostrar overlay y salir.
Emite señales que main.py conecta con el AudioProcessor y el overlay.
"""

import sys
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QWidgetAction, QLabel

from config import log

class SystemTray(QObject):
    sig_toggle_ptt = pyqtSignal(bool)
    sig_toggle_mic = pyqtSignal(bool)
    sig_open_settings = pyqtSignal()
    sig_show_overlay = pyqtSignal()
    sig_quit = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = Path(__file__).parent / "imagen" / "pengos_icon.png"
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            log.warning(f"Icono no encontrado en {icon_path}")
            
        self.tray_icon.setToolTip("Pengos — En espera")

        # Create menu
        self.menu = QMenu()
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #161b22;
                color: #e6edf3;
                border: 1px solid #30363d;
                font-family: 'Segoe UI';
                font-size: 11px;
            }
            QMenu::item {
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background-color: #21262d;
                color: #00d4aa;
            }
            QMenu::separator {
                height: 1px;
                background-color: #30363d;
                margin: 4px 0px;
            }
        """)

        # Header
        header_action = QWidgetAction(self.menu)
        header_label = QLabel("Pengos")
        header_label.setStyleSheet("font-weight: bold; color: #8b949e; padding: 4px 10px; background: transparent;")
        header_action.setDefaultWidget(header_label)
        header_action.setEnabled(False)
        self.menu.addAction(header_action)
        
        self.menu.addSeparator()

        # Toggles
        self.action_ptt = QAction("Escucha ON/OFF", self.menu)
        self.action_ptt.setCheckable(True)
        self.action_ptt.toggled.connect(self._on_ptt_toggled)
        self.menu.addAction(self.action_ptt)

        self.action_mic = QAction("Micrófono ON/OFF", self.menu)
        self.action_mic.setCheckable(True)
        self.action_mic.toggled.connect(self._on_mic_toggled)
        self.menu.addAction(self.action_mic)
        
        self.menu.addSeparator()

        # Config / Overlay
        self.action_config = QAction("Configuración...", self.menu)
        self.action_config.triggered.connect(self.sig_open_settings.emit)
        self.menu.addAction(self.action_config)

        self.action_overlay = QAction("Mostrar Overlay", self.menu)
        self.action_overlay.triggered.connect(self.sig_show_overlay.emit)
        self.menu.addAction(self.action_overlay)

        self.menu.addSeparator()

        # Salir
        self.action_quit = QAction("Salir", self.menu)
        self.action_quit.triggered.connect(self.sig_quit.emit)
        self.menu.addAction(self.action_quit)

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self._on_tray_activated)

    def show(self):
        self.tray_icon.show()

    def set_status(self, status: str):
        """Cambia el icono/tooltip según el estado ('active', 'waiting', 'error')."""
        if status == 'active':
            self.tray_icon.setToolTip("Pengos — Activo")
        elif status == 'waiting':
            self.tray_icon.setToolTip("Pengos — En espera")
        elif status == 'error':
            self.tray_icon.setToolTip("Pengos — Error")
            self.tray_icon.showMessage("Pengos Error", "Hubo un error de conexión o audio.", QSystemTrayIcon.Warning)

    def set_ptt_state(self, active: bool):
        self.action_ptt.blockSignals(True)
        self.action_ptt.setChecked(active)
        self.action_ptt.blockSignals(False)

    def set_mic_state(self, active: bool):
        self.action_mic.blockSignals(True)
        self.action_mic.setChecked(active)
        self.action_mic.blockSignals(False)

    def _on_ptt_toggled(self, checked: bool):
        log.info(f"[TRAY] PTT toggled: {checked}")
        self.sig_toggle_ptt.emit(checked)

    def _on_mic_toggled(self, checked: bool):
        log.info(f"[TRAY] MIC toggled: {checked}")
        self.sig_toggle_mic.emit(checked)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.sig_show_overlay.emit()

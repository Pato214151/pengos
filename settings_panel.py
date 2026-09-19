"""
Panel de ajustes (diálogo con pestañas): General, Audio, Teclas, Overlay,
Frases rápidas y Acerca de. Lee la config al abrir (_load_config) y al guardar
llama a config.save_config(), que escribe config.json y .env.
"""

import json
import os
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, 
    QStackedWidget, QLineEdit, QComboBox, QSlider, QListWidget, 
    QSpinBox, QFormLayout, QListWidgetItem, QInputDialog
)

from config import config, log, save_config

class HotkeyButton(QPushButton):
    """Botón que, al pulsarlo, captura la siguiente tecla y la muestra como atajo."""
    def __init__(self, key_name: str, parent=None):
        super().__init__(key_name, parent)
        self.setCheckable(True)
        self.toggled.connect(self._on_toggled)
        self.current_key = key_name
        
    def _on_toggled(self, checked):
        if checked:
            self.setText("Presiona una tecla...")
            self.setStyleSheet("border: 1px solid #00d4aa;")
            self.grabKeyboard()
        else:
            self.setText(self.current_key.upper())
            self.setStyleSheet("")
            self.releaseKeyboard()

    def keyPressEvent(self, event):
        if self.isChecked():
            key = event.key()
            if key == Qt.Key_Escape:
                self.setChecked(False)
                return
                
            key_str = ""
            if Qt.Key_F1 <= key <= Qt.Key_F12:
                key_str = f"f{key - Qt.Key_F1 + 1}"
            elif key == Qt.Key_Space:
                key_str = "space"
            elif event.text():
                key_str = event.text().lower()
                
            if key_str:
                self.current_key = key_str
                self.setChecked(False)


class SettingsPanel(QDialog):
    """Diálogo de configuración sin bordes, con menú lateral de pestañas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(750, 520)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 10px;
            }
            QComboBox, QLineEdit, QSpinBox {
                background: #161b22;
                color: #e6edf3;
                border: 1px solid #30363d;
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 12px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #161b22;
                border: 1px solid #30363d;
                selection-background-color: #21262d;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #30363d;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                background: #00d4aa;
                border-radius: 8px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background: #00d4aa;
                border-radius: 3px;
            }
            QPushButton {
                background: #161b22;
                color: #e6edf3;
                border: 1px solid #30363d;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #21262d;
                border-color: #00d4aa;
            }
            QListWidget {
                background: #161b22;
                color: #e6edf3;
                border: 1px solid #30363d;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background: #21262d;
                border-left: 2px solid #00d4aa;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title bar
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(15, 10, 15, 0)
        title_label = QLabel("⚙ Configuración — Pengos")
        title_label.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: bold;")
        
        btn_min = QPushButton("─")
        btn_min.setFixedSize(30, 24)
        btn_min.setStyleSheet("QPushButton { background: transparent; color: #8b949e; border: none; padding: 0; } QPushButton:hover { background: #21262d; color: white; }")
        btn_min.clicked.connect(self.showMinimized)
        
        btn_close = QPushButton("×")
        btn_close.setFixedSize(30, 24)
        btn_close.setStyleSheet("QPushButton { background: transparent; color: #8b949e; border: none; font-size: 16px; padding: 0; } QPushButton:hover { background: #ff6b6b; color: white; }")
        btn_close.clicked.connect(self.reject)
        
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        title_bar.addWidget(btn_min)
        title_bar.addWidget(btn_close)
        
        main_layout.addLayout(title_bar)
        
        # Content Area
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(15, 10, 15, 10)
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(180)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(5)
        
        self.tabs = QStackedWidget()
        self.nav_buttons = []
        
        tab_info = [
            ("⚙ General", self._create_tab_general),
            ("🎤 Audio", self._create_tab_audio),
            ("⌨ Hotkeys", self._create_tab_hotkeys),
            ("📐 Overlay", self._create_tab_overlay),
            ("💬 Frases", self._create_tab_frases),
            ("ℹ Acerca de", self._create_tab_about),
        ]
        
        for i, (text, func) in enumerate(tab_info):
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #8b949e;
                    border: none;
                    text-align: left;
                    padding: 8px 15px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background: #21262d;
                }
                QPushButton:checked {
                    background: rgba(0, 212, 170, 0.1);
                    color: #00d4aa;
                    border-left: 3px solid #00d4aa;
                    border-top-left-radius: 0;
                    border-bottom-left-radius: 0;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self._switch_tab(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
            self.tabs.addWidget(func())
            
        sidebar_layout.addStretch()
        
        content_layout.addWidget(sidebar)
        content_layout.addWidget(self.tabs)
        
        main_layout.addLayout(content_layout)
        
        # Bottom Bar
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(15, 0, 15, 15)
        bottom_bar.addStretch()
        
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color: #00d4aa; font-size: 11px;")
        bottom_bar.addWidget(self.lbl_status)
        bottom_bar.addSpacing(10)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        bottom_bar.addWidget(btn_cancel)
        
        btn_save = QPushButton("Guardar")
        btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d4aa, stop:1 #00b894);
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1ae8be, stop:1 #1acba8);
            }
        """)
        btn_save.clicked.connect(self._save_config)
        bottom_bar.addWidget(btn_save)
        
        main_layout.addLayout(bottom_bar)
        
        # Initialize
        self._switch_tab(0)
        self._load_config()
        
    def _create_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #8b949e; font-size: 12px;")
        return lbl
        
    def _create_value_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #e6edf3; font-size: 12px; font-weight: bold;")
        return lbl

    def _create_tab_general(self):
        w = QWidget()
        layout = QFormLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        self.inp_api = QLineEdit()
        self.inp_api.setEchoMode(QLineEdit.Password)
        self.inp_api.setPlaceholderText("gsk_...")
        
        btn_eye = QPushButton("👁")
        btn_eye.setFixedSize(30, 30)
        btn_eye.setCheckable(True)
        btn_eye.clicked.connect(lambda c: self.inp_api.setEchoMode(QLineEdit.Normal if c else QLineEdit.Password))
        
        api_layout = QHBoxLayout()
        api_layout.addWidget(self.inp_api)
        api_layout.addWidget(btn_eye)
        
        self.cmb_modo_escucha = QComboBox()
        self.cmb_modo_escucha.addItems(["siempre", "mantener"])
        
        self.cmb_idioma = QComboBox()
        self.cmb_idioma.addItems(["auto", "en", "es"])
        
        self.cmb_log = QComboBox()
        self.cmb_log.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        
        layout.addRow(self._create_label("API Key:"), api_layout)
        layout.addRow(self._create_label("Modo Escucha:"), self.cmb_modo_escucha)
        layout.addRow(self._create_label("Idioma Entrada:"), self.cmb_idioma)
        layout.addRow(self._create_label("Log Level:"), self.cmb_log)
        
        return w

    def _list_audio_devices(self):
        """Lista los dispositivos de entrada para elegir en la pestaña Audio."""
        devices = []
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    devices.append(info['name'])
            p.terminate()
        except:
            pass
        return devices

    def _create_tab_audio(self):
        w = QWidget()
        layout = QFormLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        self.cmb_audio_mode = QComboBox()
        self.cmb_audio_mode.addItems(["vbcable", "stereo_mix", "auto"])
        
        devices = self._list_audio_devices()
        
        self.cmb_sys_device = QComboBox()
        self.cmb_sys_device.addItems(devices)
        
        self.cmb_mic_device = QComboBox()
        self.cmb_mic_device.addItem("")
        self.cmb_mic_device.addItems(devices)
        
        # VAD Sensibilidad
        self.sld_vad = QSlider(Qt.Horizontal)
        self.sld_vad.setRange(0, 3)
        self.lbl_vad_val = self._create_value_label("2")
        self.sld_vad.valueChanged.connect(lambda v: self.lbl_vad_val.setText(str(v)))
        
        vad_layout = QHBoxLayout()
        vad_layout.addWidget(self.sld_vad)
        vad_layout.addWidget(self.lbl_vad_val)
        
        # Silencio
        self.sld_sil = QSlider(Qt.Horizontal)
        self.sld_sil.setRange(200, 1000)
        self.sld_sil.setSingleStep(50)
        self.lbl_sil_val = self._create_value_label("400")
        self.sld_sil.valueChanged.connect(lambda v: self.lbl_sil_val.setText(str(v)))
        
        sil_layout = QHBoxLayout()
        sil_layout.addWidget(self.sld_sil)
        sil_layout.addWidget(self.lbl_sil_val)
        
        # Buffer
        self.sld_buf = QSlider(Qt.Horizontal)
        self.sld_buf.setRange(30, 200) # x10
        self.lbl_buf_val = self._create_value_label("8.0")
        self.sld_buf.valueChanged.connect(lambda v: self.lbl_buf_val.setText(f"{v/10:.1f}"))
        
        buf_layout = QHBoxLayout()
        buf_layout.addWidget(self.sld_buf)
        buf_layout.addWidget(self.lbl_buf_val)
        
        layout.addRow(self._create_label("Modo Audio:"), self.cmb_audio_mode)
        layout.addRow(self._create_label("Dispositivo Sist:"), self.cmb_sys_device)
        layout.addRow(self._create_label("Micrófono:"), self.cmb_mic_device)
        layout.addRow(self._create_label("Sensibilidad VAD:"), vad_layout)
        layout.addRow(self._create_label("Silencio (ms):"), sil_layout)
        layout.addRow(self._create_label("Buffer Máx (s):"), buf_layout)
        
        return w

    def _create_tab_hotkeys(self):
        w = QWidget()
        layout = QFormLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        self.btn_ptt = HotkeyButton("f4")
        self.btn_mic = HotkeyButton("f5")
        self.btn_frases = HotkeyButton("f2")
        self.btn_pin = HotkeyButton("f3")
        self.inp_salir = QLineEdit("ctrl+shift+q")
        
        layout.addRow(self._create_label("Push to Talk:"), self.btn_ptt)
        layout.addRow(self._create_label("Push to Mic:"), self.btn_mic)
        layout.addRow(self._create_label("Frases Rápidas:"), self.btn_frases)
        layout.addRow(self._create_label("Pin Overlay:"), self.btn_pin)
        layout.addRow(self._create_label("Salir:"), self.inp_salir)
        
        return w

    def _create_tab_overlay(self):
        w = QWidget()
        layout = QFormLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        self.cmb_pos = QComboBox()
        self.cmb_pos.addItems(["bottom-left", "bottom-right", "top-left", "top-right"])
        
        self.spn_x = QSpinBox()
        self.spn_x.setRange(0, 3840)
        
        self.spn_y = QSpinBox()
        self.spn_y.setRange(0, 2160)
        
        self.sld_vis = QSlider(Qt.Horizontal)
        self.sld_vis.setRange(2000, 15000)
        self.sld_vis.setSingleStep(500)
        self.lbl_vis_val = self._create_value_label("6000")
        self.sld_vis.valueChanged.connect(lambda v: self.lbl_vis_val.setText(str(v)))
        
        vis_layout = QHBoxLayout()
        vis_layout.addWidget(self.sld_vis)
        vis_layout.addWidget(self.lbl_vis_val)
        
        layout.addRow(self._create_label("Posición:"), self.cmb_pos)
        layout.addRow(self._create_label("Coordenada X:"), self.spn_x)
        layout.addRow(self._create_label("Coordenada Y:"), self.spn_y)
        layout.addRow(self._create_label("Tiempo visible (ms):"), vis_layout)
        
        return w

    def _create_tab_frases(self):
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.lst_frases = QListWidget()
        
        btn_layout = QVBoxLayout()
        btn_add = QPushButton("+ Agregar")
        btn_add.clicked.connect(self._add_frase)
        btn_del = QPushButton("− Eliminar")
        btn_del.clicked.connect(lambda: self.lst_frases.takeItem(self.lst_frases.currentRow()))
        btn_up = QPushButton("▲ Subir")
        btn_up.clicked.connect(self._move_frase_up)
        btn_down = QPushButton("▼ Bajar")
        btn_down.clicked.connect(self._move_frase_down)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_del)
        btn_layout.addWidget(btn_up)
        btn_layout.addWidget(btn_down)
        btn_layout.addStretch()
        
        layout.addWidget(self.lst_frases)
        layout.addLayout(btn_layout)
        
        return w

    def _add_frase(self):
        if self.lst_frases.count() >= 8:
            return
        es, ok1 = QInputDialog.getText(self, "Agregar Frase", "Español:")
        if ok1 and es:
            en, ok2 = QInputDialog.getText(self, "Agregar Frase", "Inglés:")
            if ok2 and en:
                item = QListWidgetItem(f"{es} → {en}")
                item.setData(Qt.UserRole, {"es": es, "en": en})
                self.lst_frases.addItem(item)

    def _move_frase_up(self):
        r = self.lst_frases.currentRow()
        if r > 0:
            it = self.lst_frases.takeItem(r)
            self.lst_frases.insertItem(r-1, it)
            self.lst_frases.setCurrentRow(r-1)

    def _move_frase_down(self):
        r = self.lst_frases.currentRow()
        if r < self.lst_frases.count() - 1 and r >= 0:
            it = self.lst_frases.takeItem(r)
            self.lst_frases.insertItem(r+1, it)
            self.lst_frases.setCurrentRow(r+1)

    def _create_tab_about(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("PENGOS")
        title.setStyleSheet("color: #00d4aa; font-family: 'Segoe UI'; font-size: 32px; font-weight: bold; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignCenter)
        
        ver = QLabel("v1.0.0")
        ver.setStyleSheet("color: #8b949e; font-size: 14px;")
        ver.setAlignment(Qt.AlignCenter)
        
        desc = QLabel("Overlay de traducción de voz en tiempo real para gaming\nInglés ↔ Español")
        desc.setStyleSheet("color: #e6edf3; font-size: 14px;")
        desc.setAlignment(Qt.AlignCenter)
        
        author = QLabel("Hecho con ❤ por Ducklab")
        author.setStyleSheet("color: #8b949e; font-size: 12px; margin-top: 20px;")
        author.setAlignment(Qt.AlignCenter)

        brand = QLabel("🐥 Ducklab")
        brand.setStyleSheet("color: #db1f2e; font-size: 12px; font-weight: bold; margin-top: 2px;")
        brand.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(ver)
        layout.addSpacing(20)
        layout.addWidget(desc)
        layout.addWidget(author)
        layout.addWidget(brand)
        
        return w

    def _switch_tab(self, idx):
        self.tabs.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == idx)

    def _load_config(self):
        """Llena todos los controles con los valores actuales de config.json."""
        self.inp_api.setText(os.environ.get('GROQ_API_KEY') or config.get('api_key', ''))
        self.cmb_modo_escucha.setCurrentText(config.get('modo_escucha', 'siempre'))
        self.cmb_idioma.setCurrentText(config.get('idioma_entrada', 'auto'))
        self.cmb_log.setCurrentText(config.get('log_level', 'INFO'))
        
        self.cmb_audio_mode.setCurrentText(config.get('audio_mode', 'vbcable'))
        
        sys_dev = config.get('audio_device_name', 'CABLE Output')
        if self.cmb_sys_device.findText(sys_dev) >= 0:
            self.cmb_sys_device.setCurrentText(sys_dev)
        elif self.cmb_sys_device.count() > 0:
            self.cmb_sys_device.setCurrentText(self.cmb_sys_device.itemText(0))
            
        mic_dev = config.get('microphone_device_name', '')
        if mic_dev and self.cmb_mic_device.findText(mic_dev) >= 0:
            self.cmb_mic_device.setCurrentText(mic_dev)
            
        self.sld_vad.setValue(config.get('vad_sensibilidad', 2))
        self.sld_sil.setValue(config.get('vad_silencio_ms', 400))
        self.sld_buf.setValue(int(config.get('max_buffer_s', 8.0) * 10))
        
        hk = config.get('hotkeys', {})
        self.btn_ptt.current_key = hk.get('push_to_talk', 'f4')
        self.btn_ptt.setText(self.btn_ptt.current_key.upper())
        self.btn_mic.current_key = hk.get('push_to_mic', 'f5')
        self.btn_mic.setText(self.btn_mic.current_key.upper())
        self.btn_frases.current_key = hk.get('frases_rapidas', 'f2')
        self.btn_frases.setText(self.btn_frases.current_key.upper())
        self.btn_pin.current_key = hk.get('pin_overlay', 'f3')
        self.btn_pin.setText(self.btn_pin.current_key.upper())
        self.inp_salir.setText(hk.get('salir', 'ctrl+shift+q'))
        
        ov = config.get('overlay', {})
        self.cmb_pos.setCurrentText(ov.get('posicion', 'bottom-left'))
        self.spn_x.setValue(ov.get('x', 50))
        self.spn_y.setValue(ov.get('y', 680))
        self.sld_vis.setValue(ov.get('tiempo_visible', 6000))
        
        for frase in config.get('frases_rapidas', []):
            item = QListWidgetItem(f"{frase['es']} → {frase['en']}")
            item.setData(Qt.UserRole, frase)
            self.lst_frases.addItem(item)

    def _save_config(self):
        """Lee los controles, arma el dict de config y lo guarda."""
        new_api = self.inp_api.text().strip()
        
        frases = []
        for i in range(self.lst_frases.count()):
            frases.append(self.lst_frases.item(i).data(Qt.UserRole))
            
        data = {
            "api_key": new_api,
            "modo_escucha": self.cmb_modo_escucha.currentText(),
            "log_level": self.cmb_log.currentText(),
            "audio_mode": self.cmb_audio_mode.currentText(),
            "audio_device_name": self.cmb_sys_device.currentText(),
            "microphone_device_name": self.cmb_mic_device.currentText() if self.cmb_mic_device.currentText() != "(Default del sistema)" else "",
            "hotkeys": {
                "push_to_talk": self.btn_ptt.current_key,
                "push_to_mic": self.btn_mic.current_key,
                "frases_rapidas": self.btn_frases.current_key,
                "pin_overlay": self.btn_pin.current_key,
                "salir": self.inp_salir.text().strip()
            },
            "overlay": {
                "posicion": self.cmb_pos.currentText(),
                "x": self.spn_x.value(),
                "y": self.spn_y.value(),
                "tiempo_visible": self.sld_vis.value()
            },
            "vad_sensibilidad": self.sld_vad.value(),
            "vad_silencio_ms": self.sld_sil.value(),
            "max_buffer_s": self.sld_buf.value() / 10.0,
            "idioma_entrada": self.cmb_idioma.currentText(),
            "frases_rapidas": frases
        }
        
        save_config(data, new_api if new_api != os.environ.get('GROQ_API_KEY') else None)
        self.lbl_status.setText("✓ Guardado")
        self.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() < 40:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

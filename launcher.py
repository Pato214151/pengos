import os
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect

from config import config, log

class Launcher(QWidget):
    sig_start = pyqtSignal()
    sig_settings = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFixedSize(480, 620)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setStyleSheet("""
            QWidget#MainWidget {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 12px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_widget = QWidget()
        self.main_widget.setObjectName("MainWidget")
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Title bar
        title_bar = QHBoxLayout()
        title_label = QLabel("PENGOS")
        title_label.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: bold;")
        
        btn_min = QPushButton("─")
        btn_min.setFixedSize(30, 24)
        btn_min.setStyleSheet("QPushButton { background: transparent; color: #8b949e; border: none; } QPushButton:hover { background: #21262d; color: white; }")
        btn_min.clicked.connect(self.showMinimized)
        
        btn_close = QPushButton("×")
        btn_close.setFixedSize(30, 24)
        btn_close.setStyleSheet("QPushButton { background: transparent; color: #8b949e; border: none; font-size: 16px; } QPushButton:hover { background: #ff6b6b; color: white; }")
        btn_close.clicked.connect(self.close)
        
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        title_bar.addWidget(btn_min)
        title_bar.addWidget(btn_close)
        
        layout.addLayout(title_bar)
        layout.addStretch(1)
        
        # Logo
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        icon_path = Path(__file__).parent / 'imagen' / 'pengos_icon.png'
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path)).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            
            # Subtle drop shadow
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 212, 170, 80))
            shadow.setOffset(0, 4)
            logo_label.setGraphicsEffect(shadow)
            
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)
        layout.addLayout(logo_layout)
        
        layout.addSpacing(10)
        
        # Title
        app_title = QLabel("PENGOS")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setStyleSheet("color: #00d4aa; font-family: 'Segoe UI'; font-size: 28px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(app_title)
        
        subtitle = QLabel("Traducción de voz en tiempo real")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #8b949e; font-size: 13px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Buttons
        btns_layout = QVBoxLayout()
        btns_layout.setAlignment(Qt.AlignCenter)
        btns_layout.setSpacing(12)
        
        btn_start = QPushButton("▶  INICIAR PENGOS")
        btn_start.setFixedSize(320, 50)
        btn_start.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d4aa, stop:1 #00b894);
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1ae8be, stop:1 #1acba8);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00b894, stop:1 #00997a);
            }
        """)
        btn_start.clicked.connect(self.sig_start.emit)
        btns_layout.addWidget(btn_start)
        
        btn_settings = QPushButton("⚙  CONFIGURACIÓN")
        btn_settings.setFixedSize(320, 44)
        btn_settings.setStyleSheet("""
            QPushButton {
                background: #161b22;
                color: #e6edf3;
                font-size: 13px;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: #21262d;
                border-color: #00d4aa;
            }
        """)
        btn_settings.clicked.connect(self.sig_settings.emit)
        btns_layout.addWidget(btn_settings)
        
        btn_glossary = QPushButton("📖  GLOSARIO")
        btn_glossary.setFixedSize(320, 44)
        btn_glossary.setStyleSheet("""
            QPushButton {
                background: #161b22;
                color: #484f58;
                font-size: 13px;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
        """)
        btn_glossary.setEnabled(False)
        btn_glossary.setToolTip("Próximamente")
        btns_layout.addWidget(btn_glossary)
        
        layout.addLayout(btns_layout)
        layout.addStretch(1)
        
        # Status Bar
        status_layout = QHBoxLayout()
        status_layout.setAlignment(Qt.AlignCenter)
        status_layout.setSpacing(20)
        
        self._api_label = QLabel("● API: Verificando...")
        self._api_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        
        self._audio_label = QLabel("● Audio: Verificando...")
        self._audio_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        
        status_layout.addWidget(self._api_label)
        status_layout.addWidget(self._audio_label)
        
        layout.addLayout(status_layout)
        
        # Version
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: #484f58; font-size: 10px;")
        version_label.setAlignment(Qt.AlignRight)
        layout.addWidget(version_label)
        
        main_layout.addWidget(self.main_widget)
        
        QTimer.singleShot(500, self._check_status)

    def _check_status(self):
        # Check API
        try:
            api_key = os.environ.get('GROQ_API_KEY') or config.get('api_key', '')
            if api_key and api_key.startswith('gsk_'):
                self._api_label.setText('● API: Conectada')
                self._api_label.setStyleSheet('color: #00d4aa; font-size: 11px;')
            else:
                self._api_label.setText('● API: Sin key')
                self._api_label.setStyleSheet('color: #ff6b6b; font-size: 11px;')
        except:
            self._api_label.setText('● API: Error')
            self._api_label.setStyleSheet('color: #ff6b6b; font-size: 11px;')
        
        # Check Audio
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            device_name = config.get('audio_device_name', 'CABLE Output')
            found = False
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if device_name in info['name'] and info['maxInputChannels'] > 0:
                    found = True
                    break
            p.terminate()
            if found:
                self._audio_label.setText(f'● Audio: {device_name}')
                self._audio_label.setStyleSheet('color: #00d4aa; font-size: 11px;')
            else:
                self._audio_label.setText('● Audio: No detectado')
                self._audio_label.setStyleSheet('color: #ff6b6b; font-size: 11px;')
        except:
            self._audio_label.setText('● Audio: Error')
            self._audio_label.setStyleSheet('color: #ff6b6b; font-size: 11px;')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() < 40:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

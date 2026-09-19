"""
Overlay: ventana flotante, siempre encima y semitransparente, donde se ven
los subtítulos (inglés en gris arriba, español en verde abajo).

Recibe los resultados de audio.py por señales Qt (show_final, show_mic_result...).
Los métodos públicos solo emiten señales internas para que el dibujado ocurra
siempre en el hilo de la interfaz (_on_*). También muestra las frases rápidas
(F2) y se puede fijar para que no se oculte (F3).
"""

import pyperclip
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QGraphicsDropShadowEffect, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QVBoxLayout, QWidget,
)

from config import config, log


class Overlay(QWidget):
    sig_partial    = pyqtSignal(str)
    sig_final      = pyqtSignal(str, str, str)
    sig_frase_show = pyqtSignal(str, str)
    sig_mic_show   = pyqtSignal(str, str)

    sig_cmd_pin    = pyqtSignal()
    sig_cmd_frases = pyqtSignal()
    sig_cmd_frase  = pyqtSignal(int)
    sig_ptt        = pyqtSignal(bool)
    sig_mic        = pyqtSignal(bool)
    sig_proc       = pyqtSignal(bool)

    MAX_LINES = 2
    OVERLAY_WIDTH = 620

    _FONT = "'Segoe UI', 'Inter', sans-serif"

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |
            Qt.Tool | Qt.SubWindow
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedWidth(self.OVERLAY_WIDTH)

        self._lines_layout = QVBoxLayout()
        self._lines_layout.setContentsMargins(0, 0, 0, 0)
        self._lines_layout.setSpacing(4)

        self._frases_widget = QWidget()
        self._frases_widget.setStyleSheet(
            "background: rgba(13,17,23,235);"
            "border: 1px solid #30363d;"
            "border-radius: 8px;"
        )
        frases_outer = QVBoxLayout(self._frases_widget)
        frases_outer.setContentsMargins(10, 8, 10, 10)
        frases_outer.setSpacing(7)

        frases_header = QLabel("⚡ FRASES RÁPIDAS")
        frases_header.setStyleSheet(
            "color: #00d4aa; font-family: %s; font-size: 10px;"
            "font-weight: bold; letter-spacing: 1.5px; background: transparent;"
            "border: none;" % self._FONT
        )
        frases_outer.addWidget(frases_header)

        frases_grid = QGridLayout()
        frases_grid.setContentsMargins(0, 0, 0, 0)
        frases_grid.setHorizontalSpacing(6)
        frases_grid.setVerticalSpacing(6)
        self._frase_buttons: list[QPushButton] = []
        for i, frase in enumerate(config.get("frases_rapidas", [])[:4]):
            btn = QPushButton(f"{i+1}  {frase['es']}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                "QPushButton {"
                "  color: #c9d1d9; background: rgba(22,27,34,230);"
                "  border: 1px solid #30363d; padding: 7px 12px;"
                "  border-radius: 6px; font-family: %s; font-size: 12px;"
                "  font-weight: 600; text-align: left;"
                "}"
                "QPushButton:hover {"
                "  border-color: #00d4aa; color: #00d4aa;"
                "  background: rgba(0,212,170,0.10);"
                "}"
                "QPushButton:pressed {"
                "  background: rgba(0,212,170,0.18);"
                "}" % self._FONT
            )
            btn.clicked.connect(lambda _checked, idx=i: self._on_frase(idx))
            frases_grid.addWidget(btn, i // 2, i % 2)
            self._frase_buttons.append(btn)
        frases_outer.addLayout(frases_grid)
        _frases_shadow = QGraphicsDropShadowEffect(self)
        _frases_shadow.setBlurRadius(24)
        _frases_shadow.setColor(QColor(0, 0, 0, 180))
        _frases_shadow.setOffset(0, 4)
        self._frases_widget.setGraphicsEffect(_frases_shadow)
        self._frases_widget.setVisible(False)

        indicators = QHBoxLayout()
        indicators.setContentsMargins(8, 0, 8, 0)
        indicators.setSpacing(6)

        self._ptt_label = QLabel("●  ESCUCHANDO")
        self._ptt_label.setStyleSheet(self._badge_style("255,170,0", "#ffaa00"))
        self._ptt_label.setVisible(False)

        self._mic_label = QLabel("●  MIC")
        self._mic_label.setStyleSheet(self._badge_style("88,166,255", "#58a6ff"))
        self._mic_label.setVisible(False)

        self._proc_label = QLabel("⟳  traduciendo…")
        self._proc_label.setStyleSheet(self._badge_style("255,221,68", "#ffdd44"))
        self._proc_label.setVisible(False)

        indicators.addWidget(self._ptt_label)
        indicators.addWidget(self._mic_label)
        indicators.addWidget(self._proc_label)
        indicators.addStretch()

        self.status_dot = QLabel(self)
        self.status_dot.setFixedSize(10, 10)
        self.status_dot.setStyleSheet("background: #00d4aa; border-radius: 5px;")

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(4)
        main.addLayout(self._lines_layout)
        main.addSpacing(2)
        main.addLayout(indicators)
        main.addWidget(self._frases_widget)

        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self._maybe_hide)
        self.hide_timer.setSingleShot(True)
        self.pinned = False

        self._pending_es_queue: list[QLabel] = []
        self._line_pairs: list[tuple[QWidget, QLabel, QLabel]] = []

        self.sig_partial.connect(self._on_partial,          Qt.QueuedConnection)
        self.sig_final.connect(self._on_final,              Qt.QueuedConnection)
        self.sig_frase_show.connect(self._on_frase_show,    Qt.QueuedConnection)
        self.sig_mic_show.connect(self._on_mic_show,        Qt.QueuedConnection)
        self.sig_cmd_pin.connect(self._do_toggle_pin,       Qt.QueuedConnection)
        self.sig_cmd_frases.connect(self._do_toggle_frases, Qt.QueuedConnection)
        self.sig_cmd_frase.connect(self._do_select_frase,   Qt.QueuedConnection)
        self.sig_ptt.connect(self._on_ptt,                  Qt.QueuedConnection)
        self.sig_mic.connect(self._on_mic,                  Qt.QueuedConnection)
        self.sig_proc.connect(self._on_proc,                Qt.QueuedConnection)

    @classmethod
    def _badge_style(cls, rgb: str, hex_color: str) -> str:
        return (
            "color: %s; font-family: %s; font-size: 10px; font-weight: bold;"
            "letter-spacing: 0.5px;"
            "background: rgba(%s,0.12); padding: 3px 9px; border-radius: 9px;"
            "border: 1px solid rgba(%s,0.30);" % (hex_color, cls._FONT, rgb, rgb)
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.status_dot.move(self.width() - 16, 6)

    # ── API pública ──

    def show_partial(self, english: str):
        """Texto provisional mientras se procesa."""
        self.sig_partial.emit(english)

    def show_final(self, original: str, translated: str, direction: str = "en2es"):
        """Par final (original, traducción) del audio del sistema."""
        self.sig_final.emit(original, translated, direction)

    def show_ptt(self, active: bool):
        self.sig_ptt.emit(active)

    def show_mic(self, active: bool):
        self.sig_mic.emit(active)

    def show_procesando(self, active: bool):
        self.sig_proc.emit(active)

    def show_mic_result(self, es: str, en: str):
        """Par final (lo que dijiste, traducción) del micrófono."""
        self.sig_mic_show.emit(es, en)

    def toggle_pin(self):
        self.sig_cmd_pin.emit()

    def toggle_frases(self):
        self.sig_cmd_frases.emit()

    def select_frase(self, n: int):
        self.sig_cmd_frase.emit(n)

    def set_status(self, color: str):
        """Cambia el color del indicador de estado (verde/rojo/...)."""
        self.status_dot.setStyleSheet(f"background: {color}; border-radius: 5px;")

    # ── Slots ──

    def _on_proc(self, active: bool):
        self._proc_label.setVisible(active)
        if active:
            self.show()
            self.hide_timer.stop()

    def _on_ptt(self, active: bool):
        self._ptt_label.setVisible(active)
        if active:
            self.show()
            self.hide_timer.stop()

    def _on_mic(self, active: bool):
        self._mic_label.setVisible(active)
        if active:
            self.show()
            self.hide_timer.stop()

    def _on_partial(self, english: str):
        en_lbl = QLabel(english)
        en_lbl.setWordWrap(True)
        es_lbl = QLabel("…")
        es_lbl.setWordWrap(True)
        self._add_pair(en_lbl, es_lbl, pending=True)
        self._pending_es_queue.append(es_lbl)
        self._show_and_reset_timer()

    def _on_final(self, _original: str, translated: str, direction: str = "en2es"):
        if self._pending_es_queue:
            lbl = self._pending_es_queue.pop(0)
            lbl.setText(translated)
            lbl.setStyleSheet(
                self._STYLE_ES_ACTIVE if direction == "en2es" else self._STYLE_ES_AMBER
            )
        self._refresh_dim()
        self._show_and_reset_timer()

    def _on_frase_show(self, es: str, en: str):
        en_lbl = QLabel(f"Tú: {es}")
        en_lbl.setWordWrap(True)
        es_lbl = QLabel(en)
        es_lbl.setWordWrap(True)
        self._add_pair(en_lbl, es_lbl)
        self._show_and_reset_timer()

    def _on_mic_show(self, es: str, en: str):
        lbl_es = QLabel(f"Vos: {es}")
        lbl_es.setWordWrap(True)
        lbl_en = QLabel(en)
        lbl_en.setWordWrap(True)
        self._add_pair(lbl_es, lbl_en,
                       bottom_style=self._STYLE_ES_MIC,
                       accent=self._STYLE_ACCENT_BLUE)
        self._show_and_reset_timer()

    _STYLE_ACCENT_TEAL = "#00d4aa"
    _STYLE_ACCENT_AMBER = "#ffdd44"
    _STYLE_ACCENT_BLUE  = "#58a6ff"

    _STYLE_EN_ACTIVE = (
        "color: #8b949e; font-family: %s; font-size: 11px; font-style: italic;"
        "background: transparent; border: none; padding: 2px 0 0 0;" % _FONT
    )
    _STYLE_ES_ACTIVE = (
        "color: #00d4aa; font-family: %s; font-size: 19px; font-weight: bold;"
        "letter-spacing: 0.3px; background: transparent; border: none;"
        "padding: 0 0 2px 0;" % _FONT
    )
    _STYLE_ES_AMBER = (
        "color: #ffdd44; font-family: %s; font-size: 19px; font-weight: bold;"
        "letter-spacing: 0.3px; background: transparent; border: none;"
        "padding: 0 0 2px 0;" % _FONT
    )

    _STYLE_EN_DIM = (
        "color: #565f6a; font-family: %s; font-size: 10px; font-style: italic;"
        "background: transparent; border: none; padding: 2px 0 0 0;" % _FONT
    )
    _STYLE_ES_DIM = (
        "color: #6a737d; font-family: %s; font-size: 14px; font-weight: bold;"
        "background: transparent; border: none; padding: 0 0 2px 0;" % _FONT
    )

    _STYLE_EN_MIC = (
        "color: #8b949e; font-family: %s; font-size: 11px; font-style: italic;"
        "background: transparent; border: none; padding: 2px 0 0 0;" % _FONT
    )
    _STYLE_ES_MIC = (
        "color: #e6edf3; font-family: %s; font-size: 19px; font-weight: bold;"
        "letter-spacing: 0.3px; background: transparent; border: none;"
        "padding: 0 0 2px 0;" % _FONT
    )

    _STYLE_CONTAINER = (
        "background: rgba(10,10,14,200);"
        "border-left: 3px solid %s;"
        "border-radius: 6px;"
        "padding: 0px;"
    )
    _STYLE_CONTAINER_DIM = (
        "background: rgba(5,5,8,150);"
        "border-left: 3px solid rgba(60,60,60,150);"
        "border-radius: 6px;"
        "padding: 0px;"
    )

    def _add_pair(self, top: QLabel, bottom: QLabel, pending: bool = False,
                  bottom_style: str = None, accent: str = None):
        """Agrega un bloque original+traducción al overlay con su estilo y acento."""
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(8, 4, 8, 4)
        vbox.setSpacing(1)

        if bottom_style is None:
            bottom_style = self._STYLE_ES_ACTIVE
        if accent is None:
            accent = self._STYLE_ACCENT_TEAL

        if pending:
            top.setStyleSheet(self._STYLE_EN_ACTIVE)
            bottom.setStyleSheet(
                "color: #6e7681; font-family: %s; font-size: 19px; font-weight: bold;"
                "background: transparent; border: none; padding: 0 0 2px 0;" % self._FONT
            )
            container.setStyleSheet(self._STYLE_CONTAINER % accent)
        else:
            top.setStyleSheet(self._STYLE_EN_ACTIVE)
            bottom.setStyleSheet(bottom_style)
            container.setStyleSheet(self._STYLE_CONTAINER % accent)

        vbox.addWidget(top)
        vbox.addWidget(bottom)

        self._lines_layout.addWidget(container)
        self._line_pairs.append((container, top, bottom))
        self._trim_lines()
        self._refresh_dim()

    def _refresh_dim(self):
        last = len(self._line_pairs) - 1
        for i, (c, top, bottom) in enumerate(self._line_pairs):
            if i == last:
                continue
            c.setStyleSheet(self._STYLE_CONTAINER_DIM)
            top.setStyleSheet(self._STYLE_EN_DIM)
            bottom.setStyleSheet(self._STYLE_ES_DIM)

    def _trim_lines(self):
        """Deja solo las últimas N traducciones visibles."""
        while len(self._line_pairs) > self.MAX_LINES:
            container, _t, _b = self._line_pairs.pop(0)
            if _b in self._pending_es_queue:
                self._pending_es_queue.remove(_b)
            container.setParent(None)
            container.deleteLater()

    def _show_and_reset_timer(self):
        """Muestra el overlay y reinicia el temporizador de auto-ocultado."""
        self.show()
        if not self.pinned:
            self.hide_timer.start(config["overlay"].get("tiempo_visible", 6000))

    def _maybe_hide(self):
        """Oculta el overlay por inactividad, salvo que esté fijado."""
        if not self.pinned and not self.underMouse() and not self._pending_es_queue:
            self.hide()

    def _do_toggle_pin(self):
        self.pinned = not self.pinned
        log.info("[PIN] %s", "Fijado" if self.pinned else "Suelto")
        if self.pinned:
            self.show()
            self.hide_timer.stop()
        else:
            self.hide_timer.start(config["overlay"].get("tiempo_visible", 6000))

    def _do_toggle_frases(self):
        visible = not self._frases_widget.isVisible()
        self._frases_widget.setVisible(visible)
        if visible:
            self.show()
            self.hide_timer.stop()
        else:
            self._show_and_reset_timer()

    def _do_select_frase(self, n: int):
        if self._frases_widget.isVisible() and 0 <= n < len(self._frase_buttons):
            self._on_frase(n)

    def _on_frase(self, idx: int):
        frases = config.get("frases_rapidas", [])
        if 0 <= idx < len(frases):
            frase = frases[idx]
            pyperclip.copy(frase["en"])
            self.sig_frase_show.emit(frase["es"], frase["en"])
        self._frases_widget.setVisible(False)
        self._show_and_reset_timer()

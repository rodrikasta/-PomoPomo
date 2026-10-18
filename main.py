#!/usr/bin/env python3
import sys
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QEvent, QPoint, QRectF, QTimer, Qt, QVariantAnimation
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class VectorIconButton(QPushButton):
    def __init__(self, icon_name, accessible_name, parent=None):
        super().__init__(parent)
        from PyQt6.QtGui import QIcon

        self.setWindowIcon(QIcon("assets/icon.png"))
        self.icon_name = icon_name
        self.hover_progress = 0.0
        self.setFixedSize(64, 64)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setStyleSheet("border: none; background: transparent;")
        self.set_icon(icon_name, accessible_name)

        self.hover_animation = QVariantAnimation(self)
        self.hover_animation.setDuration(180)
        self.hover_animation.setStartValue(0.0)
        self.hover_animation.setEndValue(1.0)
        self.hover_animation.valueChanged.connect(self.set_hover_progress)

    def set_icon(self, icon_name, accessible_name):
        self.icon_name = icon_name
        self.setAccessibleName(accessible_name)
        self.setToolTip(accessible_name)
        self.update()

    def set_hover_progress(self, value):
        self.hover_progress = float(value)
        self.update()

    def enterEvent(self, event):
        self.hover_animation.stop()
        self.hover_animation.setStartValue(self.hover_progress)
        self.hover_animation.setEndValue(1.0)
        self.hover_animation.start()
        event.accept()

    def leaveEvent(self, event):
        self.hover_animation.stop()
        self.hover_animation.setStartValue(self.hover_progress)
        self.hover_animation.setEndValue(0.0)
        self.hover_animation.start()
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, round(18 * self.hover_progress)))
        painter.drawEllipse(center, 30, 30)

        painter.save()
        painter.translate(center)
        scale = 2.0 * (1.0 + self.hover_progress * 0.04)
        painter.scale(scale, scale)
        painter.setPen(
            QPen(
                QColor("#000000"),
                2.6,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.setBrush(QColor("#000000"))

        if self.icon_name == "pause":
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(-6.5, -8, 4.5, 16), 1.5, 1.5)
            painter.drawRoundedRect(QRectF(2, -8, 4.5, 16), 1.5, 1.5)
        elif self.icon_name == "play":
            path = QPainterPath()
            path.moveTo(-5, -8)
            path.lineTo(7, 0)
            path.lineTo(-5, 8)
            path.closeSubpath()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(path)
        elif self.icon_name == "skip":
            path = QPainterPath()
            path.moveTo(-9, -7)
            path.lineTo(-1, 0)
            path.lineTo(-9, 7)
            path.closeSubpath()
            path.moveTo(0, -7)
            path.lineTo(8, 0)
            path.lineTo(0, 7)
            path.closeSubpath()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(path)
            painter.setPen(
                QPen(QColor("#000000"), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            )
            painter.drawLine(9, -7, 9, 7)

        painter.restore()


class VentanaRedondeada(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(300, 170)
        self.position_click = QPoint()
        self._system_move_started = False
        self._dragging = False

        self.timer = QTimer(self)
        self.focus_seconds = 25 * 60
        self.phase = "focus"
        self.focuses_since_long_break = 0
        self.remaining_seconds = self.focus_seconds
        self.phase_durations = {
            "focus": 25 * 60,
            "break": 5 * 60,
            "long_break": 20 * 60,
        }
        self.phase_colors = {
            "focus": QColor("#F54927"),
            "break": QColor("#74C8E4"),
            "long_break": QColor("#51B154"),
        }
        self.timer.timeout.connect(self.actualizar_tiempo)

        contenedor = QWidget(self)
        contenedor.setObjectName("ContenedorPrincipal")
        self.contenedor = contenedor
        self.color_actual = self.phase_colors["focus"]
        self.animacion_color = QVariantAnimation(self)
        self.animacion_color.setDuration(700)
        self.animacion_color.valueChanged.connect(self.actualizar_color)
        self.actualizar_color(self.color_actual)
        contenedor.installEventFilter(self)

        layout = QVBoxLayout(contenedor)
        layout.setContentsMargins(18, 12, 18, 14)
        layout.setSpacing(6)
        layout.addSpacing(12)
        self.label = QLabel("25:00", contenedor)
        self.label.setStyleSheet("color: black;")
        system_font = QFont("Inter Display Medium", 30)
        system_font.setBold(True)
        self.label.setFont(system_font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label.installEventFilter(self)
        layout.addWidget(self.label)

        layout.addStretch(1)
        botones = QHBoxLayout()
        botones.setAlignment(Qt.AlignmentFlag.AlignRight)
        botones.setSpacing(14)
        self.boton_pausa = VectorIconButton("play", "Reanudar", contenedor)
        self.boton_pausa.clicked.connect(self.alternar_pausa)
        self.boton_adelantar = VectorIconButton("skip", "Adelantar fase", contenedor)
        self.boton_adelantar.clicked.connect(self.adelantar)
        botones.addWidget(self.boton_pausa)
        botones.addWidget(self.boton_adelantar)
        layout.addLayout(botones)

        self.setCentralWidget(contenedor)

    def actualizar_tiempo(self):
        self.remaining_seconds -= 1
        if self.remaining_seconds <= 0:
            self.avanzar_fase()
        else:
            self.actualizar_etiqueta(self.remaining_seconds)

    def actualizar_etiqueta(self, seconds):
        minutos, segundos = divmod(seconds, 60)
        self.label.setText(f"{minutos:02d}:{segundos:02d}")

    def avanzar_fase(self):
        if self.phase == "focus":
            self.focuses_since_long_break += 1
            if self.focuses_since_long_break == 4:
                siguiente_fase = "long_break"
            else:
                siguiente_fase = "break"
        elif self.phase == "long_break":
            self.focuses_since_long_break = 0
            siguiente_fase = "focus"
        else:
            siguiente_fase = "focus"

        self.cambiar_fase(siguiente_fase)

    def adelantar(self):
        self.avanzar_fase()

    def cambiar_fase(self, phase):
        self.phase = phase
        QApplication.beep()
        if phase == "focus":
            self.focus_seconds = self.phase_durations[phase]
            self.remaining_seconds = self.focus_seconds
        else:
            self.remaining_seconds = self.phase_durations[phase]

        self.animacion_color.stop()
        self.animacion_color.setStartValue(self.color_actual)
        self.animacion_color.setEndValue(self.phase_colors[phase])
        self.animacion_color.start()
        self.actualizar_etiqueta(self.remaining_seconds)
        if not self.timer.isActive():
            self.timer.start(1000)

    def actualizar_color(self, color):
        self.color_actual = QColor(color)
        self.contenedor.setStyleSheet(
            "#ContenedorPrincipal {"
            f"background-color: rgba({color.red()}, {color.green()}, "
            f"{color.blue()}, {color.alpha()});"
            "border-radius: 50px;"
            "}"
        )

    def alternar_pausa(self):
        if self.timer.isActive():
            self.timer.stop()
            self.boton_pausa.set_icon("play", "Reanudar")
        else:
            self.timer.start(1000)
            self.boton_pausa.set_icon("pause", "Pausar")

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.position_click = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
                self._dragging = False
                self._system_move_started = False
        elif event.type() == QEvent.Type.MouseMove:
            if event.buttons() & Qt.MouseButton.LeftButton:
                pointer = event.globalPosition().toPoint()
                if not self._dragging:
                    delta = pointer - (
                        self.frameGeometry().topLeft() + self.position_click
                    )
                    if delta.manhattanLength() < QApplication.startDragDistance():
                        return True
                    self._dragging = True
                    window_handle = self.windowHandle()
                    self._system_move_started = (
                        window_handle is not None and window_handle.startSystemMove()
                    )
                if not self._system_move_started:
                    self.move(pointer - self.position_click)
                return True
        elif event.type() == QEvent.Type.MouseButtonRelease:
            if event.button() == Qt.MouseButton.LeftButton:
                self._dragging = False
            self._system_move_started = False
        return super().eventFilter(watched, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setDesktopFileName("pomopomo")
    
    base_dir = Path(__file__).resolve().parent
    icon_path = str(base_dir / "assets" / "icon.png")
    
    app.setWindowIcon(QIcon(icon_path))

    ventana = VentanaRedondeada()
    ventana.setWindowIcon(QIcon(icon_path)) # Por si acaso en la ventana individual
    ventana.show()
    sys.exit(app.exec())
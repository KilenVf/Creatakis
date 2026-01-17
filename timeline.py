from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt

class Timeline(QWidget):
    def __init__(self, duration=100):
        super().__init__()
        self.duration = duration  # durée totale (secondes)
        self.current_time = 0

        self.setMinimumHeight(60)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Fond
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        # Barre timeline
        bar_y = self.height() // 2
        painter.setPen(Qt.white)
        painter.drawLine(10, bar_y, self.width() - 10, bar_y)

        # Curseur
        x = 10 + (self.current_time / self.duration) * (self.width() - 20)
        painter.setPen(Qt.red)
        painter.drawLine(int(x), bar_y - 15, int(x), bar_y + 15)

    def mousePressEvent(self, event):
        self.update_time(event.x())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.update_time(event.x())

    def update_time(self, x):
        x = max(10, min(x, self.width() - 10))
        self.current_time = ((x - 10) / (self.width() - 20)) * self.duration
        self.update()

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from utils import import_video
from config import bloc_media, index


class Timeline(QWidget):
    positionChanged = pyqtSignal(int)

    def __init__(self, duration=100):
        super().__init__()
        self.duration = duration
        self.current_time = 0
        self.setMinimumHeight(60)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        
        bar_y = self.height() // 2
        painter.setPen(Qt.white)
        painter.drawLine(10, bar_y, self.width() - 10, bar_y)
        
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
        self.positionChanged.emit(int(self.current_time))

    def set_total_frames(self, total):
        self.duration = total

    def set_current_frame(self, frame):
        self.current_time = frame
        self.update()
    
    def add_Mediabloc():
        if import_video:
            bloc = QLabel()
            index += 1
            bloc_media.append()
        return bloc, index

    def add_pisteMedia():
        #si import_media: une piste s'ajoute (un endroit ou mettre le bloc)
        return 
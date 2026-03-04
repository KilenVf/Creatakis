from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QPoint


class Clip:
    def __init__(self, clip_type, start_frame, end_frame, file_path="", text_content="", color=(100, 150, 255)):
        self.clip_type = clip_type
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.file_path = file_path
        self.text_content = text_content
        self.color = color

    @property
    def duration(self):
        return self.end_frame - self.start_frame

    def __repr__(self):
        return f"<Clip {self.clip_type} [{self.start_frame}-{self.end_frame}]>"


class ClipItem(QWidget):
    clicked = pyqtSignal(object)

    def __init__(self, clip, parent=None):
        super().__init__(parent)
        self.clip = clip
        self.is_selected = False
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.is_selected:
            color = QColor(255, 200, 0)
        else:
            color = QColor(*self.clip.color)

        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.white, 2 if self.is_selected else 1))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 5, 5)

        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 9))
        label = self.clip.clip_type.upper()
        if self.clip.text_content:
            label = self.clip.text_content[:10] + "..."
        painter.drawText(self.rect(), Qt.AlignCenter, label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self)


class TrackWidget(QWidget):
    clipSelected = pyqtSignal(object)

    def __init__(self, track_name, track_color, parent=None):
        super().__init__(parent)
        self.track_name = track_name
        self.track_color = track_color
        self.clips = []
        self.clip_items = []
        self.pixels_per_frame = 2.0
        self.setMinimumHeight(60)
        self.setStyleSheet(f"background-color: rgb{track_color.getRgb()[:3]};")

    def add_clip(self, clip):
        self.clips.append(clip)
        item = ClipItem(clip, self)
        item.clicked.connect(lambda i: self.clipSelected.emit(i.clip))
        self.clip_items.append(item)
        self._update_clips()

    def remove_clip(self, clip):
        if clip in self.clips:
            i = self.clips.index(clip)
            self.clips.pop(i)
            item = self.clip_items.pop(i)
            item.deleteLater()
            self._update_clips()

    def set_zoom(self, zoom):
        self.pixels_per_frame = 2.0 * zoom
        self._update_clips()

    def _update_clips(self):
        for item in self.clip_items:
            x = int(item.clip.start_frame * self.pixels_per_frame)
            width = int(item.clip.duration * self.pixels_per_frame)
            item.setGeometry(x, 10, width, 40)
            item.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.track_color)
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(5, 25, self.track_name)


class TimeRuler(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.zoom = 1.0
        self.pixels_per_frame = 2.0
        self.fps = 30
        self.setMinimumHeight(30)
        self.setStyleSheet("background-color: rgb(40, 40, 40);")

    def set_zoom(self, zoom):
        self.zoom = zoom
        self.pixels_per_frame = 2.0 * zoom
        self.update()

    def set_fps(self, fps):
        self.fps = fps
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(40, 40, 40))
        painter.setPen(QColor(150, 150, 150))
        painter.setFont(QFont("Arial", 8))

        if self.zoom > 2.0:
            interval_sec = 1
        elif self.zoom > 0.5:
            interval_sec = 5
        else:
            interval_sec = 10

        interval_frames = interval_sec * self.fps
        frame = 0
        while True:
            x = int(frame * self.pixels_per_frame)
            if x >= self.width():
                break
            painter.drawLine(x, self.height() - 10, x, self.height())
            seconds = frame / self.fps
            time_str = f"{int(seconds // 60)}:{int(seconds % 60):02d}"
            painter.drawText(x + 2, 15, time_str)
            frame += interval_frames


class Playhead(QWidget):
    positionChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_frame = 0
        self.pixels_per_frame = 2.0
        self.dragging = False
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: transparent;")
        self.setCursor(Qt.ArrowCursor)

    def set_zoom(self, zoom):
        self.pixels_per_frame = 2.0 * zoom
        self.update()

    def set_current_frame(self, frame):
        self.current_frame = frame
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        x = int(self.current_frame * self.pixels_per_frame)
        painter.setPen(QPen(QColor(255, 50, 50), 2))
        painter.drawLine(x, 0, x, self.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self._update_position(event.x())

    def mouseMoveEvent(self, event):
        if self.dragging:
            self._update_position(event.x())

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def _update_position(self, x):
        frame = max(0, int(x / self.pixels_per_frame))
        self.current_frame = frame
        self.update()
        self.positionChanged.emit(frame)


class Timeline(QWidget):
    positionChanged = pyqtSignal(int)
    clipSelected = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.fps = 30
        self.total_frames = 0
        self.zoom = 1.0
        self.tracks = []

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.time_ruler = TimeRuler(self)
        main_layout.addWidget(self.time_ruler)

        self.tracks_container = QWidget()
        self.tracks_layout = QVBoxLayout()
        self.tracks_layout.setContentsMargins(0, 0, 0, 0)
        self.tracks_layout.setSpacing(2)
        self.tracks_container.setLayout(self.tracks_layout)

        scroll = QScrollArea()
        scroll.setWidget(self.tracks_container)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(scroll)

        self.playhead = Playhead(self)
        self.playhead.positionChanged.connect(self.positionChanged.emit)

        self.setLayout(main_layout)
        self.setMinimumHeight(200)
        self._create_default_tracks()

    def _create_default_tracks(self):
        video_track = TrackWidget("VIDEO", QColor(50, 50, 70), self)
        video_track.clipSelected.connect(self.clipSelected.emit)
        self.tracks.append(video_track)
        self.tracks_layout.addWidget(video_track)

        text_track = TrackWidget("TEXT", QColor(70, 50, 50), self)
        text_track.clipSelected.connect(self.clipSelected.emit)
        self.tracks.append(text_track)
        self.tracks_layout.addWidget(text_track)

        print("Pistes crees : VIDEO + TEXT")

    def add_video_clip(self, file_path, start_frame, duration_frames):
        clip = Clip("video", start_frame, start_frame + duration_frames, file_path=file_path, color=(100, 150, 255))
        self.tracks[0].add_clip(clip)
        print(f"Clip video ajoute : frames {start_frame} -> {start_frame + duration_frames}")

    def add_text_clip(self, text_content, start_frame, duration_frames):
        clip = Clip("text", start_frame, start_frame + duration_frames, text_content=text_content, color=(255, 150, 100))
        self.tracks[1].add_clip(clip)
        print(f"Clip texte ajoute : '{text_content}' frames {start_frame} -> {start_frame + duration_frames}")

    def remove_selected_clip(self):
        pass

    def set_zoom(self, zoom):
        self.zoom = max(0.1, min(zoom, 5.0))
        self.time_ruler.set_zoom(self.zoom)
        self.playhead.set_zoom(self.zoom)
        for track in self.tracks:
            track.set_zoom(self.zoom)
        self.update()

    def set_fps(self, fps):
        self.fps = fps
        self.time_ruler.set_fps(fps)

    def set_total_frames(self, total):
        self.total_frames = total

    def set_current_frame(self, frame):
        self.playhead.set_current_frame(frame)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.playhead.setGeometry(0, 0, self.width(), self.height())

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            factor = 1.1 if delta > 0 else 0.9
            self.set_zoom(self.zoom * factor)
            event.accept()
        else:
            super().wheelEvent(event)
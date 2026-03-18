from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QMenu, QAction
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

        self.font = "Arial"
        self.size = 1.0
        self.text_color = (255, 255, 255)
        self.position = (0.5, 0.5)
        self.align = "center"
        self.background_color = None
        self.stroke = None

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
        self.drag_start_x = 0 
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
            self.drag_start_x = event.x()
            self.clicked.emit(self)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta_x = event.x() - self.drag_start_x
            new_x = self.x() + delta_x
            new_start = int(new_x / self.parent().pixels_per_frame)
            new_start = max(0, new_start)
            duration = self.clip.duration
            self.clip.start_frame = new_start
            self.clip.end_frame = new_start + duration
            self.parent()._update_clips()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        delete_action = QAction("Supprimer", self)
        delete_action.triggered.connect(self._delete_clip)
        menu.addAction(delete_action)
        duplicate_action = QAction("Dupliquer", self)
        duplicate_action.triggered.connect(self._duplicate_clip)
        menu.addAction(duplicate_action)
        menu.exec_(event.globalPos())

    def _delete_clip(self):
        track = self.parent()
        if track:
            track.remove_clip(self.clip)

    def _duplicate_clip(self):
        track = self.parent()
        if track:
            new_clip = Clip(
                clip_type=self.clip.clip_type,
                start_frame=self.clip.end_frame,
                end_frame=self.clip.end_frame + self.clip.duration,
                file_path=self.clip.file_path,
                text_content=self.clip.text_content,
                color=self.clip.color
            )
        
            if hasattr(self.clip, 'font'):
                new_clip.font = self.clip.font
                new_clip.size = self.clip.size
                new_clip.text_color = self.clip.text_color
                new_clip.position = self.clip.position
                new_clip.align = self.clip.align
                new_clip.background_color = self.clip.background_color
                new_clip.stroke = self.clip.stroke
            track.add_clip(new_clip)

class TrackWidget(QWidget):
    clipSelected = pyqtSignal(object)

    def __init__(self, track_name, track_color, parent=None):
        super().__init__(parent)
        self.track_name = track_name
        self.track_color = track_color
        self.clips = []
        self.clip_items = []
        self.selected_clip = None
        self.pixels_per_frame = 2.0
        self.setMinimumHeight(60)
        self.setStyleSheet(f"background-color: rgb{track_color.getRgb()[:3]};")

    def add_clip(self, clip):
        self.clips.append(clip)
        item = ClipItem(clip, self)
        item.clicked.connect(self._on_clip_clicked)
        self.clip_items.append(item)
        self._update_clips()

    def _on_clip_clicked(self, item):
        for clip_item in self.clip_items:
            clip_item.is_selected = False
            clip_item.update()
        item.is_selected = True
        item.update()
        self.selected_clip = item.clip
        self.clipSelected.emit(item.clip)

    def remove_clip(self, clip):
        if clip in self.clips:
            i = self.clips.index(clip)
            self.clips.pop(i)
            item = self.clip_items.pop(i)
            item.deleteLater()
            self._update_clips()
    
    def remove_selected_clip(self):
        if self.selected_clip:
            self.remove_clip(self.selected_clip)
            self.selected_clip = None

    def set_zoom(self, zoom):
        self.pixels_per_frame = 2.0 * zoom
        self._update_clips()

    def _update_clips(self):
        max_width = 0
        for item in self.clip_items:
            x = int(item.clip.start_frame * self.pixels_per_frame)
            width = int(item.clip.duration * self.pixels_per_frame)
            item.setGeometry(x, 10, width, 40)
            item.show()
        
            clip_end_x = x + width
            if clip_end_x > max_width:
                max_width = clip_end_x
    
        if max_width > 0:
            self.setMinimumWidth(max_width + 100)
        
            timeline = self._get_timeline()
            if timeline:
                timeline._sync_widths(max_width + 100)

    def _get_timeline(self):  
        parent = self.parent()
        while parent:
            if isinstance(parent, Timeline):
                return parent
            parent = parent.parent()
        return None

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
        self.setMaximumHeight(30)
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._update_playhead_position(event.x())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self._update_playhead_position(event.x())

    def _update_playhead_position(self, x):
        frame = max(0, int(x / self.pixels_per_frame))

        timeline = self._get_timeline()
        if timeline:
            timeline.set_current_frame(frame)
            timeline.positionChanged.emit(frame)

    def _get_timeline(self):
        parent = self.parent()
        while parent:
            if isinstance(parent, Timeline):
                return parent
            parent = parent.parent()
        return None

class Playhead(QWidget):
    positionChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_frame = 0
        self.pixels_per_frame = 2.0
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
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


class Timeline(QWidget):
    positionChanged = pyqtSignal(int)
    clipSelected = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.fps = 30
        self.total_frames = 0
        self.zoom = 1.0
        self.tracks = []
        self.setFocusPolicy(Qt.StrongFocus)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.scroll_container = QWidget()
        scroll_container_layout = QVBoxLayout()
        scroll_container_layout.setContentsMargins(0, 0, 0, 0)
        scroll_container_layout.setSpacing(0)

        self.time_ruler = TimeRuler(self)
        scroll_container_layout.addWidget(self.time_ruler)

        self.tracks_container = QWidget()
        self.tracks_layout = QVBoxLayout()
        self.tracks_layout.setContentsMargins(0, 0, 0, 0)
        self.tracks_layout.setSpacing(2)
        self.tracks_container.setLayout(self.tracks_layout)
        scroll_container_layout.addWidget(self.tracks_container)

        self.scroll_container.setLayout(scroll_container_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.scroll_container)
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumHeight(150)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(self.scroll)

        self.playhead = Playhead(self)
        self.playhead.positionChanged.connect(self.positionChanged.emit)
        self.playhead.raise_()  
        self.playhead.show()    

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
        for track in self.tracks:
            track.remove_selected_clip()
        print("Clip selectionne supprime")

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

    def _sync_widths(self, width):
        self.time_ruler.setMinimumWidth(width)
        self.tracks_container.setMinimumWidth(width)
        self.scroll_container.setMinimumWidth(width) 

    def resizeEvent(self, event):
        super().resizeEvent(event)
        playhead_width = max(self.scroll.width(), self.scroll_container.width())
        playhead_height = self.scroll.height()
        
        self.playhead.setGeometry(
            self.scroll.x(), 
            self.scroll.y(), 
            playhead_width, 
            playhead_height
        )
        self.playhead.raise_() 

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            factor = 1.1 if delta > 0 else 0.9
            self.set_zoom(self.zoom * factor)
            event.accept()
        else:
            super().wheelEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.remove_selected_clip()
        else:
            super().keyPressEvent(event)
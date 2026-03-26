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
        self.is_resizing = False
        self.was_moved = False
        self.resize_margin = 6
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

    def _outil_coupe_actif(self):
        timeline = self.parent()._trouver_timeline()
        return bool(timeline and getattr(timeline, "current_tool", "select") == "cut")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._outil_coupe_actif():
                timeline = self.parent()._trouver_timeline()
                if timeline:
                    local_x = max(0, min(event.x(), self.width()))
                    pixels_per_frame = max(0.1, float(self.parent().pixels_per_frame))
                    cut_frame = self.clip.start_frame + int(local_x / pixels_per_frame)
                    timeline.couper_clip(self.clip, cut_frame)
                self.is_resizing = False
                self.was_moved = False
                self.drag_start_x = 0
                event.accept()
                return
            if event.x() >= self.width() - self.resize_margin:
                self.is_resizing = True
            else:
                self.is_resizing = False
            self.drag_start_x = event.x()
            self.was_moved = False
            self.clicked.emit(self)

    def mouseMoveEvent(self, event):
        if self._outil_coupe_actif():
            return
        if event.buttons() == Qt.LeftButton:
            if self.is_resizing:
                local_x = max(1, event.x())
                new_end = int((self.x() + local_x) / self.parent().pixels_per_frame)
                if new_end <= self.clip.start_frame:
                    new_end = self.clip.start_frame + 1
                self.clip.end_frame = new_end
                self.parent()._maj_clips()
            else:
                delta_x = event.x() - self.drag_start_x
                if delta_x != 0:
                    self.was_moved = True
                new_x = self.x() + delta_x
                new_start = int(new_x / self.parent().pixels_per_frame)
                new_start = max(0, new_start)
                duration = self.clip.duration
                self.clip.start_frame = new_start
                self.clip.end_frame = new_start + duration
                self.parent()._maj_clips()

    def mouseReleaseEvent(self, event):
        if self._outil_coupe_actif():
            return
        if event.button() == Qt.LeftButton:
            if self.is_resizing or self.was_moved:
                timeline = self.parent()._trouver_timeline()
                if timeline:
                    timeline.clipsChanged.emit()
            self.is_resizing = False
            self.was_moved = False

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        delete_action = QAction("Supprimer", self)
        delete_action.triggered.connect(self._supprimer_clip)
        menu.addAction(delete_action)
        duplicate_action = QAction("Dupliquer", self)
        duplicate_action.triggered.connect(self._dupliquer_clip)
        menu.addAction(duplicate_action)
        if self.clip.clip_type == "text":
            shorten_action = QAction("Raccourcir 1s", self)
            shorten_action.triggered.connect(self._raccourcir_texte)
            menu.addAction(shorten_action)
            lengthen_action = QAction("Allonger 1s", self)
            lengthen_action.triggered.connect(self._allonger_texte)
            menu.addAction(lengthen_action)
        menu.exec_(event.globalPos())

    def _supprimer_clip(self):
        track = self.parent()
        if track:
            track.supprimer_clip(self.clip)
            timeline = track._trouver_timeline()
            if timeline:
                timeline.clipsChanged.emit()

    def _dupliquer_clip(self):
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
            if hasattr(self.clip, "source_in"):
                new_clip.source_in = self.clip.source_in
            track.ajouter_clip(new_clip)
            timeline = track._trouver_timeline()
            if timeline:
                timeline.clipsChanged.emit()

    def _raccourcir_texte(self):
        self._ajuster_duree_texte(delta_seconds=-1)

    def _allonger_texte(self):
        self._ajuster_duree_texte(delta_seconds=1)

    def _ajuster_duree_texte(self, delta_seconds):
        if self.clip.clip_type != "text":
            return
        track = self.parent()
        if not track:
            return
        timeline = track._trouver_timeline()
        fps = timeline.fps if timeline and timeline.fps else 30
        delta_frames = int(max(1, round(delta_seconds * fps)))
        new_end = self.clip.end_frame + delta_frames
        if new_end <= self.clip.start_frame:
            new_end = self.clip.start_frame + 1
        self.clip.end_frame = new_end
        track._maj_clips()

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
        self.setAcceptDrops(True)

    def _curseur_outil(self, tool):
        return Qt.SplitVCursor if tool == "cut" else Qt.PointingHandCursor

    def _appliquer_curseur(self, item):
        timeline = self._trouver_timeline()
        tool = getattr(timeline, "current_tool", "select") if timeline else "select"
        item.setCursor(self._curseur_outil(tool))

    def ajouter_clip(self, clip):
        self.clips.append(clip)
        item = ClipItem(clip, self)
        item.clicked.connect(self._clip_clique)
        self.clip_items.append(item)
        self._appliquer_curseur(item)
        self._maj_clips()

    def inserer_clip(self, index, clip):
        self.clips.insert(index, clip)
        item = ClipItem(clip, self)
        item.clicked.connect(self._clip_clique)
        self.clip_items.insert(index, item)
        self._appliquer_curseur(item)
        self._maj_clips()

    def regler_curseur_outil(self, tool):
        cursor = self._curseur_outil(tool)
        self.setCursor(cursor)
        for item in self.clip_items:
            item.setCursor(cursor)

    def _clip_clique(self, item):
        for clip_item in self.clip_items:
            clip_item.is_selected = False
            clip_item.update()
        item.is_selected = True
        item.update()
        self.selected_clip = item.clip
        self.clipSelected.emit(item.clip)

    def supprimer_clip(self, clip):
        if clip in self.clips:
            i = self.clips.index(clip)
            self.clips.pop(i)
            item = self.clip_items.pop(i)
            item.deleteLater()
            self._maj_clips()
    
    def supprimer_clip_selectionne(self):
        if self.selected_clip:
            self.supprimer_clip(self.selected_clip)
            self.selected_clip = None
    
    def vider(self):
        for item in self.clip_items:
            item.deleteLater()
        self.clips = []
        self.clip_items = []
        self.selected_clip = None
        self._maj_clips()

    def regler_zoom(self, zoom):
        self.pixels_per_frame = 2.0 * zoom
        self._maj_clips()

    def _maj_clips(self):
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
        
            timeline = self._trouver_timeline()
            if timeline:
                timeline._maj_largeurs(max_width + 100)

    def _trouver_timeline(self):  
        parent = self.parent()
        while parent:
            if isinstance(parent, Timeline):
                return parent
            parent = parent.parent()
        return None

    def dragEnterEvent(self, event):
        if self.track_name == "VIDEO" and event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if self.track_name == "VIDEO" and event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if self.track_name != "VIDEO" or not event.mimeData().hasUrls():
            return
        timeline = self._trouver_timeline()
        if not timeline:
            return
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path:
                timeline.mediaDropped.emit(path)
        event.acceptProposedAction()

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

    def regler_zoom(self, zoom):
        self.zoom = zoom
        self.pixels_per_frame = 2.0 * zoom
        self.update()

    def regler_fps(self, fps):
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
            self._maj_position_lecture(event.x())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self._maj_position_lecture(event.x())

    def _maj_position_lecture(self, x):
        frame = max(0, int(x / self.pixels_per_frame))

        timeline = self._trouver_timeline()
        if timeline:
            timeline.regler_frame(frame)
            timeline.positionChanged.emit(frame)

    def _trouver_timeline(self):
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

    def regler_zoom(self, zoom):
        self.pixels_per_frame = 2.0 * zoom
        self.update()

    def regler_frame(self, frame):
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
    clipsChanged = pyqtSignal()
    mediaDropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.fps = 30
        self.total_frames = 0
        self.zoom = 1.0
        self.tracks = []
        self.current_tool = "select"
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
        self._creer_pistes()
        self.choisir_outil(self.current_tool)

    def _creer_pistes(self):
        video_track = TrackWidget("VIDEO", QColor(50, 50, 70), self)
        video_track.clipSelected.connect(self.clipSelected.emit)
        self.tracks.append(video_track)
        self.tracks_layout.addWidget(video_track)

        text_track = TrackWidget("TEXT", QColor(70, 50, 50), self)
        text_track.clipSelected.connect(self.clipSelected.emit)
        self.tracks.append(text_track)
        self.tracks_layout.addWidget(text_track)

        print("Pistes crees : VIDEO + TEXT")

    def choisir_outil(self, tool):
        self.current_tool = tool or "select"
        for track in self.tracks:
            track.regler_curseur_outil(self.current_tool)

    def _copier_style(self, source, target):
        for attr in ("font", "size", "text_color", "position", "align", "background_color", "stroke"):
            if hasattr(source, attr):
                setattr(target, attr, getattr(source, attr))
        if hasattr(source, "preview_size"):
            target.preview_size = source.preview_size

    def _piste_du_clip(self, clip):
        for track in self.tracks:
            if clip in track.clips:
                return track
        return None

    def couper_clip(self, clip, frame):
        if not clip:
            return None
        if frame <= clip.start_frame or frame >= clip.end_frame:
            return None
        track = self._piste_du_clip(clip)
        if not track:
            return None

        original_start = clip.start_frame
        original_end = clip.end_frame
        left_duration = frame - original_start
        right_duration = original_end - frame
        if left_duration <= 0 or right_duration <= 0:
            return None

        clip.end_frame = frame
        new_clip = Clip(
            clip_type=clip.clip_type,
            start_frame=frame,
            end_frame=original_end,
            file_path=clip.file_path,
            text_content=clip.text_content,
            color=clip.color
        )
        self._copier_style(clip, new_clip)
        if hasattr(clip, "source_in"):
            base_in = getattr(clip, "source_in", 0)
            try:
                base_in = int(base_in)
            except Exception:
                pass
            new_clip.source_in = base_in + left_duration

        track.inserer_clip(track.clips.index(clip) + 1, new_clip)
        self.clipsChanged.emit()
        return new_clip

    def ajouter_clip_video(self, file_path, start_frame, duration_frames):
        clip = Clip("video", start_frame, start_frame + duration_frames, file_path=file_path, color=(100, 150, 255))
        clip.source_in = 0
        self.tracks[0].ajouter_clip(clip)
        print(f"Clip video ajoute : frames {start_frame} -> {start_frame + duration_frames}")
        return clip

    def ajouter_clip_texte(self, text_content, start_frame, duration_frames, text_color=None, text_size=1.0, position=(0.5, 0.5), align="center"):
        clip = Clip("text", start_frame, start_frame + duration_frames, text_content=text_content, color=(255, 150, 100))
        clip.text_color = text_color if text_color is not None else clip.text_color
        clip.size = text_size if text_size is not None else clip.size
        clip.position = position if position is not None else clip.position
        clip.align = align if align is not None else clip.align
        self.tracks[1].ajouter_clip(clip)
        print(f"Clip texte ajoute : '{text_content}' frames {start_frame} -> {start_frame + duration_frames}")
        return clip

    def supprimer_clip_selectionne(self):
        for track in self.tracks:
            track.supprimer_clip_selectionne()
        print("Clip selectionne supprime")

    def vider_tous_les_clips(self):
        for track in self.tracks:
            track.vider()
        self.regler_frame(0)
        self.regler_total_frames(0)

    def regler_zoom(self, zoom):
        self.zoom = max(0.1, min(zoom, 5.0))
        self.time_ruler.regler_zoom(self.zoom)
        self.playhead.regler_zoom(self.zoom)
        for track in self.tracks:
            track.regler_zoom(self.zoom)
        self.update()

    def regler_fps(self, fps):
        self.fps = fps
        self.time_ruler.regler_fps(fps)

    def regler_total_frames(self, total):
        self.total_frames = total
        if total:
            width = int(total * self.time_ruler.pixels_per_frame) + 100
            self._maj_largeurs(width)

    def regler_frame(self, frame):
        self.playhead.regler_frame(frame)

    def _maj_largeurs(self, width):
        min_width = width
        if self.total_frames:
            min_width = max(min_width, int(self.total_frames * self.time_ruler.pixels_per_frame) + 100)
        self.time_ruler.setMinimumWidth(min_width)
        self.tracks_container.setMinimumWidth(min_width)
        self.scroll_container.setMinimumWidth(min_width)

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
            self.regler_zoom(self.zoom * factor)
            event.accept()
        else:
            super().wheelEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.supprimer_clip_selectionne()
        else:
            super().keyPressEvent(event)

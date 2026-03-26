
from PyQt5.QtWidgets import (QLineEdit, QWidget, QPushButton, QLabel, 
                             QVBoxLayout, QHBoxLayout, QMainWindow, QSlider,
                             QGridLayout, QProgressDialog, QApplication,
                             QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QEvent, QUrl
from PyQt5.QtGui import QIcon, QImage, QPixmap
try:
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
except Exception:
    QMediaPlayer = None
    QMediaContent = None
import cv2
import numpy as np

from utils import import_video, save_as_path
from dialogs import txt_contentWindow, txt_videotitle
from save_manager import sauver_projet, load_project_data, load_project_data_from_path
from timeline import Timeline
import config

from toolbox import ToolboxDock

import sys
import json
import os
import glob
from pathlib import Path

VIDEO_EXTENSIONS = {
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg",
    ".mpg", ".3gp", ".ts", ".mts", ".m2ts", ".vob", ".ogv", ".rm", ".rmvb",
    ".divx", ".xvid",
}





class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Creatakis")
        self.setWindowIcon(QIcon("assets/logo.png"))
        self.setGeometry(300, 300, 1280, 720)
        self.setStyleSheet('background-color: grey;')

        # TOOLBOX
        self.toolbox = ToolboxDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.toolbox)
        self.toolbox.definir_controleur(self)

        #enlever le focus des boutons
        config.focus_boutons(self)

        # ===== MENU =====
        menubar = self.menuBar()
        menubar.setStyleSheet('background-color: grey;')

        fichier = menubar.addMenu("Fichier")
        fichier.setStyleSheet("background-color: white; color: black;")
        fichier.addAction("Nouveau")
        fichier.addAction("Ouvrir", self.load)
        fichier.addAction("Enregistrer")
        fichier.addAction("Enregistrer sous", self.sauvegarder)
        fichier.addAction("Importer media", self.importer_media)
        fichier.addAction("Exporter media", self.exporter_media)
        fichier.addAction("Quitter", self.quitter)

        affichage = menubar.addMenu("Affichage")
        affichage.setStyleSheet("background-color: white; color: black;")
        affichage.addAction("Plein ecran", self.showFullScreen)
        affichage.addAction("Quitter plein ecran", self.showNormal)
        affichage.addAction("Afficher la ToolBox", self.showtoolbox)

        # ===== CENTRAL WIDGET =====
        central = QWidget(self)
        self.setCentralWidget(central)

        # ===== VIDEO PLAYER OpenCV =====
        self.selected_text_clip = None
        self.dragging_text = False

        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 360)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.installEventFilter(self)

        self.btn_play = QPushButton('▶️')
        self.btn_pause = QPushButton('⏸️')
        self.btn_stop = QPushButton('⏹️')

        self.btn_play.setStyleSheet('background-color: grey;')
        self.btn_pause.setStyleSheet('background-color: grey;')
        self.btn_stop.setStyleSheet('background-color: grey;')
        self.toolbox.btn_add_text.setStyleSheet('background-color: grey;')
        self.toolbox.btn_cut_tool.setStyleSheet(
            "QPushButton { background-color: grey; }"
            "QPushButton:checked { background-color: #d08a2b; color: black; }"
        )
        self.toolbox.btn_remove_text.setStyleSheet('background-color: grey;')

        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)
        self.toolbox.btn_add_text.clicked.connect(self.add_text_dialog)
        self.toolbox.btn_cut_tool.toggled.connect(self.on_cut_tool_toggled)
        self.toolbox.btn_remove_text.clicked.connect(self.remove_text)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)

        self.timeline = Timeline(self)
        self.timeline.positionChanged.connect(self.seek_video)
        self.timeline.clipSelected.connect(self.on_clip_selected)
        self.timeline.clipsChanged.connect(self.on_timeline_clips_changed)
        self.timeline.mediaDropped.connect(self.on_media_dropped)

        # LAYOUT
        videoTimeline_layout = QVBoxLayout()
        videoTimeline_layout.addWidget(self.timeline)

        VideoControl_layout = QHBoxLayout()
        VideoControl_layout.addWidget(self.btn_play)
        VideoControl_layout.addWidget(self.btn_pause)
        VideoControl_layout.addWidget(self.btn_stop)
        #VideoControl_layout.addWidget(self.btn_add_text)
        #VideoControl_layout.addWidget(self.btn_remove_text)
        VideoControl_layout.addStretch()
        VideoControl_layout.addWidget(QLabel("Volume:"))
        VideoControl_layout.addWidget(self.volume_slider)

        VideoToolbox_layout = QHBoxLayout()
        VideoToolbox_layout.addWidget(self.toolbox)

        video_container = QVBoxLayout()
        video_container.addWidget(self.video_label, 0, Qt.AlignCenter)
        video_container.addLayout(VideoControl_layout)

        VideoMain_layout = QGridLayout()
        VideoMain_layout.addLayout(videoTimeline_layout, 5, 0, 1, 3)
        VideoMain_layout.addLayout(video_container, 1, 2)
        VideoMain_layout.addLayout(VideoToolbox_layout,1,0,1,2)
        VideoMain_layout.setColumnStretch(0, 1)
        VideoMain_layout.setColumnStretch(1, 1)
        VideoMain_layout.setColumnStretch(2, 2)

        central.setLayout(VideoMain_layout)

        self.cap = None
        self.fps = 30
        self.frame_interval = 33
        self.timeline_fps = None
        self.is_playing = False
        self.text_to_display = None
        self.text_color = (255, 255, 255)
        self.text_font = cv2.FONT_HERSHEY_SIMPLEX
        self.text_size = 1
        self.text_thickness = 2
        config.total_frames = 0
        self.export_font_path = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.display_frame)

        self.media_playlist = []
        self.media_offsets = []
        self.current_media_index = -1
        self.current_media_in = None
        self.current_media_out = None
        self.audio_player = None
        self.audio_current_path = None
        self.audio_sync_threshold_ms = 120
        self._init_audio()

    def _est_video(self, path):
        if not path:
            return False
        return Path(path).suffix.lower() in VIDEO_EXTENSIONS

    def _popup_fichier_non_video(self):
        QMessageBox.warning(self, "Fichier invalide", "Le fichier importé doit etre une vidéo !")

    def _init_audio(self):
        if not QMediaPlayer or not QMediaContent:
            print("Audio indisponible (QtMultimedia manquant).")
            return
        self.audio_player = QMediaPlayer(self)
        self.audio_player.setVolume(self.volume_slider.value())

    def on_volume_changed(self, value):
        if self.audio_player:
            self.audio_player.setVolume(int(value))

    def _set_audio_media(self, path):
        if not self.audio_player or not path:
            return False
        if self.audio_current_path != path:
            self.audio_player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
            self.audio_current_path = path
        return True

    def _audio_position_ms(self, frame, fps):
        if not fps or fps <= 0:
            fps = 30
        return int((frame / fps) * 1000)

    def _sync_audio_to_frame(self, frame_number, force=False):
        if not self.audio_player or not self.media_playlist:
            return
        index, local_frame = self._media_pour_frame(frame_number)
        if index is None:
            return
        clip_info = self.media_playlist[index]
        path = clip_info.get("path")
        in_frame = int(clip_info.get("in_frame") or 0)
        fps = clip_info.get("fps") or self.fps or 30
        if not self._set_audio_media(path):
            return
        target_ms = self._audio_position_ms(in_frame + local_frame, fps)
        current_ms = self.audio_player.position()
        if force or abs(current_ms - target_ms) > self.audio_sync_threshold_ms:
            self.audio_player.setPosition(target_ms)
        if self.is_playing:
            if self.audio_player.state() != QMediaPlayer.PlayingState:
                self.audio_player.play()
        else:
            if self.audio_player.state() == QMediaPlayer.PlayingState:
                self.audio_player.pause()

    def _stop_audio(self):
        if self.audio_player:
            self.audio_player.stop()

    def _reset_audio(self):
        if self.audio_player:
            self.audio_player.stop()
            try:
                self.audio_player.setMedia(QMediaContent())
            except Exception:
                pass
        self.audio_current_path = None

    def _maj_playlist(self):
        if not self.timeline.tracks:
            return
        video_track = self.timeline.tracks[0]
        clips = sorted(video_track.clips, key=lambda c: c.start_frame)
        config.clips = {}
        fps = self.timeline_fps or self.fps or 30
        idx = 0
        for clip in clips:
            frames = int(clip.duration)
            if frames <= 0:
                continue
            in_frame = int(getattr(clip, "source_in", 0))
            config.clips[str(idx)] = {
                "path": clip.file_path,
                "fps": fps,
                "frames": frames,
                "in_frame": in_frame,
            }
            idx += 1
        self._recalcule_playlist()

    def on_timeline_clips_changed(self):
        current_frame = self.timeline.playhead.current_frame
        self.is_playing = False
        self.timer.stop()
        self._reset_audio()
        self._maj_playlist()
        self.cap = None
        self.current_media_index = -1
        if config.total_frames and config.total_frames > 0:
            current_frame = min(current_frame, config.total_frames - 1)
            self.seek_video(current_frame)

    def _recalcule_playlist(self):
        self.media_playlist = list(config.clips.values())
        self.media_offsets = []
        total = 0
        for clip_info in self.media_playlist:
            self.media_offsets.append(total)
            total += int(clip_info.get("frames") or 0)
        config.total_frames = total
        self.timeline.regler_total_frames(total)

    def _ouvrir_media(self, index):
        if index < 0 or index >= len(self.media_playlist):
            return False

        clip_info = self.media_playlist[index]
        path = clip_info.get("path")
        in_frame = int(clip_info.get("in_frame") or 0)
        frames = int(clip_info.get("frames") or 0)
        if not path:
            return False

        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(path)
        if not self.cap or not self.cap.isOpened():
            print(f"Impossible d'ouvrir la video: {path}")
            return False

        self.current_media_index = index
        self.current_media_in = in_frame
        self.current_media_out = in_frame + frames if frames else None
        fps = clip_info.get("fps") or self.cap.get(cv2.CAP_PROP_FPS)
        self.fps = fps if fps and fps > 0 else 30
        self.frame_interval = int(1000 / self.fps) if self.fps > 0 else 33

        if in_frame:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, in_frame)

        if self.timeline_fps is None:
            self.timeline_fps = self.fps
            self.timeline.regler_fps(self.timeline_fps)
        elif abs(self.timeline_fps - self.fps) > 0.01:
            print("Avertissement: FPS differents entre les clips (lecture supposee identique).")

        return True

    def _media_pour_frame(self, frame_number):
        if not self.media_playlist:
            return None, None

        for i, clip_info in enumerate(self.media_playlist):
            frames = int(clip_info.get("frames") or 0)
            start = self.media_offsets[i]
            end = start + frames
            if frame_number < end:
                return i, max(0, frame_number - start)

        last = len(self.media_playlist) - 1
        start = self.media_offsets[last]
        return last, max(0, frame_number - start)

    def _ajouter_media(self, path, start_frame=None):
        if not path:
            return
        if not self._est_video(path):
            self._popup_fichier_non_video()
            return

        fps, frames = self._infos_video(path)
        if not fps or not frames:
            self._popup_fichier_non_video()
            print(f"Impossible de lire les metadonnees video: {path}")
            return

        if self.timeline_fps is None:
            self.timeline_fps = fps if fps and fps > 0 else 30
            self.timeline.regler_fps(self.timeline_fps)
        elif fps and abs(self.timeline_fps - fps) > 0.01:
            print("Avertissement: FPS differents entre les clips (timeline supposee identique).")

        config.file_path = str(path)

        if start_frame is None:
            if not config.clips:
                id_media = 0
            else:
                try:
                    id_media = max(int(k) for k in config.clips.keys()) + 1
                except (ValueError, TypeError):
                    id_media = len(config.clips)

            config.clips[str(id_media)] = {
                "path": str(path),
                "fps": fps,
                "frames": frames,
                "in_frame": 0,
            }

            self._recalcule_playlist()
            index = len(self.media_playlist) - 1
            start_frame = self.media_offsets[index]

            self.timeline.ajouter_clip_video(str(path), start_frame, frames)
            self.timeline.regler_frame(start_frame)

            if self.cap is None:
                self._ouvrir_media(0)
                if self.cap:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        else:
            self.timeline.ajouter_clip_video(str(path), start_frame, frames)
            self.timeline.regler_frame(start_frame)
            self.on_timeline_clips_changed()

        print(f"Video imported: {path}")
        print(f"FPS: {self.fps}, Total frames: {config.total_frames}")

    def _infos_video(self, path):
        cap_probe = cv2.VideoCapture(path)
        if not cap_probe or not cap_probe.isOpened():
            return None, None

        fps = cap_probe.get(cv2.CAP_PROP_FPS)
        frames_raw = int(cap_probe.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_ms = 0
        try:
            cap_probe.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
            duration_ms = cap_probe.get(cv2.CAP_PROP_POS_MSEC)
        except Exception:
            duration_ms = 0
        cap_probe.release()

        frames = frames_raw
        if fps and duration_ms:
            frames_from_time = int(round((duration_ms / 1000.0) * fps))
            if frames_from_time > 0:
                frames = frames_from_time

        if (not fps or fps <= 0) or (not frames or frames <= 0):
            try:
                from moviepy import VideoFileClip
                clip = VideoFileClip(path)
                fps = clip.fps or fps or 30
                frames = int(round(clip.duration * fps)) if clip.duration else frames
                clip.close()
            except Exception as e:
                print(f"Fallback MoviePy echoue: {e}")

        if fps and frames:
            return fps, frames
        return None, None

    def add_media_from_path(self, path):
        self._ajouter_media(path)

    def on_media_dropped(self, path):
        self.is_playing = False
        self.timer.stop()
        start_frame = 0
        if self.timeline.tracks:
            video_track = self.timeline.tracks[0]
            if video_track.clips:
                start_frame = max(c.end_frame for c in video_track.clips)
        self._ajouter_media(path, start_frame=start_frame)

    def importer_media(self):
        config.file_path, config.nom_fichier = import_video()
        if config.file_path:
            if not self._est_video(config.file_path):
                self._popup_fichier_non_video()
                config.file_path = None
                return
            if hasattr(self.toolbox, "tree"):
                self.toolbox.tree.ajouter_media(config.file_path)
            else:
                print("Toolbox indisponible, impossible d'ajouter le media a la bibliotheque.")

    def display_frame(self, force=False):
        global text
        if self.cap is None or (not self.is_playing and not force):
            return

        if self.current_media_out is not None:
            pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            if pos >= self.current_media_out:
                if self._ouvrir_media(self.current_media_index + 1):
                    self.timer.start(self.frame_interval)
                else:
                    self.stop()
                    return

        ret, frame = self.cap.read()
        if not ret:
            if self._ouvrir_media(self.current_media_index + 1):
                self.timer.start(self.frame_interval)
                ret, frame = self.cap.read()
                if not ret:
                    self.stop()
                    return
            else:
                self.stop()
                return

        label_width = self.video_label.width()
        label_height = self.video_label.height()
        frame = cv2.resize(frame, (label_width, label_height))

        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        if self.current_media_in is not None:
            current_frame = current_frame - self.current_media_in
        if 0 <= self.current_media_index < len(self.media_offsets):
            current_frame += self.media_offsets[self.current_media_index]
        self._dessiner_textes(frame, current_frame)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgba = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2RGBA)
        h, w, ch = frame_rgba.shape
        bytes_per_line = 4 * w
        qt_image = QImage(
            frame_rgba.tobytes(),
            w,
            h,
            bytes_per_line,
            QImage.Format_RGBA8888
        )

        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap)

        self.timeline.regler_frame(current_frame)
        if self.is_playing:
            self._sync_audio_to_frame(current_frame)

    def play(self):
        if self.cap is None:
            if self.media_playlist:
                if not self._ouvrir_media(0):
                    print("Veuillez importer une video d'abord")
                    return
            else:
                print("Veuillez importer une video d'abord")
                return
        self.is_playing = True
        self.timer.start(self.frame_interval)
        self._sync_audio_to_frame(self.timeline.playhead.current_frame, force=True)
        print("Lecture en cours...")

    def pause(self):
        self.is_playing = False
        self.timer.stop()
        if self.audio_player:
            self.audio_player.pause()
        print("Pause...")

    def stop(self):
        self.is_playing = False
        self.timer.stop()
        if self.media_playlist:
            self._ouvrir_media(0)
            if self.cap:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.timeline.regler_frame(0)
        elif self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.timeline.regler_frame(0)
        self._sync_audio_to_frame(0, force=True)
        self._stop_audio()
        print("Arret...")

    def seek_video(self, frame_number):
        if not self.media_playlist:
            if self.cap:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                self.display_frame(force=True)
            self._sync_audio_to_frame(frame_number, force=True)
            return

        index, local_frame = self._media_pour_frame(frame_number)
        if index is None:
            return
        if index != self.current_media_index:
            if not self._ouvrir_media(index):
                return
        if self.cap:
            in_frame = self.current_media_in or 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, in_frame + local_frame)
            self.display_frame(force=True)
        self._sync_audio_to_frame(frame_number, force=True)

    def add_text_dialog(self):
        if self.cap is None:
            print("Veuillez importer une video d'abord")
            return

        dialog = txt_contentWindow()
        if dialog.exec_():
            self.text_color = dialog.text_color
            self.text_size = float(dialog.text_size)

            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            if 0 <= self.current_media_index < len(self.media_offsets):
                current_frame += self.media_offsets[self.current_media_index]
            fps = self.timeline_fps or self.fps or 30
            text_duration = int(5 * fps)

            clip = self.timeline.ajouter_clip_texte(
                text_content=dialog.text_value,
                start_frame=current_frame,
                duration_frames=text_duration,
                text_color=self.text_color,
                text_size=self.text_size,
                position=(0.5, 0.5),
                align="center",
            )
            self.selected_text_clip = clip
            if clip:
                clip.preview_size = (self.video_label.width(), self.video_label.height())

            print(f"Texte ajoute: {dialog.text_value}")
            self.display_frame(force=True)

    def on_clip_selected(self, clip):
        print(f"Clip selectionne : {clip}")
        if clip.clip_type == "text":
            print(f"Contenu texte : {clip.text_content}")
            self.selected_text_clip = clip
        else:
            self.selected_text_clip = None

    def remove_text(self):
        if self.selected_text_clip and self.timeline.tracks:
            self.timeline.tracks[1].supprimer_clip(self.selected_text_clip)
            self.selected_text_clip = None
            self.display_frame(force=True)
            print("Texte supprime")
        else:
            print("Aucun texte selectionne")

    def on_cut_tool_toggled(self, checked):
        if hasattr(self, "timeline"):
            self.timeline.choisir_outil("cut" if checked else "select")

    def demander_nom_export(self):
        dialog = txt_videotitle()
        if dialog.exec_():
            return dialog.text_value
        return None

    def exporter_media(self, export_name=None):
        if not self.timeline.tracks:
            print("No timeline available.")
            return
        video_track = self.timeline.tracks[0] if len(self.timeline.tracks) > 0 else None
        text_track = self.timeline.tracks[1] if len(self.timeline.tracks) > 1 else None
        if not video_track or not video_track.clips:
            print("No video loaded. Please import a video first.")
            return
        if export_name is None:
            export_name = self.demander_nom_export()
        if export_name:
            from moviepy import VideoFileClip, CompositeVideoClip, ColorClip, ImageClip
            from proglog import ProgressBarLogger

            fps = self.timeline_fps or self.fps or 30
            total_frames = self.timeline.total_frames
            if not total_frames:
                max_end = 0
                for track in self.timeline.tracks:
                    for c in track.clips:
                        max_end = max(max_end, c.end_frame)
                total_frames = max_end
            total_duration = total_frames / fps if fps else 0

            base_size = None
            layers = []
            opened = []

            try:
                progress = QProgressDialog("Exportation en cours...", None, 0, 0, self)
                progress.setWindowTitle("Exportation")
                progress.setWindowModality(Qt.ApplicationModal)
                progress.setCancelButton(None)
                progress.setMinimumDuration(0)
                progress.setAutoClose(True)
                progress.show()

                class ExportLogger(ProgressBarLogger):
                    def __init__(self, dialog):
                        super().__init__()
                        self.dialog = dialog
                        self.main_bar = None
                        self.total = None

                    def bars_callback(self, bar, attr, value, old_value=None):
                        if bar not in ("frame_index", "chunk"):
                            return
                        if self.main_bar is None:
                            self.main_bar = "frame_index" if bar == "frame_index" else "chunk"
                        elif self.main_bar == "chunk" and bar == "frame_index":
                            self.main_bar = "frame_index"
                            self.total = None
                            self.dialog.setRange(0, 0)
                        if bar != self.main_bar:
                            return

                        if attr == "total":
                            self.total = int(value) if value is not None else None
                            if self.total:
                                self.dialog.setRange(0, self.total)
                            else:
                                self.dialog.setRange(0, 0)
                        elif attr == "index":
                            if self.total:
                                self.dialog.setValue(min(int(value), self.total))
                            else:
                                self.dialog.setValue(int(value))
                        QApplication.processEvents()

                logger = ExportLogger(progress)

                for clip in sorted(video_track.clips, key=lambda c: c.start_frame):
                    if not clip.file_path:
                        continue
                    v = VideoFileClip(clip.file_path)
                    opened.append(v)
                    if base_size is None:
                        base_size = v.size
                    in_frame = int(getattr(clip, "source_in", 0))
                    start_t = clip.start_frame / fps
                    duration_t = clip.duration / fps
                    start_sec = in_frame / fps
                    end_sec = start_sec + duration_t
                    if hasattr(v, "subclip"):
                        v = v.subclip(start_sec, end_sec)
                    else:
                        v = v.subclipped(start_sec, end_sec)
                    if base_size and v.size != base_size:
                        if hasattr(v, "resize"):
                            v = v.resize(newsize=base_size)
                        else:
                            v = v.resized(new_size=base_size)
                    if hasattr(v, "set_start"):
                        v = v.set_start(start_t)
                    else:
                        v = v.with_start(start_t)
                    layers.append(v)

                if base_size is None:
                    base_size = (1280, 720)

                background = ColorClip(size=base_size, color=(0, 0, 0), duration=total_duration)
                layers.insert(0, background)

                if text_track:
                    for clip in text_track.clips:
                        if not clip.text_content:
                            continue
                        start_t = clip.start_frame / fps
                        duration_t = clip.duration / fps

                        preview_size = (self.video_label.width(), self.video_label.height())
                        if preview_size[0] <= 0 or preview_size[1] <= 0:
                            preview_size = getattr(clip, "preview_size", base_size)
                        overlay = self._creer_overlay_texte(clip, base_size, preview_size)
                        text_clip = ImageClip(overlay)
                        if hasattr(text_clip, "set_start"):
                            text_clip = text_clip.set_start(start_t)
                        else:
                            text_clip = text_clip.with_start(start_t)
                        if hasattr(text_clip, "set_duration"):
                            text_clip = text_clip.set_duration(duration_t)
                        else:
                            text_clip = text_clip.with_duration(duration_t)
                        if hasattr(text_clip, "set_position"):
                            text_clip = text_clip.set_position((0, 0))
                        else:
                            text_clip = text_clip.with_position((0, 0))
                        layers.append(text_clip)

                final = CompositeVideoClip(layers, size=base_size)
                if hasattr(final, "set_duration"):
                    final = final.set_duration(total_duration)
                else:
                    final = final.with_duration(total_duration)
                return final.write_videofile(export_name + config.CODEC, fps=fps, logger=logger)
            finally:
                try:
                    progress.close()
                except Exception:
                    pass
                for v in opened:
                    try:
                        v.close()
                    except Exception:
                        pass

    def _get_export_font(self, fontsize, ImageFont):
        if self.export_font_path and os.path.exists(self.export_font_path):
            try:
                return ImageFont.truetype(self.export_font_path, fontsize)
            except Exception:
                pass

        candidates = [
            "/usr/share/fonts/google-noto-vf/NotoSansMono[wght].ttf",
            "/usr/share/fonts/google-noto-vf/NotoSansDevanagari[wght].ttf",
            "/usr/share/fonts/google-noto-vf/NotoSansArabic[wght].ttf",
            "/usr/share/fonts/google-noto-vf/NotoSansHebrew[wght].ttf",
            "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",
            "/usr/share/fonts/abattis-cantarell-fonts/Cantarell-Regular.ttf",
            "/usr/share/fonts/urw-base35/NimbusSans-Regular.ttf",
            "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, fontsize)
                    self.export_font_path = path
                    return font
                except Exception:
                    continue

        for path in glob.glob("/usr/share/fonts/**/*.ttf", recursive=True):
            try:
                font = ImageFont.truetype(path, fontsize)
                self.export_font_path = path
                return font
            except Exception:
                continue

        return ImageFont.load_default()

    def _creer_overlay_texte(self, clip, base_size, preview_size=None):
        width, height = base_size
        if preview_size is None:
            preview_size = base_size
        preview_w, preview_h = preview_size
        if preview_w <= 0 or preview_h <= 0:
            preview_w, preview_h = base_size
        overlay = np.zeros((height, width, 4), dtype=np.uint8)

        font_scale = float(clip.size) if clip.size else 1.0
        scale = height / preview_h if preview_h else 1.0
        font_scale *= scale
        thickness = max(1, int(round(self.text_thickness * scale)))
        color = clip.text_color if clip.text_color else (255, 255, 255)
        (tw, th), _ = cv2.getTextSize(
            clip.text_content,
            self.text_font,
            font_scale,
            thickness
        )

        pos_x, pos_y = clip.position if clip.position else (0.5, 0.5)
        px = int(pos_x * width)
        py = int(pos_y * height)

        if clip.align == "left":
            x = px
        elif clip.align == "right":
            x = px - tw
        else:
            x = px - (tw // 2)

        y = py + (th // 2)
        x = max(0, min(x, width - tw))
        y = max(th, min(y, height - 2))

        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.putText(
            mask,
            clip.text_content,
            (x, y),
            self.text_font,
            font_scale,
            255,
            thickness
        )

        b, g, r = int(color[0]), int(color[1]), int(color[2])
        idx = mask > 0
        overlay[idx, 0] = b
        overlay[idx, 1] = g
        overlay[idx, 2] = r
        overlay[idx, 3] = mask[idx]
        return overlay

    def sauvegarder(self):
        project_data = self._creer_donnees_projet()
        sauver_projet(project_data=project_data)
        return

    def load(self):
        data = load_project_data()
        if not data:
            return
        self._charger_projet(data)
        return

    def load_from_path(self, path):
        data = load_project_data_from_path(path)
        if not data:
            return
        self._charger_projet(data)
        return

    def _charger_projet(self, data):
        self.timeline.vider_tous_les_clips()
        config.clips = {}
        self.media_playlist = []
        self.media_offsets = []
        self.current_media_index = -1
        self.cap = None
        self.timeline_fps = None
        self.current_media_in = None
        self.current_media_out = None

        # toolbox
        paths = data.get("toolbox", {}).get("paths", [])
        if hasattr(self.toolbox, "tree"):
            self.toolbox.tree.clear()
        config.media_library_paths = {}
        for path in paths:
            if hasattr(self.toolbox, "tree"):
                self.toolbox.tree.ajouter_media(path)

        # timeline
        timeline_data = data.get("timeline", {})
        fps = timeline_data.get("fps", 30)
        self.timeline_fps = fps
        self.timeline.regler_fps(fps)
        zoom = timeline_data.get("zoom")
        if zoom:
            self.timeline.regler_zoom(zoom)

        for v in timeline_data.get("video_clips", []):
            path = v.get("path")
            start = int(v.get("start_frame", 0))
            end = int(v.get("end_frame", start))
            duration = max(1, end - start)
            if path:
                clip = self.timeline.ajouter_clip_video(path, start, duration)
                if clip:
                    clip.source_in = int(v.get("source_in", 0))

        for t in timeline_data.get("text_clips", []):
            content = t.get("content", "")
            start = int(t.get("start_frame", 0))
            end = int(t.get("end_frame", start))
            duration = max(1, end - start)
            color = t.get("color", [255, 255, 255])
            size = t.get("size", 1.0)
            position = t.get("position", [0.5, 0.5])
            align = t.get("align", "center")
            if content:
                self.timeline.ajouter_clip_texte(
                    text_content=content,
                    start_frame=start,
                    duration_frames=duration,
                    text_color=tuple(color),
                    text_size=float(size),
                    position=tuple(position),
                    align=align,
                )

        self._maj_playlist()
        current_frame = int(timeline_data.get("current_frame", 0))
        if config.total_frames and config.total_frames > 0:
            current_frame = min(current_frame, config.total_frames - 1)
            self.seek_video(current_frame)
        else:
            self.timeline.regler_frame(current_frame)

    def _creer_donnees_projet(self):
        video_clips = []
        text_clips = []
        if self.timeline.tracks:
            video_track = self.timeline.tracks[0]
            text_track = self.timeline.tracks[1] if len(self.timeline.tracks) > 1 else None
            for clip in video_track.clips:
                video_clips.append({
                    "path": clip.file_path,
                    "start_frame": clip.start_frame,
                    "end_frame": clip.end_frame,
                    "source_in": int(getattr(clip, "source_in", 0)),
                })
            if text_track:
                for clip in text_track.clips:
                    text_clips.append({
                        "content": clip.text_content,
                        "start_frame": clip.start_frame,
                        "end_frame": clip.end_frame,
                        "color": list(clip.text_color) if clip.text_color else [255, 255, 255],
                        "size": clip.size,
                        "position": list(clip.position) if clip.position else [0.5, 0.5],
                        "align": clip.align if clip.align else "center",
                    })

        return {
            "project_version": 1,
            "settings": {
                "codec": config.CODEC,
                "default_duration": config.DEFAULT_DURATION,
                "default_font_size": config.FONT_SIZE,
            },
            "toolbox": {
                "paths": list(config.media_library_paths.values()),
            },
            "timeline": {
                "fps": self.timeline_fps or self.timeline.fps,
                "zoom": self.timeline.zoom,
                "current_frame": self.timeline.playhead.current_frame,
                "video_clips": video_clips,
                "text_clips": text_clips,
            }
        }

    def _dessiner_textes(self, frame, current_frame):
        if not self.timeline.tracks or len(self.timeline.tracks) < 2:
            return
        text_track = self.timeline.tracks[1]
        if not text_track.clips:
            return

        frame_h, frame_w = frame.shape[:2]
        for clip in text_track.clips:
            if clip.start_frame <= current_frame < clip.end_frame and clip.text_content:
                font_scale = float(clip.size) if clip.size else 1.0
                color = clip.text_color if clip.text_color else (255, 255, 255)
                (tw, th), _ = cv2.getTextSize(clip.text_content, self.text_font, font_scale, self.text_thickness)

                pos_x, pos_y = clip.position if clip.position else (0.5, 0.5)
                px = int(pos_x * frame_w)
                py = int(pos_y * frame_h)

                if clip.align == "left":
                    x = px
                elif clip.align == "right":
                    x = px - tw
                else:
                    x = px - (tw // 2)

                y = py + (th // 2)
                x = max(0, min(x, frame_w - tw))
                y = max(th, min(y, frame_h - 2))

                cv2.putText(frame, clip.text_content, (x, y), self.text_font, font_scale, color, self.text_thickness)

    def _maj_position_texte(self, pos):
        if not self.selected_text_clip:
            return
        w = self.video_label.width()
        h = self.video_label.height()
        if w <= 0 or h <= 0:
            return
        nx = max(0.0, min(1.0, pos.x() / w))
        ny = max(0.0, min(1.0, pos.y() / h))
        self.selected_text_clip.position = (nx, ny)
        self.display_frame(force=True)

    def eventFilter(self, obj, event):
        if obj == self.video_label and getattr(self, "selected_text_clip", None):
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.dragging_text = True
                self._maj_position_texte(event.pos())
                return True
            if event.type() == QEvent.MouseMove and getattr(self, "dragging_text", False) and (event.buttons() & Qt.LeftButton):
                self._maj_position_texte(event.pos())
                return True
            if event.type() == QEvent.MouseButtonRelease and getattr(self, "dragging_text", False):
                self.dragging_text = False
                return True
        return super().eventFilter(obj, event)

    def quitter(self):
        self.close()

    def closeEvent(self, event):
        self._cleanup_resources()
        event.accept()

    def _cleanup_resources(self):
        try:
            self.is_playing = False
            if self.timer.isActive():
                self.timer.stop()
        except Exception:
            pass
        try:
            if self.cap:
                self.cap.release()
        except Exception:
            pass
        try:
            if self.audio_player:
                self.audio_player.stop()
        except Exception:
            pass
        self.cap = None

    def showtoolbox(self):
        self.toolbox.show()
        self.toolbox.raise_()
        print('ToolBox ok')

    def dragEnterEvent(self, event):
        print("MAIN drag ok")

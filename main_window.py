# ============================================
# UIS - MAIN WINDOW (avec OpenCV)
# ============================================

from PyQt5.QtWidgets import (QLineEdit, QWidget, QPushButton, QLabel, 
                             QVBoxLayout, QHBoxLayout, QMainWindow, QSlider,
                             QGridLayout)
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QIcon, QImage, QPixmap
import cv2
import numpy as np

from utils import import_video, save_as_path
from dialogs import txt_contentWindow, txt_videotitle
from save_manager import save_, load_save_data, update_datas
from timeline import Timeline
import config

from toolbox import ToolboxDock

import sys
import json
import os
from pathlib import Path





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
        self.toolbox.set_controller(self)

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
        fichier.addAction("Importer media", self.add_media_toGlobal)
        fichier.addAction("Exporter media", self.exporter_media)
        fichier.addAction("Quitter", self.quitter)

        edition = menubar.addMenu("Edition")
        edition.setStyleSheet("background-color: white; color: black;")
        edition.addAction("Annuler")
        edition.addAction("Retablir")
        edition.addAction("Couper")
        edition.addAction("Supprimer")
        edition.addAction("Dupliquer")

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
        self.toolbox.btn_remove_text.setStyleSheet('background-color: grey;')

        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)
        self.toolbox.btn_add_text.clicked.connect(self.add_text_dialog)
        self.toolbox.btn_remove_text.clicked.connect(self.remove_text)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMaximumWidth(100)

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

        self.timer = QTimer()
        self.timer.timeout.connect(self.display_frame)

        self.media_playlist = []
        self.media_offsets = []
        self.current_media_index = -1

    def _sync_playlist_from_timeline(self):
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
            config.clips[str(idx)] = {
                "path": clip.file_path,
                "fps": fps,
                "frames": frames,
            }
            idx += 1
        self._rebuild_media_playlist()

    def on_timeline_clips_changed(self):
        current_frame = self.timeline.playhead.current_frame
        self.is_playing = False
        self.timer.stop()
        self._sync_playlist_from_timeline()
        self.cap = None
        self.current_media_index = -1
        if config.total_frames and config.total_frames > 0:
            current_frame = min(current_frame, config.total_frames - 1)
            self.seek_video(current_frame)

    def _rebuild_media_playlist(self):
        self.media_playlist = list(config.clips.values())
        self.media_offsets = []
        total = 0
        for clip_info in self.media_playlist:
            self.media_offsets.append(total)
            total += int(clip_info.get("frames") or 0)
        config.total_frames = total
        self.timeline.set_total_frames(total)

    def _open_media_index(self, index):
        if index < 0 or index >= len(self.media_playlist):
            return False

        clip_info = self.media_playlist[index]
        path = clip_info.get("path")
        if not path:
            return False

        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(path)
        if not self.cap or not self.cap.isOpened():
            print(f"Impossible d'ouvrir la video: {path}")
            return False

        self.current_media_index = index
        fps = clip_info.get("fps") or self.cap.get(cv2.CAP_PROP_FPS)
        self.fps = fps if fps and fps > 0 else 30
        self.frame_interval = int(1000 / self.fps) if self.fps > 0 else 33

        if self.timeline_fps is None:
            self.timeline_fps = self.fps
            self.timeline.set_fps(self.timeline_fps)
        elif abs(self.timeline_fps - self.fps) > 0.01:
            print("Avertissement: FPS differents entre les clips (lecture supposee identique).")

        return True

    def _find_media_for_frame(self, frame_number):
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

    def _add_media_path(self, path, start_frame=None):
        if not path:
            return

        fps, frames = self._probe_media_info(path)
        if not fps or not frames:
            print(f"Impossible de lire les metadonnees video: {path}")
            return

        if self.timeline_fps is None:
            self.timeline_fps = fps if fps and fps > 0 else 30
            self.timeline.set_fps(self.timeline_fps)
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
            }

            self._rebuild_media_playlist()
            index = len(self.media_playlist) - 1
            start_frame = self.media_offsets[index]

            self.timeline.add_video_clip(str(path), start_frame, frames)
            self.timeline.set_current_frame(start_frame)

            if self.cap is None:
                self._open_media_index(0)
                if self.cap:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        else:
            self.timeline.add_video_clip(str(path), start_frame, frames)
            self.timeline.set_current_frame(start_frame)
            self.on_timeline_clips_changed()

        print(f"Video imported: {path}")
        print(f"FPS: {self.fps}, Total frames: {config.total_frames}")

    def _probe_media_info(self, path):
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
        self._add_media_path(path)

    def on_media_dropped(self, path):
        self.is_playing = False
        self.timer.stop()
        start_frame = 0
        if self.timeline.tracks:
            video_track = self.timeline.tracks[0]
            if video_track.clips:
                start_frame = max(c.end_frame for c in video_track.clips)
        self._add_media_path(path, start_frame=start_frame)

    def add_media_toGlobal(self):
        config.file_path, config.nom_fichier = import_video()
        if config.file_path:
            if hasattr(self.toolbox, "tree"):
                self.toolbox.tree.ajouter_medias(config.file_path)
            else:
                print("Toolbox indisponible, impossible d'ajouter le media a la bibliotheque.")

    def display_frame(self, force=False):
        global text
        if self.cap is None or (not self.is_playing and not force):
            return

        ret, frame = self.cap.read()
        if not ret:
            if self._open_media_index(self.current_media_index + 1):
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

        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        if 0 <= self.current_media_index < len(self.media_offsets):
            current_frame += self.media_offsets[self.current_media_index]
        self._render_text_clips(frame, current_frame)
        self.timeline.set_current_frame(current_frame)

    def play(self):
        if self.cap is None:
            if self.media_playlist:
                if not self._open_media_index(0):
                    print("Veuillez importer une video d'abord")
                    return
            else:
                print("Veuillez importer une video d'abord")
                return
        self.is_playing = True
        self.timer.start(self.frame_interval)
        print("Lecture en cours...")

    def pause(self):
        self.is_playing = False
        self.timer.stop()
        print("Pause...")

    def stop(self):
        self.is_playing = False
        self.timer.stop()
        if self.media_playlist:
            self._open_media_index(0)
            if self.cap:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.timeline.set_current_frame(0)
        elif self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.timeline.set_current_frame(0)
        print("Arret...")

    def seek_video(self, frame_number):
        if not self.media_playlist:
            if self.cap:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                self.display_frame(force=True)
            return

        index, local_frame = self._find_media_for_frame(frame_number)
        if index is None:
            return
        if index != self.current_media_index:
            if not self._open_media_index(index):
                return
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, local_frame)
            self.display_frame(force=True)

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

            clip = self.timeline.add_text_clip(
                text_content=dialog.text_value,
                start_frame=current_frame,
                duration_frames=text_duration,
                text_color=self.text_color,
                text_size=self.text_size,
                position=(0.5, 0.5),
                align="center",
            )
            self.selected_text_clip = clip

            print(f"Texte ajoute: {dialog.text_value}")

    def on_clip_selected(self, clip):
        print(f"Clip selectionne : {clip}")
        if clip.clip_type == "text":
            print(f"Contenu texte : {clip.text_content}")
            self.selected_text_clip = clip
        else:
            self.selected_text_clip = None

    def remove_text(self):
        if self.selected_text_clip and self.timeline.tracks:
            self.timeline.tracks[1].remove_clip(self.selected_text_clip)
            self.selected_text_clip = None
            self.display_frame(force=True)
            print("Texte supprime")
        else:
            print("Aucun texte selectionne")

    def askMediaOutput(self):
        dialog = txt_videotitle()
        if dialog.exec_():
            return dialog.text_value
        return None

    def exporter_media(self):
        if not config.clips:
            print("No video loaded. Please import a video first.")
            return
        export_name = self.askMediaOutput()
        if export_name:
            from moviepy import VideoFileClip, concatenate_videoclips
            clips = []
            final = None
            try:
                for clip_info in config.clips.values():
                    path = clip_info.get("path")
                    if path:
                        clips.append(VideoFileClip(path))
                if not clips:
                    print("Aucun clip valide a exporter.")
                    return
                final = concatenate_videoclips(clips, method="compose")
                return final.write_videofile(export_name + config.CODEC)
            finally:
                for c in clips:
                    c.close()
                if final is not None:
                    final.close()

    def sauvegarder(self):
        save = save_(config.media, config.video, config.file_path, config.text, config.bloc_media, config.index)
        return

    def load(self):
        update = update_datas()
        if update and config.file_path:
            self.timeline.clear_all_clips()
            config.clips = {}
            self.media_playlist = []
            self.media_offsets = []
            self.current_media_index = -1
            self.cap = None
            self.timeline_fps = None

            self._add_media_path(config.file_path)

        return

    def _render_text_clips(self, frame, current_frame):
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

    def _update_selected_text_position(self, pos):
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
                self._update_selected_text_position(event.pos())
                return True
            if event.type() == QEvent.MouseMove and getattr(self, "dragging_text", False) and (event.buttons() & Qt.LeftButton):
                self._update_selected_text_position(event.pos())
                return True
            if event.type() == QEvent.MouseButtonRelease and getattr(self, "dragging_text", False):
                self.dragging_text = False
                return True
        return super().eventFilter(obj, event)

    def quitter(self):
        return

    def showtoolbox(self):
        self.toolbox.show()
        self.toolbox.raise_()
        print('ToolBox ok')

    def dragEnterEvent(self, event):
        print("MAIN drag ok")

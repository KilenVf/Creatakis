# ============================================
# UIS - MAIN WINDOW (avec OpenCV)
# ============================================

from PyQt5.QtWidgets import (QLineEdit, QWidget, QPushButton, QLabel, 
                             QVBoxLayout, QHBoxLayout, QMainWindow, QSlider,
                             QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap
import cv2
import numpy as np

from utils import import_video, save_as_path
from dialogs import txt_contentWindow, txt_videotitle
from config import CODEC, media, video, file_path, text, save_file_path, bloc_media, index
from save_manager import save_, load_save_data, update_datas
from timeline import Timeline

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
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 360)
        self.video_label.setStyleSheet("background-color: black;")

        self.btn_play = QPushButton('▶️')
        self.btn_pause = QPushButton('⏸️')
        self.btn_stop = QPushButton('⏹️')
        self.btn_add_text = QPushButton('Ajouter texte')
        self.btn_remove_text = QPushButton('Supprimer texte')

        self.btn_play.setStyleSheet('background-color: grey;')
        self.btn_pause.setStyleSheet('background-color: grey;')
        self.btn_stop.setStyleSheet('background-color: grey;')
        self.btn_add_text.setStyleSheet('background-color: grey;')
        self.btn_remove_text.setStyleSheet('background-color: grey;')

        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_add_text.clicked.connect(self.add_text_dialog)
        self.btn_remove_text.clicked.connect(self.remove_text)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMaximumWidth(100)

        self.timeline = Timeline(self)
        self.timeline.positionChanged.connect(self.seek_video)
        self.timeline.clipSelected.connect(self.on_clip_selected)

        # TOOLBOX
        self.toolbox = ToolboxDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.toolbox)
        self.toolbox.gotoFrame.connect(self.seek_video)
        self.toolbox.set_controller(self)

            


        # LAYOUT
        videoTimeline_layout = QVBoxLayout()
        videoTimeline_layout.addWidget(self.timeline)

        VideoControl_layout = QHBoxLayout()
        VideoControl_layout.addWidget(self.btn_play)
        VideoControl_layout.addWidget(self.btn_pause)
        VideoControl_layout.addWidget(self.btn_stop)
        VideoControl_layout.addWidget(self.btn_add_text)
        VideoControl_layout.addWidget(self.btn_remove_text)
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
        self.is_playing = False
        self.text_to_display = None
        self.text_color = (255, 255, 255)
        self.text_font = cv2.FONT_HERSHEY_SIMPLEX
        self.text_size = 1
        self.text_thickness = 2

        self.timer = QTimer()
        self.timer.timeout.connect(self.display_frame)

    def importer_media(self):
        from media_editor import create_clip
        global video, file_path
        file_path = import_video()
        if file_path:
            video = create_clip(file_path, text)

            self.cap = cv2.VideoCapture(file_path)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.frame_interval = int(1000 / self.fps) if self.fps > 0 else 33

            self.timeline.set_fps(self.fps)
            self.timeline.set_total_frames(self.total_frames)
            self.timeline.set_current_frame(0)
            self.timeline.add_video_clip(file_path, 0, self.total_frames)

            print(f"Video imported: {file_path}")
            print(f"FPS: {self.fps}, Total frames: {self.total_frames}")

    def display_frame(self, force=False):
        global text
        if self.cap is None or (not self.is_playing and not force):
            return

        ret, frame = self.cap.read()
        if not ret:
            self.stop()
            return

        label_width = self.video_label.width()
        label_height = self.video_label.height()
        frame = cv2.resize(frame, (label_width, label_height))

        if self.text_to_display is not None:
            text_size = cv2.getTextSize(self.text_to_display, self.text_font,
                                        self.text_size, self.text_thickness)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            text_y = (frame.shape[0] + text_size[1]) // 2
            frame = cv2.putText(frame, self.text_to_display, (text_x, text_y),
                                self.text_font, self.text_size, self.text_color,
                                self.text_thickness)
            text = self.text_to_display

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
        self.timeline.set_current_frame(current_frame)

    def play(self):
        if self.cap is None:
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
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.timeline.set_current_frame(0)
        print("Arret...")

    def seek_video(self, frame_number):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.display_frame(force=True)

    def add_text_dialog(self):
        if self.cap is None:
            print("Veuillez importer une video d'abord")
            return

        dialog = txt_contentWindow()
        if dialog.exec_():
            self.text_to_display = dialog.text_value
            self.text_color = dialog.text_color
            self.text_size = int(dialog.text_size)

            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            text_duration = 150

            self.timeline.add_text_clip(
                text_content=self.text_to_display,
                start_frame=current_frame,
                duration_frames=text_duration
            )

            print(f"Texte ajoute: {self.text_to_display}")

    def on_clip_selected(self, clip):
        print(f"Clip selectionne : {clip}")
        if clip.clip_type == "text":
            print(f"Contenu texte : {clip.text_content}")

    def remove_text(self):
        self.text_to_display = None
        print("Texte supprime")

    def askMediaOutput(self):
        dialog = txt_videotitle()
        if dialog.exec_():
            return dialog.text_value
        return None

    def exporter_media(self):
        if video is None:
            print("No video loaded. Please import a video first.")
            return
        export_name = self.askMediaOutput()
        if export_name:
            return video.write_videofile(export_name + CODEC)

    def sauvegarder(self):
        save = save_(media, video, file_path, text, bloc_media, index)
        return

    def load(self):
        update = update_datas()
        return

    def quitter(self):
        return

    def showtoolbox(self):
        self.toolbox.show()
        self.toolbox.raise_()
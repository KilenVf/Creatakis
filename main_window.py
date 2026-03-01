# ============================================
# UIS - MAIN WINDOW (avec OpenCV)
# ============================================

from PyQt6.QtWidgets import (QLineEdit, QWidget, QPushButton, QLabel, 
                             QVBoxLayout, QHBoxLayout, QMainWindow, QSlider,
                             QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QImage, QPixmap
import cv2
import numpy as np

from utils import import_video, save_as_path
from dialogs import txt_contentWindow, txt_videotitle
from config import CODEC, media, video, file_path, text, save_file_path
from save_manager import save_, load_save_data, update_datas
from timeline import bloc_media, index

import sys
import importlib
from timeline import Timeline

import json
import os
from pathlib import Path 


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Creatakis")
        self.setWindowIcon(QIcon("assets/logo.png"))
        self.setMinimumSize(1280, 720)
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
        fichier.addAction("Importer média", self.importer_media)
        fichier.addAction("Exporter média", self.exporter_media)
        fichier.addAction("Quitter", self.quitter)

        edition = menubar.addMenu("Edition")
        edition.addAction("Annuler")
        edition.addAction("Rétablir")
        edition.addAction("Couper")
        edition.addAction("Supprimer")
        edition.addAction("Dupliquer")

        affichage = menubar.addMenu("Affichage")
        affichage.addAction("Plein écran", self.showFullScreen)
        affichage.addAction("Quitter plein écran", self.showNormal)

        # ===== CENTRAL WIDGET =====
        central = QWidget(self)
        self.setCentralWidget(central)


        # ===== VIDEO PLAYER OpenCV =====
        self.video_label = QLabel()
        self.video_label.setMinimumSize(400,300)
        self.video_label.setMaximumSize(400,300)
        self.video_label.setStyleSheet("background-color: black;")

        self.btn_play = QPushButton('Play')
        self.btn_pause = QPushButton('Pause')
        self.btn_stop = QPushButton('Stop')
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

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMaximumWidth(100)

        self.timeline = Timeline()
        self.timeline.positionChanged.connect(self.seek_video)

        videoTimeline_layout =QVBoxLayout()
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

        video_container = QVBoxLayout()
        video_container.addWidget(self.video_label, 0, Qt.AlignmentFlag.AlignCenter)
        video_container.addLayout(VideoControl_layout)

        VideoMain_layout = QGridLayout()
        VideoMain_layout.addLayout(videoTimeline_layout, 3,0, 2, 3)
        VideoMain_layout.addLayout(video_container, 0, 2)
        VideoMain_layout.setColumnStretch(0, 1)
        VideoMain_layout.setColumnStretch(1, 1)
        VideoMain_layout.setRowStretch(4, 1) 

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
            video = create_clip(file_path,text)
            
            self.cap = cv2.VideoCapture(file_path)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.frame_interval = int(1000 / self.fps) if self.fps > 0 else 33

            self.timeline.set_total_frames(self.total_frames)
            self.timeline.set_current_frame(0)

            
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

        frame = cv2.resize(frame, (400, 300))

        if self.text_to_display is not None:
            global text
            text_size = cv2.getTextSize(self.text_to_display, self.text_font, 
                                       self.text_size, self.text_thickness)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            text_y = (frame.shape[0] + text_size[1]) // 2
            frame = cv2.putText(frame, self.text_to_display, (text_x, text_y), 
                       self.text_font, self.text_size, self.text_color, 
                       self.text_thickness)
            text = self.text_to_display

        # Convertir BGR en RGB pour PyQt
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Afficher l'image
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap)

        # Mettre à jour le slider de position
        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.timeline.set_current_frame(current_frame)


    def play(self):
        if self.cap is None:
            print("Veuillez importer une vidéo d'abord")
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
        print("Arrêt...")

    def seek_video(self, frame_number):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.display_frame(force=True)

    def add_text_dialog(self):
        """Ajouter du texte via dialog"""
        if self.cap is None:
            print("Veuillez importer une vidéo d'abord")
            return
        
        dialog = txt_contentWindow()
        if dialog.exec_():
            self.text_to_display = dialog.text_value
            self.text_color = dialog.text_color
            self.text_size = int(dialog.text_size)
            print(f"Texte ajouté: {self.text_to_display}")
            

    def remove_text(self):
        """Supprimer le texte"""
        self.text_to_display = None
        print("Texte supprimé")

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


      

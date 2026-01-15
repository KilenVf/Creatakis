# =========================
# IMPORTS LIBS
# =========================
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QMenuBar, QMainWindow, QSlider
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap
import cv2
import numpy as np


# =========================
# IMPORT VAR/FONCTIONS
# =========================
from utils.file_dialog import import_video
from config import CODEC
from Medias.editor import create_clip


# =========================
#  DEF VARIABLES
# =========================
media = ''
video = None
file_path = None


# =========================
# MAIN WINDOW
# =========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Creatakis")
        self.setWindowIcon(QIcon("assets/logo.png"))
        self.setMinimumSize(1280, 720)

        # ===== MENU =====
        menubar = self.menuBar()

        fichier = menubar.addMenu("Fichier")
        fichier.addAction("Nouveau" )
        fichier.addAction("Ouvrir")
        fichier.addAction("Enregistrer" )
        fichier.addAction("Enregistrer sous" )
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

        # ===== VIDEO PLAYER STRUCTURE =====
        self.video_back = QLabel()
        self.video_back.setMinimumSize(800,600)
        self.video_back.setStyleSheet('background-color: black;')
        self.video_back.setAlignment(Qt.AlignCenter)

        self.btn_play = QPushButton('Play')
        self.btn_pause = QPushButton('Pause')
        self.btn_stop = QPushButton('Stop')
        self.btn_add_text = QPushButton('Ajouter un texte')
        self.btn_remove_text = QPushButton('Supprimer un texte')

        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_add_text.clicked.connect(self.add_text)
        self.btn_remove_text.clicked.connect(self.remove_text)
        

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0,100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.player.setVolume)

        # === video position slider ===
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0,100)
        self.position_slider.sliderMoved.connect(self.seek_video)

        
        # ==== positioning ====
        VideoControl_layout = QHBoxLayout()
        VideoControl_layout.addWidget(self.btn_play)
        VideoControl_layout.addWidget(self.btn_pause)
        VideoControl_layout.addWidget(self.btn_stop)
        VideoControl_layout.addWidget(self.btn_add_text)
        VideoControl_layout.addWidget(self.btn_remove_text)
        VideoControl_layout.addWidget(QLabel("Volume:"))
        VideoControl_layout.addWidget(self.volume_slider)


        VideoMain_layout = QVBoxLayout()
        VideoMain_layout.addWidget(self.video_back)
        VideoMain_layout.addWidget(self.position_slider)
        VideoMain_layout.addLayout(VideoControl_layout)

        central.setLayout(VideoMain_layout)

        # ===== Opencv variables =====
        self.cap = None
        self.is_playing = False
        self.text_to_display = None
        self.text_color = (255,255,255)
        self.txt_font = cv2.FONT_HERSHEY_COMPLEX
        self.text_size = 1
        self.text_thickness = 2

        # === timer update vidéo ===
        self.timer = QTimer
        self.timer.timeout.connect(self.display_frame)

        

        # FONCTIONS

    def importer_media(self):
        global video, file_path
        file_path = import_video()
        if file_path:
            video = create_clip(file_path)

            self.cap = cv2.VideoCapture(file_path)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frame = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.frame_interval = int(1000 / self.fps) if self.fps > 0 else 33
    

        return

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

    def quitter(self): 
            return



class txt_contentWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Text completion")
        self.setFixedSize(400,150)

        label = QLabel("Entre le texte à afficher")
        label.setAlignment(Qt.AlignCenter)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Ton texte ici ...")

        btn_ok = QPushButton("Valider")
        btn_ok.clicked.connect(self.valider)

        layout =QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addWidget(btn_ok)

        self.setLayout(layout)
        self.text_value =""

    def valider(self):
        self.text_value = self.line_edit.text()
        self.accept()

class txt_videotitle(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Title Completion")
        self.setFixedSize(400,150)

        label = QLabel("Entre le titre de ta vidéo")
        label.setAlignment(Qt.AlignCenter)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Ton titre ici ...")

        btn_ok = QPushButton("Valider")
        btn_ok.clicked.connect(self.valider)

        layout =QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addWidget(btn_ok)

        self.setLayout(layout)
        self.text_value =""

    def valider(self):
        self.text_value = self.line_edit.text()
        self.accept()
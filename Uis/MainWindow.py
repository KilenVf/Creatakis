from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QMenuBar, QMainWindow, QSlider
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap
from utils.file_dialog import import_video
from config import CODEC
from moviepy import *
from Medias.editor import create_clip
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget
media = ''
video = None
file_path = None

""" fenetres"""

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

        # ===== VIDEO PLAYER =====
        self.player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        

        self.btn_play = QPushButton('Play')
        self.btn_pause = QPushButton('Pause')
        self.btn_stop = QPushButton('Stop')

        self.btn_play.clicked.connect(self.player.play)
        self.btn_pause.clicked.connect(self.player.pause)
        self.btn_stop.clicked.connect(self.player.stop)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0,100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.player.setVolume)

        VideoControl_layout = QHBoxLayout()
        VideoControl_layout.addWidget(self.btn_play)
        VideoControl_layout.addWidget(self.btn_pause)
        VideoControl_layout.addWidget(self.btn_stop)
        VideoControl_layout.addWidget(self.volume_slider)

        VideoMain_layout = QVBoxLayout()
        VideoMain_layout.addWidget(self.video_widget)
        VideoMain_layout.addLayout(VideoControl_layout)

        central.setLayout(VideoMain_layout)
        

        # FONCTIONS

    def importer_media(self):
        global video, file_path
        file_path = import_video()
        if file_path:
            video = create_clip(file_path)
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            print(f"Video imported: {file_path}")
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



        

class ask_txt(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Confirmation")
        self.setFixedSize(300, 120)

        label = QLabel("Voulez-vous ajouter un texte ?")
        label.setAlignment(Qt.AlignCenter)

        btn_oui = QPushButton("Oui")
        btn_non = QPushButton("Non")

        btn_oui.clicked.connect(self.accept)
        btn_non.clicked.connect(self.reject)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_oui)
        hbox.addWidget(btn_non)

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

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
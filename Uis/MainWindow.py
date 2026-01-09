from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QMenuBar, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from utils.file_dialog import import_video
from config import CODEC
from moviepy import *
from Medias.editor import create_clip
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
import sys


"""fonctions"""
def Nouveau_projet():
    return

def Ouvrir_projet():
    return

def Enregistrer_projet():
    return

def Enregistrer_sous():
    return
media = ''
video = None
file_path = None

def importer_media():
    global video, file_path
    file_path = import_video()
    if file_path:
        video = create_clip(file_path)
        print(f"Video imported: {file_path}")
    return

def askMediaOutput():
    dialog = txt_videotitle()
    if dialog.exec_():
        return dialog.text_value
    return None

def exporter_media():
    if video is None:
        print("No video loaded. Please import a video first.")
        return
    export_name = askMediaOutput()
    if export_name:
        return video.write_videofile(export_name + CODEC)

def quitter():
    return


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
        fichier.addAction("Nouveau", Nouveau_projet)
        fichier.addAction("Ouvrir", Ouvrir_projet)
        fichier.addAction("Enregistrer", Enregistrer_projet)
        fichier.addAction("Enregistrer sous", Enregistrer_sous)
        fichier.addAction("Importer média", importer_media)
        fichier.addAction("Exporter média", exporter_media)
        fichier.addAction("Quitter", quitter)

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
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        # ===== VIDEO PLAYER =====
        self.player = QMediaPlayer(self)
        self.video_widget = QVideoWidget(self)

        self.player.setVideoOutput(self.video_widget)
        layout.addWidget(self.video_widget)


        

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
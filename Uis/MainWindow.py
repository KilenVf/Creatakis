from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QMenuBar, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from utils.file_dialog import import_video
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

def importer_media():
    media = import_video()
    return

def exporter_media():
    return

def quitter():
    return


""" fenetres"""
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Creatakis')
        self.setWindowIcon(QIcon('assets/logo.png'))
        self.setMinimumSize(1280,720)

        menubar = QMenuBar(self)
        menubar.setGeometry(0,0,1280,25)

        Fichier = menubar.addMenu('Fichier')
        Fichier.addAction('Nouveau', Nouveau_projet)
        Fichier.addAction('Ouvrir', Ouvrir_projet)
        Fichier.addAction('Enregistrer', Enregistrer_projet)
        Fichier.addAction('Enregistrer sous', Enregistrer_sous)
        Fichier.addAction('Importer média', importer_media)
        Fichier.addAction('Exporter média', exporter_media)
        Fichier.addAction('Quitter', quitter)

        Edition = menubar.addMenu('Edition')
        Edition.addAction('Annuler')
        Edition.addAction('Rétablir')
        Edition.addAction('Couper')
        Edition.addAction('Supprimer')
        Edition.addAction('Dupliquer')

        Affichage = menubar.addMenu('Affichage')
        Affichage.addAction('Plein Ecran')
        Affichage.addAction('Aperçu vidéo')

        

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
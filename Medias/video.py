from moviepy import *
from tkinter import Tk, filedialog
from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sys

""" fenêtres """

class FirstWindowImport(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Creatakis")
        self.setWindowIcon(QIcon("logo.png"))
        self.setGeometry(100,100,1280,720)

        btn_import = QPushButton("importer un média")

        hbox = QHBoxLayout()
        hbox.addWidget(btn_import)

        btn_import.clicked.connect(self.accept)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)

        self.setLayout(vbox)


class fenetre_OuiNon(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Confirmation")
        self.setFixedSize(300, 120)

        label = QLabel("Voulez-vous continuer")
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

""" fonctions """

def import_de_videos():
    root =Tk()
    root.withdraw()
    return filedialog.askopenfilename()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    FirstWindow = FirstWindowImport()
    if FirstWindow.exec_() == QDialog.Accepted:
        imported_video = import_de_videos()
    else :
        sys.exit()

    clip = VideoFileClip(imported_video).subclipped(0,5)

    dialog = fenetre_OuiNon()
    ask_txt =(dialog.exec_() == QDialog.Accepted)

    txt_content = ""

    if ask_txt:
        dialog_text = txt_contentWindow()
        if dialog_text.exec_() == QDialog.Accepted:
            txt_content = dialog_text.text_value
        else:
            txt_content = ''

    if txt_content:    
        txt_clip =  TextClip(
            text = txt_content,
            font_size = 100,
            color = 'white',
            size=(clip.w, 200)
        ).with_position("center").with_duration(5)

        video = CompositeVideoClip([clip, txt_clip])
    else:
        video = clip
    
    title = txt_videotitle()
    ask_title = (title.exec_()==QDialog.Accepted)

    export_name = ""

    if ask_title == True:
        export_name = title.text_value
    
    codec = ".mp4"



    
    #export_name = input("Comment veux tu appeler ta vidéo terminée ?") + ".mp4"
    video.write_videofile(export_name + codec)
from moviepy import *
from tkinter import Tk, filedialog
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
import sys


def import_de_vidéos():
    chemin_fichier = filedialog.askopenfilename()
    return chemin_fichier
imported_video = import_de_vidéos()

clip = VideoFileClip(imported_video).subclipped(0,5)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = fenetre_OuiNon()
    result = dialog.exec_()

    if result ==QDialog.Accepted:
        ask_txt = True
    else:
        ask_txt = False

    

def ask_content():
    if ask_txt == True:
        txt_content = input("Que veut tu afficher comme texte ?")
    else:
        txt_content = ""
    return txt_content

txt_content = ask_content()



txt_clip =  TextClip(
    text = txt_content,font_size = 100, color = 'white', size=(clip.w, 200)
)



txt_clip = txt_clip.with_position("center").with_duration(5)

video = CompositeVideoClip([clip, txt_clip])
export_name = input("Comment veux tu appeler ta vidéo terminée ?") + ".mp4"
video.write_videofile(export_name)
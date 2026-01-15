# ============================================
# CONFIG
# ============================================
CODEC = ".mp4"
DEFAULT_DURATION = 5
FONT_SIZE = 100


# ============================================
# UTILS - FILE DIALOG
# ============================================
from tkinter import Tk, filedialog

def import_video():
    root = Tk()
    root.withdraw()
    return filedialog.askopenfilename()


# ============================================
# MEDIAS - EDITOR
# ============================================
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def create_clip(video_path, text=None):
    clip = VideoFileClip(video_path).subclipped(0, DEFAULT_DURATION)

    if text:
        txt = (
            TextClip(
                text=text,
                font_size=FONT_SIZE,
                color="white",
                size=(clip.w, 200)
            )
            .with_position("center")
            .with_duration(DEFAULT_DURATION)
        )
        return CompositeVideoClip([clip, txt])

    return clip


def export_video(video, name):
    video.write_videofile(name + CODEC)


# ============================================
# UIS - MAIN WINDOW (avec OpenCV)
# ============================================
from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QMenuBar, QMainWindow, QSlider
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QIcon, QImage, QPixmap
import cv2
import numpy as np

media = ''
video = None
file_path = None

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

        # ===== VIDEO PLAYER avec OpenCV =====
        self.video_label = QLabel()
        self.video_label.setMinimumSize(800, 600)
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setAlignment(Qt.AlignCenter)

        self.btn_play = QPushButton('Play')
        self.btn_pause = QPushButton('Pause')
        self.btn_stop = QPushButton('Stop')
        self.btn_add_text = QPushButton('Ajouter texte')
        self.btn_remove_text = QPushButton('Supprimer texte')

        self.btn_play.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_add_text.clicked.connect(self.add_text_dialog)
        self.btn_remove_text.clicked.connect(self.remove_text)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMaximumWidth(100)

        # Slider pour la position de la vidéo
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 100)
        self.position_slider.sliderMoved.connect(self.seek_video)

        VideoControl_layout = QHBoxLayout()
        VideoControl_layout.addWidget(self.btn_play)
        VideoControl_layout.addWidget(self.btn_pause)
        VideoControl_layout.addWidget(self.btn_stop)
        VideoControl_layout.addWidget(self.btn_add_text)
        VideoControl_layout.addWidget(self.btn_remove_text)
        VideoControl_layout.addWidget(QLabel("Volume:"))
        VideoControl_layout.addWidget(self.volume_slider)

        VideoMain_layout = QVBoxLayout()
        VideoMain_layout.addWidget(self.video_label)
        VideoMain_layout.addWidget(self.position_slider)
        VideoMain_layout.addLayout(VideoControl_layout)

        central.setLayout(VideoMain_layout)

        # Variables OpenCV
        self.cap = None
        self.is_playing = False
        self.text_to_display = None
        self.text_color = (255, 255, 255)  # Blanc en BGR
        self.text_font = cv2.FONT_HERSHEY_SIMPLEX
        self.text_size = 1
        self.text_thickness = 2

        # Timer pour mettre à jour la vidéo
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_frame)

    def importer_media(self):
        global video, file_path
        file_path = import_video()
        if file_path:
            video = create_clip(file_path)
            
            # Ouvrir la vidéo avec OpenCV
            self.cap = cv2.VideoCapture(file_path)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.frame_interval = int(1000 / self.fps) if self.fps > 0 else 33
            
            self.position_slider.setRange(0, self.total_frames)
            
            print(f"Video imported: {file_path}")
            print(f"FPS: {self.fps}, Total frames: {self.total_frames}")

    def display_frame(self):
        if self.cap is None or not self.is_playing:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.stop()
            return

        # Redimensionner le frame pour l'affichage
        frame = cv2.resize(frame, (800, 600))

        # Ajouter le texte si présent
        if self.text_to_display:
            text_size = cv2.getTextSize(self.text_to_display, self.text_font, self.text_size, self.text_thickness)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            text_y = (frame.shape[0] + text_size[1]) // 2
            cv2.putText(frame, self.text_to_display, (text_x, text_y), 
                       self.text_font, self.text_size, self.text_color, self.text_thickness)

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
        self.position_slider.setValue(current_frame)

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
            self.position_slider.setValue(0)
        print("Arrêt...")

    def seek_video(self, frame_number):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.display_frame()

    def add_text_dialog(self):
        """Ajouter du texte via dialog"""
        if self.cap is None:
            print("Veuillez importer une vidéo d'abord")
            return
        
        dialog = txt_contentWindow()
        if dialog.exec_():
            self.text_to_display = dialog.text_value
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


# ============================================
# MAIN
# ============================================
def main():
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())
 
if __name__ == "__main__":
    import sys
    main()

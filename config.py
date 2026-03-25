

CODEC = ".mp4"
DEFAULT_DURATION = 5
FONT_SIZE = 100


data = None
json_text = None
nom_chemin = None



media= {}
video=None
file_path= None
media_library_paths = {}
text=None
save_file_path = None
nom_fichier = None
audio = None
current_index = None
current_path = None
clips = {}
total_frames = None

bloc_media = []
index = -1

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt

def focus_boutons(window):
    for bouton in window.findChildren(QPushButton):
        bouton.setFocusPolicy(Qt.NoFocus)

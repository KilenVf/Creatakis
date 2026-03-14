# ============================================
# CONFIG
# ============================================

CODEC = ".mp4"
DEFAULT_DURATION = 5
FONT_SIZE = 100

# SAVE_MANAGER
data = None
json_text = None
nom_chemin = None

# MAIN_WINDOW

media=''
video=None
file_path=None
text=None
save_file_path = None
nom_fichier = None
audio = None

# TIMELINE
bloc_media = []
index = -1

#focus des boutons une fois cliqué
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt

def focus_boutons(window):
    for bouton in window.findChildren(QPushButton):
        bouton.setFocusPolicy(Qt.NoFocus)

# ============================================
# UTILS - FILE DIALOG
# ============================================

from tkinter import Tk, filedialog
from tkinter.filedialog import asksaveasfilename, askopenfilename

save_file_path = None

def import_video():
    root = Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="Importer une vidéo",
                                      filetypes=[("Fichiers vidéo", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.webm"),
                                                   ("Tous les fichiers", "*.*")])

def save_as_path():
    save_file_path = asksaveasfilename(
        title="Enregistrer sous",
        defaultextension=".txt",
        filetypes=[("Fichier Json", "*.json")])
    return save_file_path

def load_save():
    loadedsave = askopenfilename(
        title="Ouvrir un fichier",
        defaultextension=".json",
        filetypes=[("Fichier Json", "*.json")])
    return loadedsave






 
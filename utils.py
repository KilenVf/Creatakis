
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
import os

save_file_path = None

def import_video():
    return QFileDialog.getOpenFileName(parent=None,
                                       caption='Ouvrir un Fichier',
                                       directory=os.path.expanduser("~"),
                                       filter=(
    "Tous les médias ("
    "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v *.mpeg *.mpg *.3gp *.ts *.mts *.m2ts *.vob *.ogv *.rm *.rmvb *.divx *.xvid "
    "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tiff *.tif *.svg *.ico *.heic *.heif *.raw *.cr2 *.nef *.arw *.dng *.psd *.xcf "
    "*.mp3 *.wav *.flac *.aac *.ogg *.wma *.m4a *.opus *.aiff *.alac *.ape *.mka *.mid *.midi"
    ");;"
    "Vidéos (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v *.mpeg *.mpg *.3gp *.ts *.mts *.m2ts *.vob *.ogv *.rm *.rmvb *.divx *.xvid);;"
    "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tiff *.tif *.svg *.ico *.heic *.heif *.raw *.cr2 *.nef *.arw *.dng *.psd *.xcf);;"
    "Audio (*.mp3 *.wav *.flac *.aac *.ogg *.wma *.m4a *.opus *.aiff *.alac *.ape *.mka *.mid *.midi);;"
    "Tous les fichiers (*)"
                                       ))

    

def save_as_path():
    save_file_path = QFileDialog.getSaveFileName(
            parent=None,
            caption="Enregistrer sous",
            directory=os.path.expanduser("~"),
            filter="Fichier JSON (*.json)"
        )
    return save_file_path

def load_save():
    load_save = QFileDialog.getOpenFileName(
        None,
        "Ouvrir un fichier",
        os.path.expanduser("~"),
        "Fichier JSON (*.json)"
    )
    return load_save






 
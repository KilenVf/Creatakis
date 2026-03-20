import json
from pathlib import Path
import os
import config
from config import CODEC, DEFAULT_DURATION, FONT_SIZE
from utils import save_as_path, load_save
from config import media, video, file_path, bloc_media, index, text, nom_chemin

def save_(media=None, video=None, file_path=None, text=None, bloc_media=None, index=None, project_data=None):
    chemin, nom_chemin = save_as_path()
    if not chemin:
        print('destination non sélectionnée')
        return False
    if project_data is None:
        data = {
            'default_data': {
                'codec' : str(CODEC),
                'default_duration' : str(DEFAULT_DURATION),
                'default_font_size' : str(FONT_SIZE)
            },
            'medias' : {
                'media': str(media),
                'video': str(video),
                'file_path': file_path
            },
            'effects' : {
                'text' : str(text),
            },
            'timeline_data' : {
                'bloc_media' : str(bloc_media),
                'index' : str(index)
            }
        }
    else:
        data = project_data

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_save_data():
    chemin, _= load_save()
    if not chemin:
        return False
    with open(chemin, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def load_project_data():
    return load_save_data()

def load_project_data_from_path(path):
    if not path:
        return False
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def update_datas():
    data = load_save_data()
    if not data:
        return False

    medias = data.get('medias', {})
    effects = data.get('effects', {})
    timeline_data = data.get('timeline_data', {})

    config.media = medias.get('media', '')
    file_path = medias.get('file_path')
    if file_path in (None, "", "None"):
        config.file_path = None
    else:
        config.file_path = file_path  # le chemin suffit, on recharge le clip après
    config.text = effects.get('text')
    config.index = int(timeline_data.get('index', -1))
    
    return True

        

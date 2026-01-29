import json
from pathlib import Path
import os
import config
from config import CODEC, DEFAULT_DURATION, FONT_SIZE
from utils import save_as_path, load_save
from config import media, video, file_path, bloc_media, index, text

def save_(media, video, file_path, text, bloc_media, index):
    chemin = save_as_path()
    if not chemin:
        print('destination non sélectionnée')
        return False
    data = {
        'default_data': {
            'codec' : str(CODEC),
            'default_duration' : str(DEFAULT_DURATION),
            'default_font_size' : str(FONT_SIZE)
        },
        
        'medias' : {
            'media': str(media),
            'video': str(video),
            'file_path': str(file_path)
        },

        'effects' : {
            'text' : str(text),
        },

        'timeline_data' : {
            'bloc_media' : str(bloc_media),
            'index' : str(index)
        }
    }

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_save_data():
    chemin = load_save()
    if not chemin:
         return False
    with open(chemin, "r", encoding="utf-8") as f:
            data = json.load(f)
    return data

def update_datas():
    data = load_save_data()
    if not data:
        return False
    
    default_data = data.get('default_data', {})
    medias = data.get('medias', {})
    effects = data.get('effects', {})
    timeline_data = data.get('timeline_data', {})

    # Reconversion des données
    media_val = medias.get('media', '')
    config.media = media_val
    
    video_val = medias.get('video')
    config.video = video_val
    
    file_path_val = medias.get('file_path')
    config.file_path = file_path_val
    
    text_val = effects.get('text')
    config.text = text_val
    
    config.bloc_media = eval(timeline_data.get('bloc_media', '[]'))
    config.index = int(timeline_data.get('index', -1))
    
    return True


        



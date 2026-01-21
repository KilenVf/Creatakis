import json
import os
from pathlib import Path
from config import CODEC, DEFAULT_DURATION, FONT_SIZE

save = {}
def save_( media, video, file_path, text, bloc_media, index):
    save = {
        'codec': str(CODEC),
        'default_duration': str(DEFAULT_DURATION),
        'font_size_default': str(FONT_SIZE),
        'media': str(media),
        'video': str(video),
        'file_path': str(file_path),
        'text': str(text),
        'bloc_media': str(bloc_media),
        'index': str(index)
    }
    return save



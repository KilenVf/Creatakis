
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
import config



def create_clip(video_path, text=None):
    clip = VideoFileClip(video_path)
    
    if text:
        return CompositeVideoClip([clip, text])
    else:
        return clip


def export_video(video, name):
   video.write_videofile(name + config.CODEC)

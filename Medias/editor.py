from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from config import FONT_SIZE, DEFAULT_DURATION, CODEC

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

from moviepy import VideoFileClip, TextClip, CompositeVideoClip


clip = ( 
    VideoFileClip("test.mp4")
    .subclipped(10, 20)
    .with_volume_scaled(0.8)
)


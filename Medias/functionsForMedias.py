
from libs_var import*
from Medias.video import*
from Medias.functionsForMedias import*

video = CompositeVideoClip([clip, txt_clip])
clip = VideoFileClip(imported_video).subclipped(0,5)

def cut():
    return
    
def add_text():
    return

def import_de_videos():
    root =Tk()
    root.withdraw()
    return filedialog.askopenfilename()


def export_medias():
    video.write_videofile(export_name + codec)





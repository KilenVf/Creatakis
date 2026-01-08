import sys
from PyQt5.QtWidgets import QApplication, QDialog

from Uis.ImportMedia import Import_windowMedia
from Uis.MainWindow import ask_txt
from Uis.MainWindow import txt_contentWindow
from Uis.MainWindow import txt_videotitle

from utils.file_dialog import import_video
from Medias.editor import create_clip, export_video


def main():
    app = QApplication(sys.argv)

    if Import_windowMedia().exec_() != QDialog.Accepted:
        sys.exit()

    video_path = import_video()

    text = ""
    if ask_txt().exec_() == QDialog.Accepted:
        dialog = txt_contentWindow()
        if dialog.exec_() == QDialog.Accepted:
            text = dialog.text_value

    video = create_clip(video_path, text)

    title_dialog = txt_videotitle()
    export_name = "video"
    if title_dialog.exec_() == QDialog.Accepted:
        export_name = title_dialog.text_value

    export_video(video, export_name)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

import sys
from PyQt5.QtWidgets import QApplication, QDialog
from Uis.MainWindow import MainWindow
from Uis.MainWindow import txt_contentWindow
from Uis.MainWindow import txt_videotitle

from utils.file_dialog import import_video
from Medias.editor import create_clip, export_video


def main():
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())
 
if __name__ == "__main__":
    main()

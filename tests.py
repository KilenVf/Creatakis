import sys
import vlc
from PyQt5 import QtWidgets, QtCore


class VideoPlayer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Central widget and layout
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        vbox = QtWidgets.QVBoxLayout(central)

        # Video frame (where VLC will render)
        self.video_frame = QtWidgets.QFrame()
        self.video_frame.setStyleSheet("background-color: black;")
        vbox.addWidget(self.video_frame)

        # Position slider
        self.position_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.position_slider.setRange(0, 1000)
        vbox.addWidget(self.position_slider)

        # Controls
        hbox = QtWidgets.QHBoxLayout()
        self.open_btn = QtWidgets.QPushButton("Open")
        self.play_btn = QtWidgets.QPushButton("Play")
        self.stop_btn = QtWidgets.QPushButton("Stop")
        hbox.addWidget(self.open_btn)
        hbox.addWidget(self.play_btn)
        hbox.addWidget(self.stop_btn)
        vbox.addLayout(hbox)

        # Connections
        self.open_btn.clicked.connect(self.open_file)
        self.play_btn.clicked.connect(self.play_pause)
        self.stop_btn.clicked.connect(self.stop)
        self.position_slider.sliderMoved.connect(self.set_position)

        # Timer to update UI
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start()

    def open_file(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Video", "", "Video Files (*.mp4 *.mkv *.avi *.mov);;All Files (*)"
        )
        if not fname:
            return
        media = self.instance.media_new(fname)
        self.player.set_media(media)

        # Tell VLC to render into the Qt widget
        if sys.platform.startswith("win"):
            self.player.set_hwnd(int(self.video_frame.winId()))
        elif sys.platform.startswith("linux"):
            self.player.set_xwindow(int(self.video_frame.winId()))
        elif sys.platform.startswith("darwin"):
            # macOS: set_nsobject expects the NSView pointer; int(winId()) may work in many cases
            self.player.set_nsobject(int(self.video_frame.winId()))

        self.player.play()
        self.play_btn.setText("Pause")

    def play_pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_btn.setText("Play")
        else:
            self.player.play()
            self.play_btn.setText("Pause")

    def stop(self):
        self.player.stop()
        self.play_btn.setText("Play")
        self.position_slider.setValue(0)

    def set_position(self, value):
        # slider value is 0..1000
        pos = value / 1000.0
        try:
            self.player.set_position(pos)
        except Exception:
            pass

    def update_ui(self):
        # Update position slider while playing
        try:
            if self.player is None:
                return
            pos = self.player.get_position()
            if pos is not None and pos >= 0:
                self.position_slider.blockSignals(True)
                self.position_slider.setValue(int(pos * 1000))
                self.position_slider.blockSignals(False)
        except Exception:
            pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())

from PyQt5.QtWidgets import QApplication, QLineEdit, QWidget, QDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class Import_windowMedia(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Creatakis")
        self.setWindowIcon(QIcon("logo.png"))
        self.setGeometry(100,100,1280,720)

        btn_import = QPushButton("importer un média")

        hbox = QHBoxLayout()
        hbox.addWidget(btn_import)

        btn_import.clicked.connect(self.accept)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)

        self.setLayout(vbox)
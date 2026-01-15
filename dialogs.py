# ============================================
# DIALOGS - Fenêtres de dialogue
# ============================================

from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt


class ask_txt(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Confirmation")
        self.setFixedSize(300, 120)

        label = QLabel("Voulez-vous ajouter un texte ?")
        label.setAlignment(Qt.AlignCenter)

        btn_oui = QPushButton("Oui")
        btn_non = QPushButton("Non")

        btn_oui.clicked.connect(self.accept)
        btn_non.clicked.connect(self.reject)

        hbox = QHBoxLayout()
        hbox.addWidget(btn_oui)
        hbox.addWidget(btn_non)

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addLayout(hbox)

        self.setLayout(vbox)


class txt_contentWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Text completion")
        self.setFixedSize(400, 150)

        label = QLabel("Entre le texte à afficher")
        label.setAlignment(Qt.AlignCenter)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Ton texte ici ...")

        btn_ok = QPushButton("Valider")
        btn_ok.clicked.connect(self.valider)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addWidget(btn_ok)

        self.setLayout(layout)
        self.text_value = ""

    def valider(self):
        self.text_value = self.line_edit.text()
        self.accept()


class txt_videotitle(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Title Completion")
        self.setFixedSize(400, 150)

        label = QLabel("Entre le titre de ta vidéo")
        label.setAlignment(Qt.AlignCenter)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Ton titre ici ...")

        btn_ok = QPushButton("Valider")
        btn_ok.clicked.connect(self.valider)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addWidget(btn_ok)

        self.setLayout(layout)
        self.text_value = ""

    def valider(self):
        self.text_value = self.line_edit.text()
        self.accept()

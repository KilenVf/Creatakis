# ============================================
# DIALOGS - Fenêtres de dialogue
# ============================================

from PyQt6.QtWidgets import QDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox
from PyQt6.QtCore import Qt


class ask_txt(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Confirmation")
        self.setFixedSize(300, 120)

        label = QLabel("Voulez-vous ajouter un texte ?")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        self.setFixedSize(400, 200)

        self.label = QLabel("Entre le texte à afficher et ses paramètres")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.labelcolor = QLabel("Couleur")
        self.labelcolor.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.labelsize = QLabel("Taille")
        self.labelsize.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.choix_couleur = QComboBox()
        self.choix_couleur.addItems(['Noir','Blanc','Bleu','Jaune','Violet','Rouge','Vert'])

        self.choix_taille =QComboBox()
        self.choix_taille.addItems(['1','2','3','4','5'])

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Ton texte ici ...")

        btn_ok = QPushButton("Valider")
        btn_ok.clicked.connect(self.valider)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.labelcolor)
        layout.addWidget(self.choix_couleur)
        layout.addWidget(self.labelsize)
        layout.addWidget(self.choix_taille)
        layout.addWidget(btn_ok)

        self.setLayout(layout)
        self.text_value = ""
        self.text_color = ""
        self.text_size = 1

    def valider(self):
        self.text_value = self.line_edit.text()
        self.text_size = self.choix_taille.currentText()

        #trouver un moyen de convertir les couleur en numérique automatiquement#
        if self.choix_couleur.currentText() == 'Noir':
            self.text_color = (0,0,0)
        elif self.choix_couleur.currentText() == 'Blanc':
            self.text_color = (255,255,255)
        elif self.choix_couleur.currentText() == 'Bleu':
            self.text_color = (255,0,0)
        elif self.choix_couleur.currentText() == 'Jaune':
            self.text_color = (0,255,255)
        elif self.choix_couleur.currentText() == 'Violet':
            self.text_color = (128,0,128)
        elif self.choix_couleur.currentText() == 'Rouge':
            self.text_color = (0,0,255)
        elif self.choix_couleur.currentText() == 'Vert':
            self.text_color = (0,255,0)
        else:
            self.text_color = (0,0,0)
         
        
        self.accept()


class txt_videotitle(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Title Completion")
        self.setFixedSize(400, 150)

        label = QLabel("Entre le titre de ta vidéo")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

        

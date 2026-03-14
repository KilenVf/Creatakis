import sys, os
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QFileDialog
 
def openFileDialog():
    options = QFileDialog.Options()
    fileName, _ = QFileDialog.getOpenFileName(None, "Ouvrir un fichier", "", "Tous les fichiers (*);;Python Files (*.py);; Text File (*.txt) ", options=options)
    if fileName:
        print("Fichier sélectionné:", fileName)
        # ouvrir le fichier sélectionné
 
app = QApplication(sys.argv)
window = QWidget()
window.setGeometry(100, 100, 400, 200)
button = QPushButton("Ouvrir un fichier", window)
button.setGeometry(100, 50, 150, 30)
button.clicked.connect(openFileDialog)
window.show()
sys.exit(app.exec_())
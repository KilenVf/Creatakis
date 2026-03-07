import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any

from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QLabel, QPushButton, QSlider, QColorDialog,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QGridLayout, QSizePolicy, QTreeWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from config import focus_boutons


class ToolboxDock(QDockWidget):

    def __init__(self, parent=None):
        super().__init__("Toolbox", parent)

    #enlever le focus des boutons
        focus_boutons(self)

    # définitions des widgets d'effets
        self.btn_add_text = QPushButton('Ajouter texte')
        self.btn_remove_text = QPushButton('Supprimer texte')

    #définitions de la zone d'import avec Qtreewidget

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(['Nom','Type','Taille'])
        self.tree.header().setVisible(True)
        self.tree;self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


        self.container = QWidget(self)

    # layouts

        self.layout_import = QVBoxLayout()
        self.layout_effets = QVBoxLayout()
        self.big_layout = QGridLayout()

        self.zone_effets = QLabel()
        self.zone_effets.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.zone_effets.setStyleSheet('background: grey;')

        self.layout_import.addWidget(self.tree)
        
        self.layout_effets.addWidget(self.btn_add_text)
        self.layout_effets.addWidget(self.btn_remove_text)
        self.layout_effets.addWidget(self.zone_effets)
        
        self.big_layout.addLayout(self.layout_import, 0, 1)
        self.big_layout.addLayout(self.layout_effets, 0,2)

        self.container.setLayout(self.big_layout)
        self.setWidget(self.container)
                
        self.controller = None

    def set_controller(self, controller: object):
        self.controller = controller


    


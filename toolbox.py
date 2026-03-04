"""Toolbox dock (squelette) pour gérer les effets vidéo.

Fournit un `QDockWidget` léger qui émet des signaux pour que la
`main_window` ou un contrôleur média applique les effets.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any

from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QLabel, QPushButton, QSlider, QColorDialog,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor


class ToolboxDock(QDockWidget):
    """Dockable toolbox emitting signals to control media effects.

    Signals:
        applyEffect(dict): demande l'application d'un effet (params dict)
        exportFrame(str): demande d'export d'une frame (chemin)
        gotoFrame(int): demande de déplacement de la tête de lecture
    """

    applyEffect = pyqtSignal(dict)
    exportFrame = pyqtSignal(str)
    gotoFrame = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__("Toolbox", parent)

        self.container = QWidget(self)
        self.layout = QVBoxLayout(self.container)

        self.container.setLayout(self.layout)
        self.setWidget(self.container)

        self.setStyleSheet(
                        "border : 2px solid red;"
                        "border-radius: 4px;")

        self.controller = None

    def set_controller(self, controller: object):
        self.controller = controller


    

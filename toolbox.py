import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any

from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QLabel, QPushButton, QSlider, QColorDialog,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QGridLayout, QSizePolicy, QTreeWidget, QHeaderView, QTreeWidgetItem, QAbstractItemView, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont

import config

path = None


class ToolboxDock(QDockWidget):

    def __init__(self, parent=None):
        super().__init__("Toolbox", parent)

    #enlever le focus des boutons
        config.focus_boutons(self)

    # définitions des widgets d'effets
        self.btn_add_text = QPushButton('Ajouter texte')
        self.btn_remove_text = QPushButton('Supprimer texte')

    #définitions de la zone d'import avec Qtreewidget

        self.tree = DropTree()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(['Nom','Type','Taille'])
        self.tree.header().setVisible(True)
        self.tree.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.header = self.tree.header()
        self.header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        #tri par clic
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
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


    

class DropTree(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()

            self.ajouter_medias(path)

            print(path)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()


    def ajouter_medias(self, path):

        fichier = Path(path)
        taille = fichier.stat().st_size
        self.item_top = QTreeWidgetItem(self)
        self.item_top.setText(0, str(fichier.stem))
        self.item_top.setText(1, str(fichier.suffix))
        self.item_top.setText(2, str(taille))

        if config.file_path == {}:
            id_media = 1
        else:
             id_media = list(config.file_path)[-1] + 1
        config.file_path[str(id_media)] = str(path)
        print(config.file_path)

        self.item_top.setData(0, Qt.UserRole, id_media)
        self.item_top.setData(0, Qt.UserRole + 1, path)

        return id_media
    
    def index_selectionner(self, path):
        item = self.currentItem()
        if item is None:
            config.current_index = None
            config.current_path = None

        else:
            config.current_index = item.data(0, Qt.UserRole)
            config.current_path = item.data(0, Qt.UserRole + 1)
            return config.file_path.get(str(config.current_index))
        
    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item is None:
            return
        self.setCurrentItem(item)
        self.index_selectionner(None)

        menu = QMenu(self)
        ajouter_sequence = QAction('Ajouter à la séquence', self)
        supprimer = QAction('Supprimer', self)
        ajouter_sequence.triggered.connect(self._ajouter_a_sequence)
        supprimer.triggered.connect(self._supprimer_selection)
        menu.addAction(ajouter_sequence)
        menu.addAction(supprimer)
        menu.exec_(event.globalPos())

    def _ajouter_a_sequence(self):
        # TODO: brancher à la timeline plus tard
        print(f"Ajouter à la séquence: {config.current_index} -> {config.current_path}")

    def _supprimer_selection(self):
        # TODO: compléter la suppression (timeline, etc.)
        item = self.currentItem()
        if item is None:
            return
        id_media = item.data(0, Qt.UserRole)
        if id_media is not None:
            config.file_path.pop(str(id_media), None)
        index = self.indexOfTopLevelItem(item)
        if index >= 0:
            self.takeTopLevelItem(index)

    

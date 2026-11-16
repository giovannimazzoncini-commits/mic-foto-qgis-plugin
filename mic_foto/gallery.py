# SPDX-License-Identifier: GPL-3.0-or-later
from functools import wraps
from pathlib import Path
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QKeySequence
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                                QLabel, QShortcut)
from .lifecycle import Plugin as SafePlugin, alive
from .viewer import Panel, PhotoLabel


class Gallery(QDialog):
    def __init__(self, panel):
        super().__init__(panel)
        self.panel = panel
        self.setModal(False)
        self.resize(1000, 750)
        self.setMinimumSize(420, 350)
        layout = QVBoxLayout(self)
        self.photo = PhotoLabel()
        layout.addWidget(self.photo, 1)
        row = QHBoxLayout()
        self.previous = QPushButton('Precedente')
        self.counter = QLabel()
        self.counter.setAlignment(Qt.AlignCenter)
        self.next = QPushButton('Successiva')
        for button in (self.previous, self.next):
            button.setFocusPolicy(Qt.NoFocus)
        self.previous.clicked.connect(lambda: self.step(-1))
        self.next.clicked.connect(lambda: self.step(1))
        row.addWidget(self.previous)
        row.addWidget(self.counter)
        row.addWidget(self.next)
        layout.addLayout(row)
        self.details = QLabel()
        self.details.setWordWrap(True)
        layout.addWidget(self.details)
        self.hint = QLabel('Frecce sinistra/destra: cambia foto | Esc: chiudi | Navigazione nell’elenco filtrato')
        self.hint.setWordWrap(True)
        layout.addWidget(self.hint)
        self.shortcuts = []
        for key, delta in ((Qt.Key_Left, -1), (Qt.Key_Right, 1)):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.setContext(Qt.WindowShortcut)
            shortcut.activated.connect(lambda d=delta: self.step(d))
            self.shortcuts.append(shortcut)
        self.refresh()

    def step(self, delta):
        if not alive(self.panel):
            self.close()
            return
        self.panel.navigate(delta)
        self.refresh()

    def refresh(self):
        if not alive(self.panel):
            self.close()
            return
        row = self.panel.photos.currentRow()
        count = self.panel.photos.count()
        self.counter.setText(f'{row + 1 if row >= 0 else 0} / {count}')
        self.previous.setEnabled(row > 0)
        self.next.setEnabled(0 <= row < count - 1)
        record = self.panel.current()
        if record:
            self.setWindowTitle('MIC_FOTO 0.2.2 — ' + Path(record['path']).name)
            self.photo.setImage(self.panel.preview.image)
            self.details.setText(self.panel.info.text())
        else:
            self.setWindowTitle('MIC_FOTO 0.2.2 — nessuna foto selezionata')
            from qgis.PyQt.QtGui import QPixmap
            self.photo.setImage(QPixmap())
            self.details.setText('Seleziona una foto nel pannello principale.')


def enlarge(panel):
    if not panel.current():
        return
    dialog = getattr(panel, '_gallery', None)
    if not alive(dialog):
        dialog = Gallery(panel)
        panel._gallery = dialog
    dialog.refresh()
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()


_original_show_photo = Panel.show_photo


@wraps(_original_show_photo)
def show_photo(panel, *args):
    _original_show_photo(panel, *args)
    dialog = getattr(panel, '_gallery', None)
    if alive(dialog):
        dialog.refresh()


Panel.enlarge = enlarge
Panel.show_photo = show_photo


class Plugin(SafePlugin):
    def run(self):
        super().run()
        self.panel.setWindowTitle('MIC_FOTO 0.2.2 — sperimentale')
        for button in self.panel.findChildren(QPushButton):
            if button.text() == 'Collega layer attivo':
                button.setText('Usa layer foto selezionato')
                button.setToolTip('Carica le foto del layer selezionato in QGIS. Richiede il campo filepath. Non modifica il layer originale.')

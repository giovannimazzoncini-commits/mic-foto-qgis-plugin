# SPDX-License-Identifier: GPL-3.0-or-later
from pathlib import Path
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QTabWidget, QSplitter, QPushButton, QGroupBox, QToolButton,
    QMenu, QScrollArea)
from .direct_layer import Plugin as WorkingPlugin
from .gallery import Gallery


STYLE = """
QWidget#micFotoRoot { background: #F3F7F8; color: #213B43; }
QWidget#micFotoRoot QLabel { color: #213B43; }
QFrame#micFotoHeader { background: #14646D; border-radius: 9px; }
QFrame#micFotoHeader QLabel { color: white; background: transparent; }
QLabel#micFotoTitle { font-size: 19px; font-weight: 600; }
QLabel#micFotoSubtitle { font-size: 11px; color: #D9ECEE; }
QLabel#micFotoMode { background: #E3EFF0; border-radius: 6px; padding: 7px; }
QLabel#micFotoCount { font-size: 11px; padding: 2px; }
QWidget#micFotoRoot QPushButton, QWidget#micFotoRoot QToolButton {
    background: white; color: #213B43; border: 1px solid #C8DADD;
    border-radius: 5px; padding: 6px 9px; min-height: 17px;
}
QWidget#micFotoRoot QPushButton:hover, QWidget#micFotoRoot QToolButton:hover {
    background: #E6F1F2; border-color: #187F86;
}
QWidget#micFotoRoot QPushButton:disabled { color: #89999D; background: #EDF1F2; border-color: #DCE4E6; }
QWidget#micFotoRoot QPushButton#micFotoPrimary { background: #14646D; color: white; border-color: #14646D; }
QWidget#micFotoRoot QPushButton#micFotoPrimary:hover { background: #187F86; }
QWidget#micFotoRoot QTabWidget::pane { background: white; border: 1px solid #D5E1E4; border-radius: 6px; }
QWidget#micFotoRoot QTabBar::tab { background: #E7EFF1; color: #47626A; padding: 7px 18px; margin-right: 3px; }
QWidget#micFotoRoot QTabBar::tab:selected { background: #14646D; color: white; }
QWidget#micFotoRoot QListWidget { background: white; color: #213B43; border: 1px solid #D5E1E4; border-radius: 5px; }
QWidget#micFotoRoot QListWidget::item { padding: 4px; }
QWidget#micFotoRoot QListWidget::item:selected { background: #D7ECEE; color: #124F57; }
QWidget#micFotoRoot QComboBox { background: white; color: #213B43; padding: 5px; border: 1px solid #C8DADD; border-radius: 5px; }
QLabel#micFotoPreview { background: #E8EFF1; border: 1px solid #D5E1E4; border-radius: 7px; }
QLabel#micFotoInfo { background: #F3F7F8; padding: 7px; border-radius: 5px; font-size: 11px; }
QLabel#micFotoStatus { color: #536D75; font-size: 10px; padding: 3px; }
QWidget#micFotoRoot QGroupBox { border: 1px solid #D5E1E4; border-radius: 6px; margin-top: 14px; padding-top: 14px; }
QWidget#micFotoRoot QGroupBox::title { subcontrol-origin: margin; left: 9px; color: #14646D; }
QWidget#micFotoRoot QSplitter::handle { background: #D5E1E4; height: 5px; }
"""


def restyle(panel):
    if getattr(panel, '_modern_panel', False):
        return
    old = panel.widget()
    split = old.findChild(QSplitter)
    if split is None:
        raise RuntimeError('Layout MIC_FOTO non riconosciuto: divisore foto assente')
    controls = {button.text(): button for button in old.findChildren(QPushButton)}
    def button(prefix):
        for caption, widget in controls.items():
            if caption.startswith(prefix):
                return widget
        raise RuntimeError('Comando MIC_FOTO mancante: ' + prefix)
    edit = next(group for group in old.findChildren(QGroupBox) if group.title() == 'Modifica posizione')
    export_group = next(group for group in old.findChildren(QGroupBox) if group.title() == 'Esporta e scrivi GPS')
    export_buttons = [(label, button(prefix)) for label, prefix in
                      [('Esporta GeoPackage…', 'Esporta GeoPackage'), ('Scrivi GPS nelle copie…', 'GPS nelle copie')]]
    body = QWidget()
    body.setObjectName('micFotoRoot')
    box = QVBoxLayout(body)
    box.setContentsMargins(10, 10, 10, 8)
    box.setSpacing(8)
    header = QFrame()
    header.setObjectName('micFotoHeader')
    hb = QHBoxLayout(header)
    icon = QLabel()
    icon.setPixmap(QPixmap(str(Path(__file__).with_name('icon.svg'))).scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    hb.addWidget(icon)
    titles = QVBoxLayout()
    title = QLabel('MIC_FOTO'); title.setObjectName('micFotoTitle')
    subtitle = QLabel('Fotografie di sopralluogo'); subtitle.setObjectName('micFotoSubtitle')
    titles.addWidget(title); titles.addWidget(subtitle)
    hb.addLayout(titles, 1)
    export_menu = QToolButton()
    export_menu.setText('Esporta')
    export_menu.setToolTip('Esporta i punti o scrivi le coordinate nelle copie delle foto')
    export_menu.setPopupMode(QToolButton.InstantPopup)
    menu = QMenu(export_menu)
    for label, original in export_buttons:
        action = menu.addAction(label)
        action.triggered.connect(lambda checked=False, b=original: b.click())
    export_menu.setMenu(menu)
    hb.addWidget(export_menu)
    box.addWidget(header)
    panel._mode_label.setObjectName('micFotoMode')
    box.addWidget(panel._mode_label)
    tools = QGridLayout()
    tools.setHorizontalSpacing(6); tools.setVerticalSpacing(6)
    for row, col, prefix, label in (
        (0, 0, 'Apri foto', 'Apri foto…'), (0, 1, 'Apri lavoro', 'Apri lavoro…'),
        (1, 0, 'Salva lavoro', 'Salva lavoro'), (1, 1, 'Usa layer foto', 'Usa layer selezionato')):
        control = button(prefix)
        control.setText(label)
        tools.addWidget(control, row, col)
    box.addLayout(tools)
    tabs = QTabWidget()
    photo_tab = QWidget()
    photo_layout = QVBoxLayout(photo_tab)
    photo_layout.setContentsMargins(8, 8, 8, 8)
    panel.count.setObjectName('micFotoCount')
    photo_layout.addWidget(panel.count)
    photo_layout.addWidget(panel.filter)
    photo_layout.addWidget(split, 1)
    panel.preview.setObjectName('micFotoPreview')
    panel.preview.setMinimumHeight(180)
    panel.info.setObjectName('micFotoInfo')
    panel.info.setTextFormat(Qt.PlainText)
    panel.photos.setMinimumHeight(60)
    split.setSizes([110, 430])
    photo_layout.addWidget(panel.follow)
    consult = button('Consulta sulla mappa')
    consult.setObjectName('micFotoPrimary')
    photo_layout.addWidget(consult)
    tabs.addTab(photo_tab, 'Foto')
    position_tab = QWidget()
    position_layout = QVBoxLayout(position_tab)
    help_text = QLabel('Assegna o correggi le posizioni nel lavoro MIC_FOTO. In consultazione diretta del GeoPackage questi comandi restano disabilitati.')
    help_text.setWordWrap(True)
    position_layout.addWidget(help_text)
    position_layout.addWidget(edit)
    position_layout.addStretch(1)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setWidget(position_tab)
    tabs.addTab(scroll, 'Posizionamento')
    box.addWidget(tabs, 1)
    panel.status.setObjectName('micFotoStatus')
    panel.status.setTextFormat(Qt.PlainText)
    box.addWidget(panel.status)
    export_group.setParent(body)
    export_group.setChecked(True)
    export_group.setEnabled(True)
    export_group.hide()
    panel._export_controls = export_group
    old.setParent(None)
    panel.setWidget(body)
    body.setStyleSheet(STYLE)
    old.deleteLater()
    panel.setMinimumWidth(340)
    panel._modern_panel = True
    panel._photo_tabs = tabs


_original_gallery_refresh = Gallery.refresh


def gallery_refresh(dialog):
    _original_gallery_refresh(dialog)
    dialog.setWindowTitle(dialog.windowTitle().replace('MIC_FOTO 0.2.5', 'MIC_FOTO 0.3.0', 1))


Gallery.refresh = gallery_refresh


class Plugin(WorkingPlugin):
    def run(self):
        super().run()
        restyle(self.panel)
        self.panel.setWindowTitle('MIC_FOTO 0.3.0 — sperimentale')

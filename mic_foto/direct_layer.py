# SPDX-License-Identifier: GPL-3.0-or-later
from pathlib import Path
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QLabel, QGroupBox, QMessageBox
from qgis.core import (QgsVectorLayer, QgsWkbTypes, QgsCoordinateTransform,
    QgsCoordinateReferenceSystem, QgsProject, QgsPointXY, QgsProviderRegistry, NULL)
from .branding import Plugin as StyledPlugin, update_marker
from .viewer import Panel
from .gallery import Gallery
from .lifecycle import alive, prune


def direct(panel):
    return getattr(panel, '_direct_layer_id', None) is not None


def text(value):
    return '' if value is None or value == NULL else str(value)


def mode_label(panel):
    label = getattr(panel, '_mode_label', None)
    if label is not None:
        if direct(panel):
            name = panel.layer.name() if alive(panel.layer) else 'layer rimosso'
            label.setText('Consultazione senza modifica: ' + name)
        else:
            label.setText('Importazione e posizionamento — lavoro MIC_FOTO')


def edit_controls(panel, enabled):
    for group in panel.findChildren(QGroupBox):
        if group.title() == 'Modifica posizione':
            if not enabled:
                group.setChecked(False)
            group.setEnabled(enabled)


def disconnect_current(panel):
    panel.stop_tool()
    if alive(panel.layer):
        try:
            panel.layer.selectionChanged.disconnect(panel.from_map)
        except (TypeError, RuntimeError):
            pass
    panel.disconnect_external()


def leave_direct(panel):
    if not direct(panel):
        return True
    answer = QMessageBox.question(panel, 'MIC_FOTO',
        'Scollegare il layer consultato e aprire un altro lavoro? Il GeoPackage non verra modificato.',
        QMessageBox.Yes | QMessageBox.No)
    if answer != QMessageBox.Yes:
        return False
    disconnect_current(panel)
    panel._direct_layer_id = None
    panel._direct_fids = {}
    panel.layer = None
    panel.records = []
    panel.session = None
    panel.history = []
    edit_controls(panel, True)
    panel.refresh_list()
    mode_label(panel)
    return True


_old_link = Panel.link_layer
_old_sync = Panel.sync_selection
_old_from_map = Panel.from_map
_old_identify = Panel.identify_photo
_old_rebuild = Panel.rebuild_layer
_old_scan = Panel.scan
_old_open = Panel.open_work
_old_place = Panel.place
_old_clicked = Panel.clicked
_old_undo = Panel.undo
_old_browse = Panel.browse


def link_layer(panel, checked=False):
    layer = panel.iface.activeLayer()
    if not isinstance(layer, QgsVectorLayer) or not layer.isValid():
        QMessageBox.warning(panel, 'MIC_FOTO', 'Seleziona un layer vettoriale fotografico.'); return
    if 'filepath' not in layer.fields().names() or QgsWkbTypes.geometryType(layer.wkbType()) != QgsWkbTypes.PointGeometry:
        QMessageBox.warning(panel, 'MIC_FOTO', 'Serve un layer di punti con il campo filepath.'); return
    if QgsWkbTypes.isMultiType(layer.wkbType()):
        QMessageBox.warning(panel, 'MIC_FOTO', 'Sono supportati punti singoli, non multipunti.'); return
    if layer is panel.layer and not direct(panel):
        panel.browse(); return
    if panel.records and QMessageBox.question(panel, 'MIC_FOTO',
        'Collegare il layer selezionato? Salva prima l’eventuale lavoro corrente. Il layer non verra modificato.',
        QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
        return
    records = []; fids = {}
    try:
        fields = layer.fields().names()
        uri = QgsProviderRegistry.instance().decodeUri(layer.providerType(), layer.source())
        file_path = uri.get('path', '')
        folder = Path(file_path).parent if file_path else Path(QgsProject.instance().homePath() or '.')
        transform = QgsCoordinateTransform(layer.crs(), QgsCoordinateReferenceSystem('EPSG:4326'), QgsProject.instance())
        for feature in layer.getFeatures():
            photo_id = 'fid:' + str(feature.id())
            raw_path = text(feature['filepath'])
            path = Path(raw_path)
            if raw_path and not path.is_absolute():
                path = folder / path
            lat = lon = None
            if feature.hasGeometry() and not feature.geometry().isEmpty():
                pt = transform.transform(feature.geometry().asPoint())
                lat, lon = pt.y(), pt.x()
            records.append(dict(id=photo_id, path=str(path) if raw_path else '', lat=lat, lon=lon,
                source=text(feature['source']) if 'source' in fields else 'layer',
                date=text(feature['datetime']) if 'datetime' in fields else '',
                error='' if raw_path and path.is_file() else 'Foto non trovata nel percorso indicato'))
            fids[photo_id] = feature.id()
    except Exception as exc:
        QMessageBox.warning(panel, 'MIC_FOTO', str(exc)); return
    disconnect_current(panel)
    panel._direct_layer_id = layer.id()
    panel._direct_fids = fids
    panel.layer = layer
    panel.records = records
    panel.history = []
    panel.session = None
    layer.selectionChanged.connect(panel.from_map)
    edit_controls(panel, False)
    panel.refresh_list()
    mode_label(panel)
    panel.status.setText('Layer collegato direttamente: nessuna copia temporanea, nessuna modifica ai dati. Premi Consulta sulla mappa.')


def sync(panel, record):
    if not direct(panel):
        return _old_sync(panel, record)
    prune(panel)
    if panel.syncing or not alive(panel.layer):
        return
    panel.syncing = True
    try:
        fid = panel._direct_fids.get(record['id']) if record else None
        panel.layer.selectByIds([] if fid is None or record['lat'] is None else [fid])
        if record and record['lat'] is not None and panel.follow.isChecked():
            canvas = panel.iface.mapCanvas()
            transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'), canvas.mapSettings().destinationCrs(), QgsProject.instance())
            canvas.setCenter(transform.transform(QgsPointXY(record['lon'], record['lat'])))
            canvas.refresh()
    finally:
        panel.syncing = False
    update_marker(panel)


def from_map(panel, *args):
    if not direct(panel):
        return _old_from_map(panel, *args)
    prune(panel)
    if panel.syncing or not alive(panel.layer):
        return
    selected = panel.layer.selectedFeatureIds()
    if selected:
        photo_id = next((key for key, fid in panel._direct_fids.items() if fid == selected[0]), None)
        if photo_id is not None:
            panel.choose(photo_id)


def identify(panel, feature):
    if direct(panel):
        panel.choose('fid:' + str(feature.id()))
    else:
        _old_identify(panel, feature)


def rebuild(panel, *args):
    if direct(panel):
        return
    return _old_rebuild(panel, *args)


def scan(panel, checked=False):
    if leave_direct(panel):
        return _old_scan(panel)


def open_work(panel, checked=False):
    if leave_direct(panel):
        return _old_open(panel)


def place(panel, checked=False):
    if direct(panel):
        QMessageBox.information(panel, 'MIC_FOTO', 'Modalita consultazione: le posizioni del layer non vengono modificate.'); return
    return _old_place(panel)


def clicked(panel, *args):
    if not direct(panel):
        return _old_clicked(panel, *args)


def undo(panel, checked=False):
    if not direct(panel):
        return _old_undo(panel)


def browse(panel, checked=False):
    prune(panel)
    if direct(panel) and not alive(panel.layer):
        QMessageBox.warning(panel, 'MIC_FOTO', 'Il layer collegato e stato rimosso. Seleziona e collega nuovamente il GeoPackage.'); return
    result = _old_browse(panel)
    if direct(panel) and alive(panel.layer):
        panel.status.setText('Consulta direttamente: ' + panel.layer.name() + '. Clicca un punto per aprire la foto.')
    return result


Panel.link_layer = link_layer
Panel.sync_selection = sync
Panel.from_map = from_map
Panel.identify_photo = identify
Panel.rebuild_layer = rebuild
Panel.scan = scan
Panel.open_work = open_work
Panel.place = place
Panel.clicked = clicked
Panel.undo = undo
Panel.browse = browse
_original_gallery_refresh = Gallery.refresh


def gallery_refresh(dialog):
    _original_gallery_refresh(dialog)
    dialog.setWindowTitle(dialog.windowTitle().replace('MIC_FOTO 0.2.4', 'MIC_FOTO 0.2.5', 1))


Gallery.refresh = gallery_refresh


class Plugin(StyledPlugin):
    def run(self):
        saved_renderer = None
        target = None
        if alive(self.panel) and direct(self.panel) and alive(self.panel.layer):
            target = self.panel.layer
            renderer = target.renderer()
            saved_renderer = renderer.clone() if renderer is not None else None
        try:
            super().run()
        finally:
            if alive(target) and saved_renderer is not None:
                target.setRenderer(saved_renderer)
                target.triggerRepaint()
        panel = self.panel
        panel.setWindowTitle('MIC_FOTO 0.2.5 — sperimentale')
        if not hasattr(panel, '_mode_label'):
            panel._mode_label = QLabel()
            panel._mode_label.setTextFormat(Qt.PlainText)
            panel._mode_label.setWordWrap(True)
            panel.widget().layout().insertWidget(2, panel._mode_label)
        mode_label(panel)

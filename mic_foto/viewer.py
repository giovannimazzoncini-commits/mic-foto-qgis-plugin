# SPDX-License-Identifier: GPL-3.0-or-later
import uuid
from pathlib import Path
from qgis.PyQt.QtCore import Qt, QSignalBlocker
from qgis.PyQt.QtGui import QPixmap, QImageReader
from qgis.PyQt.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QCheckBox, QSplitter, QGroupBox, QDialog, QSizePolicy, QMessageBox)
from qgis.core import (QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsPointXY)
from qgis.gui import QgsMapToolIdentifyFeature
from .plugin import Plugin as BasePlugin, Panel as BasePanel

class PhotoLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.image = QPixmap()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(120, 120)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
    def setImage(self, image):
        self.image = image
        self.updateImage()
    def updateImage(self):
        if self.image.isNull():
            self.clear()
            self.setText('Nessuna immagine disponibile')
        else:
            self.setPixmap(self.image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateImage()

class Plugin(BasePlugin):
    def run(self):
        if self.panel is None:
            self.panel = Panel(self.iface)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.panel)
        self.panel.show()
        self.panel.raise_()
    def unload(self):
        if self.panel:
            self.panel.disconnect_external()
        super().unload()

class Panel(BasePanel):
    def __init__(self, iface):
        self.syncing = False
        self.building = False
        self.external = None
        self.external_ids = {}
        super().__init__(iface)
        self.setWindowTitle('MIC_FOTO 0.2.0 — sperimentale')
        old = self.widget()
        body = QWidget()
        box = QVBoxLayout(body)
        def buttons(parent, specs):
            row = QHBoxLayout()
            for title, fn in specs:
                b = QPushButton(title)
                b.clicked.connect(fn)
                row.addWidget(b)
            parent.addLayout(row)
        buttons(box, [('Apri foto…', self.scan), ('Apri lavoro…', self.open_work), ('Salva lavoro', self.save_work)])
        buttons(box, [('Collega layer attivo', self.link_layer), ('Consulta sulla mappa', self.browse)])
        box.addWidget(self.count)
        box.addWidget(self.filter)
        split = QSplitter(Qt.Vertical)
        split.addWidget(self.photos)
        photo_box = QWidget()
        pb = QVBoxLayout(photo_box)
        self.preview = PhotoLabel()
        pb.addWidget(self.preview, 1)
        nav = QHBoxLayout()
        self.prev = QPushButton('Precedente'); self.prev.clicked.connect(lambda: self.navigate(-1))
        self.next = QPushButton('Successiva'); self.next.clicked.connect(lambda: self.navigate(1))
        self.index = QLabel('0 / 0'); self.index.setAlignment(Qt.AlignCenter)
        nav.addWidget(self.prev); nav.addWidget(self.index); nav.addWidget(self.next)
        pb.addLayout(nav)
        b = QPushButton('Ingrandisci foto'); b.clicked.connect(self.enlarge); pb.addWidget(b)
        pb.addWidget(self.info)
        split.addWidget(photo_box)
        split.setStretchFactor(0, 1); split.setStretchFactor(1, 3)
        split.setSizes([160, 430]); box.addWidget(split, 1)
        self.follow = QCheckBox('Segui foto sulla mappa (mantieni scala)')
        self.follow.setChecked(True); box.addWidget(self.follow)
        edit = QGroupBox('Modifica posizione'); edit.setCheckable(True); edit.setChecked(False)
        eb = QVBoxLayout(edit)
        buttons(eb, [('Posiziona / correggi', self.place), ('Termina', self.stop_tool)])
        buttons(eb, [('Annulla ultima posizione', self.undo)])
        box.addWidget(edit)
        export = QGroupBox('Esporta e scrivi GPS'); export.setCheckable(True); export.setChecked(False)
        xb = QVBoxLayout(export)
        buttons(xb, [('Esporta GeoPackage…', self.export), ('GPS nelle copie…', self.write_copies)])
        box.addWidget(export)
        box.addWidget(self.status)
        old.setParent(None)
        self.setWidget(body)
        old.deleteLater()
        self.preview.mouseDoubleClickEvent = lambda event: self.enlarge()
        self.refresh_list()

    def refresh_list(self, *args):
        selected = self.current()
        wanted = selected['id'] if selected else None
        guard = QSignalBlocker(self.photos)
        BasePanel.refresh_list(self, *args)
        for i in range(self.photos.count()):
            it = self.photos.item(i)
            rec = next(r for r in self.records if r['id'] == it.data(Qt.UserRole))
            state = 'ERRORE' if rec['error'] else ('DA POSIZIONARE' if rec['lat'] is None else
                ('MANUALE' if rec['source'] == 'manual' else 'EXIF' if rec['source'] == 'exif' else 'DA LAYER'))
            it.setText(f'[{state}] {Path(rec["path"]).name}')
            if rec['id'] == wanted:
                self.photos.setCurrentItem(it)
        if self.photos.currentRow() < 0 and self.photos.count():
            self.photos.setCurrentRow(0)
        del guard
        if hasattr(self, 'follow'):
            self.show_photo()

    def show_photo(self, *args):
        if not hasattr(self, 'follow'):
            return BasePanel.show_photo(self, *args)
        rec = self.current()
        row = self.photos.currentRow()
        self.index.setText(f'{row+1 if row >= 0 else 0} / {self.photos.count()}')
        self.prev.setEnabled(row > 0)
        self.next.setEnabled(0 <= row < self.photos.count()-1)
        if not rec:
            self.preview.setImage(QPixmap()); self.info.clear()
            self.sync_selection(None)
            return
        reader = QImageReader(rec['path']); reader.setAutoTransform(True)
        size = reader.size()
        if size.isValid():
            size.scale(1800, 1400, Qt.KeepAspectRatio); reader.setScaledSize(size)
        self.preview.setImage(QPixmap.fromImage(reader.read()))
        origin = {'manual':'Posizione manuale', 'exif':'Da metadati EXIF', 'layer':'Da layer'}.get(rec['source'], 'Da posizionare')
        coords = 'Senza posizione' if rec['lat'] is None else f'Lat {rec["lat"]:.7f} | Lon {rec["lon"]:.7f}'
        self.info.setText(f'{Path(rec["path"]).name}\n{rec["date"]}\n{origin} — {coords}\n{rec["error"]}')
        self.sync_selection(rec)

    def sync_selection(self, rec):
        if self.syncing or self.building:
            return
        self.syncing = True
        try:
            for layer, mapping in [(self.layer, None), (self.external, self.external_ids)]:
                if layer is None or not QgsProject.instance().mapLayer(layer.id()):
                    continue
                if rec is None or rec['lat'] is None:
                    layer.removeSelection(); continue
                ids = ([fid for fid, photo_id in mapping.items() if photo_id == rec['id']] if mapping is not None else
                       [f.id() for f in layer.getFeatures() if f['photo_id'] == rec['id']])
                layer.selectByIds(ids)
            if rec and rec['lat'] is not None and self.follow.isChecked() and self.layer:
                canvas = self.iface.mapCanvas()
                tr = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'), canvas.mapSettings().destinationCrs(), QgsProject.instance())
                canvas.setCenter(tr.transform(QgsPointXY(rec['lon'], rec['lat'])))
                canvas.refresh()
        finally:
            self.syncing = False

    def from_map(self, *args):
        if self.syncing or self.building or not self.layer:
            return
        selected = self.layer.selectedFeatures()
        if selected:
            self.choose(selected[0]['photo_id'])

    def choose(self, photo_id):
        row = next((i for i in range(self.photos.count()) if self.photos.item(i).data(Qt.UserRole) == photo_id), None)
        if row is None:
            self.filter.setCurrentIndex(0)
            row = next((i for i in range(self.photos.count()) if self.photos.item(i).data(Qt.UserRole) == photo_id), None)
        if row is not None:
            self.photos.setCurrentRow(row)
            self.photos.scrollToItem(self.photos.item(row))
            self.show_photo()

    def navigate(self, step):
        row = self.photos.currentRow() + step
        if 0 <= row < self.photos.count():
            self.photos.setCurrentRow(row)

    def rebuild_layer(self):
        self.building = True
        try:
            BasePanel.rebuild_layer(self)
        finally:
            self.building = False

    def browse(self):
        if not self.layer:
            QMessageBox.information(self, 'MIC_FOTO', 'Apri foto, un lavoro o collega un layer fotografico.'); return
        self.stop_tool()
        canvas = self.iface.mapCanvas()
        self.iface.setActiveLayer(self.layer)
        self.previous_tool = canvas.mapTool()
        self.tool = QgsMapToolIdentifyFeature(canvas)
        self.tool.setLayer(self.layer)
        self.tool.featureIdentified.connect(self.identify_photo)
        canvas.setMapTool(self.tool)
        self.status.setText('Consultazione: clicca un punto per vedere la foto. Le coordinate non vengono modificate.')

    def identify_photo(self, feature):
        self.choose(feature['photo_id'])

    def enlarge(self):
        rec = self.current()
        if not rec:
            return
        dialog = QDialog(self); dialog.setWindowTitle(Path(rec['path']).name)
        layout = QVBoxLayout(dialog)
        label = PhotoLabel(); layout.addWidget(label)
        reader = QImageReader(rec['path']); reader.setAutoTransform(True)
        label.setImage(QPixmap.fromImage(reader.read()))
        dialog.resize(1000, 750); dialog.exec_()

    def disconnect_external(self):
        if self.external:
            try:
                self.external.selectionChanged.disconnect(self.external_selected)
            except (RuntimeError, TypeError):
                pass
        self.external = None; self.external_ids = {}

    def external_selected(self, *args):
        if self.syncing or not self.external:
            return
        ids = self.external.selectedFeatureIds()
        if ids and ids[0] in self.external_ids:
            self.choose(self.external_ids[ids[0]])

    def link_layer(self):
        layer = self.iface.activeLayer()
        if not layer or not hasattr(layer, 'fields') or 'filepath' not in layer.fields().names():
            QMessageBox.warning(self, 'Collega layer', 'Seleziona un layer fotografico con il campo filepath, ad esempio il GeoPackage esportato da MIC_FOTO.'); return
        if layer is self.layer:
            self.browse(); return
        if self.records and QMessageBox.question(self, 'Collega layer', 'Sostituire il lavoro corrente? Salvalo prima se necessario.', QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        records = []; mapping = {}; used = set()
        try:
            fields = layer.fields().names()
            transform = QgsCoordinateTransform(layer.crs(), QgsCoordinateReferenceSystem('EPSG:4326'), QgsProject.instance())
            for feature in layer.getFeatures():
                photo_id = str(feature['photo_id']) if 'photo_id' in fields else str(uuid.uuid4())
                if photo_id in used:
                    photo_id = str(uuid.uuid4())
                used.add(photo_id)
                path = str(feature['filepath'])
                lat = lon = None
                if feature.hasGeometry() and not feature.geometry().isEmpty():
                    if feature.geometry().isMultipart():
                        raise ValueError('Sono supportati solo punti singoli')
                    point = transform.transform(feature.geometry().asPoint())
                    lat, lon = point.y(), point.x()
                records.append(dict(id=photo_id, path=path, lat=lat, lon=lon,
                    source=str(feature['source']) if 'source' in fields else 'layer',
                    date=str(feature['datetime']) if 'datetime' in fields else '',
                    error='' if Path(path).is_file() else 'File non trovato: percorso da verificare'))
                mapping[feature.id()] = photo_id
        except Exception as exc:
            QMessageBox.warning(self, 'Collega layer', str(exc)); return
        self.stop_tool(); self.disconnect_external()
        self.external = layer; self.external_ids = mapping
        layer.selectionChanged.connect(self.external_selected)
        self.records = records; self.session = None; self.history = []
        self.rebuild_layer(); self.refresh_list()
        self.status.setText('Layer collegato. Modifiche solo nel lavoro MIC_FOTO: esporta un nuovo GPKG per conservarle. Premi Salva lavoro.')

    def open_work(self):
        BasePanel.open_work(self)
        if self.external and any(r['id'] not in self.external_ids.values() for r in self.records):
            self.disconnect_external()

# SPDX-License-Identifier: GPL-3.0-or-later
import os
import json
import math
import uuid
from pathlib import Path
from qgis.PyQt.QtCore import Qt, QVariant
from qgis.PyQt.QtGui import QPixmap, QImageReader
from qgis.PyQt.QtWidgets import (QAction, QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QFileDialog, QMessageBox, QComboBox)
from qgis.core import (QgsExifTools, QgsProject, QgsVectorLayer, QgsField, QgsFeature,
    QgsGeometry, QgsPointXY, QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsVectorFileWriter)
from qgis.gui import QgsMapToolEmitPoint

class Plugin:
    def __init__(self, iface):
        self.iface = iface
        self.panel = None

    def initGui(self):
        self.action = QAction('MIC_FOTO', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu('MIC_FOTO', self.action)
        self.iface.addToolBarIcon(self.action)

    def run(self):
        if self.panel is None:
            self.panel = Panel(self.iface)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.panel)
        self.panel.show()
        self.panel.raise_()

    def unload(self):
        if self.panel:
            self.panel.stop_tool()
            if self.panel.layer:
                try:
                    self.panel.layer.selectionChanged.disconnect(self.panel.from_map)
                except (TypeError, RuntimeError):
                    pass
            self.iface.removeDockWidget(self.panel)
            self.panel.deleteLater()
        self.iface.removePluginMenu('MIC_FOTO', self.action)
        self.iface.removeToolBarIcon(self.action)

class Panel(QDockWidget):
    def __init__(self, iface):
        super().__init__('MIC_FOTO — sperimentale 0.1.0', iface.mainWindow())
        self.setObjectName('MIC_FOTO_PANEL')
        self.iface = iface
        self.records = []
        self.layer = None
        self.history = []
        self.tool = None
        self.previous_tool = None
        self.session = None
        self.setMinimumWidth(330)
        body = QWidget()
        box = QVBoxLayout(body)
        self.setWidget(body)
        for specs in [ [('Apri cartella', self.scan), ('Apri lavoro', self.open_work)],
                       [('Salva lavoro', self.save_work), ('Esporta GPKG', self.export)]]:
            row = QHBoxLayout()
            for name, fn in specs:
                b = QPushButton(name); b.clicked.connect(fn); row.addWidget(b)
            box.addLayout(row)
        self.filter = QComboBox()
        self.filter.addItems(['Tutte', 'Con posizione', 'Da posizionare', 'Non leggibili'])
        self.filter.currentIndexChanged.connect(self.refresh_list)
        box.addWidget(self.filter)
        self.count = QLabel(); box.addWidget(self.count)
        self.photos = QListWidget(); box.addWidget(self.photos, 2)
        self.photos.currentItemChanged.connect(self.show_photo)
        self.preview = QLabel('Seleziona una fotografia')
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(170)
        box.addWidget(self.preview, 1)
        self.info = QLabel(); self.info.setWordWrap(True); box.addWidget(self.info)
        b = QPushButton('Posiziona / correggi sulla mappa'); b.clicked.connect(self.place); box.addWidget(b)
        row = QHBoxLayout()
        for name, fn in [('Annulla posizione', self.undo), ('Termina posizionamento', self.stop_tool)]:
            b = QPushButton(name); b.clicked.connect(fn); row.addWidget(b)
        box.addLayout(row)
        b = QPushButton('Scrivi GPS nelle copie…'); b.clicked.connect(self.write_copies); box.addWidget(b)
        self.status = QLabel('JPG/JPEG • originali mai modificati'); self.status.setWordWrap(True); box.addWidget(self.status)
        self.refresh_list()

    def current(self):
        item = self.photos.currentItem()
        return next((r for r in self.records if item and r['id'] == item.data(Qt.UserRole)), None)

    def scan(self):
        folder = QFileDialog.getExistingDirectory(self, 'Cartella JPG/JPEG (incluse sottocartelle)')
        if not folder:
            return
        known = {os.path.normcase(os.path.abspath(r['path'])) for r in self.records}
        for path in sorted(Path(folder).rglob('*')):
            if path.suffix.lower() not in ('.jpg', '.jpeg') or not path.is_file():
                continue
            key = os.path.normcase(os.path.abspath(str(path)))
            if key in known:
                continue
            known.add(key)
            rec = dict(id=str(uuid.uuid4()), path=str(path), lat=None, lon=None,
                       source='pending', date='', error='')
            try:
                if not QImageReader(str(path)).canRead():
                    rec['error'] = 'Immagine non leggibile'
                tags = QgsExifTools.readTags(str(path))
                dt = tags.get('Exif.Photo.DateTimeOriginal', tags.get('Exif.Image.DateTime', ''))
                rec['date'] = dt.toString(Qt.ISODate) if hasattr(dt, 'toString') else str(dt or '')
                point, ok = QgsExifTools.getGeoTag(str(path))
                if ok and math.isfinite(point.x()) and math.isfinite(point.y()):
                    if -180 <= point.x() <= 180 and -90 <= point.y() <= 90:
                        rec.update(lon=point.x(), lat=point.y(), source='exif')
            except Exception as exc:
                rec['error'] = 'Errore lettura metadati: ' + str(exc)
            self.records.append(rec)
        self.rebuild_layer(); self.refresh_list(); self.autosave()
        self.status.setText('Importazione terminata. Premi Salva lavoro per scegliere il file di sessione.')

    def refresh_list(self, *args):
        selected = self.current()
        selected_id = selected['id'] if selected else None
        self.photos.clear()
        f = self.filter.currentIndex()
        n = sum(r['lat'] is not None for r in self.records)
        self.count.setText(f'{len(self.records)} foto | {n} con posizione | {len(self.records)-n} senza posizione')
        for r in self.records:
            pos = r['lat'] is not None
            if (f == 1 and not pos) or (f == 2 and (pos or r['error'])) or (f == 3 and not r['error']):
                continue
            state = 'ERRORE' if r['error'] else ('GPS' if pos else 'DA POSIZIONARE')
            it = QListWidgetItem(f'[{state}] {Path(r["path"]).name}')
            it.setData(Qt.UserRole, r['id']); it.setToolTip(r['path'])
            self.photos.addItem(it)
            if r['id'] == selected_id:
                self.photos.setCurrentItem(it)

    def show_photo(self, *args):
        r = self.current()
        if not r:
            self.preview.clear(); self.info.clear(); return
        reader = QImageReader(r['path']); reader.setAutoTransform(True)
        size = reader.size()
        if size.isValid():
            size.scale(1000, 700, Qt.KeepAspectRatio); reader.setScaledSize(size)
        pix = QPixmap.fromImage(reader.read())
        self.preview.setPixmap(pix.scaled(max(250, self.width()-35), 270, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        coords = 'Senza posizione' if r['lat'] is None else f'Lat {r["lat"]:.7f} • Lon {r["lon"]:.7f}'
        self.info.setText(f'{Path(r["path"]).name}\n{r["date"]}\n{coords}\nOrigine: {r["source"]}\n{r["error"]}')

    def rebuild_layer(self):
        if self.layer is None or not QgsProject.instance().mapLayer(self.layer.id()):
            self.layer = QgsVectorLayer('Point?crs=EPSG:4326', 'MIC_FOTO — lavoro', 'memory')
            p = self.layer.dataProvider()
            p.addAttributes([QgsField(k, QVariant.String) for k in ['photo_id', 'filename', 'filepath', 'datetime', 'source', 'error']]
                            + [QgsField('latitude', QVariant.Double), QgsField('longitude', QVariant.Double)])
            self.layer.updateFields()
            self.layer.setCustomProperty('MIC_FOTO', True)
            QgsProject.instance().addMapLayer(self.layer)
            self.layer.selectionChanged.connect(self.from_map)
        p = self.layer.dataProvider()
        p.deleteFeatures([f.id() for f in self.layer.getFeatures()])
        features = []
        for r in self.records:
            feat = QgsFeature(self.layer.fields())
            feat.setAttributes([r['id'], Path(r['path']).name, r['path'], r['date'], r['source'], r['error'], r['lat'], r['lon']])
            if r['lat'] is not None:
                feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(r['lon'], r['lat'])))
            features.append(feat)
        p.addFeatures(features); self.layer.updateExtents(); self.layer.triggerRepaint()

    def from_map(self, *args):
        selected = self.layer.selectedFeatures()
        if not selected:
            return
        photo_id = selected[0]['photo_id']
        for i in range(self.photos.count()):
            it = self.photos.item(i)
            if it.data(Qt.UserRole) == photo_id:
                self.photos.setCurrentItem(it); break

    def place(self):
        if not self.current():
            QMessageBox.information(self, 'MIC_FOTO', 'Seleziona prima una foto.'); return
        self.stop_tool()
        canvas = self.iface.mapCanvas()
        self.previous_tool = canvas.mapTool()
        self.tool = QgsMapToolEmitPoint(canvas)
        self.tool.canvasClicked.connect(self.clicked)
        canvas.setMapTool(self.tool)
        self.status.setText('Clicca il punto di scatto sulla mappa. Poi seleziona un’altra foto o termina.')

    def clicked(self, point, button):
        if button != Qt.LeftButton:
            self.stop_tool(); return
        r = self.current()
        if not r:
            return
        try:
            transform = QgsCoordinateTransform(self.iface.mapCanvas().mapSettings().destinationCrs(),
                QgsCoordinateReferenceSystem('EPSG:4326'), QgsProject.instance())
            pt = transform.transform(point)
            if not (-180 <= pt.x() <= 180 and -90 <= pt.y() <= 90):
                raise ValueError('Coordinate fuori intervallo')
            self.history.append((r['id'], r['lat'], r['lon'], r['source']))
            r.update(lat=pt.y(), lon=pt.x(), source='manual')
            self.rebuild_layer(); self.refresh_list(); self.show_photo(); self.autosave()
        except Exception as exc:
            QMessageBox.warning(self, 'Posizionamento', str(exc))

    def stop_tool(self):
        if self.tool:
            canvas = self.iface.mapCanvas()
            if canvas.mapTool() is self.tool:
                canvas.unsetMapTool(self.tool)
                if self.previous_tool:
                    canvas.setMapTool(self.previous_tool)
            self.tool = None

    def undo(self):
        if not self.history:
            return
        photo_id, lat, lon, source = self.history.pop()
        for r in self.records:
            if r['id'] == photo_id:
                r.update(lat=lat, lon=lon, source=source); break
        self.rebuild_layer(); self.refresh_list(); self.show_photo(); self.autosave()

    def save_work(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Salva sessione (include foto senza posizione)', self.session or '', 'MIC_FOTO (*.micfoto.json)')
        if not path:
            return
        if not path.endswith('.micfoto.json'):
            path += '.micfoto.json'
        self.session = path
        if self.autosave():
            self.status.setText('Lavoro salvato. Le modifiche successive saranno salvate automaticamente in questo file.')

    def autosave(self):
        if not self.session:
            return False
        try:
            tmp = Path(self.session + '.tmp')
            tmp.write_text(json.dumps(dict(format='MIC_FOTO', version=1, photos=self.records), ensure_ascii=False, indent=2), encoding='utf-8')
            os.replace(str(tmp), self.session)
            return True
        except Exception as exc:
            QMessageBox.warning(self, 'Salvataggio non riuscito', str(exc)); return False

    def open_work(self):
        if self.records:
            if QMessageBox.question(self, 'Apri lavoro', 'Sostituire l’elenco attuale? Salva prima il lavoro se necessario.', QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                return
        path, _ = QFileDialog.getOpenFileName(self, 'Apri sessione', '', 'MIC_FOTO (*.micfoto.json)')
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding='utf-8'))
            if data.get('format') != 'MIC_FOTO' or data.get('version') != 1:
                raise ValueError('Formato di sessione non riconosciuto')
            records = data['photos']
            keys = {'id', 'path', 'lat', 'lon', 'source', 'date', 'error'}
            if not isinstance(records, list) or any(not isinstance(r, dict) or not keys.issubset(r) for r in records):
                raise ValueError('Elenco foto non valido')
            self.stop_tool(); self.records = records; self.session = path; self.history = []
            self.rebuild_layer(); self.refresh_list()
        except Exception as exc:
            QMessageBox.warning(self, 'Apertura', str(exc))

    def export(self):
        if not self.records:
            return
        path, _ = QFileDialog.getSaveFileName(self, 'Nuovo GeoPackage', '', 'GeoPackage (*.gpkg)')
        if not path:
            return
        if not path.lower().endswith('.gpkg'):
            path += '.gpkg'
        if Path(path).exists():
            QMessageBox.warning(self, 'Esportazione', 'Scegli un nome nuovo: questa versione non sovrascrive GeoPackage esistenti.'); return
        self.rebuild_layer()
        opt = QgsVectorFileWriter.SaveVectorOptions()
        opt.driverName = 'GPKG'; opt.layerName = 'foto'; opt.fileEncoding = 'UTF-8'
        result = QgsVectorFileWriter.writeAsVectorFormatV3(self.layer, path, QgsProject.instance().transformContext(), opt)
        if result[0] != QgsVectorFileWriter.NoError:
            QMessageBox.warning(self, 'Esportazione', str(result)); return
        saved = QgsVectorLayer(path + '|layername=foto', 'MIC_FOTO — salvato', 'ogr')
        if saved.isValid():
            QgsProject.instance().addMapLayer(saved)
        QMessageBox.information(self, 'GeoPackage salvato', 'Esportati tutti i record. Le foto senza posizione hanno geometria nulla.\nGli originali non sono stati modificati.\nPer riprendere le modifiche usa anche Salva lavoro.')

    def write_copies(self):
        positioned = [r for r in self.records if r['lat'] is not None]
        if not positioned:
            return
        folder = QFileDialog.getExistingDirectory(self, 'Cartella di destinazione delle copie JPG')
        if not folder:
            return
        if QMessageBox.question(self, 'Scrivi GPS nelle copie', f'Creare {len(positioned)} copie con GPS? Gli originali non saranno modificati.\nI nomi esistenti saranno saltati.', QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        import shutil
        report = []
        for r in positioned:
            dest = Path(folder) / Path(r['path']).name
            try:
                if dest.exists():
                    raise ValueError('Nome già presente: saltato')
                with open(r['path'], 'rb') as src, dest.open('xb') as dst:
                    shutil.copyfileobj(src, dst)
                if not QgsExifTools.geoTagImage(str(dest), QgsPointXY(r['lon'], r['lat'])):
                    raise ValueError('Scrittura GPS non riuscita: copia da controllare')
                point, ok = QgsExifTools.getGeoTag(str(dest))
                if not ok or abs(point.y()-r['lat']) > 0.00001 or abs(point.x()-r['lon']) > 0.00001:
                    raise ValueError('Verifica GPS fallita: copia da controllare')
                status = 'OK: GPS scritto e verificato'
            except Exception as exc:
                status = str(exc)
            report.append(dict(source=r['path'], destination=str(dest), result=status))
        report_path = Path(folder) / ('MIC_FOTO_report_' + uuid.uuid4().hex[:8] + '.json')
        try:
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        except OSError as exc:
            QMessageBox.warning(self, 'Rapporto', str(exc)); return
        n = sum(r['result'].startswith('OK:') for r in report)
        QMessageBox.information(self, 'Scrittura completata', f'{n}/{len(report)} copie verificate.\nRapporto: {report_path}')

    def closeEvent(self, event):
        self.stop_tool()
        if self.records and not self.session:
            answer = QMessageBox.question(self, 'MIC_FOTO', 'Il lavoro non ha un file di sessione. Chiudere il pannello?\nIl lavoro resta in memoria solo finché QGIS e il plugin rimangono aperti.', QMessageBox.Yes | QMessageBox.No)
            if answer != QMessageBox.Yes:
                event.ignore(); return
        if self.session and not self.autosave():
            event.ignore(); return
        super().closeEvent(event)


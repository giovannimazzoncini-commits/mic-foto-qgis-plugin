# SPDX-License-Identifier: GPL-3.0-or-later
from functools import wraps
from pathlib import Path
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QToolBar
from qgis.core import (QgsMarkerSymbol, QgsRuleBasedRenderer, QgsProject,
    QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsPointXY)
from qgis.gui import QgsVertexMarker
from .gallery import Plugin as GalleryPlugin, Gallery
from .viewer import Panel
from .lifecycle import alive


def apply_style(layer):
    root = QgsRuleBasedRenderer.Rule(None)
    for shape, color, expression, label in (
        ('circle', '#187F86', 'coalesce("source", \'\') <> \'manual\'', 'Posizione EXIF / da layer'),
        ('diamond', '#EE8A32', '"source" = \'manual\'', 'Posizione manuale')):
        symbol = QgsMarkerSymbol.createSimple(dict(name=shape, color=color,
            outline_color='#FFFFFF', outline_style='solid', outline_width='0.4',
            size='3.4' if shape == 'diamond' else '3.0'))
        rule = QgsRuleBasedRenderer.Rule(symbol)
        rule.setFilterExpression(expression)
        rule.setLabel(label)
        root.appendChild(rule)
    layer.setRenderer(QgsRuleBasedRenderer(root))
    layer.triggerRepaint()


def update_marker(panel, *args):
    rings = getattr(panel, '_photo_rings', [])
    if not alive(panel):
        return
    record = panel.current()
    if not panel.isVisible() or not record or record['lat'] is None or not alive(panel.layer):
        for marker in rings:
            if alive(marker):
                marker.hide()
        return
    canvas = panel.iface.mapCanvas()
    if not rings or any(not alive(marker) for marker in rings):
        rings = []
        for size, color, width in ((25, '#FFFFFF', 5), (23, '#EE8A32', 2)):
            marker = QgsVertexMarker(canvas)
            marker.setIconType(QgsVertexMarker.ICON_CIRCLE)
            marker.setIconSize(size)
            marker.setColor(QColor(color))
            marker.setFillColor(QColor(0, 0, 0, 0))
            marker.setPenWidth(width)
            marker.setZValue(10000)
            rings.append(marker)
        panel._photo_rings = rings
    transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'),
        canvas.mapSettings().destinationCrs(), QgsProject.instance())
    point = transform.transform(QgsPointXY(record['lon'], record['lat']))
    for marker in rings:
        marker.setCenter(point)
        marker.show()


_original_rebuild = Panel.rebuild_layer
_original_sync = Panel.sync_selection
_original_export = Panel.export


@wraps(_original_rebuild)
def rebuild(panel, *args):
    result = _original_rebuild(panel, *args)
    if alive(panel.layer):
        apply_style(panel.layer)
    return result


@wraps(_original_sync)
def sync(panel, *args):
    result = _original_sync(panel, *args)
    update_marker(panel)
    return result


@wraps(_original_export)
def export(panel, *args):
    project = QgsProject.instance()
    previous = set(project.mapLayers())
    result = _original_export(panel, *args)
    for layer_id, layer in project.mapLayers().items():
        if layer_id in previous or not hasattr(layer, 'fields'):
            continue
        if layer.providerType() == 'ogr' and 'photo_id' in layer.fields().names():
            apply_style(layer)
            try:
                error = layer.saveStyleToDatabase('MIC_FOTO', 'MIC_FOTO 0.2.3', True, '')
                if error:
                    panel.status.setText('GeoPackage esportato, ma stile non salvato: ' + str(error))
            except Exception as exc:
                panel.status.setText('GeoPackage esportato, ma stile non salvato: ' + str(exc))
    return result


Panel.rebuild_layer = rebuild
Panel.sync_selection = sync
Panel.export = export
_original_gallery_refresh = Gallery.refresh


@wraps(_original_gallery_refresh)
def gallery_refresh(dialog):
    _original_gallery_refresh(dialog)
    dialog.setWindowTitle(dialog.windowTitle().replace('MIC_FOTO 0.2.2', 'MIC_FOTO 0.2.3', 1))


Gallery.refresh = gallery_refresh


class Plugin(GalleryPlugin):
    def initGui(self):
        super().initGui()
        icon = QIcon(str(Path(__file__).with_name('icon.svg')))
        self.action.setIcon(icon)
        self.action.setToolTip('MIC_FOTO — Gestisci e consulta le foto di sopralluogo')
        self.action.setStatusTip('Importa, posiziona e consulta fotografie sulla mappa')
        for toolbar in self.iface.mainWindow().findChildren(QToolBar):
            button = toolbar.widgetForAction(self.action)
            if button is not None and hasattr(button, 'setToolButtonStyle'):
                button.setToolButtonStyle(Qt.ToolButtonIconOnly)

    def run(self):
        super().run()
        panel = self.panel
        panel.setWindowTitle('MIC_FOTO 0.2.3 — sperimentale')
        panel.setWindowIcon(self.action.icon())
        if not hasattr(panel, '_marker_crs_slot'):
            panel._marker_crs_slot = lambda *args: update_marker(panel)
            self.iface.mapCanvas().destinationCrsChanged.connect(panel._marker_crs_slot)
            panel.visibilityChanged.connect(panel._marker_crs_slot)
        if alive(panel.layer):
            apply_style(panel.layer)
        update_marker(panel)

    def unload(self):
        panel = self.panel
        if alive(panel):
            slot = getattr(panel, '_marker_crs_slot', None)
            if slot is not None:
                try:
                    self.iface.mapCanvas().destinationCrsChanged.disconnect(slot)
                except (RuntimeError, TypeError):
                    pass
            for marker in getattr(panel, '_photo_rings', []):
                if alive(marker):
                    marker.hide()
                    self.iface.mapCanvas().scene().removeItem(marker)
            panel._photo_rings = []
        super().unload()

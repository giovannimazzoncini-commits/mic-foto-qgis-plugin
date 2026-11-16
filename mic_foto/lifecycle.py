# SPDX-License-Identifier: GPL-3.0-or-later
from functools import wraps
from qgis.PyQt import sip
from qgis.PyQt.QtCore import Qt
from .viewer import Plugin as ViewerPlugin, Panel


def alive(obj):
    return obj is not None and not sip.isdeleted(obj)


def prune(panel):
    for name in ('layer', 'external', 'tool', 'previous_tool'):
        obj = getattr(panel, name, None)
        if obj is not None and not alive(obj):
            setattr(panel, name, None)
            if name == 'external':
                panel.external_ids = {}


def guarded(method):
    @wraps(method)
    def call(self, *args, **kwargs):
        prune(self)
        if method.__name__ in ('browse', 'link_layer', 'stop_tool', 'export'):
            if len(args) == 1 and isinstance(args[0], bool):
                args = ()
        return method(self, *args, **kwargs)
    return call


for name in ('rebuild_layer', 'sync_selection', 'from_map', 'external_selected',
             'disconnect_external', 'stop_tool', 'closeEvent', 'browse', 'link_layer', 'export'):
    setattr(Panel, name, guarded(getattr(Panel, name)))


class Plugin(ViewerPlugin):
    def run(self):
        if self.panel is not None and not alive(self.panel):
            self.panel = None
        if self.panel is not None:
            prune(self.panel)
        super().run()
        self.panel.setWindowTitle('MIC_FOTO 0.2.1 — sperimentale')

    def unload(self):
        if self.panel is not None:
            if alive(self.panel):
                prune(self.panel)
            else:
                self.panel = None
        super().unload()
        self.panel = None

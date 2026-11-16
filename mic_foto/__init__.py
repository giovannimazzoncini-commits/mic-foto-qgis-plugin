# SPDX-License-Identifier: GPL-3.0-or-later
def classFactory(iface):
    from .panel_style import Plugin
    return Plugin(iface)

# SPDX-License-Identifier: GPL-3.0-or-later
def classFactory(iface):
    from .viewer import Plugin
    return Plugin(iface)

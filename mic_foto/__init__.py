# SPDX-License-Identifier: GPL-3.0-or-later
def classFactory(iface):
    from .direct_layer import Plugin
    return Plugin(iface)

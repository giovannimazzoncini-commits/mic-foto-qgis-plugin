# SPDX-License-Identifier: GPL-3.0-or-later
def classFactory(iface):
    from .branding import Plugin
    return Plugin(iface)

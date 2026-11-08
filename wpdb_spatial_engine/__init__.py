"""
QGIS Plugin initialization package for WPDB Spatial Engine.

Author: Md Abu Sayem Sarker
Email: mdabusayemsarker9@gmail.com
License: MIT
"""


def classFactory(iface):
    """
    QGIS Plugin entry point.
    Loads and instantiates WPDBPlugin with the QGIS interface reference.
    """
    from .plugin import WPDBPlugin
    return WPDBPlugin(iface)


"""
Main QGIS Plugin lifecycle class for WPDB Spatial Engine.

Author: Md Abu Sayem Sarker
Data Scientist & GeoAI Researcher
"""

import os
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .ui.wpdb_dialog import WPDBDialog


class WPDBPlugin:
    """QGIS Plugin implementation for WPDB Spatial Engine."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.dialog = None

    def initGui(self):
        """Create menu entry and toolbar icon inside QGIS."""
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

        self.action = QAction(
            icon,
            "WPDB Spatial Engine",
            self.iface.mainWindow() if self.iface else None
        )
        self.action.setStatusTip("Launch WPDB Spatial Engine (Riverine Non-Water Extractor & Dilution Bias Auditor)")
        self.action.triggered.connect(self.run)

        if self.iface:
            self.iface.addToolBarIcon(self.action)
            self.iface.addPluginToMenu("&WPDB Spatial Engine", self.action)

    def unload(self):
        """Remove menu entry and toolbar icon from QGIS interface."""
        if self.iface and self.action:
            self.iface.removeToolBarIcon(self.action)
            self.iface.removePluginMenu("&WPDB Spatial Engine", self.action)
            del self.action

    def run(self):
        """Launch the main WPDB-Corrector dialog."""
        if not self.dialog:
            self.dialog = WPDBDialog(iface=self.iface)
        self.dialog.show()
        return self.dialog.exec()

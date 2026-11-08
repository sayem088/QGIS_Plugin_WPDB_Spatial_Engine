"""
Tests for QGIS Plugin metadata compliance and UI resources.
Author: Md Abu Sayem Sarker
"""

import configparser
import os
import xml.etree.ElementTree as ET
from PIL import Image


PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "..")


def test_metadata_compliance():
    """Verify that metadata.txt follows the official QGIS 3 plugin specification."""
    meta_path = os.path.join(PLUGIN_DIR, "metadata.txt")
    assert os.path.exists(meta_path), "metadata.txt missing!"

    config = configparser.ConfigParser()
    config.read(meta_path, encoding="utf-8")

    assert "general" in config.sections(), "metadata.txt missing [general] section"
    general = config["general"]

    required_keys = [
        "name",
        "qgisMinimumVersion",
        "description",
        "about",
        "version",
        "author",
        "email",
        "repository",
    ]

    for key in required_keys:
        assert key in general, f"Missing required metadata key: {key}"
        assert len(general[key].strip()) > 0, f"Metadata key {key} is empty"

    # Verify single authorship
    assert general["author"] == "Md Abu Sayem Sarker"
    assert general["email"] == "mdabusayemsarker9@gmail.com"
    assert general["name"] == "WPDB Spatial Engine"
    assert general["repository"] == "https://github.com/sayem088/QGIS_Plugin_WPDB_Spatial_Engine"


def test_plugin_icon():
    """Verify icon.png exists and is a valid square image."""
    icon_path = os.path.join(PLUGIN_DIR, "icon.png")
    assert os.path.exists(icon_path), "icon.png missing!"

    with Image.open(icon_path) as img:
        assert img.width == img.height, "Icon must be square"
        assert img.width >= 32, "Icon must be at least 32x32"


def test_ui_xml_validity():
    """Verify wpdb_dialog_base.ui is valid Qt Designer XML."""
    ui_path = os.path.join(PLUGIN_DIR, "ui", "wpdb_dialog_base.ui")
    assert os.path.exists(ui_path), "wpdb_dialog_base.ui missing!"

    tree = ET.parse(ui_path)
    root = tree.getroot()
    assert root.tag == "ui", "Root element must be <ui>"

    # Check key widgets exist
    widget_names = [w.attrib.get("name") for w in root.iter("widget")]
    # 4 Dedicated Tabs
    assert "tabCorridor" in widget_names
    assert "tabTable" in widget_names
    assert "tabCloudGEE" in widget_names
    assert "tabAbout" in widget_names

    # Tab 1 widgets
    assert "btnRunCorridorExtraction" in widget_names
    assert "comboStationLayer" in widget_names
    assert "comboCenterlineLayer" in widget_names

    # Tab 2 widgets
    assert "btnBrowseInput" in widget_names
    assert "comboWaterCol" in widget_names
    assert "comboTargetCol" in widget_names
    assert "btnRunCorrection" in widget_names
    assert "tablePreview" in widget_names
    assert "textReport" in widget_names

    # Tab 3 widgets
    assert "btnRunGeePipeline" in widget_names
    assert "btnAuthGee" in widget_names


def test_class_factory_structure():
    """Verify classFactory can be imported and referenced."""
    import wpdb_spatial_engine
    assert hasattr(wpdb_spatial_engine, "classFactory")
    assert callable(wpdb_spatial_engine.classFactory)


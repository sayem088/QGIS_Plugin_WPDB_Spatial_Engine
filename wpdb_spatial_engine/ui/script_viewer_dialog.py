"""
Script Viewer Dialog for WPDB Spatial Engine.

Displays generated Google Earth Engine JavaScript and Python code with
one-click copy to clipboard and file export capabilities.

Author: Md Abu Sayem Sarker | Data Scientist & GeoAI Researcher
Core Domains: GeoAI · Remote Sensing · Machine Learning · Software Engineering
"""

import os

try:
    from qgis.PyQt.QtWidgets import (
        QDialog,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QPlainTextEdit,
        QPushButton,
        QFileDialog,
        QMessageBox,
        QRadioButton,
        QButtonGroup,
        QApplication,
    )
    from qgis.PyQt.QtGui import QFont
    from qgis.PyQt.QtCore import Qt
    HAS_QT = True
except ImportError:
    try:
        from PyQt5.QtWidgets import (
            QDialog,
            QVBoxLayout,
            QHBoxLayout,
            QLabel,
            QPlainTextEdit,
            QPushButton,
            QFileDialog,
            QMessageBox,
            QRadioButton,
            QButtonGroup,
            QApplication,
        )
        from PyQt5.QtGui import QFont
        from PyQt5.QtCore import Qt
        HAS_QT = True
    except ImportError:
        HAS_QT = False
        class QDialog:
            pass


class GEEScriptViewerDialog(QDialog):
    """Dialog for viewing and exporting generated Google Earth Engine scripts."""

    def __init__(self, js_code: str, py_code: str, parent=None):
        if not HAS_QT:
            return
        super(GEEScriptViewerDialog, self).__init__(parent)
        self.js_code = js_code
        self.py_code = py_code

        self.setWindowTitle("Google Earth Engine Cloud Script Generator")
        self.resize(850, 600)

        # Apply dark slate theme if style.qss exists
        try:
            qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
            if os.path.exists(qss_path):
                with open(qss_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
        except Exception:
            pass

        layout = QVBoxLayout(self)

        # Header Info
        header = QLabel(
            "<h3>Google Earth Engine (GEE) Production Script Generator</h3>"
            "<span>Generated cloud pipeline implementing JRC Centerline, Dynamic World 10m LULC, "
            "and Non-Water Inversion. Copy into the <b>GEE Code Editor</b> or save as standalone script.</span>"
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        # Radio buttons for format selection
        h_format = QHBoxLayout()
        self.radio_js = QRadioButton("GEE JavaScript (for code.earthengine.google.com)")
        self.radio_py = QRadioButton("GEE Python (for headless / batch runner)")
        self.radio_js.setChecked(True)

        self.btn_group = QButtonGroup(self)
        self.btn_group.addButton(self.radio_js)
        self.btn_group.addButton(self.radio_py)

        self.radio_js.toggled.connect(self._on_format_changed)

        h_format.addWidget(self.radio_js)
        h_format.addWidget(self.radio_py)
        h_format.addStretch()
        layout.addLayout(h_format)

        # Text Editor
        self.text_editor = QPlainTextEdit(self)
        self.text_editor.setReadOnly(True)
        font = QFont("Consolas", 10)
        self.text_editor.setFont(font)
        self.text_editor.setPlainText(self.js_code)
        layout.addWidget(self.text_editor)

        # Bottom Buttons
        h_buttons = QHBoxLayout()
        self.btn_copy = QPushButton("📋 Copy Script to Clipboard")
        self.btn_copy.setStyleSheet("font-weight: bold; background-color: #0284c7; color: white; padding: 6px 14px;")
        self.btn_copy.clicked.connect(self.copy_to_clipboard)

        self.btn_save = QPushButton("💾 Save Script File...")
        self.btn_save.setStyleSheet("padding: 6px 14px;")
        self.btn_save.clicked.connect(self.save_script_file)

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)

        h_buttons.addWidget(self.btn_copy)
        h_buttons.addWidget(self.btn_save)
        h_buttons.addStretch()
        h_buttons.addWidget(self.btn_close)
        layout.addLayout(h_buttons)

    def _on_format_changed(self):
        """Switches between JavaScript and Python display."""
        if self.radio_js.isChecked():
            self.text_editor.setPlainText(self.js_code)
        else:
            self.text_editor.setPlainText(self.py_code)

    def copy_to_clipboard(self):
        """Copies current script content to system clipboard."""
        text = self.text_editor.toPlainText()
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)
            QMessageBox.information(
                self, "Copied",
                "Script copied to clipboard successfully!\nYou can now paste it directly into code.earthengine.google.com"
            )

    def save_script_file(self):
        """Saves current script content to a .js or .py file."""
        is_js = self.radio_js.isChecked()
        ext = "JavaScript Files (*.js)" if is_js else "Python Files (*.py)"
        default_name = "wpdb_gee_pipeline.js" if is_js else "wpdb_gee_pipeline.py"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Earth Engine Script", default_name, f"{ext};;All Files (*)"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.text_editor.toPlainText())
            QMessageBox.information(self, "Saved", f"Script saved successfully to:\n{file_path}")


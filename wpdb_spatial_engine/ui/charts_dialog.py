"""
Scientific Charts Dialog for WPDB-Corrector.
Displays publication-ready figures embedded directly within QGIS.

Author: Md Abu Sayem Sarker
Data Scientist & GeoAI Researcher
"""

import logging
import os
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)

try:
    from qgis.PyQt.QtWidgets import (
        QDialog,
        QVBoxLayout,
        QHBoxLayout,
        QPushButton,
        QLabel,
        QFileDialog,
        QMessageBox,
        QRadioButton,
        QButtonGroup,
    )
    from qgis.PyQt.QtCore import Qt
except ImportError:
    QDialog = object

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
except ImportError:
    try:
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
    except ImportError:
        FigureCanvasQTAgg = None
        NavigationToolbar2QT = None

from ..core.visualizer import (
    create_theoretical_curve_plot,
    create_before_after_comparison_plot,
    create_combined_audit_figure,
    export_figure,
)


class WPDBChartsDialog(QDialog):
    """Interactive visual analytics window for WPDB bias diagnostics."""

    def __init__(self, df: pd.DataFrame, parent=None):
        super(WPDBChartsDialog, self).__init__(parent)
        self.df = df.copy()
        self.current_figure = None
        self.canvas = None
        self.toolbar = None

        self.setWindowTitle("WPDB Spatial Engine: Diagnostic Visualizations")
        self.resize(960, 620)

        # Apply dark slate theme if style.qss exists
        try:
            qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
            if os.path.exists(qss_path):
                with open(qss_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
        except (OSError, IOError) as err:
            logger.debug("Failed to load style.qss: %s", err)

        self._detect_plot_columns()
        self._build_ui()
        self._render_current_plot()

    def _detect_plot_columns(self):
        """Identifies column names for water, naive, corrected, and bias metrics."""
        cols = self.df.columns

        self.water_col = [c for c in cols if "water" in c.lower()][0] if any("water" in c.lower() for c in cols) else cols[0]
        self.naive_col = [c for c in cols if "naive" in c.lower()][0] if any("naive" in c.lower() for c in cols) else cols[1]
        
        corr_candidates = [c for c in cols if "corrected" in c.lower() or "nonwater" in c.lower()]
        self.corr_col = corr_candidates[0] if corr_candidates else self.naive_col

        bias_candidates = [c for c in cols if "bias" in c.lower()]
        self.bias_col = bias_candidates[0] if bias_candidates else cols[0]

        st_candidates = [c for c in cols if "station" in c.lower() or "id" in c.lower()]
        self.st_col = st_candidates[0] if st_candidates else cols[0]

    def _build_ui(self):
        """Constructs layout, radio selectors, matplotlib canvas, and export controls."""
        main_layout = QVBoxLayout(self)

        # Header bar with chart selection
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("<b>Select Scientific Figure:</b>"))

        self.radio_group = QButtonGroup(self)
        self.radio_composite = QRadioButton("Composite 2-Panel (IEEE Format)")
        self.radio_curve = QRadioButton("Theorem 1 Invariance Curve")
        self.radio_bars = QRadioButton("Before vs. After Urbanization")

        self.radio_composite.setChecked(True)
        self.radio_group.addButton(self.radio_composite, 0)
        self.radio_group.addButton(self.radio_curve, 1)
        self.radio_group.addButton(self.radio_bars, 2)

        top_bar.addWidget(self.radio_composite)
        top_bar.addWidget(self.radio_curve)
        top_bar.addWidget(self.radio_bars)
        top_bar.addStretch()

        self.radio_group.buttonClicked.connect(self._on_chart_selection_changed)
        main_layout.addLayout(top_bar)

        # Plot canvas container layout
        self.plot_container = QVBoxLayout()
        main_layout.addLayout(self.plot_container, stretch=1)

        # Bottom export toolbar
        bottom_bar = QHBoxLayout()
        bottom_bar.addWidget(QLabel("DPI Quality:"))
        self.combo_dpi = QComboBox()
        self.combo_dpi.addItems(["300 DPI (Publication Standard)", "600 DPI (High Resolution)", "150 DPI (Screen Web)"])
        bottom_bar.addWidget(self.combo_dpi)

        self.btn_export = QPushButton("💾 Save Figure for Paper...")
        self.btn_export.setStyleSheet("font-weight: bold; padding: 6px 14px; background-color: #1976D2; color: white;")
        self.btn_export.clicked.connect(self.export_current_figure)
        bottom_bar.addWidget(self.btn_export)

        bottom_bar.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        bottom_bar.addWidget(btn_close)

        main_layout.addLayout(bottom_bar)

    def _on_chart_selection_changed(self):
        """Handles switching between chart modes."""
        self._render_current_plot()

    def _render_current_plot(self):
        """Generates the selected figure and embeds it into the dialog canvas."""
        if FigureCanvasQTAgg is None:
            return

        selected_id = self.radio_group.checkedId()

        if selected_id == 1:
            self.current_figure = create_theoretical_curve_plot(
                self.df,
                water_col=self.water_col,
                naive_col=self.naive_col,
                bias_col=self.bias_col,
                station_col=self.st_col
            )
        elif selected_id == 2:
            self.current_figure = create_before_after_comparison_plot(
                self.df,
                station_col=self.st_col,
                naive_col=self.naive_col,
                corr_col=self.corr_col
            )
        else:
            self.current_figure = create_combined_audit_figure(
                self.df,
                water_col=self.water_col,
                naive_col=self.naive_col,
                corr_col=self.corr_col,
                bias_col=self.bias_col,
                station_col=self.st_col
            )

        # Remove old canvas and toolbar if present
        if self.canvas is not None:
            self.plot_container.removeWidget(self.canvas)
            self.canvas.deleteLater()
            self.canvas = None

        if self.toolbar is not None:
            self.plot_container.removeWidget(self.toolbar)
            self.toolbar.deleteLater()
            self.toolbar = None

        self.canvas = FigureCanvasQTAgg(self.current_figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.plot_container.addWidget(self.toolbar)
        self.plot_container.addWidget(self.canvas)
        self.canvas.draw()

    def export_current_figure(self):
        """Exports current figure to file selected by user."""
        if self.current_figure is None:
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Publication Figure",
            "wpdb_scientific_audit_figure.png",
            "PNG Images (*.png);;PDF Documents (*.pdf);;SVG Vector (*.svg);;All Files (*)"
        )
        if save_path:
            dpi_map = {0: 300, 1: 600, 2: 150}
            dpi = dpi_map.get(self.combo_dpi.currentIndex(), 300)
            try:
                export_figure(self.current_figure, save_path, dpi=dpi)
                QMessageBox.information(
                    self, "Figure Saved",
                    f"Publication figure exported successfully at {dpi} DPI:\n{save_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Could not save figure:\n{str(e)}")


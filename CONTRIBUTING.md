# Contributing to WPDB Spatial Engine

Thank you for your interest in contributing to **WPDB Spatial Engine**! We welcome contributions from hydrologists, GIS practitioners, data scientists, and software engineers.

## Code of Conduct
We are committed to providing a friendly, safe, and welcoming environment for all participants. Please be respectful and considerate in your communications and interactions.

## How to Contribute

### Reporting Bugs and Requesting Features
1. Check the existing [GitHub Issues](https://github.com/sayem088/QGIS_Plugin_WPDB_Spatial_Engine/issues) to ensure the bug or feature hasn't already been reported.
2. If opening a new issue, clearly describe:
   - The operating system and QGIS version (e.g., Windows 11, QGIS 3.34 / QGIS 4.x).
   - Python version and environment dependencies.
   - Exact steps to reproduce the issue with sample inputs if possible.
   - Expected behavior vs. actual behavior (including stack traces).

### Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/sayem088/QGIS_Plugin_WPDB_Spatial_Engine.git
   cd QGIS_Plugin_WPDB_Spatial_Engine
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Run the automated test suite:
   ```bash
   pytest tests/ -v
   ```

### Code Style and Standards
- **Python 3 / PyQt Compliance:** All GUI components must import exclusively from `qgis.PyQt` (`qgis.PyQt.QtWidgets`, `qgis.PyQt.QtCore`, `qgis.PyQt.QtGui`). Never import directly from `PyQt5` or `PyQt6`.
- **Modern Qt Lifecycle:** Use `dialog.exec()` instead of the legacy `exec_()`.
- **Security & Bandit Compliance:** Ensure that exception blocks contain explicit handling or logging (`logger.debug(...)`). Avoid empty `except: pass` blocks (Bandit B110).
- **Flake8 & Pyflakes:** All pull requests must pass static analysis without undefined variables or unused imports.

### Submitting Pull Requests
1. Fork the repository and create a new feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Write unit tests for new functionality in `tests/`.
3. Verify that all existing and new unit tests pass:
   ```bash
   pytest tests/ -v
   ```
4. Commit your changes with clear, descriptive commit messages.
5. Push to your fork and submit a Pull Request to the `main` branch.

## Contact
For research collaboration, inquiries, or bug reports:
- **Lead Author & Maintainer:** Md Abu Sayem Sarker ([mdabusayemsarker9@gmail.com](mailto:mdabusayemsarker9@gmail.com))
- **GitHub Repository:** [https://github.com/sayem088/QGIS_Plugin_WPDB_Spatial_Engine](https://github.com/sayem088/QGIS_Plugin_WPDB_Spatial_Engine)


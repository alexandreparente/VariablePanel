# coding=utf-8
"""DockWidget test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = "alexandre.parente@gmail.com"
__date__ = "2024-11-16"
__copyright__ = "Copyright 2024, Alexandre Parente Lima"

import unittest
from unittest.mock import MagicMock, patch

from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()

# Patch iface inside the dockwidget module before it is imported,
# so the module-level `from qgis.utils import iface` gets our mock.
_mock_iface = MagicMock()
_mock_iface.activeLayer.return_value = None

with patch("qgis.utils.iface", _mock_iface):
    from variable_panel_dockwidget import VariablePanelDockWidget


class VariablePanelDockWidgetTest(unittest.TestCase):
    """Test dockwidget works."""

    def setUp(self):
        """Runs before each test."""
        with patch("variable_panel_dockwidget.iface", _mock_iface):
            self.dockwidget = VariablePanelDockWidget(None)

    def tearDown(self):
        """Runs after each test."""
        self.dockwidget = None

    def test_dockwidget_ok(self):
        """Test dockwidget instantiates without errors."""
        self.assertIsNotNone(self.dockwidget)

    def test_window_title(self):
        """Test the dockwidget has the correct window title."""
        self.assertEqual(self.dockwidget.windowTitle(), "Variables")


if __name__ == "__main__":
    suite = unittest.makeSuite(VariablePanelDockWidgetTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

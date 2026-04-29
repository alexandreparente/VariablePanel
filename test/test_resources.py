# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = "alexandre.parente@gmail.com"
__date__ = "2024-11-16"
__copyright__ = "Copyright 2024, Alexandre Parente Lima"

import os
import unittest

from qgis.PyQt.QtGui import QIcon

from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class VariablePanelDialogTest(unittest.TestCase):
    """Test resources work."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_icon_exists(self):
        """Test that the SVG icon file exists on disk."""
        icon_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "mIconExpression.svg")
        )
        self.assertTrue(os.path.isfile(icon_path), f"Icon not found: {icon_path}")

    def test_icon_loads(self):
        """Test that QIcon loads the SVG without producing a null icon."""
        icon_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "mIconExpression.svg")
        )
        icon = QIcon(icon_path)
        self.assertFalse(icon.isNull(), f"QIcon is null for: {icon_path}")


if __name__ == "__main__":
    suite = unittest.makeSuite(VariablePanelDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

# coding=utf-8
"""Translation tests for VariablePanel plugin.

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

from qgis.PyQt.QtCore import QCoreApplication, QTranslator

from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()

I18N_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "i18n"))


class TranslationsTest(unittest.TestCase):
    """Test that plugin translation files exist and load correctly."""

    def _load_qm(self, filename):
        """Helper: load a .qm file and return the translator, or None if file missing."""
        path = os.path.join(I18N_DIR, filename)
        if not os.path.isfile(path):
            return None
        translator = QTranslator()
        translator.load(path)
        return translator

    def test_i18n_directory_exists(self):
        """The i18n directory exists in the plugin root."""
        self.assertTrue(os.path.isdir(I18N_DIR), f"i18n dir not found: {I18N_DIR}")

    def test_qm_files_exist(self):
        """At least one compiled .qm translation file is present."""
        qm_files = [f for f in os.listdir(I18N_DIR) if f.endswith(".qm")]
        self.assertTrue(
            len(qm_files) > 0,
            f"No .qm files found in {I18N_DIR}. Run 'python helper.py translate' first.",
        )

    def test_pt_br_loads(self):
        """Brazilian Portuguese .qm file loads without errors."""
        translator = self._load_qm("VariablePanel_pt_BR.qm")
        if translator is None:
            self.skipTest("VariablePanel_pt_BR.qm not found — run translate first.")
        # Installing a translator should not raise
        QCoreApplication.installTranslator(translator)
        QCoreApplication.removeTranslator(translator)

    def test_en_loads(self):
        """English .qm file loads without errors."""
        translator = self._load_qm("VariablePanel_en.qm")
        if translator is None:
            self.skipTest("VariablePanel_en.qm not found — run translate first.")
        QCoreApplication.installTranslator(translator)
        QCoreApplication.removeTranslator(translator)


if __name__ == "__main__":
    unittest.main()

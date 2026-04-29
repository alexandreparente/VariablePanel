# coding=utf-8
"""Tests for QGIS environment.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = "tim@linfiniti.com"
__date__ = "20/01/2011"
__copyright__ = "Copyright 2012, Australia Indonesia Facility for Disaster Reduction"

import unittest

from qgis.core import QgsCoordinateReferenceSystem, QgsProviderRegistry

from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class QGISTest(unittest.TestCase):
    """Test the QGIS environment."""

    def test_qgis_environment(self):
        """QGIS environment has the essential providers."""
        providers = QgsProviderRegistry.instance().providerList()
        self.assertIn("gdal", providers)
        self.assertIn("ogr", providers)

    def test_projection(self):
        """QGIS correctly parses a WKT CRS string to EPSG:4326."""
        crs = QgsCoordinateReferenceSystem()
        wkt = (
            'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
            'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
            'PRIMEM["Greenwich",0.0],UNIT["Degree",'
            "0.0174532925199433]]"
        )
        crs.createFromWkt(wkt)
        self.assertEqual(crs.authid(), "EPSG:4326")


if __name__ == "__main__":
    unittest.main()

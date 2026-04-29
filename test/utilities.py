# coding=utf-8
"""Utilities for QGIS tests."""

import os
from unittest.mock import MagicMock

import qgis.utils
from qgis.core import QgsApplication

QGIS_APP = None
IFACE = None


def get_qgis_app():
    """Start one QgsApplication and return it. Returns existing instance if already started."""
    global QGIS_APP, IFACE  # noqa: PLW0603

    if QGIS_APP is None:
        QGIS_APP = QgsApplication([], True)

        if os.environ.get("QGIS_PREFIX_PATH"):
            QGIS_APP.setPrefixPath(os.environ["QGIS_PREFIX_PATH"], True)

        QGIS_APP.initQgis()

        # Build a mock iface and inject it into qgis.utils so that any module
        # that does `from qgis.utils import iface` gets a usable object.
        IFACE = _build_mock_iface()
        qgis.utils.iface = IFACE

    return QGIS_APP


def _build_mock_iface():
    """Return a minimal QgisInterface mock sufficient for the dockwidget tests."""
    mock = MagicMock()

    # layerTreeView().currentLayerChanged needs to be a real signal-like object
    # MagicMock handles .connect() and .disconnect() calls automatically.
    mock.activeLayer.return_value = None

    return mock

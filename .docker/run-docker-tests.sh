#!/usr/bin/env bash
set -e

pip3 install pytest --break-system-packages -q 2>/dev/null || \
    pip3 install pytest --user -q 2>/dev/null || \
    pip3 install pytest -q

export QGIS_PREFIX_PATH=/usr
export PYTHONPATH=/usr/share/qgis/python:$PYTHONPATH

pushd /src

DEFAULT_PARAMS="test/ -v --tb=short"
xvfb-run -s '+extension GLX -screen 0 1024x768x24' pytest ${@:-$DEFAULT_PARAMS}

popd

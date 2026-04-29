#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fnmatch
import glob
import os
import re
import shutil
import subprocess
import sys
import xmlrpc.client
import zipfile
from configparser import ConfigParser
from io import StringIO

# ── Plugin identity ──────────────────────────────────────────────────────────
PLUGIN_NAME = "variable_panel"
PLUGIN_DISPLAY = "VariablePanel"

# ── QGIS Docker image tags ───────────────────────────────────────────────────
QGIS_TEST_VERSION = "latest"
QGIS_MINIMUM_VERSION = "release-3_34"
QGIS_MAXIMUM_VERSION = "latest"

# NOTE: This repo uses a FLAT structure — plugin files live at the repo root,
# not inside a variable_panel/ subfolder. All functions below account for this.
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Container path where QGIS loads plugins
CONTAINER_PLUGIN_PATH = (
    f"/root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/{PLUGIN_NAME}"
)

# Files/patterns to exclude from the zip package
PACKAGE_EXCLUDES = {
    "test",
    ".git",
    ".venv",
    ".github",
    ".idea",
    ".ruff_cache",
    ".pre-commit-config.yaml",
    "screenshot",
    "pb_tool.cfg",
    "Makefile",
    "helper.py",
    "pytest.ini",
    "README.md",
    "*.pyc",
    "__pycache__",
    "metadata.txt",
    ".*",
}


# ── translate ────────────────────────────────────────────────────────────────


def translate(locale=None):
    """
    Update translation sources (.ts) and compile them to .qm files.

    :param locale: Locale to process (e.g., 'en', 'pt_BR').
                   Omit to process all locales.

    Examples:
      python helper.py translate
      python helper.py translate pt_BR
    """
    print("Updating translation files...")

    i18n_dir = os.path.join(REPO_ROOT, "i18n")

    if locale:
        ts_files = glob.glob(os.path.join(i18n_dir, f"{PLUGIN_DISPLAY}_{locale}.ts"))
        if not ts_files:
            print(f"Error: No .ts file found for locale '{locale}' in {i18n_dir}")
            return
    else:
        ts_files = glob.glob(os.path.join(i18n_dir, f"{PLUGIN_DISPLAY}_*.ts"))

    if not ts_files:
        print(f"Error: No .ts files found in {i18n_dir}")
        return

    # Plugin Python sources are at the repo root
    source_files = sorted(glob.glob(os.path.join(REPO_ROOT, "*.py")))

    try:
        if source_files:
            subprocess.run(
                ["pylupdate5", "-noobsolete"] + source_files + ["-ts"] + ts_files,
                check=True,
            )
        subprocess.run(["lrelease"] + ts_files, check=True)
        print(f"Success: {len(ts_files)} translation file(s) updated.")

    except FileNotFoundError as e:
        print(f"Error: '{e.filename}' not found. Install Qt tools first.")
    except subprocess.CalledProcessError as e:
        print(f"Error during translation process: {e}")


# ── run_tests ────────────────────────────────────────────────────────────────


def run_tests(qgis_version=QGIS_TEST_VERSION, *pytest_args):
    """
    Run the test suite inside a QGIS Docker container.

    :param qgis_version: Docker tag — 'latest', 'release-3_34', or 'all'.
                         'all' runs QGIS_MINIMUM_VERSION and QGIS_MAXIMUM_VERSION.
    :param pytest_args:  Extra arguments forwarded to pytest.

    Examples:
      python helper.py pytest
      python helper.py pytest release-3_34
      python helper.py pytest all
      python helper.py pytest latest -k test_init -vv
    """
    versions = (
        [QGIS_MINIMUM_VERSION, QGIS_MAXIMUM_VERSION]
        if qgis_version == "all"
        else [qgis_version]
    )

    for version in versions:
        image = f"qgis/qgis:{version}"
        print(f"\n▶  Running tests in Docker ({image}) ...")

        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{REPO_ROOT}:/src",
                "--user",
                f"{os.getuid()}:{os.getgid()}",
                image,
                "bash",
                "/src/.docker/run-docker-tests.sh",
            ]
            + list(pytest_args)
        )

        if result.returncode != 0:
            sys.exit(result.returncode)


# ── pre_commit ───────────────────────────────────────────────────────────────


def pre_commit(scope="all"):
    """
    Run pre-commit hooks.

    :param scope: 'all' to check all files (default), or omit for staged files only.

    Examples:
      python helper.py pre-commit        # staged files only
      python helper.py pre-commit all    # all files in the repo
    """
    cmd = ["pre-commit", "run"]
    if scope == "all":
        cmd.append("--all-files")

    label = "all files" if scope == "all" else "staged files"
    print(f"▶  Running pre-commit on {label} ...")

    result = subprocess.run(cmd, cwd=REPO_ROOT)
    if result.returncode not in (0, 1):  # 1 = hooks fixed/failed (expected)
        sys.exit(result.returncode)


# ── package ──────────────────────────────────────────────────────────────────


def package(version=None):
    """
    Build a distributable .zip ready to install in QGIS.

    Plugin files are at the repo root and will be zipped under variable_panel/.

    :param version: Version string to embed (e.g., '1.2.0').
                    Omit to use the version already in metadata.txt.

    Examples:
      python helper.py package
      python helper.py package 1.2.0
    """
    translate()

    archive = f"{PLUGIN_NAME}.zip" if not version else f"{PLUGIN_NAME}-{version}.zip"
    print(f"Creating {archive} ...")

    metadata_path = os.path.join(REPO_ROOT, "metadata.txt")
    cfg = ConfigParser()
    cfg.optionxform = str
    cfg.read(metadata_path)

    if version:
        cfg.set("general", "version", re.sub(r"^v", "", version))

    buf = StringIO()
    cfg.write(buf)

    def exclude(name):
        return any(fnmatch.fnmatch(name, p) for p in PACKAGE_EXCLUDES)

    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        # metadata.txt always included (possibly with overridden version)
        zf.writestr(f"{PLUGIN_NAME}/metadata.txt", buf.getvalue())

        for root, dirs, files in os.walk(REPO_ROOT):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if not exclude(d)]

            for fname in files:
                if exclude(fname):
                    continue
                abs_path = os.path.join(root, fname)
                rel_to_repo = os.path.relpath(abs_path, REPO_ROOT)
                # Skip metadata.txt — already written above
                if rel_to_repo == "metadata.txt":
                    continue
                zf.write(abs_path, os.path.join(PLUGIN_NAME, rel_to_repo))

    print(f"Build complete: {archive}")


# ── install ──────────────────────────────────────────────────────────────────


def install(qgis_version="3"):
    """
    Install the plugin into your local QGIS profile via symlink (copy on Windows).

    The repo root is linked/copied as variable_panel/ inside the QGIS plugins folder.

    :param qgis_version: '3' or '4' (default: '3').

    Examples:
      python helper.py install
      python helper.py install 4
    """
    qgis_folder = f"QGIS{qgis_version}"

    if os.name == "nt":
        base = f"~/AppData/Roaming/QGIS/{qgis_folder}/profiles/default/python/plugins"
    elif sys.platform == "darwin":
        base = (
            f"~/Library/Application Support/QGIS/{qgis_folder}"
            "/profiles/default/python/plugins"
        )
    else:
        flatpak = os.path.expanduser(
            f"~/.var/app/org.qgis.qgis/data/QGIS/{qgis_folder}/profiles/default/python/plugins"
        )
        base = (
            flatpak
            if os.path.exists(os.path.dirname(flatpak))
            else (f"~/.local/share/QGIS/{qgis_folder}/profiles/default/python/plugins")
        )

    plugins_dir = os.path.expanduser(base)
    os.makedirs(plugins_dir, exist_ok=True)
    dst = os.path.join(plugins_dir, PLUGIN_NAME)

    print(f"Installing to {dst} ...")

    if os.path.exists(dst) or os.path.islink(dst):
        try:
            os.remove(dst)
        except IsADirectoryError:
            shutil.rmtree(dst)

    if hasattr(os, "symlink"):
        os.symlink(REPO_ROOT, dst, target_is_directory=True)
        print("Symlink created — source changes are reflected immediately.")
    else:
        shutil.copytree(REPO_ROOT, dst)
        print("Directory copied.")


# ── publish ──────────────────────────────────────────────────────────────────


def publish(archive):
    """
    Upload the plugin zip to plugins.qgis.org via XML-RPC.

    Requires QGIS_CREDENTIALS=user:password in the environment.

    Example:
      QGIS_CREDENTIALS=myuser:mypass python helper.py publish variable_panel-1.2.0.zip
    """
    try:
        creds = os.environ["QGIS_CREDENTIALS"]
    except KeyError:
        print("Error: QGIS_CREDENTIALS not set (expected 'user:password').")
        sys.exit(2)

    url = f"https://{creds}@plugins.qgis.org/plugins/RPC2/"
    conn = xmlrpc.client.ServerProxy(url)
    print(f"Uploading {archive} to https://plugins.qgis.org ...")
    with open(archive, "rb") as fd:
        conn.plugin.upload(xmlrpc.client.Binary(fd.read()))
    print("Upload complete.")


# ── CLI ──────────────────────────────────────────────────────────────────────


def usage():
    print(
        "Usage:\n"
        f"  {sys.argv[0]} install [3|4]                         Install in local QGIS (default: 3)\n"
        f"  {sys.argv[0]} translate [LOCALE]                    Compile .ts → .qm files\n"
        f"  {sys.argv[0]} pytest [QGIS_VERSION] [PYTEST_ARGS]   Run tests in Docker (default: latest)\n"
        f"  {sys.argv[0]} pre-commit [all]                      Run pre-commit hooks (default: all files)\n"
        f"  {sys.argv[0]} package [VERSION]                     Build {PLUGIN_NAME}.zip\n"
        f"  {sys.argv[0]} publish ARCHIVE                       Upload zip to plugins.qgis.org\n",
        file=sys.stderr,
    )
    sys.exit(2)


args = sys.argv[1:]

if not args:
    usage()
elif args[0] == "install":
    install(*args[1:2])
elif args[0] == "translate":
    translate(*args[1:2])
elif args[0] == "pytest":
    run_tests(*args[1:])
elif args[0] == "pre-commit":
    pre_commit(*args[1:2])
elif args[0] == "package":
    package(*args[1:2])
elif args[0] == "publish" and len(args) == 2:
    publish(args[1])
else:
    usage()

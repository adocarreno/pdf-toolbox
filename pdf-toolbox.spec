# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller build spec for PDF Tool Box.

Local build:
    pyinstaller pdf-toolbox.spec

Output lands in dist/
  macOS  → dist/PDF Tool Box.app   (then packaged into a .dmg by the CI workflow)
  Windows→ dist/PDF Tool Box/      (then zipped by the CI workflow)
  Linux  → dist/PDF Tool Box/      (then tarball'd by the CI workflow)
"""

import sys
from pathlib import Path

IS_MACOS   = sys.platform == "darwin"
IS_WINDOWS = sys.platform == "win32"
IS_LINUX   = sys.platform.startswith("linux")

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    # Entry point
    [str(Path("pdftoolbox") / "app.py")],
    pathex=[str(Path(".").resolve())],
    binaries=[],
    datas=[],
    hiddenimports=[
        # Tool panels are imported at runtime via explicit imports in
        # main_window.py, but list them here as a safety net in case the
        # static analyser misses the side-effect-only imports.
        "pdftoolbox.tools.merger_tool",
        "pdftoolbox.tools.splitter_tool",
        "pdftoolbox.tools.secure_tool",
        "pdftoolbox.tools.unsecure_tool",
        "pdftoolbox.tools.metadata_tool",
        # cryptography backends used by pypdf's AES encryption
        "cryptography.hazmat.primitives.ciphers.algorithms",
        "cryptography.hazmat.primitives.ciphers.modes",
        "cryptography.hazmat.backends.openssl.backend",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Strip heavy packages that we definitely don't use
    excludes=[
        "tkinter", "matplotlib", "numpy", "scipy",
        "pandas", "PIL", "IPython", "jupyter",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

# ---------------------------------------------------------------------------
# Executable
# ---------------------------------------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PDF Tool Box",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No terminal window
    disable_windowed_traceback=False,
    argv_emulation=IS_MACOS,
    # Icon placeholders — replace paths with real .icns / .ico files if desired
    # icon="assets/icon.icns" if IS_MACOS else ("assets/icon.ico" if IS_WINDOWS else None),
)

# ---------------------------------------------------------------------------
# Collect (onedir bundle — faster startup than onefile)
# ---------------------------------------------------------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PDF Tool Box",
)

# ---------------------------------------------------------------------------
# macOS .app bundle
# ---------------------------------------------------------------------------
if IS_MACOS:
    app = BUNDLE(
        coll,
        name="PDF Tool Box.app",
        # icon="assets/icon.icns",
        bundle_identifier="com.pdftoolbox.app",
        info_plist={
            "CFBundleName": "PDF Tool Box",
            "CFBundleDisplayName": "PDF Tool Box",
            "CFBundleVersion": "1.0.0",
            "CFBundleShortVersionString": "1.0.0",
            "NSHighResolutionCapable": True,
            # Allow running on both light and dark mode
            "NSRequiresAquaSystemAppearance": False,
            # Suppress "App is damaged" on unsigned builds opened via Finder
            "LSEnvironment": {"QT_MAC_WANTS_LAYER": "1"},
        },
    )

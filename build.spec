# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置：把项目打包成单个可执行 exe。"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集 RapidOCR 的模型文件与所有子模块
datas = []
hiddenimports = []
try:
    datas += collect_data_files("rapidocr_onnxruntime")
    hiddenimports += collect_submodules("rapidocr_onnxruntime")
except Exception:
    pass

# pynput 在 Windows 上按需引入子模块
hiddenimports += [
    "pynput.keyboard._win32",
    "pynput.mouse._win32",
    "onnxruntime",
]

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="屏幕翻译",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,           # 不用 UPX 压缩，避免被杀软误报
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,        # 无控制台窗口（GUI 应用）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

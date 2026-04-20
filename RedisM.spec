# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),
    ],
    hiddenimports=[
        'src',
        'src.config',
        'src.main',
        'src.ui',
        'src.ui.main_window',
        'src.ui.left_panel',
        'src.ui.right_panel',
        'src.ui.key_manager',
        'src.ui.cli_interface',
        'src.ui.styles',
        'src.redis',
        'src.redis.connection',
        'src.redis.operations',
        'src.dialogs',
        'src.dialogs.base_dialog',
        'src.dialogs.simple_dialog',
        'src.dialogs.search_mixin',
        'src.dialogs.connection_dialog',
        'src.dialogs.key_dialogs',
        'src.utils',
        'src.utils.helpers',
        'redis',
        'paramiko',
        'paramiko.rsakey',
        'paramiko.ecdsakey',
        'paramiko.ed25519key',
        'phpserialize',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
    ],
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
    [],
    exclude_binaries=True,
    name='RedisM',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RedisM',
)

app = BUNDLE(
    coll,
    name='RedisM.app',
    icon=None,
    bundle_identifier='com.redismanager.app',
)
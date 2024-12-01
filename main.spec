# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None


datas = [
    ('src/Database/database.db', '.'),
    ('src/ArchiveManager/archive_manager.py', 'ArchiveManager'),
    ('src/GUIController/gui_controller.py', 'GUIController'),
    ('src/GUIController/archive_viewer.py', 'GUIController'),
    ('src/GUIController/drag_drop.py', 'GUIController'),
    ('src/GUIController/filter_controller.py', 'GUIController'),
    ('src/GUIController/login_window.py', 'GUIController'),
    ('src/GUIController/settings_window.py', 'GUIController'),
    ('src/GUIController/task_editor.py', 'GUIController'),
    ('src/NotificationManager/notification_manager.py', 'NotificationManager'),
    ('src/SettingsManager/settings_manager.py', 'SettingsManager'),
    ('src/Task/task.py', 'Task'),
    ('src/User/user.py', 'User'),
    ('src/User/UserRepository/user_repository.py', 'User/UserRepository'),
]

binaries = [
    ('C:/Users/Grech/AppData/Local/Programs/Python/Python312/DLLs/sqlite3.dll', '.'),
]

hidden_imports = [
    'sqlite3',
    'json',
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.constants',
]

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

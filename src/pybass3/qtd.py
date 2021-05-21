"""
    QT Dependancy imports
"""

try:
    from PySide2 import QtCore
    from PySide2.QtCore import QObject, QTimer, Signal, Qt
except ImportError:
    raise NotImplementedError("Missing Pyside2 and PyQT5 imports not implemented yet")
"""
    QT Dependancy imports
"""

try:
    from PySide2.QtCore import QObject, QTimer
    from PySide2.QtCore import Signal
except ImportError:
    raise NotImplementedError("Missing Pyside2 and PyQT5 imports not implemented yet")
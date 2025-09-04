from PySide6 import QtCore, QtGui

PALETTE_MIME = "application/x-drawsvg-shape"
SHAPES = ("Rectangle", "Circle", "Line", "Text")

DEFAULTS = {
    "Rectangle": (160.0, 100.0),   # w, h
    "Circle":    (100.0, 100.0),   # diameter, diameter
    "Line":      (150.0, 0.0),     # length, (unused)
    "Text":      (100.0, 30.0),    # placeholder bbox
}

PEN_NORMAL = QtGui.QPen(QtGui.QColor("#222"), 2)
PEN_SELECTED = QtGui.QPen(QtGui.QColor("#1e88e5"), 2, QtCore.Qt.PenStyle.DashLine)

from PySide6 import QtCore, QtGui

# DIN A4 size in pixels at 96 DPI (rounded to whole pixels)
A4_WIDTH = int(round(210 / 25.4 * 96))
A4_HEIGHT = int(round(297 / 25.4 * 96))

PALETTE_MIME = "application/x-drawsvg-shape"
SHAPES = (
    "Rectangle",
    "Ellipse",
    "Circle",
    "Triangle",
    "Line",
    "Arrow",
    "Text",
)

DEFAULTS = {
    "Rectangle": (160.0, 100.0),   # w, h
    "Ellipse":   (160.0, 100.0),   # w, h
    "Circle":    (100.0, 100.0),   # diameter, diameter
    "Triangle":  (160.0, 100.0),   # w, h
    "Line":      (150.0, 0.0),     # length, (unused)
    "Arrow":     (150.0, 0.0),     # length, (unused)
    "Text":      (100.0, 30.0),    # placeholder bbox
}

PEN_NORMAL = QtGui.QPen(QtGui.QColor("#222"), 2)
PEN_SELECTED = QtGui.QPen(QtGui.QColor("#1e88e5"), 2, QtCore.Qt.PenStyle.DashLine)

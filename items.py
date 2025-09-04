from PySide6 import QtCore, QtGui, QtWidgets

from constants import PEN_NORMAL, PEN_SELECTED


class RectItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, w, h):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.setTransformOriginPoint(w / 2.0, h / 2.0)
        self.setFlags(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable
        )
        self.setPen(PEN_NORMAL)
        self.setBrush(QtCore.Qt.BrushStyle.NoBrush)

    def paint(self, painter, option, widget=None):
        self.setPen(PEN_SELECTED if self.isSelected() else PEN_NORMAL)
        super().paint(painter, option, widget)


class EllipseItem(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, x, y, w, h):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.setTransformOriginPoint(w / 2.0, h / 2.0)
        self.setFlags(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable
        )
        self.setPen(PEN_NORMAL)
        self.setBrush(QtCore.Qt.BrushStyle.NoBrush)

    def paint(self, painter, option, widget=None):
        self.setPen(PEN_SELECTED if self.isSelected() else PEN_NORMAL)
        super().paint(painter, option, widget)


class LineItem(QtWidgets.QGraphicsLineItem):
    def __init__(self, x, y, length):
        super().__init__(0.0, 0.0, length, 0.0)
        self._length = length
        self.setPos(x, y)
        self.setTransformOriginPoint(length / 2.0, 0.0)
        self.setFlags(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable
        )
        self.setPen(PEN_NORMAL)

    def paint(self, painter, option, widget=None):
        self.setPen(PEN_SELECTED if self.isSelected() else PEN_NORMAL)
        super().paint(painter, option, widget)


class TextItem(QtWidgets.QGraphicsTextItem):
    def __init__(self, x, y, w, h):
        super().__init__("Text")
        self.setPos(x, y)
        font = QtGui.QFont()
        font.setPointSizeF(24.0)
        self.setFont(font)
        self.setDefaultTextColor(QtGui.QColor("#222"))
        self.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextEditorInteraction)
        self.setFlags(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable
        )
        br = self.boundingRect()
        self.setTransformOriginPoint(br.width() / 2.0, br.height() / 2.0)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.setPen(PEN_SELECTED if self.isSelected() else PEN_NORMAL)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawRect(self.boundingRect())

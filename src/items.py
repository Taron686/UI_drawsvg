from PySide6 import QtCore, QtGui, QtWidgets

from constants import PEN_NORMAL, PEN_SELECTED


class RectItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, w, h, rx: float = 0.0, ry: float = 0.0):
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
        self.rx = rx
        self.ry = ry

    def paint(self, painter, option, widget=None):
        if self.rx or self.ry:
            painter.setPen(self.pen())
            painter.setBrush(self.brush())
            painter.drawRoundedRect(self.rect(), self.rx, self.ry)
        else:
            super().paint(painter, option, widget)
        if self.isSelected():
            painter.save()
            painter.setPen(PEN_SELECTED)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            if self.rx or self.ry:
                painter.drawRoundedRect(self.rect(), self.rx, self.ry)
            else:
                painter.drawRect(self.rect())
            painter.restore()


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
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.save()
            painter.setPen(PEN_SELECTED)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self.rect())
            painter.restore()


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
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.save()
            painter.setPen(PEN_SELECTED)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawLine(self.line())
            painter.restore()


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
        if self.isSelected():
            painter.save()
            painter.setPen(PEN_SELECTED)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect())
            painter.restore()

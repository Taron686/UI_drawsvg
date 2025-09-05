from PySide6 import QtCore, QtGui, QtWidgets

from constants import PEN_NORMAL, PEN_SELECTED


HANDLE_COLOR = QtGui.QColor("#14b5ff")
HANDLE_SIZE = 8.0


class ResizeHandle(QtWidgets.QGraphicsEllipseItem):
    """Small circular handle used for interactive resizing."""

    def __init__(self, parent: QtWidgets.QGraphicsItem, direction: str):
        super().__init__(-HANDLE_SIZE / 2.0, -HANDLE_SIZE / 2.0, HANDLE_SIZE, HANDLE_SIZE, parent)
        self.setBrush(HANDLE_COLOR)
        self.setPen(QtGui.QPen(QtCore.Qt.PenStyle.NoPen))
        self.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton)
        self.setCursor(self._cursor_for_direction(direction))
        self._direction = direction
        self._start_rect = None
        self._start_pos = None
        self._parent_start_pos = None
        self._parent_was_movable = False

    @staticmethod
    def _cursor_for_direction(direction: str) -> QtCore.Qt.CursorShape:
        mapping = {
            "top_left": QtCore.Qt.CursorShape.SizeFDiagCursor,
            "top_right": QtCore.Qt.CursorShape.SizeBDiagCursor,
            "bottom_left": QtCore.Qt.CursorShape.SizeBDiagCursor,
            "bottom_right": QtCore.Qt.CursorShape.SizeFDiagCursor,
            "left": QtCore.Qt.CursorShape.SizeHorCursor,
            "right": QtCore.Qt.CursorShape.SizeHorCursor,
            "top": QtCore.Qt.CursorShape.SizeVerCursor,
            "bottom": QtCore.Qt.CursorShape.SizeVerCursor,
        }
        return mapping[direction]

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        self._start_pos = event.scenePos()
        parent = self.parentItem()
        if isinstance(parent, (QtWidgets.QGraphicsRectItem, QtWidgets.QGraphicsEllipseItem)):
            self._start_rect = QtCore.QRectF(parent.rect())
        else:
            self._start_rect = QtCore.QRectF(parent.boundingRect())
        self._parent_start_pos = QtCore.QPointF(parent.pos())
        flags = parent.flags()
        self._parent_was_movable = bool(
            flags & QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        if self._parent_was_movable:
            parent.setFlag(
                QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable,
                False,
            )
        event.accept()

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        if self._start_pos is None:
            event.ignore()
            return
        delta = event.scenePos() - self._start_pos
        parent = self.parentItem()
        rect = QtCore.QRectF(self._start_rect)
        pos = QtCore.QPointF(self._parent_start_pos)

        if "left" in self._direction:
            rect.setWidth(max(10.0, rect.width() - delta.x()))
            pos.setX(self._parent_start_pos.x() + delta.x())
        if "right" in self._direction:
            rect.setWidth(max(10.0, rect.width() + delta.x()))
        if "top" in self._direction:
            rect.setHeight(max(10.0, rect.height() - delta.y()))
            pos.setY(self._parent_start_pos.y() + delta.y())
        if "bottom" in self._direction:
            rect.setHeight(max(10.0, rect.height() + delta.y()))

        if isinstance(parent, QtWidgets.QGraphicsRectItem):
            parent.setRect(0, 0, rect.width(), rect.height())
            parent.setTransformOriginPoint(rect.width() / 2.0, rect.height() / 2.0)
            if hasattr(parent, "rx"):
                sx = rect.width() / self._start_rect.width() if self._start_rect.width() else 1.0
                parent.rx *= sx
            if hasattr(parent, "ry"):
                sy = rect.height() / self._start_rect.height() if self._start_rect.height() else 1.0
                parent.ry *= sy
        elif isinstance(parent, QtWidgets.QGraphicsEllipseItem):
            parent.setRect(0, 0, rect.width(), rect.height())
            parent.setTransformOriginPoint(rect.width() / 2.0, rect.height() / 2.0)
        else:  # fallback for other items using boundingRect
            br = parent.boundingRect()
            sx = rect.width() / br.width() if br.width() else 1.0
            sy = rect.height() / br.height() if br.height() else 1.0
            parent.setScale(max(sx, sy))

        parent.setPos(pos)
        if hasattr(parent, "update_handles"):
            parent.update_handles()
        event.accept()

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        parent = self.parentItem()
        if self._parent_was_movable:
            parent.setFlag(
                QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable,
                True,
            )
            self._parent_was_movable = False
        self._start_pos = None
        self._start_rect = None
        event.accept()


class ResizableItem:
    """Mixin providing 8-direction resize handles for graphics items."""

    def __init__(self):
        # NOTE: this mixin should not call super().__init__() because concrete
        # QGraphicsItem subclasses are already initialised explicitly.
        # Calling super() here would attempt to re-initialise them and triggers
        # runtime errors like "You can't initialize ... twice".
        self._handles = []

    def _ensure_handles(self):
        if self._handles:
            return
        directions = [
            "top_left",
            "top",
            "top_right",
            "right",
            "bottom_right",
            "bottom",
            "bottom_left",
            "left",
        ]
        for d in directions:
            h = ResizeHandle(self, d)
            h.hide()
            self._handles.append(h)

    def update_handles(self):
        self._ensure_handles()
        rect = self.boundingRect()
        points = [
            rect.topLeft(),
            QtCore.QPointF(rect.center().x(), rect.top()),
            rect.topRight(),
            QtCore.QPointF(rect.right(), rect.center().y()),
            rect.bottomRight(),
            QtCore.QPointF(rect.center().x(), rect.bottom()),
            rect.bottomLeft(),
            QtCore.QPointF(rect.left(), rect.center().y()),
        ]
        for pt, h in zip(points, self._handles):
            h.setPos(pt)

    def show_handles(self):
        self.update_handles()
        for h in self._handles:
            h.show()

    def hide_handles(self):
        for h in self._handles:
            h.hide()

    def itemChange(self, change, value):  # type: ignore[override]
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            if value:
                self.show_handles()
            else:
                self.hide_handles()
        elif change in (
            QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged,
            QtWidgets.QGraphicsItem.GraphicsItemChange.ItemTransformHasChanged,
        ):
            if self.isSelected():
                self.update_handles()
        return super().itemChange(change, value)  # type: ignore[misc]


class RectItem(ResizableItem, QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, w, h, rx: float = 0.0, ry: float = 0.0):
        QtWidgets.QGraphicsRectItem.__init__(self, 0, 0, w, h)
        ResizableItem.__init__(self)
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


class EllipseItem(ResizableItem, QtWidgets.QGraphicsEllipseItem):
    def __init__(self, x, y, w, h):
        QtWidgets.QGraphicsEllipseItem.__init__(self, 0, 0, w, h)
        ResizableItem.__init__(self)
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

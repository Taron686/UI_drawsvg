import math

from PySide6 import QtCore, QtGui, QtWidgets

from constants import PEN_NORMAL, PEN_SELECTED


HANDLE_COLOR = QtGui.QColor("#14b5ff")
HANDLE_SIZE = 8.0
HANDLE_OFFSET = 10.0


def snap_to_grid(item: QtWidgets.QGraphicsItem, pos: QtCore.QPointF) -> QtCore.QPointF:
    """Return pos aligned to the view's grid, if available."""
    scene = item.scene()
    if scene:
        views = scene.views()
        if views:
            size = getattr(views[0], "_grid_size", 20)
            x = round(pos.x() / size) * size
            y = round(pos.y() / size) * size
            return QtCore.QPointF(x, y)
    return pos


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
                parent.rx = min(parent.rx * sx, 50.0)
            if hasattr(parent, "ry"):
                sy = rect.height() / self._start_rect.height() if self._start_rect.height() else 1.0
                parent.ry = min(parent.ry * sy, 50.0)
        elif isinstance(parent, QtWidgets.QGraphicsEllipseItem):
            parent.setRect(0, 0, rect.width(), rect.height())
            parent.setTransformOriginPoint(rect.width() / 2.0, rect.height() / 2.0)
        elif isinstance(parent, TriangleItem):
            parent.set_size(rect.width(), rect.height())
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


class RotationHandle(QtWidgets.QGraphicsPixmapItem):
    """Handle used to rotate the parent item when dragged."""

    def __init__(self, parent: QtWidgets.QGraphicsItem):
        # Create a small pixmap with a circular arrow.
        pix = QtGui.QPixmap(20, 20)
        pix.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter(pix)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        pen = QtGui.QPen(HANDLE_COLOR)
        pen.setWidth(2)
        painter.setPen(pen)
        rect = QtCore.QRectF(5, 5, 10, 10)
        painter.drawArc(rect, 30 * 16, 300 * 16)
        path = QtGui.QPainterPath()
        path.moveTo(15, 8)
        path.lineTo(11, 8)
        path.lineTo(13, 4)
        path.closeSubpath()
        painter.fillPath(path, HANDLE_COLOR)
        painter.end()

        super().__init__(pix, parent)
        self.setOffset(-pix.width() / 2.0, -pix.height() / 2.0)
        self.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton)
        self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
        self._start_angle = None
        self._start_rotation = 0.0
        self._center = QtCore.QPointF()
        self._parent_was_movable = False
        self._angle_label: QtWidgets.QGraphicsSimpleTextItem | None = None
        self._angle_label_bg: QtWidgets.QGraphicsRectItem | None = None

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        parent = self.parentItem()
        self._center = parent.mapToScene(parent.boundingRect().center())
        pos = event.scenePos()
        self._start_angle = math.degrees(math.atan2(pos.y() - self._center.y(), pos.x() - self._center.x()))
        self._start_rotation = parent.rotation()
        flags = parent.flags()
        self._parent_was_movable = bool(
            flags & QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        if self._parent_was_movable:
            parent.setFlag(
                QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False
            )
        self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
        if parent.scene():
            scene = parent.scene()
            if self._angle_label is None:
                self._angle_label = QtWidgets.QGraphicsSimpleTextItem()
                self._angle_label.setZValue(1001)
                scene.addItem(self._angle_label)
            if self._angle_label_bg is None:
                self._angle_label_bg = QtWidgets.QGraphicsRectItem()
                self._angle_label_bg.setBrush(QtGui.QColor(220, 220, 220))
                self._angle_label_bg.setPen(QtGui.QPen(QtCore.Qt.PenStyle.NoPen))
                self._angle_label_bg.setZValue(1000)
                scene.addItem(self._angle_label_bg)
        self._update_label(parent.rotation())
        event.accept()

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        if self._start_angle is None:
            event.ignore()
            return
        pos = event.scenePos()
        angle = math.degrees(
            math.atan2(pos.y() - self._center.y(), pos.x() - self._center.x())
        )
        delta = angle - self._start_angle
        parent = self.parentItem()
        new_angle = self._start_rotation + delta
        mods = QtWidgets.QApplication.keyboardModifiers()
        if not mods & QtCore.Qt.KeyboardModifier.AltModifier:
            new_angle = round(new_angle / 5.0) * 5.0
        parent.setRotation(new_angle)
        self._update_label(parent.rotation())
        if hasattr(parent, "update_handles"):
            parent.update_handles()
        event.accept()

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        parent = self.parentItem()
        if self._parent_was_movable:
            parent.setFlag(
                QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True
            )
            self._parent_was_movable = False
        self._start_angle = None
        if parent.scene():
            scene = parent.scene()
            if self._angle_label:
                scene.removeItem(self._angle_label)
            if self._angle_label_bg:
                scene.removeItem(self._angle_label_bg)
        self._angle_label = None
        self._angle_label_bg = None
        self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
        event.accept()

    def _update_label(self, angle: float) -> None:
        if not self._angle_label:
            return
        self._angle_label.setText(f"{angle:.1f}\N{DEGREE SIGN}")
        parent = self.parentItem()
        if not parent:
            return
        scene_rect = parent.mapToScene(parent.boundingRect()).boundingRect()
        pos = QtCore.QPointF(scene_rect.center().x(), scene_rect.bottom() + 25)
        br = self._angle_label.boundingRect()
        self._angle_label.setPos(pos.x() - br.width() / 2.0, pos.y())
        if self._angle_label_bg:
            padding = 2.0
            rect = QtCore.QRectF(
                self._angle_label.pos().x() - padding,
                self._angle_label.pos().y() - padding,
                br.width() + 2 * padding,
                br.height() + 2 * padding,
            )
            self._angle_label_bg.setRect(rect)


class ResizableItem:
    """Mixin providing 8-direction resize handles for graphics items."""

    def __init__(self):
        # NOTE: this mixin should not call super().__init__() because concrete
        # QGraphicsItem subclasses are already initialised explicitly.
        # Calling super() here would attempt to re-initialise them and triggers
        # runtime errors like "You can't initialize ... twice".
        self._handles = []
        self._rotation_handle = None

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
        self._rotation_handle = RotationHandle(self)
        self._rotation_handle.hide()

    def update_handles(self):
        self._ensure_handles()
        rect = self.boundingRect()
        o = HANDLE_OFFSET
        points = [
            rect.topLeft() - QtCore.QPointF(o, o),
            QtCore.QPointF(rect.center().x(), rect.top() - o),
            rect.topRight() + QtCore.QPointF(o, -o),
            QtCore.QPointF(rect.right() + o, rect.center().y()),
            rect.bottomRight() + QtCore.QPointF(o, o),
            QtCore.QPointF(rect.center().x(), rect.bottom() + o),
            rect.bottomLeft() + QtCore.QPointF(-o, o),
            QtCore.QPointF(rect.left() - o, rect.center().y()),
        ]
        for pt, h in zip(points, self._handles):
            h.setPos(pt)
        if self._rotation_handle:
            rot_offset = QtCore.QPointF(o + 10.0, -o - 10.0)
            self._rotation_handle.setPos(rect.topRight() + rot_offset)

    def show_handles(self):
        self.update_handles()
        for h in self._handles:
            h.show()
        if self._rotation_handle:
            self._rotation_handle.show()

    def hide_handles(self):
        for h in self._handles:
            h.hide()
        if self._rotation_handle:
            self._rotation_handle.hide()

    def itemChange(self, change, value):  # type: ignore[override]
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            mods = QtWidgets.QApplication.keyboardModifiers()
            if not mods & QtCore.Qt.KeyboardModifier.AltModifier:
                value = snap_to_grid(self, value)
        elif change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
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


class LineHandle(QtWidgets.QGraphicsEllipseItem):
    """Handle placed at each end of a line for resizing/rotating."""

    def __init__(self, parent: QtWidgets.QGraphicsLineItem, endpoint: str):
        super().__init__(
            -HANDLE_SIZE / 2.0,
            -HANDLE_SIZE / 2.0,
            HANDLE_SIZE,
            HANDLE_SIZE,
            parent,
        )
        self.setBrush(HANDLE_COLOR)
        self.setPen(QtGui.QPen(QtCore.Qt.PenStyle.NoPen))
        self.setAcceptedMouseButtons(QtCore.Qt.MouseButton.LeftButton)
        self.setCursor(QtCore.Qt.CursorShape.SizeAllCursor)
        self._endpoint = endpoint  # "start" or "end"
        self._line_start_scene = QtCore.QPointF()
        self._line_end_scene = QtCore.QPointF()
        self._parent_was_movable = False

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        parent = self.parentItem()
        line = parent.line()
        self._line_start_scene = parent.mapToScene(line.p1())
        self._line_end_scene = parent.mapToScene(line.p2())
        flags = parent.flags()
        self._parent_was_movable = bool(
            flags & QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        if self._parent_was_movable:
            parent.setFlag(
                QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False
            )
        event.accept()

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        parent = self.parentItem()
        mods = event.modifiers()
        if self._endpoint == "start":
            new_start = event.scenePos()
            if not mods & QtCore.Qt.KeyboardModifier.AltModifier:
                new_start = snap_to_grid(parent, new_start)
            end_scene = self._line_end_scene
            parent.setPos(new_start)
            parent.setLine(
                0.0,
                0.0,
                end_scene.x() - new_start.x(),
                end_scene.y() - new_start.y(),
            )
        else:  # end handle
            start_scene = self._line_start_scene
            new_end = event.scenePos()
            if not mods & QtCore.Qt.KeyboardModifier.AltModifier:
                new_end = snap_to_grid(parent, new_end)
            parent.setPos(start_scene)
            parent.setLine(
                0.0,
                0.0,
                new_end.x() - start_scene.x(),
                new_end.y() - start_scene.y(),
            )
        line = parent.line()
        parent._length = line.length()
        mid = QtCore.QPointF((line.x1() + line.x2()) / 2.0, (line.y1() + line.y2()) / 2.0)
        parent.setTransformOriginPoint(mid)
        parent.update_handles()
        event.accept()

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent):
        parent = self.parentItem()
        if self._parent_was_movable:
            parent.setFlag(
                QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True
            )
            self._parent_was_movable = False
        event.accept()


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


class TriangleItem(ResizableItem, QtWidgets.QGraphicsPolygonItem):
    def __init__(self, x, y, w, h):
        QtWidgets.QGraphicsPolygonItem.__init__(self)
        ResizableItem.__init__(self)
        self._w = w
        self._h = h
        self._update_polygon()
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

    def _update_polygon(self):
        poly = QtGui.QPolygonF(
            [
                QtCore.QPointF(self._w / 2.0, 0.0),
                QtCore.QPointF(0.0, self._h),
                QtCore.QPointF(self._w, self._h),
            ]
        )
        self.setPolygon(poly)

    def set_size(self, w, h):
        self._w = w
        self._h = h
        self._update_polygon()
        self.setTransformOriginPoint(w / 2.0, h / 2.0)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.save()
            painter.setPen(PEN_SELECTED)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawPolygon(self.polygon())
            painter.restore()


class LineItem(QtWidgets.QGraphicsLineItem):
    def __init__(self, x, y, length, arrow_start: bool = False, arrow_end: bool = False):
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
        self.arrow_start = arrow_start
        self.arrow_end = arrow_end
        self._arrow_size = 10.0

        # endpoint handles
        self._start_handle = LineHandle(self, "start")
        self._end_handle = LineHandle(self, "end")
        self._start_handle.hide()
        self._end_handle.hide()
        self.update_handles()

    def set_arrow_start(self, val: bool) -> None:
        if self.arrow_start != val:
            self.prepareGeometryChange()
            self.arrow_start = val
            self.update()

    def set_arrow_end(self, val: bool) -> None:
        if self.arrow_end != val:
            self.prepareGeometryChange()
            self.arrow_end = val
            self.update()

    def boundingRect(self):  # type: ignore[override]
        br = super().boundingRect()
        if self.arrow_start or self.arrow_end:
            extra = self._arrow_size
            return br.adjusted(-extra, -extra, extra, extra)
        return br

    def update_handles(self):
        line = self.line()
        self._start_handle.setPos(line.p1())
        self._end_handle.setPos(line.p2())

    def show_handles(self):
        self.update_handles()
        self._start_handle.show()
        self._end_handle.show()

    def hide_handles(self):
        self._start_handle.hide()
        self._end_handle.hide()

    def itemChange(self, change, value):  # type: ignore[override]
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            mods = QtWidgets.QApplication.keyboardModifiers()
            if not mods & QtCore.Qt.KeyboardModifier.AltModifier:
                value = snap_to_grid(self, value)
        elif change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
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

    def _draw_arrow_head(
        self, painter: QtGui.QPainter, start: QtCore.QPointF, end: QtCore.QPointF
    ) -> None:
        line = QtCore.QLineF(start, end)
        angle = math.atan2(-line.dy(), line.dx())
        size = self._arrow_size
        p1 = end + QtCore.QPointF(
            math.sin(angle - math.pi / 3) * size,
            math.cos(angle - math.pi / 3) * size,
        )
        p2 = end + QtCore.QPointF(
            math.sin(angle - math.pi + math.pi / 3) * size,
            math.cos(angle - math.pi + math.pi / 3) * size,
        )
        painter.drawPolygon(QtGui.QPolygonF([end, p1, p2]))

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        line = self.line()
        if self.arrow_start or self.arrow_end:
            painter.save()
            painter.setPen(self.pen())
            painter.setBrush(self.pen().color())
            if self.arrow_start:
                self._draw_arrow_head(painter, line.p2(), line.p1())
            if self.arrow_end:
                self._draw_arrow_head(painter, line.p1(), line.p2())
            painter.restore()
        if self.isSelected():
            painter.save()
            painter.setPen(PEN_SELECTED)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawLine(line)
            if self.arrow_start:
                self._draw_arrow_head(painter, line.p2(), line.p1())
            if self.arrow_end:
                self._draw_arrow_head(painter, line.p1(), line.p2())
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

    def itemChange(self, change, value):  # type: ignore[override]
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            mods = QtWidgets.QApplication.keyboardModifiers()
            if not mods & QtCore.Qt.KeyboardModifier.AltModifier:
                value = snap_to_grid(self, value)
        return super().itemChange(change, value)  # type: ignore[misc]

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.save()
            painter.setPen(PEN_SELECTED)
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect())
            painter.restore()

from PySide6 import QtCore, QtGui, QtWidgets

from constants import PALETTE_MIME, SHAPES, DEFAULTS
from items import RectItem, EllipseItem, LineItem, TextItem


class CanvasView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
        self.setAcceptDrops(True)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        scene = QtWidgets.QGraphicsScene(self)
        scene.setSceneRect(0, 0, 1000, 700)
        self.setScene(scene)
        self.setBackgroundBrush(QtGui.QColor("#fafafa"))
        self._grid_size = 20

    def clear_canvas(self):
        """Remove all items from the scene."""
        self.scene().clear()

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        super().drawBackground(painter, rect)
        left = int(rect.left()) - int(rect.left()) % self._grid_size
        top = int(rect.top()) - int(rect.top()) % self._grid_size
        lines = []
        x = left
        while x < rect.right():
            lines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
            x += self._grid_size
        y = top
        while y < rect.bottom():
            lines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
            y += self._grid_size
        pen = QtGui.QPen(QtGui.QColor("#D0D0D0"))
        painter.setPen(pen)
        painter.drawLines(lines)

    # --- Drag and drop from the palette ---
    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        md = event.mimeData()
        if md.hasFormat(PALETTE_MIME) or md.hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
        if event.mimeData().hasFormat(PALETTE_MIME) or event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QtGui.QDropEvent):
        md = event.mimeData()
        text = ""
        if md.hasFormat(PALETTE_MIME):
            text = str(bytes(md.data(PALETTE_MIME)).decode("utf-8"))
        elif md.hasText():
            text = md.text()

        shape = text.strip()
        if shape not in SHAPES:
            super().dropEvent(event)
            return

        scene_pos = self.mapToScene(event.position().toPoint())
        x = scene_pos.x()
        y = scene_pos.y()

        w, h = DEFAULTS[shape]
        if shape == "Rectangle":
            item = RectItem(x, y, w, h)
        elif shape == "Circle":
            item = EllipseItem(x, y, w, h)
        elif shape == "Line":
            item = LineItem(x, y, w)
        else:  # "Text"
            item = TextItem(x, y, w, h)

        item.setData(0, shape)  # for export
        self.scene().addItem(item)
        item.setSelected(True)
        event.acceptProposedAction()

    # --- Central mouse wheel logic for all selected items ---
    def wheelEvent(self, event: QtGui.QWheelEvent):
        mods = event.modifiers()
        delta = event.angleDelta()
        dy = delta.y() if delta.y() else delta.x()
        dy /= 120.0

        selected = self.scene().selectedItems()
        if selected and (mods & QtCore.Qt.KeyboardModifier.AltModifier):
            step_deg = 5.0
            for it in selected:
                it.setRotation(it.rotation() + dy * step_deg)
            event.accept()
            return

        if selected and (mods & QtCore.Qt.KeyboardModifier.ControlModifier):
            factor = 1.0 + dy * 0.1
            if factor <= 0:
                factor = 0.05
            for it in selected:
                if isinstance(it, QtWidgets.QGraphicsRectItem):
                    r = it.rect()
                    new_w = max(10.0, r.width() * factor)
                    new_h = max(10.0, r.height() * factor)
                    it.setRect(0, 0, new_w, new_h)
                    it.setTransformOriginPoint(new_w / 2.0, new_h / 2.0)
                    if hasattr(it, "rx"):
                        it.rx *= factor
                    if hasattr(it, "ry"):
                        it.ry *= factor
                elif isinstance(it, QtWidgets.QGraphicsEllipseItem):
                    r = it.rect()
                    new_w = max(10.0, r.width() * factor)
                    new_h = max(10.0, r.height() * factor)
                    it.setRect(0, 0, new_w, new_h)
                    it.setTransformOriginPoint(new_w / 2.0, new_h / 2.0)
                elif isinstance(it, LineItem):
                    it._length = max(10.0, it._length * factor)
                    it.setLine(0.0, 0.0, it._length, 0.0)
                    it.setTransformOriginPoint(it._length / 2.0, 0.0)
                elif isinstance(it, TextItem):
                    font = it.font()
                    new_size = max(1.0, font.pointSizeF() * factor)
                    font.setPointSizeF(new_size)
                    it.setFont(font)
                    br = it.boundingRect()
                    it.setTransformOriginPoint(br.width() / 2.0, br.height() / 2.0)
            event.accept()
            return

        super().wheelEvent(event)

    # --- Keyboard shortcut to delete selected items ---
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key.Key_Delete:
            selected = self.scene().selectedItems()
            if selected:
                for it in selected:
                    self.scene().removeItem(it)
                event.accept()
                return
        super().keyPressEvent(event)

    # --- Context menu for adjusting colors and line width ---
    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        pos = event.pos()
        item = self.itemAt(pos)
        if not item:
            super().contextMenuEvent(event)
            return

        menu = QtWidgets.QMenu(self)
        fill_act = opacity_act = stroke_act = width_act = None
        color_act = size_act = corner_act = None
        if isinstance(item, RectItem):
            fill_act = menu.addAction("Set fill color…")
            opacity_act = menu.addAction("Set fill opacity…")
            corner_act = menu.addAction("Set corner radius…")
            menu.addSeparator()
            stroke_act = menu.addAction("Set stroke color…")
            width_act = menu.addAction("Set stroke width…")
        elif isinstance(item, QtWidgets.QGraphicsEllipseItem):
            fill_act = menu.addAction("Set fill color…")
            opacity_act = menu.addAction("Set fill opacity…")
            menu.addSeparator()
            stroke_act = menu.addAction("Set stroke color…")
            width_act = menu.addAction("Set stroke width…")
        elif isinstance(item, LineItem):
            stroke_act = menu.addAction("Set stroke color…")
            width_act = menu.addAction("Set stroke width…")
        elif isinstance(item, TextItem):
            color_act = menu.addAction("Set text color…")
            size_act = menu.addAction("Set font size…")
        else:
            stroke_act = menu.addAction("Set stroke color…")
            width_act = menu.addAction("Set stroke width…")
        menu.addSeparator()
        back1_act = menu.addAction("Send backward")
        front1_act = menu.addAction("Bring forward")
        back_act = menu.addAction("Send to back")
        front_act = menu.addAction("Bring to front")

        action = menu.exec(event.globalPos())
        if not action:
            super().contextMenuEvent(event)
            return

        if action is fill_act:
            brush = item.brush()
            color = QtWidgets.QColorDialog.getColor(brush.color(), self, "Fill color")
            if color.isValid():
                item.setBrush(color)
        elif action is opacity_act:
            brush = item.brush()
            start = brush.color().alphaF() if brush.style() != QtCore.Qt.BrushStyle.NoBrush else 1.0
            val, ok = QtWidgets.QInputDialog.getDouble(self, "Fill opacity", "Opacity:", start, 0.0, 1.0, 2)
            if ok:
                color = brush.color()
                color.setAlphaF(val)
                item.setBrush(color)
        elif action is stroke_act:
            pen = item.pen()
            color = QtWidgets.QColorDialog.getColor(pen.color(), self, "Stroke color")
            if color.isValid():
                pen.setColor(color)
                item.setPen(pen)
                item.update()
        elif action is width_act:
            pen = item.pen()
            val, ok = QtWidgets.QInputDialog.getDouble(self, "Stroke width", "Width:", pen.widthF(), 0.1, 50.0, 1)
            if ok:
                pen.setWidthF(val)
                item.setPen(pen)
                item.update()
        elif action is corner_act and isinstance(item, RectItem):
            rx_val, ok = QtWidgets.QInputDialog.getDouble(self, "Corner radius", "rx:", item.rx, 0.0, 1000.0, 1)
            if ok:
                ry_val, ok2 = QtWidgets.QInputDialog.getDouble(self, "Corner radius", "ry:", item.ry, 0.0, 1000.0, 1)
                if ok2:
                    item.rx = rx_val
                    item.ry = ry_val
                    item.update()
        elif action is color_act:
            color = QtWidgets.QColorDialog.getColor(item.defaultTextColor(), self, "Text color")
            if color.isValid():
                item.setDefaultTextColor(color)
        elif action is size_act:
            font = item.font()
            val, ok = QtWidgets.QInputDialog.getDouble(self, "Font size", "Size:", font.pointSizeF(), 1.0, 500.0, 1)
            if ok:
                font.setPointSizeF(val)
                item.setFont(font)
                br = item.boundingRect()
                item.setTransformOriginPoint(br.width() / 2.0, br.height() / 2.0)
        elif action in (back1_act, front1_act, back_act, front_act):
            scene = self.scene()
            items = [it for it in scene.items() if it.data(0) in SHAPES]
            items.sort(key=lambda it: it.zValue())
            idx = items.index(item)
            if action == back1_act and idx > 0:
                items[idx - 1], items[idx] = items[idx], items[idx - 1]
            elif action == front1_act and idx < len(items) - 1:
                items[idx + 1], items[idx] = items[idx], items[idx + 1]
            elif action == back_act:
                items.insert(0, items.pop(idx))
            elif action == front_act:
                items.append(items.pop(idx))
            for z, it in enumerate(items):
                it.setZValue(z)
        else:
            super().contextMenuEvent(event)

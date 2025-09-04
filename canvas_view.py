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

    # --- Drag&Drop aus der Palette ---
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

    # --- Zentrale Mausrad-Logik für alle selektierten Items ---
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

    # --- Kontextmenü zum Anpassen von Farben und Linienbreite ---
    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        pos = event.pos()
        item = self.itemAt(pos)
        if not item:
            super().contextMenuEvent(event)
            return

        menu = QtWidgets.QMenu(self)
        fill_act = opacity_act = stroke_act = width_act = None
        color_act = size_act = None
        if isinstance(item, (QtWidgets.QGraphicsRectItem, QtWidgets.QGraphicsEllipseItem)):
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
        back1_act = menu.addAction("Eine Ebene nach hinten")
        front1_act = menu.addAction("Eine Ebene nach vorne")
        back_act = menu.addAction("Ganz nach hinten")
        front_act = menu.addAction("Ganz nach vorne")

        action = menu.exec(event.globalPos())
        if action == fill_act:
            brush = item.brush()
            color = QtWidgets.QColorDialog.getColor(brush.color(), self, "Fill color")
            if color.isValid():
                item.setBrush(color)
        elif action == opacity_act:
            brush = item.brush()
            start = brush.color().alphaF() if brush.style() != QtCore.Qt.BrushStyle.NoBrush else 1.0
            val, ok = QtWidgets.QInputDialog.getDouble(self, "Fill opacity", "Opacity:", start, 0.0, 1.0, 2)
            if ok:
                color = brush.color()
                color.setAlphaF(val)
                item.setBrush(color)
        elif action == stroke_act:
            pen = item.pen()
            color = QtWidgets.QColorDialog.getColor(pen.color(), self, "Stroke color")
            if color.isValid():
                pen.setColor(color)
                item.setPen(pen)
        elif action == width_act:
            pen = item.pen()
            val, ok = QtWidgets.QInputDialog.getDouble(self, "Stroke width", "Width:", pen.widthF(), 0.1, 50.0, 1)
            if ok:
                pen.setWidthF(val)
                item.setPen(pen)
        elif action == color_act:
            color = QtWidgets.QColorDialog.getColor(item.defaultTextColor(), self, "Text color")
            if color.isValid():
                item.setDefaultTextColor(color)
        elif action == size_act:
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

import sys
from PySide6 import QtCore, QtGui, QtWidgets

# ---------------------------
#  Helpers / Constants
# ---------------------------
PALETTE_MIME = "application/x-drawsvg-shape"
SHAPES = ("Rectangle", "Circle", "Line")

DEFAULTS = {
    "Rectangle": (160.0, 100.0),   # w, h
    "Circle":    (100.0, 100.0),   # diameter, diameter
    "Line":      (150.0, 0.0),     # length, (unused)
}

PEN_NORMAL = QtGui.QPen(QtGui.QColor("#222"), 2)
PEN_SELECTED = QtGui.QPen(QtGui.QColor("#1e88e5"), 2, QtCore.Qt.PenStyle.DashLine)


# ---------------------------
#  Interactive Items (ohne wheelEvent – Steuerung zentral im View)
# ---------------------------
class RectItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, w, h):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)  # x,y = top-left
        self.setTransformOriginPoint(w / 2.0, h / 2.0)  # rotate around center
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
        super().__init__(0.0, 0.0, length, 0.0)  # local coords
        self._length = length
        self.setPos(x, y)  # pos = start point in scene coords
        self.setTransformOriginPoint(length / 2.0, 0.0)  # rotate around middle
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


# ---------------------------
#  Canvas (View + Scene) – zentrale Steuerung von Resize/Rotate
# ---------------------------
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
        else:  # "Line"
            item = LineItem(x, y, w)

        item.setData(0, shape)  # for export
        self.scene().addItem(item)
        item.setSelected(True)
        event.acceptProposedAction()

    # --- Zentrale Mausrad-Logik für alle selektierten Items ---
    def wheelEvent(self, event: QtGui.QWheelEvent):
        mods = event.modifiers()
        # Qt liefert bei gedrückter Alt-Taste oft nur ein horizontales
        # angleDelta (x) statt y. Damit die Rotation dennoch funktioniert,
        # verwenden wir die nicht-null Komponente.
        delta = event.angleDelta()
        dy = delta.y() if delta.y() else delta.x()
        dy /= 120.0  # Mausrad-Raster

        selected = self.scene().selectedItems()
        if selected and (mods & QtCore.Qt.KeyboardModifier.AltModifier):
            # ROTATE: Alt + Wheel -> alle selektierten Items drehen
            step_deg = 5.0
            for it in selected:
                it.setRotation(it.rotation() + dy * step_deg)
            event.accept()
            return

        if selected and (mods & QtCore.Qt.KeyboardModifier.ControlModifier):
            # RESIZE: Ctrl + Wheel -> alle selektierten Items skalieren
            factor = 1.0 + dy * 0.1
            if factor <= 0:
                factor = 0.05  # harte Untergrenze gegen Negativ/Null
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
            event.accept()
            return

        # Keine Modifikator-Taste -> Standardverhalten (Scrollen)
        super().wheelEvent(event)

    # --- Kontextmenü zum Anpassen von Farben und Linienbreite ---
    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        pos = event.pos()
        item = self.itemAt(pos)
        if not item:
            super().contextMenuEvent(event)
            return

        menu = QtWidgets.QMenu(self)
        fill_act = opacity_act = None
        if isinstance(item, (QtWidgets.QGraphicsRectItem, QtWidgets.QGraphicsEllipseItem)):
            fill_act = menu.addAction("Set fill color…")
            opacity_act = menu.addAction("Set fill opacity…")
            menu.addSeparator()
        stroke_act = menu.addAction("Set stroke color…")
        width_act = menu.addAction("Set stroke width…")

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
        else:
            super().contextMenuEvent(event)


# ---------------------------
#  Palette (List mit Drag)
# ---------------------------
class PaletteList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        for name in SHAPES:
            QtWidgets.QListWidgetItem(name, self)

    def startDrag(self, supportedActions: QtCore.Qt.DropActions):
        item = self.currentItem()
        if not item:
            return
        drag = QtGui.QDrag(self)
        md = QtCore.QMimeData()
        md.setData(PALETTE_MIME, item.text().encode("utf-8"))
        md.setText(item.text())  # fallback
        drag.setMimeData(md)

        pix = QtGui.QPixmap(100, 30)
        pix.fill(QtCore.Qt.GlobalColor.transparent)
        p = QtGui.QPainter(pix)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        p.setPen(QtGui.QPen(QtGui.QColor("#444"), 2))
        p.drawRoundedRect(1, 1, 98, 28, 6, 6)
        p.drawText(pix.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, item.text())
        p.end()
        drag.setPixmap(pix)
        drag.exec(QtCore.Qt.DropAction.CopyAction)


# ---------------------------
#  Main Window + Export
# ---------------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DrawSVG Canvas – PySide6")
        self.resize(1200, 800)

        # Splitter: left palette, right canvas
        self.splitter = QtWidgets.QSplitter()
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)

        self.palette = PaletteList()
        self.palette.setMinimumWidth(220)

        self.canvas = CanvasView()

        self.splitter.addWidget(self.palette)
        self.splitter.addWidget(self.canvas)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.setCentralWidget(self.splitter)

        self._build_menu()

        # Hinweise aktualisiert
        self.statusBar().showMessage("Tipp: Strg+Mausrad = Größe (für selektierte Objekte), Alt+Mausrad = Rotation (global)")

    def _build_menu(self):
        menu = self.menuBar().addMenu("&Datei")

        act_save_py = QtGui.QAction("Als drawsvg-.py speichern…", self)
        act_save_py.triggered.connect(self.export_drawsvg_py)
        menu.addAction(act_save_py)

        menu.addSeparator()
        act_quit = QtGui.QAction("Beenden", self)
        act_quit.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Quit))
        act_quit.triggered.connect(self.close)
        menu.addAction(act_quit)

    # --------- Export ---------
    def export_drawsvg_py(self):
        scene = self.canvas.scene()
        rect = scene.sceneRect()
        width = int(rect.width())
        height = int(rect.height())

        items = [it for it in scene.items() if it.data(0) in SHAPES]
        items.reverse()  # unten->oben in Erstellreihenfolge

        lines = []
        lines.append("# Auto-generated from PySide6 Canvas to drawsvg")
        lines.append("import drawsvg as draw")
        lines.append("")
        lines.append(f"def build_drawing():")
        lines.append(f"    d = draw.Drawing({width}, {height}, origin=(0, 0))")
        lines.append("")

        for it in items:
            shape = it.data(0)
            if shape == "Rectangle" and isinstance(it, QtWidgets.QGraphicsRectItem):
                r = it.rect()
                x = it.pos().x()
                y = it.pos().y()
                w = r.width()
                h = r.height()
                cx = x + w / 2.0
                cy = y + h / 2.0
                ang = it.rotation()
                if abs(ang) > 1e-6:
                    lines.append(
                        f"    _rect = draw.Rectangle({x:.2f}, {y:.2f}, {w:.2f}, {h:.2f}, "
                        f"fill='none', stroke='#222', stroke_width=2, "
                        f"transform='rotate({ang:.2f} {cx:.2f} {cy:.2f})')"
                    )
                else:
                    lines.append(
                        f"    _rect = draw.Rectangle({x:.2f}, {y:.2f}, {w:.2f}, {h:.2f}, "
                        f"fill='none', stroke='#222', stroke_width=2)"
                    )
                lines.append("    d.append(_rect)")
                lines.append("")

            elif shape == "Circle" and isinstance(it, QtWidgets.QGraphicsEllipseItem):
                r = it.rect()
                x = it.pos().x()
                y = it.pos().y()
                w = r.width()
                h = r.height()
                d_avg = (w + h) / 2.0
                radius = d_avg / 2.0
                cx = x + w / 2.0
                cy = y + h / 2.0
                ang = it.rotation()
                if abs(ang) > 1e-6:
                    lines.append(
                        f"    _circ = draw.Circle({cx:.2f}, {cy:.2f}, {radius:.2f}, "
                        f"fill='none', stroke='#222', stroke_width=2, "
                        f"transform='rotate({ang:.2f} {cx:.2f} {cy:.2f})')"
                    )
                else:
                    lines.append(
                        f"    _circ = draw.Circle({cx:.2f}, {cy:.2f}, {radius:.2f}, "
                        f"fill='none', stroke='#222', stroke_width=2)"
                    )
                lines.append("    d.append(_circ)")
                lines.append("")

            elif shape == "Line" and isinstance(it, QtWidgets.QGraphicsLineItem):
                line = it.line()
                x = it.pos().x()
                y = it.pos().y()
                x1 = x + line.x1()
                y1 = y + line.y1()
                x2 = x + line.x2()
                y2 = y + line.y2()
                cx = (x1 + x2) / 2.0
                cy = (y1 + y2) / 2.0
                ang = it.rotation()
                if abs(ang) > 1e-6:
                    lines.append(
                        f"    _line = draw.Line({x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f}, "
                        f"stroke='#222', stroke_width=2, "
                        f"transform='rotate({ang:.2f} {cx:.2f} {cy:.2f})')"
                    )
                else:
                    lines.append(
                        f"    _line = draw.Line({x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f}, "
                        f"stroke='#222', stroke_width=2)"
                    )
                lines.append("    d.append(_line)")
                lines.append("")

        lines.append("    return d")
        lines.append("")
        lines.append("if __name__ == '__main__':")
        lines.append("    d = build_drawing()")
        lines.append("    # Erstellt eine SVG-Datei neben dem Skript:")
        lines.append("    d.save_svg('canvas.svg')")

        code = "\n".join(lines)
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Als drawsvg-.py speichern…",
            "canvas_drawsvg.py",
            "Python (*.py)",
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(code)
                self.statusBar().showMessage(f"Exportiert: {path}", 5000)
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Fehler beim Speichern", str(e))


# ---------------------------
#  App bootstrap
# ---------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

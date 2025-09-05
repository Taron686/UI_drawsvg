from PySide6 import QtCore, QtGui, QtWidgets

from constants import SHAPES


def export_drawsvg_py(scene: QtWidgets.QGraphicsScene, parent: QtWidgets.QWidget | None = None):
    rect = scene.sceneRect()
    width = int(rect.width())
    height = int(rect.height())

    items = [it for it in scene.items() if it.data(0) in SHAPES]
    items.reverse()

    lines = []
    lines.append("# Auto-generated from PySide6 Canvas to drawsvg")
    lines.append("import drawsvg as draw")
    lines.append("")
    lines.append("def build_drawing():")
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
            brush = it.brush()
            pen = it.pen()
            attrs = []
            if brush.style() == QtCore.Qt.BrushStyle.NoBrush:
                attrs.append("fill='none'")
            else:
                bcol = brush.color()
                attrs.append(f"fill='{bcol.name()}'")
                attrs.append(f"fill_opacity={bcol.alphaF():.2f}")
            attrs.append(f"stroke='{pen.color().name()}'")
            attrs.append(f"stroke_width={pen.widthF():.2f}")
            attr_str = ", ".join(attrs)
            if abs(ang) > 1e-6:
                lines.append(
                    f"    _rect = draw.Rectangle({x:.2f}, {y:.2f}, {w:.2f}, {h:.2f}, {attr_str}, transform='rotate({ang:.2f} {cx:.2f} {cy:.2f})')"
                )
            else:
                lines.append(
                    f"    _rect = draw.Rectangle({x:.2f}, {y:.2f}, {w:.2f}, {h:.2f}, {attr_str})"
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
            brush = it.brush()
            pen = it.pen()
            attrs = []
            if brush.style() == QtCore.Qt.BrushStyle.NoBrush:
                attrs.append("fill='none'")
            else:
                bcol = brush.color()
                attrs.append(f"fill='{bcol.name()}'")
                attrs.append(f"fill_opacity={bcol.alphaF():.2f}")
            attrs.append(f"stroke='{pen.color().name()}'")
            attrs.append(f"stroke_width={pen.widthF():.2f}")
            attr_str = ", ".join(attrs)
            if abs(ang) > 1e-6:
                lines.append(
                    f"    _circ = draw.Circle({cx:.2f}, {cy:.2f}, {radius:.2f}, {attr_str}, transform='rotate({ang:.2f} {cx:.2f} {cy:.2f})')"
                )
            else:
                lines.append(
                    f"    _circ = draw.Circle({cx:.2f}, {cy:.2f}, {radius:.2f}, {attr_str})"
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
            pen = it.pen()
            attr_str = f"stroke='{pen.color().name()}', stroke_width={pen.widthF():.2f}"
            if abs(ang) > 1e-6:
                lines.append(
                    f"    _line = draw.Line({x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f}, {attr_str}, transform='rotate({ang:.2f} {cx:.2f} {cy:.2f})')"
                )
            else:
                lines.append(
                    f"    _line = draw.Line({x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f}, {attr_str})"
                )
            lines.append("    d.append(_line)")
            lines.append("")

        elif shape == "Text" and isinstance(it, QtWidgets.QGraphicsTextItem):
            x = it.pos().x()
            y = it.pos().y()
            br = it.boundingRect()
            cx = x + br.width() / 2.0
            cy = y + br.height() / 2.0
            ang = it.rotation()
            font = it.font()
            size = font.pointSizeF()
            text = it.toPlainText().replace("'", "\'")
            color = it.defaultTextColor().name()
            baseline = y + br.height()
            attr_str = f"fill='{color}'"
            if abs(ang) > 1e-6:
                lines.append(
                    f"    _text = draw.Text('{text}', {size:.2f}, {x:.2f}, {baseline:.2f}, {attr_str}, transform='rotate({ang:.2f} {cx:.2f} {cy:.2f})')"
                )
            else:
                lines.append(
                    f"    _text = draw.Text('{text}', {size:.2f}, {x:.2f}, {baseline:.2f}, {attr_str})"
                )
            lines.append("    d.append(_text)")
            lines.append("")

    lines.append("    return d")
    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append("    d = build_drawing()")
    lines.append("    # Creates an SVG file next to the script:")
    lines.append("    d.save_svg('canvas.svg')")

    code = "\n".join(lines)
    path, _ = QtWidgets.QFileDialog.getSaveFileName(
        parent,
        "Save as drawsvg-.py…",
        "canvas_drawsvg.py",
        "Python (*.py)",
    )
    if path:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            if parent is not None:
                parent.statusBar().showMessage(f"Exported: {path}", 5000)
        except Exception as e:
            QtWidgets.QMessageBox.critical(parent, "Error saving file", str(e))

# Auto-generated from PySide6 Canvas to drawsvg
import drawsvg as draw

def build_drawing():
    d = draw.Drawing(1000, 700, origin=(0, 0))

    _rect = draw.Rectangle(184.00, 72.00, 160.00, 100.00, fill='#172ce5', fill_opacity=1.00, stroke='#222222', stroke_width=2.00)
    d.append(_rect)

    _circ = draw.Circle(438.00, 282.00, 50.00, fill='#ccaf7e', fill_opacity=1.00, stroke='#cacaca', stroke_width=2.00)
    d.append(_circ)

    return d

if __name__ == '__main__':
    d = build_drawing()
    # Erstellt eine SVG-Datei neben dem Skript:
    d.save_svg('canvas.svg')
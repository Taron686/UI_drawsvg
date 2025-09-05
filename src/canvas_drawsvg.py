# Auto-generated from PySide6 Canvas to drawsvg
import drawsvg as draw

def build_drawing():
    d = draw.Drawing(1000, 700, origin=(0, 0))

    _rect = draw.Rectangle(272.00, 131.00, 160.00, 100.00, fill='none', stroke='#1e88e5', stroke_width=2.00)
    d.append(_rect)

    _circ = draw.Circle(703.00, 277.00, 50.00, fill='none', stroke='#1e88e5', stroke_width=2.00)
    d.append(_circ)

    return d

if __name__ == '__main__':
    d = build_drawing()
    # Creates an SVG file next to the script:
    d.save_svg('canvas.svg')

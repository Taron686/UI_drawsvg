# DrawSVG UI

This repository provides a graphical user interface designed to make it easier to create files with the [drawsvg](https://pypi.org/project/drawsvg/) library.  
Instead of writing raw Python code by hand, you can visually place, move, and edit shapes on a canvas, then export your work as a ready-to-use `drawsvg` file.

The goal of this project is to help users quickly prototype and generate `drawsvg` code through an intuitive drag-and-drop UI built with [PySide6](https://doc.qt.io/qtforpython/).

## Requirements

The application requires **Python 3.10**.  
Dependencies include:

* **drawsvg**  
* **PySide6**

Install all dependencies with:

```bash
python -m pip install -r requirements.txt
```

## Running the Application
After installing the dependencies, start the application with:

```bash
python src/main.py
```

## UI Features
* **Create shapes:** Drag rectangles, ellipses, circles, triangles, lines and text from the palette onto the canvas.
* **Mouse adjustments:**
  * `Ctrl` + left drag duplicates selected objects.
  * `Ctrl` or `Shift` + left click adds items to the current selection.
* **Canvas panning:** Hold the mouse wheel button or `Alt` + right mouse button and drag to move around the canvas.
* Drag the rotation icon above the top-right corner of a selected object to rotate it. Rotations snap to 5° increments by default; hold `Alt` while dragging for smooth rotation. A temporary label with a light gray background below the object displays the current angle during the operation.
* **Context menu:** Right-click an object to modify colors, line width or text size.
* **Export/Import:** Use the `File` menu to export scenes as `drawsvg` Python files or load them back again.
* **Clear canvas:** Remove all objects via `Edit` → `Clear canvas`.
* **Delete objects:** Press the `Delete` key to remove selected items.



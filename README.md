# DrawSVG UI

This project provides a simple graphical interface for drawing SVG shapes with [PySide6](https://doc.qt.io/qtforpython/). Drag and drop objects from the palette onto the canvas and adjust them as needed.

## Requirements
The application requires **Python 3.10**. Install the dependencies listed in `requirements.txt` with:

```bash
python -m pip install -r requirements.txt
```

## Running the Application
After installing the dependencies, start the application with:

```bash
python src/main.py
```

## UI Features
* **Create shapes:** Drag rectangles, circles, lines and text from the palette onto the canvas.
* **Mouse adjustments:**
  * `Ctrl` + mouse wheel changes the size of selected objects.
  * `Alt` + mouse wheel rotates selected objects.
* **Context menu:** Right-click an object to modify colors, line width or text size.
* **Export/Import:** Use the `File` menu to export scenes as `drawsvg` Python files or load them back again.
* **Clear canvas:** Remove all objects via `Edit` → `Canvas delete`.



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
* **Clear canvas:** Remove all objects via `Edit` → `Clear canvas`.



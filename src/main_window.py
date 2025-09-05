from PySide6 import QtCore, QtGui, QtWidgets

from canvas_view import CanvasView
from palette import PaletteList
from export import export_drawsvg_py
from import_drawsvg import import_drawsvg_py


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DrawSVG Canvas – PySide6")
        self.resize(1200, 800)

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
        self.statusBar().showMessage(
            "Tipp: Strg+Mausrad = Größe (für selektierte Objekte), Alt+Mausrad = Rotation (global)"
        )

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("&Datei")

        act_load_py = QtGui.QAction("Load drawsvg-.py", self)
        act_load_py.triggered.connect(self.load_drawsvg_py)
        file_menu.addAction(act_load_py)

        act_save_py = QtGui.QAction("Save drawsvg-.py", self)
        act_save_py.triggered.connect(self.export_drawsvg_py)
        file_menu.addAction(act_save_py)

        file_menu.addSeparator()
        act_quit = QtGui.QAction("Beenden", self)
        act_quit.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Quit))
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        edit_menu = self.menuBar().addMenu("&Edit")
        act_clear_canvas = QtGui.QAction("Canvas delete", self)
        act_clear_canvas.triggered.connect(self.canvas.clear_canvas)
        edit_menu.addAction(act_clear_canvas)

    def export_drawsvg_py(self):
        export_drawsvg_py(self.canvas.scene(), self)

    def load_drawsvg_py(self):
        import_drawsvg_py(self.canvas.scene(), self)

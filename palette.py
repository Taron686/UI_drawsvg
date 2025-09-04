from PySide6 import QtCore, QtGui, QtWidgets

from constants import PALETTE_MIME, SHAPES


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
        md.setText(item.text())
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

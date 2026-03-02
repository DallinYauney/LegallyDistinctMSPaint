# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

# PainterWidget is the actual drawing surface
# MainWindow has the toolbar, file handling and color picker

from __future__ import annotations

from PyQt6 import QtCore

from PyQt6.QtWidgets import (
    QWidget,
    QMainWindow,
    QApplication,
    QFileDialog,
    QStyle,
    QColorDialog,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSlot, QStandardPaths
from PyQt6.QtGui import (
    QMouseEvent,
    QPaintEvent,
    QPen,
    QAction,
    QPainter,
    QColor,
    QPixmap,
    QIcon,
    QKeySequence,
    QCursor,
)
import sys


# This is a custom widget it inherits from QWidget
class PainterWidget(QWidget):
    """A widget where user can draw with their mouse

    The user draws on a QPixmap which is itself paint from paintEvent()

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.eraser_mode = False

        self.setFixedSize(680, 480)

        # QPixmap is used to show images on screen
        # QPixmap is a QPaintDevice subclass so QPainter can be used to draw directly onto pixmaps.
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.GlobalColor.white)

        self.previous_pos = None
        self.painter = QPainter()
        self.pen = QPen()
        self.pen.setWidth(10)
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

    def paintEvent(self, event: QPaintEvent):
        """Override method from QWidget

        Paint the Pixmap into the widget

        """
        with QPainter(self) as painter:
            painter.drawPixmap(0, 0, self.pixmap)

    def mousePressEvent(self, event: QMouseEvent):
        """Override from QWidget

        Called when user clicks on the mouse

        """
        self.previous_pos = event.position().toPoint()
        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Override method from QWidget

        Called when user moves and clicks on the mouse

        """
        current_pos = event.position().toPoint()
        self.painter.begin(self.pixmap)
        self.painter.setRenderHints(QPainter.RenderHint.Antialiasing, True)
        self.painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_SourceOver
        )

        if self.eraser_mode:
            eraser_pen = QPen(self.pen)
            eraser_pen.setColor(Qt.GlobalColor.white)
            eraser_pen.setCapStyle
            self.painter.setPen(eraser_pen)
        else:
            self.painter.setPen(self.pen)

        self.painter.drawLine(self.previous_pos, current_pos)
        self.painter.end()

        self.previous_pos = current_pos
        self.update()

        QWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Override method from QWidget

        Called when user releases the mouse

        """
        self.previous_pos = None
        QWidget.mouseReleaseEvent(self, event)

    def save(self, filename: str):
        """save pixmap to filename"""
        self.pixmap.save(filename)

    def load(self, filename: str):
        """load pixmap from filename"""
        self.pixmap.load(filename)
        self.pixmap = self.pixmap.scaled(
            self.size(), Qt.AspectRatioMode.KeepAspectRatio
        )
        self.update()

    def clear(self):
        """Clear the pixmap"""
        self.pixmap.fill(Qt.GlobalColor.white)
        self.update()

    def update_eraser_cursor(self):
        # Grabs the size of the current pen and adds a bit of buffer
        size = self.pen.width() + 20
        # Creates a pixmap based on size
        pixmap = QPixmap(size, size)
        # Fill the pixmap with transparent
        pixmap.fill(Qt.GlobalColor.transparent)
        # Make the painter so that we can draw on the pixmap
        painter = QPainter(pixmap)
        # Turn on antialiasing so that its smooth
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Make a pen to draw on the pixmap with and make it black
        pen = QPen(Qt.GlobalColor.black)
        # set the width of the pen to 1 for a small outline
        pen.setWidth(1)
        # Tell the painter to use the pen we made
        painter.setPen(pen)
        # Set the brush style as no brush so there will not be any fill
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # get the radius and center of the current pen used
        radius = self.pen.width() // 2
        center = size // 2
        # Draw an ellipse on the pixmap using the radius and center of the current pen
        painter.drawEllipse(QtCore.QPoint(center, center), radius, radius)
        painter.end()

        # Set the cursor as the pixmap we created and make the center based on the size of the pen
        cursor = QCursor(pixmap, center, center)
        self.setCursor(cursor)

    # reset the cursor to normal
    def restore_cursor(self):
        self.setCursor(Qt.CursorShape.ArrowCursor)


class MainWindow(QMainWindow):
    """An Application example to draw using a pen"""

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.painter_widget = PainterWidget()
        self.bar = self.addToolBar("Menu")
        self.bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._save_action = self.bar.addAction(
            QApplication.style().standardIcon(
                QStyle.StandardPixmap.SP_DialogSaveButton
            ),  # noqa: F821
            "Save",
            self.on_save,
        )
        self._save_action.setShortcut(QKeySequence.StandardKey.Save)
        self._open_action = self.bar.addAction(
            QApplication.style().standardIcon(
                QStyle.StandardPixmap.SP_DialogOpenButton
            ),  # noqa: F821
            "Open",
            self.on_open,
        )
        self._open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.bar.addAction(
            QApplication.style().standardIcon(
                QStyle.StandardPixmap.SP_DialogResetButton
            ),  # noqa: F821
            "Clear",
            self.painter_widget.clear,
        )

        self._eraser_action = self.bar.addAction(
            QApplication.style().standardIcon(
                QStyle.StandardPixmap.SP_LineEditClearButton
            ),
            "Eraser",
            self.toggle_eraser,
        )
        self._eraser_action.setCheckable(True)
        self._eraser_action.setShortcut(QKeySequence("E"))

        self.bar.addSeparator()

        self.color_action = QAction(self)
        self.color_action.triggered.connect(self.on_color_clicked)
        self.bar.addAction(self.color_action)

        self.setCentralWidget(self.painter_widget)

        self.color = Qt.GlobalColor.black
        self.set_color(self.color)

        self.mime_type_filters = ["image/png", "image/jpeg"]

    @QtCore.pyqtSlot()
    def on_save(self):

        dialog = QFileDialog(self, "Save File")
        dialog.setMimeTypeFilters(self.mime_type_filters)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setDefaultSuffix("png")
        dialog.setDirectory(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.PicturesLocation
            )
        )

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            if dialog.selectedFiles():
                self.painter_widget.save(dialog.selectedFiles()[0])

    @QtCore.pyqtSlot()
    def on_open(self):

        dialog = QFileDialog(self, "Save File")
        dialog.setMimeTypeFilters(self.mime_type_filters)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dialog.setDefaultSuffix("png")
        dialog.setDirectory(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.PicturesLocation
            )
        )

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            if dialog.selectedFiles():
                self.painter_widget.load(dialog.selectedFiles()[0])

    @QtCore.pyqtSlot()
    def on_color_clicked(self):
        if color := QColorDialog.getColor(self.color, self):
            self.set_color(color)

    def set_color(self, color: QColor = Qt.GlobalColor.black):

        self.color = color
        # Create color icon
        pix_icon = QPixmap(32, 32)
        pix_icon.fill(self.color)

        self.color_action.setIcon(QIcon(pix_icon))
        self.painter_widget.pen.setColor(self.color)
        self.color_action.setText(QColor(self.color).name())

    @QtCore.pyqtSlot()
    def toggle_eraser(self):
        self.painter_widget.eraser_mode = self._eraser_action.isChecked()

        if self.painter_widget.eraser_mode:
            self.painter_widget.update_eraser_cursor()
        else:
            self.painter_widget.restore_cursor()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())

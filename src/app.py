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
from PyQt6.QtCore import (
    Qt,
    pyqtSlot,
    QStandardPaths,
    QPoint,
)
from PyQt6.QtGui import (
    QMouseEvent,
    QKeyEvent,
    QWheelEvent,
    QInputDevice,
    QPaintEvent,
    QPen,
    QAction,
    QPainter,
    QColor,
    QPixmap,
    QIcon,
    QKeySequence,
)
import sys
from PainterStates import DrawState, PanState, InputTracker

CANVAS_SIZE = 500

# This is a custom widget it inherits from QWidget
class PainterWidget(QWidget):
    """A widget where user can draw with their mouse

    The user draws on a QPixmap which is itself paint from paintEvent()

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(CANVAS_SIZE, CANVAS_SIZE)

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

        # self.painting = False
        # self.painting_mode = True

    def paintEvent(self, event: QPaintEvent):
        """Override method from QWidget

        Paint the Pixmap into the widget

        """
        with QPainter(self) as painter:
            painter.drawPixmap(0, 0, self.pixmap)

    # def mousePressEvent(self, event: QMouseEvent):
    #     """Override from QWidget

    #     Called when user clicks on the mouse

    #     """
    #     if event.button() == Qt.MouseButton.LeftButton and self.painting_mode:
    #         self.previous_pos = event.position().toPoint()
    #         self.painting = True
    #     QWidget.mousePressEvent(self, event)

    # def mouseMoveEvent(self, event: QMouseEvent):
    #     """Override method from QWidget

    #     Called when user moves and clicks on the mouse

    #     """
    #     if self.painting:
    #         current_pos = event.position().toPoint()
    #         self.painter.begin(self.pixmap)
    #         self.painter.setRenderHints(QPainter.RenderHint.Antialiasing, True)
    #         self.painter.setPen(self.pen)
    #         self.painter.drawLine(self.previous_pos, current_pos)
    #         self.painter.end()

    #         self.previous_pos = current_pos
    #         self.update()

    #     QWidget.mouseMoveEvent(self, event)

    # def mouseReleaseEvent(self, event: QMouseEvent):
    #     """Override method from QWidget

    #     Called when user releases the mouse

    #     """
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         self.previous_pos = None
    #         self.painting = False
    #     QWidget.mouseReleaseEvent(self, event)
    
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

    def draw(self, start: QPoint, end: QPoint):
        # print(f"Draw triggered at points {start} and {end}")
        self.painter.begin(self.pixmap)
        self.painter.setRenderHints(QPainter.RenderHint.Antialiasing, True)
        self.painter.setPen(self.pen)
        self.painter.drawLine(start, end)
        self.painter.end()

        self.update()









class PainterController(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setMinimumSize(350, 350)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.painter = PainterWidget(self)
        # displacement = CANVAS_SIZE // 2
        # self.painter.move(-displacement, -displacement)
        self.inputs = InputTracker()
        # self.state = DrawState(self, self.inputs, 0)
        self.state = DrawState(self, self.inputs, 0)
        # self.state_history = []
        self.state_history = [DrawState]
        # self.change_state(DrawState)
    

    ### ### INPUT PLUMBING ### ###
    def mousePressEvent(self, event: QMouseEvent):
        self.state.mouse_down(event)

        self.inputs.new_mouse_pos(event)
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        self.state.mouse_move(event)

        self.inputs.new_mouse_pos(event)
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.state.mouse_up(event)
        return super().mousePressEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        if not event.isAutoRepeat():
            self.inputs.pressed_keys.add(event.key())
            self.state.key_down(event)
        return super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event: QKeyEvent):
        if not event.isAutoRepeat():
            self.inputs.pressed_keys.remove(event.key())
            self.state.key_up(event)
        return super().keyReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        self.state.scroll(event)
        return super().wheelEvent(event)


    ### ### STATE MANAGEMENT ### ###
    def change_state(self, target_state, transiency=0):
        # self.set_button_checked(self.state_history[-1], target_state)
        self.set_button_checked(target_state)
        self.state_history.append(target_state)
        self.state = target_state(self, self.inputs, transiency)
    
    def revert_state(self):
        # print("Reverting state with list", self.state_history)
        # old_state = self.state
        # new_state = self.state_history.pop()
        self.state_history.pop()
        new_state = self.state_history[-1]
        self.state = new_state(self, self.inputs, 0)
        # self.set_button_checked(old_state, self.state)
        self.set_button_checked(new_state)
    
    def set_button_checked(self, target_state):
        for button in self.parent.state_buttons.values():
            button.setChecked(False)
        # print(f"{from_state} to {to_state}")
        # self.parent.state_buttons[from_state].setChecked(False)
        # self.parent.state_buttons[to_state].setChecked(True)
        self.parent.state_buttons[target_state].setChecked(True)


    def button_set_state(self, target_state):
        def inner():
            if self.state != target_state:
                self.change_state(target_state, 0)
        return inner
    

    ### ### ACTUAL FUNCTIONALITY ### ###
    # probably move this to PainterWidget eventually lol
    def pan(self, delta: QPoint):
        new_pos = self.painter.pos() + delta
        self.painter.move(new_pos)






























# class PainterContainer(QWidget):
#     """
#     Widget to hold the PainterWidget and move it around
#     """
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setMinimumSize(350, 350)
#         self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

#         self.painter = PainterWidget(self)
#         displacement = CANVAS_SIZE // 2
#         self.painter.move(-displacement, -displacement)

#         self.prev_pos = None
#         self.left_mouse = False
#         self.middle_mouse = False
#         self.right_mouse = False
#         self.spacebar = False
#         self.drag_button = False
    
#     def toggle_pan(self):
#         self.drag_button = not self.drag_button
#         self.painter.painting_mode = not self.painter.painting_mode
    
#     def is_panning(self):
#         return (
#             self.middle_mouse or
#             (self.left_mouse and self.drag_button) or
#             (self.left_mouse and self.spacebar)
#         )
    
#     def mousePressEvent(self, event: QMouseEvent):
#         match event.button():
#             case Qt.MouseButton.MiddleButton:
#                 self.middle_mouse = True
#             case Qt.MouseButton.LeftButton:
#                 self.left_mouse = True
#             case Qt.MouseButton.RightButton:
#                 self.right_mouse = True
        
        
#         if self.is_panning():
#             self.is_dragging = True
#             self.prev_pos = event.position().toPoint()
#         return super().mousePressEvent(event)
    
#     def mouseMoveEvent(self, event: QMouseEvent):
#         if self.is_panning():
#             current_pos = event.position().toPoint()
#             delta = current_pos - self.prev_pos
#             self.pan(delta)
#             self.prev_pos = current_pos
#         return super().mouseMoveEvent(event)
    
#     def mouseReleaseEvent(self, event: QMouseEvent):
#         match event.button():
#             case Qt.MouseButton.MiddleButton:
#                 self.middle_mouse = False
#             case Qt.MouseButton.LeftButton:
#                 self.left_mouse = False
#             case Qt.MouseButton.RightButton:
#                 self.right_mouse = False
        
#         if not self.is_panning():
#             self.prev_pos = None

#         return super().mouseReleaseEvent(event)
    
#     def keyPressEvent(self, event: QKeyEvent):
#         if (event.key() == Qt.Key.Key_Space) and not event.isAutoRepeat():
#             self.spacebar = True
#             self.painter.painting_mode = False
#         return super().keyPressEvent(event)
    
#     def keyReleaseEvent(self, event: QKeyEvent):
#         if (event.key() == Qt.Key.Key_Space) and not event.isAutoRepeat():
#             self.spacebar = False
#             self.painter.painting_mode = True
#         return super().keyReleaseEvent(event)
    
#     def wheelEvent(self, event: QWheelEvent):

#         # I only want to pan if the scroll is from a trackpad.
#         # Curiously, scrolling with my mouse doesn't return a pixelDelta
#         # anyways (and filtering by event.device() == trackpad doesn't
#         # seem to work in the first place).
#         self.pan(event.pixelDelta())

#         return super().wheelEvent(event)
    
#     def pan(self, delta):
#         new_pos = self.painter.pos() + delta
#         self.painter.move(new_pos)


class MainWindow(QMainWindow):
    """An Application example to draw using a pen"""

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        # self.painter_holder = PainterContainer()
        # self.painter_holder = PainterController(self)
        self.painter_holder = PainterController(self)

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
            self.painter_holder.painter.clear,
        )
        
        self.bar.addSeparator()

        self.state_buttons = {}

        self.state_buttons[DrawState] = self.bar.addAction(
            QApplication.style().standardIcon(
                QStyle.StandardPixmap.SP_DialogOkButton
            ),  # noqa: F821
            "Draw",
            self.painter_holder.button_set_state(DrawState),
        )

        # self._pan_action = self.bar.addAction(
        self.state_buttons[PanState] = self.bar.addAction(
            QApplication.style().standardIcon(
                QStyle.StandardPixmap.SP_FileDialogListView
            ),  # noqa: F821
            "Pan",
            self.painter_holder.button_set_state(PanState),
        )
        # self._pan_action.setCheckable(True)

        self.bar.addSeparator()

        self.color_action = QAction(self)
        self.color_action.triggered.connect(self.on_color_clicked)
        self.bar.addAction(self.color_action)

        self.setCentralWidget(self.painter_holder)

        self.color = Qt.GlobalColor.black
        self.set_color(self.color)

        self.mime_type_filters = ["image/png", "image/jpeg"]

        for action in self.state_buttons.values():
            action.setCheckable(True)
        self.state_buttons[DrawState].setChecked(True)

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
                self.painter_holder.painter.save(dialog.selectedFiles()[0])

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
                self.painter_holder.painter.load(dialog.selectedFiles()[0])

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
        self.painter_holder.painter.pen.setColor(self.color)
        self.color_action.setText(QColor(self.color).name())


if __name__ == "__main__":

    app = QApplication(sys.argv)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())

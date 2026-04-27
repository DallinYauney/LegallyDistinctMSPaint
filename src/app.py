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
    QSlider,
    QLabel,
)
from PyQt6.QtCore import (
    Qt,
    pyqtSlot,
    QStandardPaths,
    QPoint,
    QMargins,
    QSize,
)
from PyQt6.QtGui import (
    QMouseEvent,
    QKeyEvent,
    QWheelEvent,
    QPaintEvent,
    QImage,
    QPen,
    QAction,
    QPainter,
    QColor,
    QPixmap,
    QIcon,
    QKeySequence,
    QResizeEvent,
)
import sys
from PainterStates import DrawState, PanState, EraserState, InputTracker

# This is a custom widget it inherits from QWidget
class PainterWidget(QWidget):
    """A widget where user can draw with their mouse

    The user draws on a QPixmap which is itself paint from paintEvent()
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(100, 100)
        self.setMaximumSize(12000, 12000)

        # QPixmap is used to show images on screen
        # QPixmap is a QPaintDevice subclass so QPainter can be used to draw directly onto pixmaps.
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.GlobalColor.white)

        self.painter = QPainter()

        self.draw_pen = QPen()
        self.draw_pen.setWidth(10)
        self.draw_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.draw_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        self.eraser_pen = QPen(self.draw_pen)
        self.eraser_pen.setColor(Qt.GlobalColor.white)

    def paintEvent(self, event: QPaintEvent):
        """Override method from QWidget

        Paint the Pixmap into the widget
        """
        with QPainter(self) as painter:
            painter.drawPixmap(0, 0, self.pixmap)

    def save(self, filename: str):
        """save pixmap to filename"""
        self.pixmap.save(filename)

    def load(self, filename: str):
        """load pixmap from filename"""
        
        image = QImage(filename)
        self.pixmap = QPixmap.fromImage(image)

        self.setFixedSize(image.size())

        self.parentWidget().load_center(image.size())
        self.update()

    def clear(self):
        """Clear the pixmap"""
        self.pixmap.fill(Qt.GlobalColor.white)
        self.update()

    def draw(self, start: QPoint, end: QPoint, erasing=False):
        self.painter.begin(self.pixmap)
        self.painter.setRenderHints(QPainter.RenderHint.Antialiasing, True)
        self.painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_SourceOver
        )

        if erasing:
            self.painter.setPen(self.eraser_pen)
        else:
            self.painter.setPen(self.draw_pen)

        self.painter.drawLine(start, end)
        self.painter.end()

        self.update()

    def change_pen_size(self, size):
        self.draw_pen.setWidth(size)
        self.eraser_pen.setWidth(size)


class PainterController(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setMinimumSize(350, 350)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.painter = PainterWidget(self)

        self.inputs = InputTracker()
        self.state = DrawState(self, self.inputs, 0)
        self.state_history = [DrawState]
        # ^^ note that we don't use change_state() to set the
        # default state because PainterController needs to be
        # initialized before the buttons, so they can use it to
        # connect to load, clear, button_set_state, etc.

        self.background = QLabel(self)
        self.background.setScaledContents(True)
        background_pixmap = QPixmap(1, 1)
        # background_pixmap.fill(QColor("#202326"))
        background_pixmap.fill(Qt.GlobalColor.white)
        self.background.setPixmap(background_pixmap)
        self.background.stackUnder(self.painter)
    

    ### ### INPUT PLUMBING ### ###
    def mousePressEvent(self, event: QMouseEvent):
        """passes mouse button press events to the active state"""
        self.state.mouse_down(event)

        self.inputs.new_mouse_pos(event)
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """passes mouse move events to the active state"""
        self.state.mouse_move(event)

        self.inputs.new_mouse_pos(event)
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """passes mouse button release events to the active state"""
        self.state.mouse_up(event)
        return super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        """passes key press events to the active state"""
        if not event.isAutoRepeat():
            # self.inputs.pressed_keys.add(event.key())
            self.state.key_down(event)
        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        """passes key up events to the active state"""
        if not event.isAutoRepeat():
            # self.inputs.pressed_keys.remove(event.key())
            self.state.key_up(event)
        return super().keyReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent):
        """passes scroll events (including trackpad) to the active state"""
        self.state.scroll(event)
        return super().wheelEvent(event)

    ### ### STATE MANAGEMENT ### ###
    def change_state(self, target_state, transiency=0):
        """changes the active state"""
        self.set_button_checked(target_state)
        self.state_history.append(target_state)
        self.state = target_state(self, self.inputs, transiency)

    def revert_state(self):
        """sets the state to the previous state"""
        self.state_history.pop()
        new_state = self.state_history[-1]
        self.state = new_state(self, self.inputs, 0)
        self.set_button_checked(new_state)

    def set_button_checked(self, target_state):
        """sets one state's button to be checked (the others get unchecked)"""
        for button in self.parent.state_buttons.values():
            button.setChecked(False)
        self.parent.state_buttons[target_state].setChecked(True)

    def button_set_state(self, target_state):
        """method called by state buttons to enable a certain state"""

        def inner():
            if self.state != target_state:
                self.change_state(target_state, 0)

        return inner

    ### ### ACTUAL FUNCTIONALITY ### ###
    # probably move this to PainterWidget eventually lol
    def pan(self, delta: QPoint):
        """pans across the screen"""
        new_pos = self.painter.pos() + delta
        self.painter.move(new_pos)
    
    def load_center(self, image_size: QSize):
        # reset painter location to top left
        self.painter.move(-1 * self.painter.pos())

        # math stuff to put the image in the center
        difference = self.rect().size() - image_size
        displacement = QPoint()
        displacement.setX(difference.width() // 2)
        displacement.setY(difference.height() // 2)
        self.painter.move(displacement)

        self.expand()

    def expand(self):
        """
        The core of the "infinite scrolling" feature.

        If the canvas isn't already covering the whole screen, it
        creates a new blank canvas just large enough to cover both
        the screen and the old canvas, and copies the old canvas over.
        """
        ### Calculate bounding boxes for various sections ###
        # screen_rect should be expanded by a bit so we can draw outside the window
        screen_margin = QMargins()
        screen_margin += 250 # even 250px margin on every side
        # screen_margin += -20
        drawable = self.rect().marginsAdded(screen_margin)

        canvas_rect = self.painter.rect()

        # we need an extra copy of the canvas rect later
        copy_source_rect = self.painter.rect()

        # all rects start at 0,0 so modify canvas_rect by painter displacement
        canvas_rect.translate(self.painter.pos())
        new_rect = drawable.united(canvas_rect)

        # scroll within canvas, no expansion necessary
        if canvas_rect.contains(drawable):
            return
        
        # create new blank pixmap
        new_size = new_rect.size()
        new_canvas = QPixmap(new_size)
        old_canvas = self.painter.pixmap

        ### Copy over old pixmap to new pixmap at right place ###
        self.painter.pixmap = new_canvas
        self.painter.setMinimumSize(new_size)
        
        # Fill the whole thing with white (unfortunately necessary)
        new_canvas.fill(Qt.GlobalColor.white)

        ## We only need to change the position if we're filling in up or left ##
        displacement = QPoint(0,0)
        potential_displacement = -1 * self.painter.pos()

        if self.painter.pos().x() > -screen_margin.left():
            displacement.setX(potential_displacement.x() - screen_margin.left())
        
        if self.painter.pos().y() > -screen_margin.top():
            displacement.setY(potential_displacement.y() - screen_margin.top())

        self.pan(displacement)
        copy_source_rect.translate(-1 * displacement)

        with QPainter(new_canvas) as painter:
            painter.drawPixmap(copy_source_rect, old_canvas)
        
        # update triggers a repaint of the canvas
        self.update()
    
    def resizeEvent(self, event: QResizeEvent):
        """
        Called automatically when it's resized:
        1. when someone fullscreens the app
        2. when the toolbar widget sizes get calculated on initialization
        """
        self.background.resize(event.size())

        ## keep the center of the app the same, rather than the top-left ##
        size_change = event.size() - event.oldSize()
        manhattan_change = abs(size_change.width() + size_change.height())
        # the resizing works poorly on gradual changes, so don't bother
        if manhattan_change > 50:
            delta = QPoint(size_change.width() // 2, size_change.height() // 2)
            self.pan(delta)

            # preemptive expansion so it doesn't happen on mouse_down
            self.expand()
        return super().resizeEvent(event)
        


class MainWindow(QMainWindow):
    """An Application example to draw using a pen"""

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

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

        self.state_buttons[PanState] = self.bar.addAction(
            QApplication.style().standardIcon(
                QStyle.StandardPixmap.SP_FileDialogListView
            ),  # noqa: F821
            "Pan",
            self.painter_holder.button_set_state(PanState),
        )

        self.state_buttons[EraserState] = self.bar.addAction(
            QApplication.style().standardIcon(
                QStyle.StandardPixmap.SP_LineEditClearButton
            ),  # noqa: F821
            "Eraser",
            self.painter_holder.button_set_state(EraserState),
        )

        self.bar.addSeparator()

        self.color_action = QAction(self)
        self.color_action.triggered.connect(self.on_color_clicked)
        self.bar.addAction(self.color_action)

        self.setCentralWidget(self.painter_holder)

        self.color = Qt.GlobalColor.black
        self.set_color(self.color)

        self.bar.addSeparator()

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(25)
        self.slider.setValue(10)

        # Couldn't be like the other buttons because QSlider is a widget
        # So it had to use addWidget with a QLabel
        self.bar.addWidget(QLabel("Size"))
        self.size_label = QLabel("10")
        self.bar.addWidget(self.size_label)
        self.bar.addWidget(self.slider)

        self.slider.valueChanged.connect(self.change_pen_size)

        self.mime_type_filters = ["image/png", "image/jpeg"]

        # set all state buttons to be checkable
        for action in self.state_buttons.values():
            action.setCheckable(True)

        # set default state button to be checked
        default_state = self.painter_holder.state_history[-1]
        self.state_buttons[default_state].setChecked(True)

    def change_pen_size(self, value):
        self.size_label.setText(str(value))
        self.painter_holder.painter.change_pen_size(value)

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
        self.painter_holder.painter.draw_pen.setColor(self.color)
        self.color_action.setText(QColor(self.color).name())


if __name__ == "__main__":

    app = QApplication(sys.argv)

    # set application branding
    app.setApplicationDisplayName("MS Paint")
    app_icon = QIcon("branding/notPaintLogoCropped.png")
    app.setWindowIcon(app_icon)

    w = MainWindow()
    w.show()

    sys.exit(app.exec())

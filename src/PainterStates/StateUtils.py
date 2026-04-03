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
# from .InputTracker import InputTracker
from . import InputTracker
# from app import PainterController



# def draw(event: QMouseEvent, inputs: InputTracker, controller: PainterController):
def draw(event: QMouseEvent, inputs: InputTracker, controller):
    displacement = controller.painter.pos()
    controller.painter.draw(inputs.prev_mouse_pos - displacement, event.position().toPoint() - displacement)

def erase(event: QMouseEvent, inputs: InputTracker, controller):
    print("Not yet implemented")

def pan(event: QMouseEvent, inputs: InputTracker, controller):
    delta = event.position().toPoint() - inputs.prev_mouse_pos
    controller.pan(delta)

def scroll(event: QWheelEvent, inputs: InputTracker, controller):
    controller.pan(event.pixelDelta())

def scroll_or_zoom(event: QWheelEvent, inputs: InputTracker, controller):
    scroll(event,inputs,controller)
    # angleDelta scrolling not implemented yet
    # Zoom not implemented yet




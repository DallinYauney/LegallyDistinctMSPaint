from __future__ import annotations

from PyQt6.QtGui import (
    QMouseEvent,
    QWheelEvent,
)
from PyQt6.QtCore import (
    Qt,
    QPoint,
    QRect,
)
from . import InputTracker

"""
The code within state managers that determines actual painter actions should
never be more complex than a single function call and the relevant arguments.
These functions house the callers for the shared painter logic to make the states more readable.
"""

def draw(event: QMouseEvent, inputs: InputTracker, controller):
    displacement = controller.painter.pos()
    controller.painter.draw(inputs.prev_mouse_pos - displacement, event.position().toPoint() - displacement)

def erase(event: QMouseEvent, inputs: InputTracker, controller):
    displacement = controller.painter.pos()
    controller.painter.draw(inputs.prev_mouse_pos - displacement, event.position().toPoint() - displacement, True)

def erase_rect(event: QMouseEvent, inputs: InputTracker, controller):
    displacement = controller.painter.pos()
    start_corner = inputs.mouse_down_pos - displacement
    end_corner = event.position().toPoint() - displacement
    rect_to_erase = QRect(start_corner, end_corner)

    print(f"erasing at {rect_to_erase}")
    controller.painter.erase_rect(rect_to_erase)

def pan(event: QMouseEvent, inputs: InputTracker, controller):
    delta = event.position().toPoint() - inputs.prev_mouse_pos
    controller.pan(delta)

def scroll(amount: QPoint, controller):
    controller.pan(amount)

def zoom(event: QWheelEvent, inputs: InputTracker, controller):
    print("zoooOOOOM")

def scroll_or_zoom(event: QWheelEvent, inputs: InputTracker, controller):
    # from https://doc.qt.io/qt-6/qwheelevent.html#pixelDelta
    pixels = event.pixelDelta()

    degree_factor = 6
    degrees = event.angleDelta() / degree_factor

    if not pixels.isNull():
        # def from trackpad
        scroll(pixels, controller)
    elif not degrees.isNull():
        # old API, could be trackpad or mouse
        if event.angleDelta().manhattanLength() == 120:
            # comes from mouse
            zoom(event, input, controller)
        else:
            # scroll length not 120, comes from trackpad
            scroll(degrees, controller)

def expand(event: QWheelEvent, inputs: InputTracker, controller):
    controller.expand()

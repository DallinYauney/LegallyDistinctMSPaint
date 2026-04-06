from __future__ import annotations

from PyQt6.QtGui import (
    QMouseEvent,
    QWheelEvent,
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

def pan(event: QMouseEvent, inputs: InputTracker, controller):
    delta = event.position().toPoint() - inputs.prev_mouse_pos
    controller.pan(delta)

def scroll(event: QWheelEvent, inputs: InputTracker, controller):
    controller.pan(event.pixelDelta())

def scroll_or_zoom(event: QWheelEvent, inputs: InputTracker, controller):
    scroll(event,inputs,controller)
    # angleDelta scrolling not implemented yet
    # Zoom not implemented yet




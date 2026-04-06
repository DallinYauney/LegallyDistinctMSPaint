from .StateUtils import draw,erase,pan,scroll_or_zoom
from .InputTracker import InputTracker
from . import PanState
from . import EraserState
from PyQt6.QtWidgets import (
    QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QMouseEvent,
    QKeyEvent,
    QWheelEvent,
)

"""
The default state. Left click to draw.
Also uses Middle click to pan and right click to erase.
"""

class DrawState:
    def __init__(self, controller: QWidget, inputs: InputTracker, _: int):
        self.controller = controller
        self.inputs = inputs

        # is_painting = should we be drawing lines when the cursor moves?
        self.is_painting = False

    def mouse_down(self, event: QMouseEvent):
        match event.button():
            case Qt.MouseButton.LeftButton:
                self.is_painting = True
            case Qt.MouseButton.MiddleButton:
                self.controller.change_state(PanState.PanState, 2)
            case Qt.MouseButton.RightButton:
                self.controller.change_state(EraserState.EraserState, 2)
    
    def mouse_move(self, event: QMouseEvent):
        if self.is_painting:
            draw(event, self.inputs, self.controller)

    def mouse_up(self, event: QMouseEvent):
        match event.button():
            case Qt.MouseButton.LeftButton:
                self.is_painting = False
            case Qt.MouseButton.MiddleButton:
                pass
            case Qt.MouseButton.RightButton:
                pass
    
    def key_down(self, event: QKeyEvent):
        match event.key():
            case Qt.Key.Key_Space:
                self.controller.change_state(PanState.PanState, 1)
            case Qt.Key.Key_E:
                self.controller.change_state(EraserState.EraserState, 1)
    
    def key_up(self, event: QKeyEvent):
        match event.key():
            case Qt.Key.Key_Space:
                pass
    
    def scroll(self, event: QWheelEvent):
        scroll_or_zoom(event, self.inputs, self.controller)

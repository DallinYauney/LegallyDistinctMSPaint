# from StateUtils import *
from .StateUtils import draw,erase,pan,scroll_or_zoom
from .InputTracker import InputTracker
# from .DrawState import DrawState
from . import DrawState
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
Transiency:
0 - not even slightly transient. Normal state, as if pushed by a menu button
1 - semitransient. Has the potential to graduate to normal state if nothing (such as
mouse_down) happens to take advantage of it
2 - fully transient. Can never graduate to normal state
"""

class PanState:
    def __init__(self, controller: QWidget, inputs: InputTracker, transiency: int):
        self.controller = controller
        self.inputs = inputs
        self.transiency = transiency
        self.can_graduate = transiency == 1
        self.is_panning = transiency > 0

    def mouse_down(self, event: QMouseEvent):
        match event.button():
            case Qt.MouseButton.LeftButton:
                self.is_panning = True
                self.can_graduate = False
            case Qt.MouseButton.MiddleButton:
                pass
            case Qt.MouseButton.RightButton:
                pass
    
    def mouse_move(self, event: QMouseEvent):
        if self.is_panning:
            pan(event, self.inputs, self.controller)

    def mouse_up(self, event: QMouseEvent):
        match event.button():
            case Qt.MouseButton.LeftButton:
                self.is_panning = False
            case Qt.MouseButton.MiddleButton:
                if self.transiency > 0:
                    self.controller.revert_state()

    def key_down(self, event: QKeyEvent):
        match event.key():
            case Qt.Key.Key_Space:
                self.controller.change_state(DrawState.DrawState)
                # pass

    def key_up(self, event: QKeyEvent):
        match event.key():
            case Qt.Key.Key_Space:
                if self.transiency > 0:
                    if self.can_graduate:
                        self.transiency = 0
                    else:
                        self.controller.revert_state()
    
    def scroll(self, event: QWheelEvent):
        scroll_or_zoom(event, self.inputs, self.controller)


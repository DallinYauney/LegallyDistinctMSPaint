from .StateUtils import draw,erase,pan,scroll_or_zoom
from .InputTracker import InputTracker
from . import PanState
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
Eraser. Paints stuff white.

Uses the same sort of transiency logic as in PanState, so refer to that.

One day I think it might be cool to allow modes, this mode in particular, to
semitransiently activate itself - so like holding e to erase if you're already
in eraser would let you stay in eraser.
"""

class EraserState:
    def __init__(self, controller: QWidget, inputs: InputTracker, transiency: int):
        self.controller = controller
        self.inputs = inputs
        self.transiency = transiency
        self.can_graduate = transiency == 1
        self.is_erasing = transiency > 0

    def mouse_down(self, event: QMouseEvent):
        match event.button():
            case Qt.MouseButton.LeftButton:
               self.is_erasing = True
               self.can_graduate = False
            case Qt.MouseButton.MiddleButton:
                self.controller.change_state(PanState.PanState, 2)
            case Qt.MouseButton.RightButton:
               self.is_erasing = True
               self.can_graduate = False
    
    def mouse_move(self, event: QMouseEvent):
        if self.is_erasing:
            erase(event, self.inputs, self.controller)

    def mouse_up(self, event: QMouseEvent):
        match event.button():
            case Qt.MouseButton.LeftButton:
                self.is_erasing = False
            case Qt.MouseButton.MiddleButton:
                pass
            case Qt.MouseButton.RightButton:
                if self.transiency > 1:
                    self.controller.revert_state()
                else:
                    self.is_erasing = False
    
    def key_down(self, event: QKeyEvent):
        match event.key():
            case Qt.Key.Key_Space:
                self.controller.change_state(PanState.PanState, 1)
            case Qt.Key.Key_E:
                self.controller.change_state(DrawState.DrawState)
    
    def key_up(self, event: QKeyEvent):
        match event.key():
            case Qt.Key.Key_E:
                if self.transiency > 0:
                    if self.can_graduate:
                        self.transiency = 0
                    else:
                        self.controller.revert_state()
    
    def scroll(self, event: QWheelEvent):
        scroll_or_zoom(event, self.inputs, self.controller)

from .StateUtils import draw,erase,pan,scroll_or_zoom,expand
from .InputTracker import InputTracker
from . import DrawState
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
PanState: a state for moving around and zooming (planned).
Frequently gets enabled transiently, but not always.

Transiency is the idea that some modes should be less persistent than others.
In this case, activating this mode by the MMB from DrawState shouldn't be as permanent
as pressing the "Pan" button in the toolbar. This code uses three levels of transiency,
depending on how permanent the action is intended to be.
For semitransient actions, the app decides to stay or revert state based on if the user
utilized the state, like clicking before letting up on the space bar.

Transiency Levels:
0 - not even slightly transient. Normal state, like if pushed by a menu button
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
                self.is_panning = True
            case Qt.MouseButton.RightButton:
                pass
    
    def mouse_move(self, event: QMouseEvent):
        if self.is_panning:
            pan(event, self.inputs, self.controller)

    def mouse_up(self, event: QMouseEvent):
        # not necessary, but helps avoid stuttering for future mouse_down expansions
        if self.is_panning:
            expand(event, self.inputs, self.controller)

        match event.button():
            case Qt.MouseButton.LeftButton:
                self.is_panning = False
            case Qt.MouseButton.MiddleButton:
                if self.transiency > 1:
                    self.controller.revert_state()
                else:
                    self.is_panning = False

    def key_down(self, event: QKeyEvent):
        match event.key():
            case Qt.Key.Key_Space:
                self.controller.change_state(DrawState.DrawState)
            case Qt.Key.Key_E:
                self.controller.change_state(EraserState.EraserState, 1)

    def key_up(self, event: QKeyEvent):
        match event.key():
            case Qt.Key.Key_Space:
                if self.transiency > 0:
                    if self.can_graduate:
                        self.transiency = 0
                    else:
                        self.controller.revert_state()
    
    def scroll(self, event: QWheelEvent):
        if not self.is_panning: # prevent accidental pen size changes while MMB dragging
            scroll_or_zoom(event, self.inputs, self.controller)


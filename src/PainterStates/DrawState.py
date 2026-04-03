# from StateUtils import *
from .StateUtils import draw,erase,pan,scroll_or_zoom
from .InputTracker import InputTracker
# from .PanState import PanState
from . import PanState
from PyQt6.QtWidgets import (
    QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QMouseEvent,
    QKeyEvent,
    QWheelEvent,
)

class DrawState:
    def __init__(self, controller: QWidget, inputs: InputTracker, _: int):
        self.controller = controller
        self.inputs = inputs
        self.is_painting = False
        self.is_panning = False
        self.is_erasing = False

        # self.controller.parent.bar._draw_action.setHidden(True)

    def mouse_down(self, event: QMouseEvent):
        # print("Clicked while drawing")
        match event.button():
            case Qt.MouseButton.LeftButton:
                self.is_painting = True
            case Qt.MouseButton.MiddleButton:
                # self.is_panning = True
                self.controller.change_state(PanState.PanState, 2)
            case Qt.MouseButton.RightButton:
                self.is_erasing = True
    
    def mouse_move(self, event: QMouseEvent):
        if self.is_panning:
            pan(event, self.inputs, self.controller)
        elif self.is_erasing:
            erase(event, self.inputs, self.controller)
        elif self.is_painting:
            draw(event, self.inputs, self.controller)

    def mouse_up(self, event: QMouseEvent):
        match event.button():
            case Qt.MouseButton.LeftButton:
                self.is_painting = False
            case Qt.MouseButton.MiddleButton:
                self.is_panning = False
            case Qt.MouseButton.RightButton:
                self.is_erasing = False
    
    def key_down(self, event: QKeyEvent):
        match event.key():
            case Qt.Key.Key_Space:
                self.controller.change_state(PanState.PanState, 1)
    
    def key_up(self, event: QKeyEvent):
        match event.key():
            case Qt.Key.Key_Space:
                pass
    
    def scroll(self, event: QWheelEvent):
        scroll_or_zoom(event, self.inputs, self.controller)

"""
Not currently very utilized. Sometimes you need to know what buttons
are being pressed without having access to their state.
This class was built to track any relevant inputs, but has not turned out
to be useful in real life. I'm keeping it around for now, but it could be
that we can get on without it and it should get deleted.

The commented out lines are lines that could be useful, but aren't currently
being used by any state managers.
"""

class InputTracker:
    def __init__(self):
        # self.LMB = False
        # self.MMB = False
        # self.RMB = False
        self.prev_mouse_pos = None
        # self.mouse_pos = None
        # self.pressed_keys = set()
        self.mouse_down_pos = None

    def new_mouse_pos(self, event):
        self.prev_mouse_pos = event.position().toPoint()
    
    def mouse_down(self, event):
        self.prev_mouse_pos = event.position().toPoint()
        self.mouse_down_pos = event.position().toPoint()
    
    def mouse_up(self):
        self.mouse_down_pos = None
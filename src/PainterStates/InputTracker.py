class InputTracker:
    def __init__(self):
        # self.LMB = False
        # self.MMB = False
        # self.RMB = False
        self.prev_mouse_pos = None
        # self.mouse_pos = None
        self.pressed_keys = set()
    
    def new_mouse_pos(self, event):
        # print("Calculating new mouse position")
        # self.prev_mouse_pos = self.mouse_pos
        # self.mouse_pos = event.position().toPoint()
        self.prev_mouse_pos = event.position().toPoint()
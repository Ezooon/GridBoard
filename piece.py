from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.uix.behaviors import DragBehavior
from kivy.properties import ListProperty, StringProperty


class Piece(DragBehavior, Image):
    name = StringProperty('red.png')
    relative_pos = ListProperty([0, 0])

    def __init__(self, **kwargs):
        super(Piece, self).__init__(**kwargs)
        self.drag_timeout = 1000
        self._dragging_size = self.size
        self.drag_distance = 0
        self.size_hint = [None, None]
        self.drag_rectangle = [*self.pos, *self.size]

    def on_size(self, _, size):
        self.drag_rectangle = [*self.pos, *size]

    def on_touch_down(self, touch):
        re = super().on_touch_down(touch)
        if self.collide_point(*touch.pos):
            self._dragging_size = self.size.copy()
            self.center = touch.pos
            w = dp(50) if self.width < dp(50) else self.width + dp(10)
            h = dp(50) if self.height < dp(50) else self.height + dp(10)
            self.size = [w, h]
        return re

    def on_touch_up(self, touch):
        re = super().on_touch_up(touch)
        # if self.collide_point(*touch.pos):
        center = self.center.copy()
        self.size = self._dragging_size
        self.center_x = center[0]
        return re

    def on_pos(self, _, pos):
        self.drag_rectangle = [*pos, *self.size]
        if self.parent:
            self.relative_pos = [pos[0]-self.parent.center_x, pos[1]-self.parent.center_y]


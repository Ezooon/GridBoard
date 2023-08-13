from kivy.uix.image import Image
from kivy.metrics import dp, MetricsBase
from kivy.uix.behaviors import DragBehavior
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.lang import Builder

Builder.load_string("""
<Piece>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: root.rotation
            axis: 0, 0, 1
            origin: self.center
    canvas.after:
        PopMatrix

""")


class Piece(DragBehavior, Image):
    name = StringProperty('red.png')
    relative_pos = ListProperty([0, 0])
    rotation = NumericProperty(0)

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
        if self.collide_point(*touch.pos) and self.drag_timeout:
            self.parent.log.append([self, self.pos.copy()])
            self._dragging_size = self.size.copy()
            # self.center = touch.pos
            self.center_x = touch.pos[0]
            self.y = touch.pos[1]
            w = dp(50) if self.width < dp(50) else self.width + dp(10)
            h = dp(50) if self.height < dp(50) else self.height + dp(10)
            self.size = [w, h]
            self.put_on_top()
        return re

    def put_on_top(self):
        parent = self.parent
        parent.remove_widget(self)
        parent.add_widget(self)

    def on_touch_up(self, touch):
        re = super().on_touch_up(touch)
        if self.collide_point(*touch.pos):
            self.size = self._dragging_size
            click = self.parent.ids.grid.collide_cell(*touch.pos)
            self.center_x = click[2][0] if click else touch.pos[0]
            self.y = click[1][1] + dp(3) if click else self.y + dp(3)
        self.size = self._dragging_size
        return re

    def on_pos(self, _, pos):
        self.drag_rectangle = [*pos, *self.size]
        if self.parent:
            self.relative_pos = [pos[0]-self.parent.center_x, pos[1]-self.parent.center_y]

    def click_relative_pos(self):
        """decides if the relative pos is an index in the grid"""
        if not self.parent:
            return

        grid = self.parent.ids.grid
        x, y = self.relative_pos
        if abs(x) <= grid.cols and abs(y) <= grid.rows:
            box = grid.cells[int(x)][int(y)]
            self.center_x = box[0] + ((box[2] - box[0])/2)
            self.y = box[1] + dp(3)

    def get_relative_pos(self):
        click = self.parent.ids.grid.collide_cell(*self.center)
        if click and self.parent.ids.grid.click:
            # print(self.name, click)
            return click[0]
        d = MetricsBase().density
        x, y = self.relative_pos
        return [x/d, y/d]

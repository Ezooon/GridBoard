from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.uix.behaviors import DragBehavior
from kivy.properties import ListProperty, StringProperty, NumericProperty, ObjectProperty, BooleanProperty
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
    cell = ListProperty([-1, -1])
    rotation = NumericProperty(0)
    screen = ObjectProperty()
    draggable = BooleanProperty(True)

    def __init__(self, **kwargs):
        self.player = 'Player 1'
        super(Piece, self).__init__(**kwargs)
        self.drag_timeout = 1000
        self._dragging_size = self.size
        self.drag_distance = 0
        self.size_hint = [None, None]
        self.drag_rectangle = [*self.pos, *self.size]
        self._current_cell = [-1, -1]
        self.movable = True
        self.dies_sum = 1

    def __repr__(self):
        return f"<{self.name}, {self.cell}, {self.player}>"

    def on_size(self, _, size):
        self.drag_rectangle = [*self.pos, *size]

    def on_touch_down(self, touch):
        re = False
        if self.collide_point(*touch.pos):
            if self.draggable:
                re = super().on_touch_down(touch)
            else:
                re = True

            grid = self.screen.grid
            if tuple(self.cell) in list(grid.highlighted_kills.keys()) + list(grid.highlighted_cells.keys()) or \
                    not self.movable:
                return False
            if self.draggable:
                self._dragging_size = self.size.copy()
                self.center_x = touch.pos[0]
                self.y = touch.pos[1]
                w = dp(50) if self.width < dp(50) else self.width + dp(10)
                h = dp(50) if self.height < dp(50) else self.height + dp(10)
                self.size = [w, h]
            self.put_on_top()
            if self.cell != [-1, -1]:
                grid.on_touch_cell(self)
        return re

    def on_draggable(self, _, value):
        if value:
            self.drag_timeout = 0
            self.drag_distance = 1000
        else:
            self.drag_timeout = 1000
            self.drag_distance = 0

    def put_on_top(self):
        self.parent.remove_widget(self)
        self.screen.add_widget(self)

    def on_touch_up(self, touch):
        re = super().on_touch_up(touch)
        if self.collide_point(*touch.pos):
            self.size = self._dragging_size
            if self.draggable:
                click = self.screen.grid.collide_cell(*touch.pos)
                if click:
                    self.center_x = click[2][0]
                    self.y = click[1][1] + dp(3)
                    self.cell = click[0]
                else:
                    self.center_x = touch.pos[0]
                    self.y = self.y + dp(3)
                    self.cell = [-1, -1]
                self.screen.grid.on_touch_up(touch)
        self.size = self._dragging_size
        return re

    def on_pos(self, _, pos):
        self.drag_rectangle = [*pos, *self.size]
        if self.screen:
            self.relative_pos = [pos[0]-self.screen.center_x, pos[1]-self.screen.center_y]

    def new_cell(self):
        return self.cell

    def on_cell(self, _, cell):
        """decides if the relative pos is an index in the grid"""
        if not self.screen or cell == self._current_cell:
            return
        grid = self.screen.ids.grid
        x, y = cell
        _x, _y = self._current_cell

        if cell == [-1, -1]:
            if self in grid.cells_pieces[_x][_y]:
                grid.cells_pieces[_x][_y].remove(self)
                self.screen.log.append([self, self.pos.copy()])
            return

        if 0 <= abs(x) <= grid.cols and 0 <= abs(y) <= grid.rows:
            box = grid.cells[int(x)][int(y)]
            self.screen.log.append([self, self.pos.copy()])
            self.center_x = box[0] + ((box[2] - box[0])/2)
            self.y = box[1] + dp(3)

            if self in grid.cells_pieces[_x][_y]:
                grid.cells_pieces[_x][_y].remove(self)

            grid.cells_pieces[x][y].append(self)
            self._current_cell = cell

    def get_cell(self):
        click = self.screen.ids.grid.collide_cell(*self.center)
        if click and self.screen.ids.grid.click:
            self.cell = click[0]
            return self.cell
        self.cell = [-1, -1]
        return self.cell

    def blink(self):
        color = self.color.copy()
        anim = Animation(color=[1, 1, 1, 0], d=0.2)
        anim.start(self)
        anim.on_complete = lambda m: Animation(color=color, d=0.2).start(self)

    def on_killed(self):
        pass

    def move(self, cell):
        x, y = cell
        _x, _y = self._current_cell
        dx, dy = x - _x, y - _y
        fx = -1 if dx < 0 else 1
        fy = -1 if dy < 0 else 1

        def add_to_cell(*cell):
            nx, ny = cell
            ox, oy = self._current_cell
            self.cell = [ox+nx, ny+oy]

        if not self.screen.grid.show_movement:
            self.cell = cell
            return
        elif self.screen.grid.show_movement == 'smooth':
            a,b , a_,b_ = self.screen.grid.cells[x][y]
            anim = Animation(center_x=a+((a_-a)/2), y=b + dp(3), d=0.3)
            anim.start(self)
            anim.on_complete = lambda m: add_to_cell(dx, dy)
            return

        dx, dy = abs(dx), abs(dy)

        def add_to_cell(*cell):
            nx, ny = cell
            ox, oy = self._current_cell
            self.cell = [ox+nx, ny+oy]

        if dx > dy:
            for c in range(dx):
                Clock.schedule_once(lambda dt: add_to_cell(fx, 0), (c + 1) * 0.2)
            for r in range(dy):
                Clock.schedule_once(lambda dt: add_to_cell(0, fy), (r + c + 1) * 0.2)
        elif dx < dy:
            for r in range(dy):
                Clock.schedule_once(lambda dt: add_to_cell(0, fy), (r + 1) * 0.2)
            for c in range(dx):
                Clock.schedule_once(lambda dt: add_to_cell(fx, 0), (c + r + 1) * 0.2)
        else:
            for i in range(dx):
                Clock.schedule_once(lambda dt: add_to_cell(fx, fy), (i + 1) * 0.2)


# Todo add sounds on_touch_up

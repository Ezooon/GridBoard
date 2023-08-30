from kivy.graphics import Rectangle, Color
from kivymd.uix.floatlayout import FloatLayout
from kivymd.uix.card import MDSeparator
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty
from kivy.lang import Builder
from importlib.util import spec_from_file_location, module_from_spec
from kivy.metrics import dp

Builder.load_file("grid/grid.kv")


def collide(box, x, y):
    return box[0] <= x <= box[2] and box[1] <= y <= box[3]


class Grid(FloatLayout):
    outline = BooleanProperty(True)
    cols = NumericProperty(1)
    background = BooleanProperty(False)
    rows = NumericProperty(1)
    rows_separators = ListProperty([])
    cols_separators = ListProperty([])
    line_color = ListProperty([0, 0, 0, 1])
    cells = ListProperty([])
    cells_pieces = ListProperty([])
    source = StringProperty("")
    turn = StringProperty("")
    click = BooleanProperty(True)
    fit_screen = BooleanProperty(False)
    exception_log = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._size = None
        self._spec = None
        self.code = None
        self.cell_size = None
        self.current_piece = None
        self.highlighted_cells = dict()
        self.highlighted_kills = dict()
        self.show_movement = None
        self.change_turn_on = "piece_move"
        self.players = []
        self.dies_sum = 1

    def set(self, game_set):
        set_grid = game_set.grid
        self.cols = set_grid["cols"]
        self.rows = set_grid["rows"]
        self.outline = set_grid["border"]
        self.background = set_grid["background"]
        color = set_grid["line_color"]
        self.line_color = [c/255 for c in color]
        w, h = set_grid["size"]
        self._size = dp(w), dp(h)
        self.size = dp(w), dp(h)
        self.source = game_set.grid_background
        self.fit_screen = set_grid["fit_screen"]
        self.click = set_grid["click"]

        if game_set.code_path:
            self._spec = spec_from_file_location("code", game_set.code_path)
            self.code = module_from_spec(self._spec)
            try:
                self._spec.loader.exec_module(self.code)
            except Exception as E:
                pass

    def restart(self):
        self.current_piece = None
        self.clean()
        self.dies_sum = 1
        self.update_cells()
        if self.players:
            self.turn = self.players[-1]

    def clean(self):
        self.highlighted_cells = dict()
        self.highlighted_kills = dict()
        self.exception_log = []

    def on_rows(self, _, rows):
        row_height = self.height / rows
        self.clear_widgets(self.rows_separators)
        self.rows_separators = []

        for i in range(rows-1):
            sep = Separator(y=self.y + (row_height * (i+1)), x=self.x, color=self.line_color)
            self.rows_separators.append(sep)
            self.add_widget(sep)
            sep.height = dp(3)

        self.update_cells()

    def on_cols(self, _, cols):
        col_width = self.width / cols
        self.clear_widgets(self.cols_separators)
        self.cols_separators = []

        for i in range(cols-1):
            sep = Separator(y=self.y, x=self.x + (col_width * (i+1)), color=self.line_color, orientation='vertical')
            self.cols_separators.append(sep)
            self.add_widget(sep)
            sep.width = dp(3)

        self.update_cells()

    def update_cells(self):
        self.cell_size = [self.width / self.cols, self.height / self.rows]

        xs = [self.x] + [col.x for col in self.cols_separators] + [self.width + self.x]
        ys = [self.y] + [row.y for row in self.rows_separators] + [self.top]
        cells = []
        cells_piece = []
        for c in range(self.cols):
            cells.append([])
            cells_piece.append([])
            for r in range(self.rows):
                cells[c].append([xs[c], ys[r], xs[c+1], ys[r+1]])
                cells_piece[c].append([])
        self.cells = cells
        self.cells_pieces = cells_piece

    def collide_cell(self, x, y):
        if not self.click:
            return None  # [[-1, -1], [x, y, x, y], [x, y]]
        for c in range(self.cols):
            for r in range(self.rows):
                box = self.cells[c][r]
                if collide(box, x, y):
                    return [c, r], box, [box[0] + ((box[2] - box[0])/2), box[1] + ((box[3] - box[1])/2)]

    def on_pos(self, _, value):
        cp = self.cells_pieces.copy()
        self.on_rows(_, self.rows)
        self.on_cols(_, self.cols)
        if self.fit_screen:
            self.on_fit_screen(_, True)
        self.cells_pieces = cp

    def on_size(self, _, value):
        cp = self.cells_pieces.copy()
        self.on_rows(_, self.rows)
        self.on_cols(_, self.cols)
        if self.fit_screen:
            self.on_fit_screen(_, True)
        self.cells_pieces = cp

    def on_line_color(self, _, color):
        for sep in self.rows_separators + self.cols_separators:
            sep.color = color

    def decode(self):
        piece = self.current_piece
        boxs = []
        kill_boxs = []
        self.code.self = piece
        self._spec.loader.exec_module(self.code)
        self.highlighted_kills = dict()
        self.highlighted_cells = dict()

        logic = self.code.logic[piece.name]
        if "movements" in logic:
            for movement in logic['movements']:
                if not len(movement) >= 2:
                    self.exception_log.append("movement should be a tuple of (bool, (movement,), actions)")
                    break
                con, move, actions = movement if len(movement) > 2 else movement + ([],)
                if not 0 < len(move) < 5:
                    self.exception_log.append("movements can only be a tuple of (directions: list, steps=0, "
                                              "jump=False, allow_staking=False). only directions is requiered")
                    break
                if con:
                    cells = self.cells_from_movement(*move)
                    for cell in cells:
                        self.highlighted_cells[tuple(cell)] = actions

                    boxs += [self.cells[x][y] for x, y in cells]

        if "kills" in logic:
            for kill in logic['kills']:
                if not len(kill) >= 2:
                    self.exception_log.append("kills should be a tuple of (bool, (movement,), actions)")
                    break
                con, move, actions = kill if len(kill) > 2 else kill + ([self.kill([piece.new_cell])],)
                if not 0 < len(move) < 5:
                    self.exception_log.append("movements can only be a tuple of (directions: list, steps=0, "
                                              "jump=False, allow_staking=False). only directions is requiered")
                    break
                if con:
                    cells = self.foe_in_direction(*move)
                    for cell in cells:
                        self.highlighted_kills[tuple(cell)] = actions

                    kill_boxs += [self.cells[x][y] for x, y in cells]

        if "on_press" in logic:
            for func, args in logic["on_press"]:
                func(*args)

        return boxs, kill_boxs

    def on_touch_cell(self, piece):
        self.current_piece = piece
        boxs = []
        kill_boxs = []
        if self.code:
            # boxs, kill_boxs = self.decode()
            try:
                boxs, kill_boxs = self.decode()
            except Exception as E:
                self.exception_log.append(str(E))

        self.canvas.after.clear()
        with self.canvas.after:
            for box in boxs:
                if box:
                    Color(0, 0, 1, 0.5)
                    Rectangle(pos=box[:-2], size=self.cell_size)
            for box in kill_boxs:
                if box:
                    Color(1., 0, 0, 0.5)
                    Rectangle(pos=box[:-2], size=self.cell_size)

    def on_touch_down(self, touch):
        super(Grid, self).on_touch_down(touch)
        self.canvas.after.clear()

    def on_touch_up(self, touch):
        super(Grid, self).on_touch_down(touch)
        cell = self.collide_cell(*touch.pos)
        if cell:
            if tuple(cell[0]) in self.highlighted_kills.keys():
                self.current_piece.move(cell[0])
                for func, args in self.highlighted_kills[tuple(cell[0])]:
                    func(*args)

            elif tuple(cell[0]) in self.highlighted_cells.keys():
                self.current_piece.move(cell[0])
                for func, args in self.highlighted_cells[tuple(cell[0])]:
                    func(*args)
                self.highlighted_cells = dict()

        return False

    def piece_in_cell(self, piece_name, cell):
        x, y = cell
        pieces = self.cells_pieces[x][y]
        for piece in pieces:
            if piece.name == piece_name:
                return True
        return False

    def cells_from_movement(self, directions, steps=0, jump=False, allow_staking=False):
        if not self.current_piece:
            return []
        directions = directions.copy()

        p = self.current_piece
        if steps == 0:
            steps = max(self.rows, self.cols) - 1
        pd = p.cell
        cells = []

        for i in range(steps):
            ds = directions.copy()
            for d in ds:
                x, y = (d[0] * (i + 1)) + pd[0], (d[1] * (i + 1)) + pd[1]
                if self.rows <= y or y < 0 or self.cols <= x or x < 0:
                    continue
                if self.cells_pieces[x][y] and not jump:
                    directions.remove(d)
                    continue
                if self.cells_pieces[x][y] and not allow_staking:
                    continue
                cells.append([x, y])
        return cells

    def foe_in_direction(self, directions, steps=0, jump=False, allow_staking=True):
        if not self.current_piece:
            return []
        directions = directions.copy()

        p = self.current_piece
        if steps == 0:
            steps = max(self.rows, self.cols) - 1
        pd = p.cell
        cells = []

        for i in range(steps):
            ds = directions.copy()
            for d in ds:
                x, y = (d[0] * (i + 1)) + pd[0], (d[1] * (i + 1)) + pd[1]
                if self.rows <= y or y < 0 or self.cols <= x or x < 0:
                    continue

                pieces = self.cells_pieces[x][y]
                if pieces:
                    if pieces[-1].player != p.player and allow_staking:
                        cells.append([x, y])
                    if not jump:
                        directions.remove(d)
                elif not allow_staking:
                    cells.append([x, y])

        return cells

    def pieces_from_movement(self, directions, steps=0, jump=False):
        if not self.current_piece:
            return []
        directions = directions.copy()

        p = self.current_piece
        if steps == 0:
            steps = max(self.rows, self.cols) - 1
        pd = p.cell
        cells = []

        for i in range(steps):
            ds = directions.copy()
            for d in ds:
                x, y = (d[0] * (i + 1)) + pd[0], (d[1] * (i + 1)) + pd[1]
                if self.rows <= y or y < 0 or self.cols <= x or x < 0:
                    continue

                if self.cells_pieces[x][y]:
                    cells.append([x, y])
                    if not jump:
                        directions.remove(d)
                        continue
        return cells

    def in_direction(self, other_piece_name, directions, steps=0, jump=False):
        """checks the cells in the direction and return the cells that contains `other_piece`"""
        if not self.current_piece:
            return False
        directions = directions.copy()

        p = self.current_piece
        if steps == 0:
            steps = max(self.rows, self.cols) - 1
        pd = p.cell
        cells = []
        for i in range(steps):
            ds = directions.copy()
            for d in ds:
                x, y = (d[0] * (i + 1)) + pd[0], (d[1] * (i + 1)) + pd[1]
                if self.rows <= y or y < 0 or self.cols <= x or x < 0:
                    continue
                for piece in self.cells_pieces[x][y]:
                    if not jump and piece.player == p.player:
                        if d in directions:
                            directions.remove(d)
                        if [x, y] in cells:
                            cells.remove([x, y])
                        continue

                    if other_piece_name == piece.name:
                        cells.append([x, y])
                        if not jump:
                            if d in directions:
                                directions.remove(d)
        return cells

    def to_cell(self, cell):
        x, y = cell
        _x, _y = self.current_piece.cell
        dx, dy = x - _x, y - _y
        return [[dx, dy]]

    def move(self, o_cell, n_cell, exclude_self=False):
        return self._move, (o_cell, n_cell, exclude_self)

    def _move(self, o_cell, n_cell, exclude_self):
        if callable(o_cell):
            ox, oy = o_cell()
        else:
            ox, oy = o_cell

        if callable(n_cell):
            x, y = n_cell()
        else:
            x, y = n_cell

        if self.rows <= y or y < 0 or self.cols <= x or x < 0:
            self.exception_log.append("new cell is not in the grid")
            return
        if self.rows <= oy or oy < 0 or self.cols <= ox or ox < 0:
            self.exception_log.append("old cell is not in the grid")
            return

        piece = self.cells_pieces[ox][oy][-1]
        # for piece in pieces:
        #     if piece == self.current_piece and exclude_self:
        #         continue
        piece.move((x, y))

    def kill(self, cells):
        return self._kill, (cells,)

    def _kill(self, cells):
        for cell in cells:
            if callable(cell):
                x, y = cell()
            else:
                x, y = cell

            print(self.cells_pieces[x][y])
            for piece in self.cells_pieces[x][y]:
                if self.current_piece == piece:
                    continue

                on_killed = self.code.logic[piece.name].get("on_killed")

                if on_killed:
                    for func, args in on_killed:
                        func(*args)
                    continue

                self.cells_pieces[x][y].remove(piece)
                piece.cell = [-1, -1]
                if piece.parent:
                    piece.parent.remove_widget(piece)
                self.parent.ids.get(piece.player).add_widget(piece)
        self.highlighted_kills = dict()

    def next_turn(self):
        if not self.players:
            return
        if not self.turn:
            self.turn = self.players[0]
            return
        i = self.players.index(self.turn)
        if i + 1 < len(self.players):
            self.turn = self.players[i+1]
        else:
            self.turn = self.players[0]
        pieces = self.parent.pieces
        for piece in pieces:
            if piece.player == self.turn:
                piece.blink()

    def on_turn(self, _, turn):
        pieces = self.parent.pieces
        for piece in pieces:
            if piece.player == turn:
                piece.movable = True
                piece.put_on_top()
                piece.disabled = False
            else:
                piece.movable = False
                piece.disabled = True

    def previous_turn(self):
        if not self.turn:
            self.turn = self.players[-1]
            return
        i = self.players.index(self.turn)
        self.turn = self.players[i-1]

    def on_fit_screen(self, _, fit):
        w, h = self._size
        ratio = w/h
        if fit:
            if self.parent:
                sw, sh = sz = self.parent.size
                if sh < sw:
                    height = sh - dp(30)
                    width = height * ratio
                    if width > sw:
                        self.width = sw - dp(30)
                        height = self.width / ratio
                    self.height = height
                elif sw < sh:
                    width = sw - dp(30)
                    height = width / ratio
                    if height > sh:
                        self.height = sh - dp(30)
                        width = self.height * ratio
                    self.width = width
                else:
                    self.width = self.height = min(sz) - dp(50)
        else:
            self.size = self._size


class Separator(MDSeparator):
    image = StringProperty('')

# to make suer the cells_pieces follow the UI.
# for y in reversed(list(range(self.rows))):
#     for x in range(self.cols):
#         [print(p.name, end="\t") for p in self.cells_pieces[x][y]] or print("---------", end="\t")
#     print()
# print()

from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.card import MDSeparator

from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty
from kivy.lang import Builder
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
    source = StringProperty("")
    click = BooleanProperty(True)

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
        xs = [self.x] + [col.x for col in self.cols_separators] + [self.right]
        ys = [self.y] + [row.y for row in self.rows_separators] + [self.top]
        cells = []
        for c in range(self.cols):
            cells.append([])
            for r in range(self.rows):
                cells[c].append([xs[c], ys[r], xs[c+1], ys[r+1]])
        self.cells = cells

    def collide_cell(self, x, y):
        if not self.click:
            return None  # [[-1, -1], [x, y, x, y], [x, y]]
        for c in range(self.cols):
            for r in range(self.rows):
                box = self.cells[c][r]
                if collide(box, x, y):
                    return [c, r], box, [box[0] + ((box[2] - box[0])/2), box[1] + ((box[3] - box[1])/2)]

    def on_pos(self, _, value):
        self.on_rows(_, self.rows)
        self.on_cols(_, self.cols)

    def on_line_color(self, _, color):
        for sep in self.rows_separators + self.cols_separators:
            sep.color = color

    def set(self, game_set):
        set_grid = game_set.grid
        self.cols = set_grid["cols"]
        self.rows = set_grid["rows"]
        self.outline = set_grid["border"]
        self.background = set_grid["background"]
        color = set_grid["line_color"]
        self.line_color = [c/255 for c in color]
        w, h = set_grid["size"]
        self.size = dp(w), dp(h)
        self.source = game_set.grid_background
        self.click = set_grid["click"]


class Cell(ButtonBehavior, MDAnchorLayout):
    index = NumericProperty(0)


class Separator(MDSeparator):
    image = StringProperty('')

from kivy.clock import Clock
from kivy.metrics import MetricsBase
from kivy.properties import StringProperty

from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivy.lang import Builder

Builder.load_file('grid_setup/grid_setup.kv')


class GridSetup(MDScreen):
    source = StringProperty("")

    def on_enter(self):
        Clock.schedule_once(self.setup, 0)

    def setup(self, dt):
        editing_set = App.get_running_app().root.editing_set
        self.ids.grid.set(editing_set)
        self.ids.text_.active = False
        self.ids.background_.active = editing_set.grid["background"]
        self.ids.square.active = editing_set.grid["size"][0] == editing_set.grid["size"][1]
        self.ids.width.value = editing_set.grid["size"][0]
        self.ids.height.value = editing_set.grid["size"][1]
        self.ids.outline.value = editing_set.grid["border"]
        self.ids.colslider.value = editing_set.grid["cols"]
        self.ids.rowslider.value = editing_set.grid["rows"]
        self.ids.red.value = editing_set.grid["line_color"][0]
        self.ids.green.value = editing_set.grid["line_color"][1]
        self.ids.blue.value = editing_set.grid["line_color"][2]
        if len(editing_set.grid["line_color"]) == 4:
            self.ids.alpha.value = editing_set.grid["line_color"][3]
        else:
            self.ids.alpha.value = 255

        self.source = editing_set.grid_background

    def save(self):
        editing_set = App.get_running_app().root.editing_set
        grid = self.ids.grid
        line_color = grid.line_color
        d = MetricsBase().density
        x, y = grid.size
        editing_set.grid = {
            "cols": grid.cols,
            "rows": grid.rows,
            "border": True,
            "background": grid.background,
            "line_color": [c * 255 for c in line_color],
            "size": [x/d, y/d]
        }

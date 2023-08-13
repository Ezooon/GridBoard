from kivy.clock import Clock
from kivy.metrics import dp, MetricsBase
from die import Die
from pieces.piece import Piece
from kivymd.uix.screen import MDScreen
from kivy.properties import ListProperty, BooleanProperty
from kivy.app import App
from kivy.lang import Builder
from kivy.animation import Animation

Builder.load_file('game_screen/game_screen.kv')


class GameScreen(MDScreen):
    pieces = ListProperty()
    dies = ListProperty()
    editing = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cell_size = None
        self.grid = None
        self.log = []

    def on_enter(self):
        if self.editing:
            game_set = App.get_running_app().root.editing_set
        else:
            game_set = App.get_running_app().root.game_set

        if game_set.background:
            self.background = game_set.background
            self.md_bg_color = 1, 1, 1, 1

        grid = self.grid = self.ids.grid
        grid.set(game_set)
        self.cell_size = [grid.width / grid.cols, grid.height / grid.rows]

        Clock.schedule_once(lambda x: self.setup(game_set), 0)

    def setup(self, game_set):
        piece_size = [min(self.cell_size) - dp(6)] * 2
        pieces = game_set.pieces

        self.clear_widgets(self.pieces + self.dies)
        self.pieces = []
        self.dies = []

        for piece_key in pieces.keys():
            piece = pieces[piece_key]
            for i in range(piece["num"]):
                pos = [dp(10), dp(10)]
                if i < len(piece['poses']):
                    pos = piece['poses'][i]
                auto = piece["auto_size"]
                piexe = Piece(
                    source=piece["path"], relative_pos=[dp(pos[0]), dp(pos[1])],
                    size=piece_size if auto else piece["size"],
                    rotation=piece["rotation"], color=piece["color"],
                    name=piece_key)
                self.add_widget(piexe)
                piexe.click_relative_pos()
                self.pieces.append(piexe)

        dies = game_set.dies
        for i in range(dies[0]):
            pos = [0, 0]
            if i < len(dies[1]):
                pos = dies[1][i]
            die = Die(relative_pos=[dp(pos[0]), dp(pos[1])], size=[dp(50), dp(50)])
            self.add_widget(die)
            self.dies.append(die)

        self.on_size(self, self.size)

    def on_size(self, _, size):
        for piece in self.pieces:
            piece.pos = [piece.relative_pos[0] + self.center_x, piece.relative_pos[1] + self.center_y]

        for die in self.dies:
            die.pos = [die.relative_pos[0] + self.center_x, die.relative_pos[1] + self.center_y]

    def save(self):
        if self.editing:
            game_set = App.get_running_app().root.editing_set
        else:
            game_set = App.get_running_app().root.game_set
        d = MetricsBase().density
        for piece in self.pieces:
            game_set.pieces[piece.name]['poses'] = []

        for piece in self.pieces:
            x, y = piece.get_relative_pos()
            game_set.pieces[piece.name]['poses'].append([x, y])

        dies = [len(self.dies), []]
        for i in range(dies[0]):
            x, y = self.dies[i].relative_pos
            dies[1].append([x/d, y/d])
        game_set.dies = dies

        game_set.grid["click"] = self.ids.click.active

    def restart(self):
        root = App.get_running_app().root
        self.setup(root.game_set)

    def undo(self):
        if self.log:
            piece, last_pos = self.log.pop(-1)
            # piece.pos = last_pos
            Animation(pos=last_pos, d=0.1).start(piece)

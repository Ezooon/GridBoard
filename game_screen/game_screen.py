from kivy.clock import Clock
from kivy.metrics import dp, MetricsBase
from die import Die
from piece import Piece
from kivymd.uix.screen import MDScreen
from kivy.properties import ListProperty, BooleanProperty
from kivy.app import App
from kivy.lang import Builder

Builder.load_file('game_screen/game_screen.kv')


class GameScreen(MDScreen):
    pieces = ListProperty()
    dies = ListProperty()
    editing = BooleanProperty(False)

    def on_enter(self):
        Clock.schedule_once(self.setup, 0)

    def setup(self, dt):
        if self.editing:
            game_set = App.get_running_app().root.editing_set
        else:
            game_set = App.get_running_app().root.game_set

        if game_set.background:
            self.background = game_set.background
            self.md_bg_color = 1, 1, 1, 1

        grid = self.ids.grid
        grid.set(game_set)
        cell_size = [grid.width / grid.cols, grid.height / grid.rows]

        piece_size = [min(cell_size) - dp(8),] * 2
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
                piexe = Piece(source=piece["path"], relative_pos=[dp(pos[0]), dp(pos[1])], size=piece_size, name=piece_key)
                self.add_widget(piexe)
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
        game_set = App.get_running_app().root.editing_set
        d = MetricsBase().density
        for piece in self.pieces:
            game_set.pieces[piece.name]['poses'] = []

        for piece in self.pieces:
            x, y = piece.relative_pos
            game_set.pieces[piece.name]['poses'].append([x/d, y/d])

        dies = [len(self.dies), []]
        for i in range(dies[0]):
            x, y = self.dies[i].relative_pos
            dies[1].append([x/d, y/d])
        game_set.dies = dies

    # def restart(self):
    #     self.clear_widgets(self.pieces + self.dies)
    #     self.pieces = []
    #     self.dies = []
    #
    #     for piece_key in pieces.keys():
    #         piece = pieces[piece_key]
    #         for i in range(piece["num"]):
    #             pos = [dp(10), dp(10)]
    #             if i < len(piece['poses']):
    #                 pos = piece['poses'][i]
    #             piexe = Piece(source=piece["path"], relative_pos=[dp(pos[0]), dp(pos[1])], size=piece_size, name=piece_key)
    #             self.add_widget(piexe)
    #             self.pieces.append(piexe)


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
    log = ListProperty()
    editing = BooleanProperty(False)
    debug = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cell_size = [10, 10]
        self.grid = None
        # self.log = []

    def on_enter(self):
        if self.editing:
            game_set = App.get_running_app().root.editing_set
        else:
            game_set = App.get_running_app().root.game_set

        self.debug = game_set.init["debug"]

        if game_set.background:
            self.background = game_set.background
            self.md_bg_color = 1, 1, 1, 1

        grid = self.grid = self.ids.grid
        self.grid.clean()
        grid.set(game_set)
        if self.editing:
            grid.code = None
        self.cell_size = [grid.width / grid.cols, grid.height / grid.rows]
        for s in ["Player 1", "Player 2", "Player 3", "Player 4"]:
            self.ids[s].clear_widgets()

        Clock.schedule_once(lambda x: self.setup(game_set), 0)

    def setup(self, game_set):
        piece_size = [min(self.cell_size) - dp(6)] * 2
        pieces = game_set.pieces

        self.clear_widgets(self.pieces + self.dies)
        self.pieces = []
        self.dies = []

        player = 'Player 1'
        players = set()
        pos = [dp(10), dp(10)]

        for piece_key in pieces.keys():
            piece = pieces[piece_key]
            if "player" in piece.keys():
                player = piece['player']
            for i in range(piece["num"]):
                if i < len(piece['poses']):
                    pos = piece['poses'][i]
                cell = pos
                if 'cells' in piece.keys() and i < len(piece['cells']):
                    cell = piece["cells"][i]
                draggable = piece["draggable"] if not self.editing else True

                auto = piece["auto_size"]
                piexe = Piece(
                    screen=self,
                    source=piece["path"], relative_pos=[dp(pos[0]), dp(pos[1])],
                    size=piece_size if auto else piece["size"],
                    rotation=int(piece["rotation"]), color=piece["color"],
                    name=piece_key, draggable=draggable)
                self.add_widget(piexe)
                piexe.cell = cell
                piexe.player = player
                players.add(player)
                self.pieces.append(piexe)

        self.grid.players = sorted(list(players))

        dies = game_set.dies
        for i in range(dies['num']):
            pos = [0, 0]
            if i < len(dies["poses"]):
                pos = dies["poses"][i]
            auto = dies["auto_size"]
            draggable = piece["draggable"] if not self.editing else True
            die = Die(relative_pos=[dp(pos[0]), dp(pos[1])],
                      size=piece_size if auto else dies["size"],
                      rotation=int(dies["rotation"]), color=dies["color"],
                      draggable=draggable)
            die.callback = self.sum_dies
            self.add_widget(die)
            self.dies.append(die)
            die.pos = [die.relative_pos[0] + self.center_x, die.relative_pos[1] + self.center_y]

        self.log = []

    def sum_dies(self):
        s = 0
        for die in self.dies:
            s += die.top_face
        self.grid.dies_sum = s
        if self.grid.change_turn_on == 'die_roll':
            self.grid.next_turn()

    def on_size(self, _, size):
        grid = self.grid
        if not grid: return
        _piece_size = [min(self.cell_size) - dp(6)] * 2
        self.cell_size = [grid.width / grid.cols, grid.height / grid.rows]
        piece_size = [min(self.cell_size) - dp(6)] * 2
        for piece in self.pieces:
            if piece.size == _piece_size:
                piece.size = piece_size

            if piece.cell != [-1, -1]:
                x, y = piece.cell
                box = grid.cells[int(x)][int(y)]
                piece.center_x = box[0] + ((box[2] - box[0]) / 2)
                piece.y = box[1] + dp(3)
                if piece not in grid.cells_pieces[x][y]:
                    grid.cells_pieces[x][y].append(piece)

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
            game_set.pieces[piece.name]['cells'] = []

        for piece in self.pieces:
            x, y = piece.relative_pos
            game_set.pieces[piece.name]['poses'].append([x/d, y/d])
            game_set.pieces[piece.name]['cells'].append(piece.get_cell())

        dies_poses = []
        for die in self.dies:
            x, y = die.relative_pos
            dies_poses.append([x/d, y/d])

        game_set.dies["poses"] = dies_poses
        game_set.grid["click"] = self.ids.click.active

    def restart(self):
        root = App.get_running_app().root
        self.setup(root.game_set)
        self.grid.restart()
        self.log = []
        for s in ["Player 1", "Player 2", "Player 3", "Player 4"]:
            self.ids[s].clear_widgets()

    def undo(self):
        if self.log:
            piece, last_pos = self.log.pop(-1)
            # piece.pos = last_pos
            anim = Animation(pos=last_pos, d=0.1)
            anim.start(piece)
            anim.on_complete = lambda w: w.get_cell()

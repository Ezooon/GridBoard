from os import listdir, path, makedirs, environ
from random import randint
from kivy.core.window import Window
from kivymd.toast import toast
from kivymd.uix.screenmanager import MDScreenManager
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty
from kivy.utils import platform
from kivymd.app import MDApp
from game_set import GameSet
import webbrowser

environ["KIVY_ORIENTATION"] = "portrait"

root_path = path.expanduser('~')
games_path = path.join(root_path, 'Documents', 'GridBord')
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

    root_path = primary_external_storage_path()
    games_path = path.join(root_path, 'GridBord')
    Window.softinput_mode = 'below_target'
credit = """
Developer:
    GridBoard by Ezooon licensed MIT: [ref=https://github.com/Ezooon/GridBoard][u]https://github.com/Ezooon/GridBoard[/u][/ref]
    email: mreisevil@gmail.com, EZ000N@outlook.com
    githup: [ref=https://github.com/Ezooon][u]https://github.com/Ezooon[/u][/ref]
    linkedin: [ref=https://www.linkedin.com/in/ezooon/][u]https://www.linkedin.com/in/ezooon/[/u][/ref]
    

Chess Board:
    "Simple Checkerboard" by greysondn licensed CC0: [ref=https://opengameart.org/content/simple-checkerboard][u]https://opengameart.org/content/simple-checkerboard[/u][/ref]
    
Chess Pieces:
    "Chess Pieces and Board Squares" by JohnPablok Licenced CC-BY-SA 3.0: [ref=https://opengameart.org/content/chess-pieces-and-board-squares][u]https://opengameart.org/content/chess-pieces-and-board-squares[/u][/ref]
    >> i changed the orientation of the white pieces.
    
Ludo:
    "Ludo" by khurs10101 licensed CC-BY 4.0: [ref=https://opengameart.org/content/ludo][u]https://opengameart.org/content/ludo[/u][/ref]

Application Background:
    "Ruind City Background" by TokyoGeisha licensed CC0: [ref=https://opengameart.org/content/ruined-city-background][u]https://opengameart.org/content/ruined-city-background[/u][/ref]

Default Grid Background:
    "Bamboo Wood Seamless 1k" by YCbCr licenced CC0: [ref=https://opengameart.org/content/bamboo-wood-seamless-1k][u]https://opengameart.org/content/bamboo-wood-seamless-1k[/u][/ref]
    
Default Pieces:
    "Neon Sticks" by ki2kid licenced CC-BY 4.0: [ref=https://opengameart.org/content/neon-sticks][u]https://opengameart.org/content/neon-sticks[/u][/ref]
    >> i used the nodes to make new pieces by changing the color
"""


class Game(MDScreenManager):
    game_set = ObjectProperty()
    """the active game set"""

    editing_set = ObjectProperty(GameSet(name="", external=True), allownone=True)
    """the set that is being edited"""

    new = BooleanProperty(False)
    """True if editing_set is a new set and not an existing set"""

    game_sets = ListProperty([])
    """all the installed game sets"""

    def __init__(self, **kwargs):
        self.credit = credit
        super(Game, self).__init__(**kwargs)
        self.get_game_sets()

    def get_game_sets(self):
        if not path.exists(games_path):
            makedirs(games_path)
        self.game_sets = []
        sets = listdir(games_path)
        for game_set in sets:
            self.game_sets.append(GameSet(name=game_set, external=True))

        sets = listdir("assets/game_sets")
        for game_set in sets:
            self.game_sets.append(GameSet(name=game_set))

    def on_editing_set(self, _, editing_set):
        self.ids.editing_set_text_field.text = editing_set.name

    def new_game_set(self):
        self.current = 'new_game'
        self.new = True
        self.editing_set = GameSet("")
        self.ids.editing_set_text_field.text = ""

    def editing_set_save(self):
        self.editing_set.name = name = self.ids.editing_set_text_field.text
        if not name:
            toast("invalid name")
            return
        if not self.editing_set.pieces:
            toast("you need pieces to play!")
            return
        if self.new:
            for gset in self.game_sets:
                if name == gset.name:
                    toast("used name")
                    return
        if self.editing_set.save(self.new):
            self.current = 'themes_assets'
            self.new = False
            self.game_sets = []
            self.get_game_sets()

    def open_url(self, url):
        webbrowser.open(url)


class GridBoard(MDApp):
    def build(self):
        if platform == 'android':
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

#        self.icon = 'logo.ico'
        self.theme_cls.theme_style = "Dark"
        colors = ['Pink', 'Indigo', 'Blue',
                  'LightBlue', 'Cyan', 'Teal', 'Green', 'LightGreen', 'Amber', 'Orange', 'DeepOrange',
                  'BlueGray']
        self.theme_cls.primary_palette = colors[randint(0, len(colors) - 1)]
        return Game()


if __name__ == '__main__':
    game = GridBoard()
    game.run()

# todo allow resource packs to contain backgrounds, separators, grid background, pieces, theme primary color and style.
#   i just realized i can make Yu Gi Oh field.
# to create an atlas python -m kivy.atlas <basename> <size> <list of images...>
# -m kivy.atlas medals 46x46 achievements_2.png

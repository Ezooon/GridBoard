import os
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
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
    from android.storage import primary_external_storage_path

    root_path = primary_external_storage_path()
    games_path = path.join(root_path, 'GridBord')
    Window.softinput_mode = 'below_target'

with open('Credit.txt', 'r') as f:
    credit = f.read()  # Credit the die artest and the sound one too.


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

        # TO MAKE CHANGES TO ALL GAME SETS UNCOMMENT
        # for gset in self.game_sets:
        #     gset.grid["click"] = True
        #     gset.save()

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

    def on_game_set(self, _, value):
        MDApp.get_running_app().save_confs()


class GridBoard(MDApp):
    def build_config(self, config):
        config.setdefaults('Confs', {'game_set': ''})

    def build(self):
        self.theme_cls.theme_style = "Dark"
        colors = ['Pink', 'Indigo', 'Blue',
                  'LightBlue', 'Cyan', 'Teal', 'Green', 'LightGreen', 'Amber', 'Orange', 'DeepOrange',
                  'BlueGray']
        self.theme_cls.primary_palette = colors[randint(0, len(colors) - 1)]
        game_set_name = self.config.get('Confs', 'game_set')
        if game_set_name:
            if game_set_name in os.listdir("assets/game_sets"):
                return Game(game_set=GameSet(name=game_set_name))
            elif game_set_name in os.listdir(games_path):
                return Game(game_set=GameSet(name=game_set_name, external=True))
        return Game()

    def save_confs(self):
        config = self.config
        if self.root:
            config.set('Confs', 'game_set', self.root.game_set.name)
        config.write()


if __name__ == '__main__':
    game = GridBoard()
    game.run()

# todo allow resource packs to contain backgrounds, separators, grid background, pieces, theme primary color and style.
#   i just realized i can make Yu Gi Oh field.
# to create an atlas python -m kivy.atlas <basename> <size> <list of images...>
# -m kivy.atlas medals 46x46 achievements_2.png

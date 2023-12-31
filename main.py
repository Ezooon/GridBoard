import json
import os
from os import listdir, path, makedirs, environ
from random import randint
from kivy.core.window import Window
from kivymd.toast import toast
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screenmanager import MDScreenManager
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, DictProperty, StringProperty
from kivy.utils import platform
from kivymd.app import MDApp
from game_set import GameSet
import webbrowser

environ["KIVY_ORIENTATION"] = "portrait"

root_path = path.expanduser('~')
games_path = path.join(root_path, 'Documents', 'GridBoard')
if platform == 'android':
    from android.permissions import request_permissions, Permission

    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
    from android.storage import primary_external_storage_path

    root_path = primary_external_storage_path()
    games_path = path.join(root_path, 'GridBoard')
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
        #     gset.init["grid"]['fit_screen'] = True
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
        if self.ids.debug.active:
            self.editing_set.init['debug'] = True
        if self.editing_set.save(self.new):
            if self.ids.generate_code.active:
                self.editing_set.generate_code()
            self.current = 'themes_assets'
            self.new = False
            self.game_sets = []
            self.get_game_sets()

    def confirm_code_generation(self, checkbox):
        if self.new or not self.editing_set.code_path:
            return

        def cancel(func):
            func()
            checkbox.active = False

        dialog = MDDialog(title="Confirm", text="if you keep this checked the exiting code file will be overriden",
                          buttons=[
                              MDFlatButton(
                                  text="CANCEL",
                                  theme_text_color="Custom",
                                  text_color=[1, 0, 0, 1],
                                  on_press=lambda x: cancel(dialog.dismiss)

                              ),
                              MDFlatButton(
                                  text="I'm Aware",
                                  theme_text_color="Custom",
                                  text_color=[0, 1, 0, 1],
                                  on_press=lambda x: dialog.dismiss()
                              ),
                          ])
        dialog.open()

    def open_url(self, url):
        webbrowser.open(url)

    def on_game_set(self, _, value):
        MDApp.get_running_app().save_confs()
        if "game_screen" in self.screen_names:
            self.get_screen('game_screen').restart()


class GridBoard(MDApp):
    lang_name = StringProperty("english")
    lang = DictProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.languages = [lang[:-5] for lang in listdir("assets/lang")]

        with open(f'assets/lang/{self.lang_name}.json', 'r', encoding="utf-8") as f:
            self.lang = json.load(f)

    def on_lang_name(self, _, name):
        with open(f'assets/lang/{name}.json', 'r', encoding="utf-8") as f:
            self.lang = json.load(f)
        self.config.set('Confs', 'language', self.lang_name)
        self.config.write()

    def next_lang(self):
        i = self.languages.index(self.lang_name)
        if i + 1 >= len(self.languages):
            self.lang_name = self.languages[0]
            return
        self.lang_name = self.languages[i + 1]

    def build_config(self, config):
        config.setdefaults('Confs', {'game_set': '', 'language': 'english'})

    def build(self):
        self.theme_cls.theme_style = "Dark"
        colors = ['Pink', 'Indigo', 'Blue',
                  'LightBlue', 'Cyan', 'Teal', 'Green', 'LightGreen', 'Amber', 'Orange', 'DeepOrange',
                  'BlueGray']
        self.theme_cls.primary_palette = colors[randint(0, len(colors) - 1)]
        self.lang_name = self.config.get('Confs', 'language')
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
            config.set('Confs', 'language', self.lang_name)
        config.write()


if __name__ == '__main__':
    game = GridBoard()
    game.run()

# todo allow resource packs to contain backgrounds, separators, grid background, pieces, theme primary color and style.
#   i just realized i can make Yu Gi Oh field.
# to create an atlas python -m kivy.atlas <basename> <size> <list of images...>
# -m kivy.atlas medals 46x46 achievements_2.png

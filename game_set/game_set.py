from os import listdir, path, makedirs, rename, remove
from shutil import copyfile, copytree, rmtree
from kivy.utils import platform
import json

root_path = path.expanduser('~')
games_path = path.join(root_path, 'Documents', 'GridBord')
if platform == 'android':
    from android.storage import primary_external_storage_path

    root_path = primary_external_storage_path()
    games_path = path.join(root_path, 'GridBord')


def replace(current, new, _path, name):
    if path.isfile(current):
        remove(current)
    if path.isdir(current):
        rmtree(current)
    if name:
        copyfile(new, path.abspath(path.join(_path, name)))
    else:
        print(_path, name)
        copytree(new, path.abspath(path.join(_path, name)))


class GameSet:
    def __init__(self, name='default', external=False):
        # name and path
        self.name = self._name = name
        self.external = external

        if not path.exists(games_path):
            makedirs(games_path)

        if external:
            self.path = path.join(games_path, name)
        else:
            self.path = path.join("assets/game_sets", name)

        dirs = listdir(self.path)

        # help
        self.help_path = path.join(self.path, 'help.txt') if "help.txt" in dirs else ""
        self.help = ''
        for f in dirs:
            if f.startswith('help'):
                with open(path.join(self.path, f), 'r') as help_:
                    self.help = help_.read()

        # backgrounds
        self.background = self._background = "assets/game_sets/default/backgrounds/background.png"
        self.grid_background = self._grid_background = "assets/game_sets/default/backgrounds/grid-background.png"
        self.background_path = path.join(self.path, 'backgrounds') if "backgrounds" in dirs else ""
        if self.background_path:
            for file in listdir(self.background_path):
                if file.startswith("background"):
                    self.background = self._background = path.join(self.background_path, file)
                elif file.startswith("grid-background"):
                    self.grid_background = self._grid_background = path.join(self.background_path, file)

        # init
        self.init = {
            "grid": {
                "cols": 1,
                "rows": 1,
                "border": True,
                "background": False,
                "line_color": [255, 255, 255, 255],
                "size": [100, 100],
                "click": True
            },
            "dies": [0, []],
            "pieces": {}
        }  # default init
        self.init_path = path.join(self.path, 'init.json') if "init.json" in dirs else ""
        if self.init_path:
            with open(self.init_path, 'r') as init:
                init = json.load(init)
                if 'grid' in init.keys():
                    self.init['grid'] = init['grid']

                if 'pieces' in init.keys():
                    self.init['pieces'] = init['pieces']

                if 'dies' in init.keys():
                    self.init['dies'] = init['dies']

        # grid
        self.grid = self.init['grid']

        # pieces
        self.pieces = self.init['pieces']
        self._pieces_path = path.join(self.path, 'pieces') if "pieces" in dirs else ""
        self.pieces_num = 0
        if self._pieces_path:
            for piece in list(self.pieces.keys()).copy():
                # if piece not in self.pieces.keys():
                #     self.pieces[piece] = {
                #         'num': 0, 'poses': [], "color": [1, 1, 1, 1],
                #         "auto_size": True, "size": [10, 10], "rotation": 0
                #     }
                p_path = path.join(self._pieces_path, piece)
                if path.exists(p_path):
                    self.pieces[piece]['path'] = path.join(self._pieces_path, piece)
                    self.pieces_num += self.pieces[piece]['num']
                else:
                    self.pieces.pop(piece)

        # dies
        self.dies = self.init["dies"]

    @property
    def pieces_path(self):
        return self._pieces_path

    @pieces_path.setter
    def pieces_path(self, value):
        self.pieces_num = 0
        if self._pieces_path == value:
            self.pieces = self.init["pieces"]
        else:
            self.pieces = dict()

        if path.isdir(value):
            for piece in listdir(value):
                if piece not in self.pieces:
                    self.pieces[piece] = {
                        'num': 0, 'poses': [], "color": [1, 1, 1, 1],
                        "auto_size": True, "size": [50, 50], "rotation": 0
                    }
                self.pieces[piece]["path"] = path.join(value, piece)
        self._pieces_path = value

    def save(self, new=False):
        """save game set"""
        if not self.name:
            return False

        if new:
            self.path = path.join(games_path, self.name)
            makedirs(self.path)
            self.external = True

        pieces = self.pieces
        for piece in pieces.keys():
            pieces[piece].pop("path")

        init = self.init
        init['pieces'] = pieces
        init['grid'] = self.grid
        init['dies'] = self.dies

        with open(self.init_path or path.join(self.path, 'init.json'), 'w') as f:
            json.dump(init, f, indent=4)

        with open(self.help_path or path.join(self.path, 'help.txt'), 'w') as f:
            f.write(self.help)

        if not path.isdir(self.background_path):
            self.background_path = path.join(self.path, "backgrounds")
            makedirs(self.background_path)
        if self.background != self._background:
            replace(self._background, self.background, self.background_path, 'background.png')
        if self.grid_background != self._grid_background:
            replace(self._grid_background, self.grid_background, self.background_path, 'grid-background.png')

        if not path.isdir(self.pieces_path):
            makedirs(path.join(self.path, "pieces"))

        if self.pieces_path != path.join(self.path, 'pieces'):
            replace(path.join(self.path, 'pieces'), self._pieces_path, path.join(self.path, 'pieces'), "")

        if self.name != self._name or new:
            self.rename(self.name)
            return True
        self.__init__(self.name, self.external)
        return True

    def export(self):
        """to create a zip file from a game set"""
        pass

    def delete(self):
        print('deleting:', self.name)
        rmtree(self.path)

    def rename(self, name):
        if self.external:
            new_path = path.join(games_path, name)
        else:
            new_path = path.join("assets/game_sets", name)
        print(self.external, self.path, new_path)
        rename(self.path, new_path)
        self.__init__(name, self.external)


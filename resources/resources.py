from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDIconButton
from kivy.properties import StringProperty, NumericProperty
from kivymd.uix.menu import MDDropdownMenu
from themes_assets import APiece
from kivy.utils import platform
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.app import App
from os import path

Builder.load_file('resources/resources.kv')
root_path = r''
if platform == 'android':
    from android.storage import primary_external_storage_path

    root_path = primary_external_storage_path()


class ResourcesScreen(MDScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.file_manager_is_open = False
        self.file_manager = MDFileManager(
            select_path=print,
            search='all',
            preview=True,
            # ext=['.png', '.jpg', '.gif']
        )
        self.file_manager.exit_manager = lambda x: self.file_manager.close()

    def on_enter(self, *args):
        Clock.schedule_once(self.set_up, 0)

    def load_pieces(self, editing_set):
        pieces = editing_set.pieces
        layout = self.ids.pieces_display
        layout.clear_widgets()
        for piece in pieces.keys():
            layout.add_widget(APieceAdder(name=piece, source=pieces[piece]['path'], num=pieces[piece]['num']))

        layout.add_widget(APieceAdder(name="die", source="assets/die/6.png", num=editing_set.dies[0]))

    def set_up(self, dt):
        root = App.get_running_app().root
        editing_set = root.editing_set
        self.load_pieces(editing_set)

        # Help
        self.ids.help.text = editing_set.help

        # Drop down menus
        sets = root.game_sets
        grid_background_items = [{
                    "text": "Browse",
                    "viewclass": "OneLineListItem",
                    "on_release": self.change_grid_background,
                }]
        background_items = [{
                    "text": "Browse",
                    "viewclass": "OneLineListItem",
                    "on_release": self.change_background,
                }]
        pieces_items = [{
                    "text": "Browse",
                    "viewclass": "OneLineListItem",
                    "on_release": self.change_pieces,
                }]
        str().title()

        for game_set in sets:
            if game_set.background:
                background_items.append({
                    "text": game_set.name,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=game_set: self.change_background(x.background),
                })

            if game_set.grid_background:
                grid_background_items.append({
                    "text": game_set.name,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=game_set: self.change_grid_background(x.grid_background),
                })

            if game_set.pieces_path:
                pieces_items.append({
                    "text": game_set.name,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=game_set: self.change_pieces(x.pieces_path),
                })

        self.ids.background_path.text = editing_set.background
        self.background_menu = MDDropdownMenu(
            caller=self.ids.background_card,
            items=background_items,
            width_mult=4,
            # background_color=App.get_running_app().theme_cls.primary_color[:3] + [0.7]
        )

        self.ids.grid_background_path.text = editing_set.grid_background
        self.grid_background_menu = MDDropdownMenu(
            caller=self.ids.grid_background_card,
            items=grid_background_items,
            width_mult=4,
            # background_color=App.get_running_app().theme_cls.primary_color[:3] + [0.7]
        )

        self.ids.pieces_path.text = editing_set.pieces_path
        self.pieces_menu = MDDropdownMenu(
            caller=self.ids.pieces_card,
            items=pieces_items,
            width_mult=4,
            # background_color=App.get_running_app().theme_cls.primary_color[:3] + [0.7]
        )

    def change_pieces(self, pieces_path=""):
        if self.file_manager_is_open:
            if path.isdir(pieces_path):
                self.file_manager.close()
        self.pieces_menu.dismiss()
        if not pieces_path:
            self.file_manager.select_path = self.change_pieces
            if root_path:
                self.file_manager.show(root_path)
            else:
                self.file_manager.show_disks()
            self.file_manager_is_open = True
            return

        root = App.get_running_app().root
        editing_set = root.editing_set
        editing_set.pieces_path = pieces_path
        self.load_pieces(editing_set)
        self.ids.pieces_path.text = pieces_path

    def change_background(self, background_path=""):
        if self.file_manager_is_open:
            self.file_manager.close()
        self.background_menu.dismiss()
        if not background_path:
            self.file_manager.select_path = self.change_background
            if root_path:
                self.file_manager.show(root_path)
            else:
                self.file_manager.show_disks()
            self.file_manager_is_open = True
            return

        root = App.get_running_app().root
        editing_set = root.editing_set
        editing_set.background = background_path
        self.ids.background_path.text = background_path

    def change_grid_background(self, grid_background_path=""):
        if self.file_manager_is_open:
            self.file_manager.close()
        self.grid_background_menu.dismiss()
        if not grid_background_path:
            self.file_manager.select_path = self.change_grid_background
            if root_path:
                self.file_manager.show(root_path)
            else:
                self.file_manager.show_disks()
            self.file_manager_is_open = True
            return

        root = App.get_running_app().root
        editing_set = root.editing_set
        editing_set.grid_background = grid_background_path
        self.ids.grid_background_path.text = grid_background_path

    def save(self):
        editing_set = App.get_running_app().root.editing_set
        editing_set.help = self.ids.help.text
        for p in self.ids.pieces_display.children:
            if p.name == 'die':
                editing_set.dies[0] = p.num
                continue
            editing_set.pieces[p.name]["num"] = p.num


class APieceAdder(MDBoxLayout):
    name = StringProperty("red.png")
    source = StringProperty("assets/game_sets/default/pieces/red.png")
    num = NumericProperty(0)

    def __init__(self, **kwargs):
        self.piece = APiece(source=self.source, num=self.num)
        super(APieceAdder, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.adaptive_width = True

        self.piece = APiece(source=self.source, num=self.num)
        self.add_widget(MDIconButton(icon='plus', size_hint=[None, None], on_release=self.add))
        self.add_widget(self.piece)
        self.add_widget(MDIconButton(icon='minus', size_hint=[None, None], on_release=self.take))

    def add(self, _):
        self.num += 1

    def take(self, _):
        self.num -= 1

    def on_num(self, _, value):
        if value < 0:
            self.num = 0
            return
        self.piece.num = self.num

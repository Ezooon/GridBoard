from kivy.metrics import dp

from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, ListProperty, BooleanProperty
from kivymd.uix.menu import MDDropdownMenu
from themes_assets import APiece
from kivy.utils import platform
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.app import App
from os import path

Builder.load_file('pieces/pieces.kv')
root_path = r''
if platform == 'android':
    from android.storage import primary_external_storage_path

    root_path = primary_external_storage_path()


class APieceAdder(ButtonBehavior, MDFloatLayout):
    name = StringProperty("red.png")
    source = StringProperty("assets/game_sets/default/pieces/red.png")
    num = NumericProperty(0)
    target = BooleanProperty(False)
    auto_size = BooleanProperty(True)
    p_size = ListProperty([dp(80), dp(80)])
    p_rotation = NumericProperty(0)
    p_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        self.piece = APiece(source=self.source, num=self.num)
        super(APieceAdder, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.adaptive_width = True

    def on_press(self):
        self.target = True
        # if self.auto_size:
        #     self.p_size = dp(100), dp(100)

    def add(self, _):
        self.num += 1

    def take(self, _):
        self.num -= 1

    def on_num(self, _, value):
        if value < 0:
            self.num = 0
            return
        self.piece.num = self.num


sg = APieceAdder()


class PiecesScreen(MDScreen):
    target_piece = ObjectProperty(sg)

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
            apa = APieceAdder(name=piece, source=pieces[piece]['path'], num=pieces[piece]['num'])
            layout.add_widget(apa)
            apa.bind(target=self.change_target_piece)

        die = APieceAdder(name="die", source="assets/die/6.png", num=editing_set.dies[0])
        layout.add_widget(die)
        die.bind(target=self.change_target_piece)

    def set_up(self, dt):
        root = App.get_running_app().root
        editing_set = root.editing_set
        self.load_pieces(editing_set)

        # Drop down menus
        sets = root.game_sets
        pieces_items = [{
                    "text": "Browse",
                    "viewclass": "OneLineListItem",
                    "on_release": self.change_pieces,
                }]
        str().title()

        for game_set in sets:
            if game_set.pieces_path:
                pieces_items.append({
                    "text": game_set.name,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=game_set: self.change_pieces(x.pieces_path),
                })

        self.ids.pieces_path.text = editing_set.pieces_path
        self.pieces_menu = MDDropdownMenu(
            caller=self.ids.pieces_card,
            items=pieces_items,
            width_mult=4,
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

    def change_target_piece(self, apa, value):
        if apa.name == 'die':
            apa.target == False
            self.target_piece = sg
        if value:
            self.target_piece.target = False
            self.target_piece = apa

            self.ids.auto_size.active = apa.auto_size
            self.ids.size.value = apa.p_size[0]
            self.ids.rotation.value = apa.p_rotation
            self.ids.red.value = apa.p_color[0] * 255
            self.ids.green.value = apa.p_color[1] * 255
            self.ids.blue.value = apa.p_color[2] * 255
            self.ids.alpha.value = apa.p_color[3] * 255

    def save(self):
        editing_set = App.get_running_app().root.editing_set
        for p in self.ids.pieces_display.children:
            if p.name == 'die':
                editing_set.dies[0] = p.num
                continue
            editing_set.pieces[p.name]["auto_size"] = p.auto_size
            editing_set.pieces[p.name]["size"] = p.p_size
            editing_set.pieces[p.name]["rotation"] = p.p_rotation
            editing_set.pieces[p.name]["color"] = p.p_color

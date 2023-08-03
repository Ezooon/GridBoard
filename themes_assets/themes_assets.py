from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout

from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivy.lang import Builder
from kivy.metrics import sp
from game_set import GameSet
from os import listdir

Builder.load_file('themes_assets/themes_assets.kv')


class ThemesAssets(MDScreen):
    def on_enter(self, *args):
        sets = App.get_running_app().root.game_sets
        self.ids.sets.clear_widgets([c for c in self.ids.sets.children if isinstance(c, AssetCard)])
        for game_set in sets:
            if game_set.name == "default":
                continue
            self.ids.sets.add_widget(AssetCard(game_set=game_set))


class AssetCard(MDCard):
    game_set = ObjectProperty(GameSet())
    dialog = None
    delete_dialog = None
    target = None

    def __init__(self, **kwargs):
        super(AssetCard, self).__init__(**kwargs)
        if not AssetCard.target:
            AssetCard.target = self
        if not AssetCard.dialog:
            AssetCard.init_dialog()

    @classmethod
    def init_dialog(cls):
        cls.delete_dialog = MDDialog(title="DELETE "+cls.target.game_set.name, buttons=[
            MDFlatButton(text='Cancel', text_color=cls.target.theme_cls.primary_color,
                         theme_text_color="Custom", font_size=sp(20), on_release=lambda x: cls.delete_dialog.dismiss()),
            MDRaisedButton(text="Delete", md_bg_color=[0.8, 0, 0, 1], text_color=[1, 1, 1, 1],
                           on_release=lambda x: cls.target.delete()),
        ])

        cls.dialog = MDDialog(title="Game", buttons=[
            MDFlatButton(text='PLAY', text_color=cls.target.theme_cls.primary_color,
                         theme_text_color="Custom", font_size=sp(25), on_release=lambda x: cls.target.play()),
            MDFlatButton(text='Edit', text_color=cls.target.theme_cls.primary_color,
                         theme_text_color="Custom", font_size=sp(20), on_release=lambda x: cls.target.edit()),
            MDRaisedButton(text="delete", md_bg_color=[0.8, 0, 0, 1], text_color=[1, 1, 1, 1],
                           on_release=lambda x: cls.delete_dialog.open()),
        ])

    def on_game_set(self, _, game_set):
        pieces = game_set.pieces
        if "pieces_display" not in self.ids.keys():
            Clock.schedule_once(lambda x: self.on_game_set(_, game_set), 0)
            return
        layout = self.ids.pieces_display
        layout.clear_widgets()

        for piece in pieces.keys():
            layout.add_widget(APiece(source=pieces[piece]['path'], num=pieces[piece]['num']))

    def play(self):
        AssetCard.dialog.dismiss()
        AssetCard.delete_dialog.dismiss()
        root = App.get_running_app().root
        root.game_set = self.game_set
        root.current = 'game_screen'

    def edit(self):
        AssetCard.dialog.dismiss()
        root = App.get_running_app().root
        root.editing_set = self.game_set
        root.current = 'new_game'
        root.new = False

    def delete(self):
        AssetCard.dialog.dismiss()
        AssetCard.delete_dialog.dismiss()
        self.parent.remove_widget(self)
        self.game_set.delete()
        App.get_running_app().root.get_game_sets()

    def on_press(self):
        AssetCard.target = self
        dialog = AssetCard.dialog
        dialog.title = self.game_set.name
        dialog.text = self.game_set.help
        dialog.open()


class APiece(BoxLayout):
    name = StringProperty("red.png")
    source = StringProperty("assets/game_sets/default/pieces/red.png")
    num = NumericProperty(0)

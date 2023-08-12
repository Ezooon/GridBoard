from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivy.utils import platform
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.app import App

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

    def set_up(self, dt):
        root = App.get_running_app().root
        editing_set = root.editing_set

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

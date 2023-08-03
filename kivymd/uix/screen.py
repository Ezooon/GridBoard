"""
Components/Screen
=================

:class:`~kivy.uix.screenmanager.Screen` class equivalent. Simplifies working
with some widget properties. For example:

Screen
------

.. code-block::

    Screen:
        canvas:
            Color:
                rgba: app.theme_cls.primary_color
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [25, 0, 0, 0]

MDScreen
--------

.. code-block::

    MDScreen:
        radius: [25, 0, 0, 0]
        md_bg_color: app.theme_cls.primary_color
"""

from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

from kivymd.uix import MDAdaptiveWidget
from kivymd.uix.hero import MDHeroTo


class MDScreen(Screen, MDAdaptiveWidget):
    back_click_to = StringProperty("welcome_screen")

    hero_to = ObjectProperty()
    """
    Must be a  :class:`~kivymd.uix.hero.MDHeroTo` class.
    See the documentation of the
    `MDHeroTo <https://kivymd.readthedocs.io/en/latest/components/hero/>`_
    widget for more detailed information.

    .. versionchanged:: 1.0.0

    :attr:`hero_to` is an :class:`~kivy.properties.ObjectProperty`
    and defaults to `None`.
    """

    def back_click(self, window, key, *largs):
        if key == 27 and self.back_click_to and self.name == self.manager.current:
            self.manager.current = self.back_click_to
            return True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.back_click)

    def on_hero_to(self, screen, widget) -> None:
        if not isinstance(widget, MDHeroTo) or not issubclass(
                widget.__class__, MDHeroTo
        ):
            raise TypeError(
                f"The `{widget}` widget must be an `kivymd.uix.hero.MDHeroTo` "
                f"class or inherited from this class"
            )

    def on_go_back(self):
        from kivy.app import App
        App.get_running_app().root.go_back()

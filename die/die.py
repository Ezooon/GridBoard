from random import randint

from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior, DragBehavior
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from os import path
# from kivy.lang import Builder

# Builder.load_file('die/die.kv')


class Die(DragBehavior, ButtonBehavior, Image):
    die_path = StringProperty("assets/die")
    face = NumericProperty(1)
    relative_pos = ListProperty([0, 0])

    def __init__(self, **kwargs):
        super(Die, self).__init__(**kwargs)
        self.roll_sound = SoundLoader.load("assets/die/roll.wav")
        self.source = path.join(self.die_path, '1.png')
        self.size_hint = [None, None]
        self.drag_rectangle = [*self.pos, *self.size]

    def on_size(self, _, size):
        self.drag_rectangle = [*self.pos, *size]

    def on_pos(self, _, pos):
        self.drag_rectangle = [*pos, *self.size]
        if self.parent:
            self.relative_pos = [pos[0]-self.parent.center_x, pos[1]-self.parent.center_y]

    def on_face(self, _, face):
        if 0 < face < 7:
            self.source = path.join(self.die_path, f"{face}.png")

    def on_release(self):
        self.throw()

    def throw(self):
        self.roll_sound.play()
        def throw_anim(dt):
            self.face = randint(1, 6)

        for i in range(6):
            Clock.schedule_once(throw_anim, i / 10)

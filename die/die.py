from random import randint

from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior, DragBehavior
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from os import path
from kivy.lang import Builder

Builder.load_string("""
<Die>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: root.rotation
            axis: 0, 0, 1
            origin: self.center
    canvas.after:
        PopMatrix

""")


class Die(DragBehavior, ButtonBehavior, Image):
    die_path = StringProperty("assets/die")
    face = NumericProperty(1)
    top_face = NumericProperty(1)
    relative_pos = ListProperty([0, 0])
    rotation = NumericProperty(0)
    draggable = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(Die, self).__init__(**kwargs)
        self.roll_sound = SoundLoader.load("assets/die/roll.wav")
        self.source = path.join(self.die_path, '1.png')
        self.size_hint = [None, None]
        self.drag_rectangle = [*self.pos, *self.size]
        self.callback = lambda: None
        self.drag_timeout = 1000
        self.drag_distance = 5

    def on_draggable(self, _, value):
        if value:
            self.drag_timeout = 0
        else:
            self.drag_timeout = 1000

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
        self.roll()
        self.callback()

    def roll(self):
        self.roll_sound.play()
        self.top_face = randint(1, 6)

        def roll_anim(dt):
            self.face = randint(1, 6)

        def roll_anim_complete(dt):
            self.face = self.top_face

        for i in range(6):
            Clock.schedule_once(roll_anim, i / 10)

        Clock.schedule_once(roll_anim_complete, 0.7)

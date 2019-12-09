# Plytform cutscenes

import settings


class Cutscene:
    camera_x = 0
    camera_y = 0
    frames_in = 0
    actors = {}
    is_active = False

    def __init__(self, engine):
        self.engine = engine

    def start(self):
        self.is_active = True

    def set_camera(self, x, y):
        self.engine.lose_focus()
        self.engine.view_x = x
        self.engine.view_y = y

    def focus_on(self, actor_key):
        self.engine.focus_on(self.actors[actor_key])

    def add_actor(self, actor_key, actor_ob):
        self.actors[actor_key] = actor_ob

    def remove_actor(self, actor_key):
        if actor_key in self.actors:
            self.actors.remove(actor_key)

    def cycle_frame(self):
        self.frames_in += 1


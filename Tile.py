# Plytform tiles

import settings
import re
import math


class Tile:
    x = 0
    y = 0
    w = 0
    h = 0
    currentFrame = 0
    animated = False
    layer = 0
    img = False
    frames = False

    def __init__(self, values):
        if values:
            if "x" in values.keys():
                self.x = values["x"]
            if "y" in values.keys():
                self.y = values["y"]
            if "w" in values.keys():
                self.w = values["w"]
            else:
                self.w = settings.default_tile_w
            if "h" in values.keys():
                self.h = values["h"]
            else:
                self.h = settings.default_tile_h
            if "img" in values.keys():
                self.img = values["img"]
                if re.search("&[0-9]+of[0-9]+", self.img):
                    self.animated = True
                    frames_string = re.findall("&[0-9]+of[0-9]+", self.img)[0]
                    split_string = frames_string.replace("&", "").split("of")
                    self.current_frame = int(split_string[0])
                    self.total_frames = int(split_string[1])

            if "frames" in values.keys():
                self.frames = values["frames"]
            if "layer" in values.keys():
                self.layer = values["layer"]

    def get_render_x(self):
        return self.x * settings.default_tile_w

    def get_render_y(self):
        return self.y * settings.default_tile_h

    def update_animation(self, engine):
        self.current_frame = math.floor(engine.global_frame % 16 / 4)
        if self.current_frame >= self.total_frames:
            self.current_frame = 0
        split_string = re.split("&[0-9]+of", self.img)
        self.img = split_string[0] + "&" + str(self.current_frame + 1) + "of" + split_string[1]


class TileLayer:

    def __init__(self, values):
        self.name = values["name"]
        self.tiles = {}
        for key in values:
            if key is not False and key != "name" and values[key] is not False:
                self.tiles[key] = Tile(values[key])

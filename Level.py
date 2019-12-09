# Plytform level

import settings
from Tile import Tile, TileLayer


class Level:

    def __init__(self, values):
        self.w = values["w"] if "w" in values else settings.default_level_w
        self.h = values["h"] if "h" in values else settings.default_level_h
        self.tile_w = values["tile_w"] if "tile_w" in values else settings.default_tile_w
        self.tile_h = values["tile_h"] if "tile_h" in values else settings.default_tile_h
        self.name = values["name"] if "name" in values else "Level name"
        self.bgs = values["bgs"] if "bgs" in values else []
        self.bg_tile_layers = [TileLayer(v) for v in values["bg_tile_layers"]] if "bg_tile_layers" in values else []
        self.obs = values["obs"] if "obs" in values else []
        self.fg_tile_layers = [TileLayer(v) for v in values["fg_tile_layers"]] if "fg_tile_layers" in values else []
        self.edges = values["edges"] if "edges" in values else settings.default_level_edges

        self.total_nuggets = sum(o["type"] == "Nugget" for o in self.obs)
        self.current_nuggets = self.total_nuggets

    def add_bg(self, img, img_w, img_h):
        self.bgs.append({
            "img": img,
            "w": img_w,
            "h": img_h,
        })

    def add_bg_tile_layer(self, layer):
        new_layer = layer if layer else {}
        self.bg_tile_layers.append(new_layer)
        return new_layer

    def add_bg_tile(self, layer, values):
        self.bg_tile_layers[layer][values["x"] + "-" + values["y"]] = Tile(values)

    def get_bg_tile(self, layer, x, y):
        return self.bg_tile_layers[layer][x + "-" + y]

    def add_ob(self, ob):
        self.obs.append(ob)
        return ob

    def add_obs(self, obs):
        for ob in obs:
            self.add_ob(ob)

    def add_fg_tile_layer(self, layer):
        new_layer = layer if layer else {}
        self.fg_tile_layers.append(new_layer)
        return new_layer

    def add_fg_tile(self, layer, values):
        self.fg_tile_layers[layer][values["x"] + "-" + values["y"]] = Tile(values)

    def get_fg_tile(self, layer, x, y):
        return self.fg_tile_layers[layer][x + "-" + y]

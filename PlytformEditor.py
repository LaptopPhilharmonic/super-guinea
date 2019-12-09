# PLYTFORM editor - for making levels and stuff
# Author: Sam Boulby
"""
import sys
from pygame.locals import *
import json
from obs import *
from Level import Level


class PlytformEditor:

    screen_width = settings.editor_screen_w
    screen_height = settings.editor_screen_h
    resolution_width = settings.editor_screen_w
    resolution_height = settings.editor_screen_h
    fps = settings.fps
    game_running = False
    bgs = []
    bg_tile_layers = []
    obs = []
    fg_tile_layers = []
    images = {}
    editor_x = 0
    editor_y = 0
    view_x = 0
    view_y = 0
    player_ob = 0
    level_width = False
    level_height = False

    def __init__(self):
        pygame.init()

        self.resolution_width_ratio = self.screen_width / self.resolution_width
        self.resolution_height_ratio = self.screen_height / self.resolution_height

        screen_size = (self.screen_width, self.screen_height)
        self.screen = pygame.display.set_mode(screen_size, FULLSCREEN)
        self.surface = pygame.display.get_surface()

        self.clock = pygame.time.Clock()

        level_data = {
            "name": "Test level",
            "w": 32 * 32,
            "h": 32 * 32,
            "bgs": [
                {"img": "sky-bg", "w": 640, "h": 480},
                {"img": "hills-bg", "w": 740, "h": 555},
            ]
        }

        self.load_level(Level(level_data))

        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    def start(self):
        self.game_running = True

        while self.game_running:
            dt = self.clock.tick(self.fps) / self.fps
            if dt < 1:
                dt = 1
            self.cycle_engine(dt)
            self.render()
            self.handle_events()

        pygame.quit()
        sys.exit()

    def load_level(self, level):
        self.level_width = level.w
        self.level_height = level.h
        self.bgs = level.bgs
        self.bg_tile_layers = level.bg_tile_layers
        self.obs = level.obs
        self.fg_tile_layers = level.fg_tile_layers

    def add_ob(self, ob):
        self.obs.append(ob)

    def add_obs(self, obs):
        for ob in obs:
            self.add_ob(ob)

    def load_obs_from_file(self, file_path):
        data = json.loads(open(file_path).read())
        for ob in data["obs_to_load"]:
            self.add_ob(globals()[ob["type"]](ob["values"]))

    def add_image(self, path, alpha=False):
        if alpha:
            img = pygame.image.load(path).convert_alpha()
        else:
            img = pygame.image.load(path).convert()
        name = path.replace("images/", "")
        name = name.split(".")[0]
        self.images[name] = img

    def add_image_set(self, path, number, alpha=False,):
        for i in range(1, number + 1):
            self.add_image(path + "-" + str(i) + ".png", alpha)

    def add_bg(self, img, img_w, img_h):
        self.bgs.append({
            "img": img,
            "w": img_w,
            "h": img_h,
        })

    def focus_on(self, player):
        self.player_ob = player

    def set_level_dimensions(self, w, h):
        self.level_width = w
        self.level_height = h

    def cycle_engine(self, dt):
        mouse = pygame.mouse
        mouse_pos = mouse.get_pos()
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1]

        if mouse_x < 32 and self.editor_x > 0:
            self.editor_x -= 1
        if mouse_x > (self.screen_width - 32) and self.editor_x < self.screen_width:
            self.editor_x += 1
        if mouse_y < 32 and self.editor_y > 0:
            self.editor_y -= 1
        if mouse_y > (self.screen_height - 32) and self.editor_y < self.screen_height:
            self.editor_y += 1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()

    def render(self):

        def render_image(img, x, y, w, h):
            self.surface.blit(img, (x, y))

        screen_rectangle = pygame.draw.rect(self.surface, (0, 0, 0), [0, 0, self.screen_width, self.screen_height])

        self.view_x = round(self.resolution_width / 2) - (self.editor_x)
        self.view_y = round(self.resolution_height / 2) - (self.editor_y)

        if self.view_x > 0:
            self.view_x = 0
        if self.view_y > 0:
            self.view_y = 0
        if self.level_width and self.view_x < ((self.level_width * -1) + self.resolution_width):
            self.view_x = ((self.level_width * -1) + self.resolution_width)
        if self.level_height and self.view_y < ((self.level_height * -1) + self.resolution_height):
            self.view_y = ((self.level_height * -1) + self.resolution_height)

        for bg in self.bgs:
            w_ratio = (bg["w"] - self.screen_width) / (self.level_width - self.screen_width)
            h_ratio = (bg["h"] - self.screen_height) / (self.level_height - self.screen_height)

            bg_x = round(self.view_x * w_ratio * self.resolution_width_ratio)
            bg_y = round(self.view_y * h_ratio * self.resolution_height_ratio)
            bg_w = round(bg["w"] * self.resolution_width_ratio)
            bg_h = round(bg["h"] * self.resolution_height_ratio)

            render_image(self.images[bg["img"]], bg_x, bg_y, bg_w, bg_h)

        for o in self.obs:

            o.animate()

            display_x = (self.view_x + o.x - o.offset_x) * self.resolution_width_ratio
            display_y = (self.view_y + o.y - o.offset_y) * self.resolution_height_ratio
            display_w = round(o.w * self.resolution_width_ratio)
            display_h = round(o.h * self.resolution_height_ratio)

            if o.img_w:
                display_w = round(o.img_w * self.resolution_width_ratio)
            if o.img_h:
                display_h = round(o.img_h * self.resolution_height_ratio)

            if display_x + display_w < 0:
                continue
            if display_y + display_h < 0:
                continue
            if display_x > self.screen_width:
                continue
            if display_y > self.screen_height:
                continue

            if type(o).__name__ != "Guinea":
                pygame.draw.rect(self.surface, o.color, [display_x, display_y, display_w, display_h])
            if type(o).__name__ == "Guinea":
                render_image(self.images[o.img], display_x, display_y, display_w, display_h)
            if type(o).__name__ == "Lettuce":
                render_image(self.images[o.img], display_x, display_y, display_w, display_h)

        pygame.display.update(screen_rectangle)

        self.handle_events()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_running = False
"""
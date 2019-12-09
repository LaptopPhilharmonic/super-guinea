# PLYTFORM - A platform game engine
# Author: Sam Boulby

import sys
import pygame
from pygame.locals import *
import time
import settings
import json
from obs import *


class Plytform:

    gravity_constant = settings.gravity_constant
    engine_speed = settings.engine_speed
    game_running = False
    obs = []
    moving_obs = []
    visible_obs = []
    solid_obs = []
    bgs = []
    images = {}
    view_x = 0
    view_y = 0
    player_ob = 0
    level_width = False
    level_height = False

    def __init__(self, settings):
        pygame.init()

        self.screen_size = self.screen_width, self.screen_height = settings["screen_width"], settings["screen_height"]

        if "resolution_width" in settings:
            self.resolution_width = settings["resolution_width"]
            self.resolution_width_ratio = self.screen_width / self.resolution_width
        else:
            self.resolution_width = self.screen_width
            self.resolution_width_ratio = 1

        if "resolution_height" in settings:
            self.resolution_height = settings["resolution_height"]
            self.resolution_height_ratio = self.screen_height / self.resolution_height
        else:
            self.resolution_height = self.screen_height
            self.resolution_height_ratio = 1

        self.resolution_size = self.resolution_width, self.resolution_height

        self.screen = pygame.display.set_mode(self.screen_size, FULLSCREEN)
        self.screen.set_alpha(None)
        self.surface = pygame.display.get_surface()

        if "gravity_constant" in settings:
            self.gravity_constant = settings["gravity_constant"]
        if "engine_speed" in settings:
            self.engine_speed = settings["engine_speed"]

        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

    def start(self):
        self.game_running = True

        while self.game_running:
            cycle_start = time.time()
            self.cycle_engine()
            self.render()
            self.handle_events()
            elapsed_time = time.time() - cycle_start
            if elapsed_time < self.engine_speed:
                time.sleep((self.engine_speed - elapsed_time) / 1000)

        pygame.quit()
        sys.exit()

    def add_ob(self, ob):
        self.obs.append(ob)
        if ob.is_mover:
            self.moving_obs.append(ob)
        if ob.is_visible:
            self.visible_obs.append(ob)
        if ob.is_solid:
            self.solid_obs.append(ob)

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

    def cycle_engine(self):
        for ob in self.obs:
            ob.behave()

        self.move_and_collide()

    def move_and_collide(self):
        if len(self.moving_obs) < 1:
            return

        fastest_speed = 0
        for ob in self.moving_obs:
            ob.is_on_floor = False
            if max(abs(ob.xs), abs(ob.ys)) > fastest_speed:
                fastest_speed = max(abs(ob.xs), abs(ob.ys))

        if fastest_speed == 0:
            return

        for i in range(round(fastest_speed)):
            for ob in self.moving_obs:
                if ob.is_moving():
                    if ob.y_direction() != 0:
                        old_y = ob.y
                        ob.move_y(i * (ob.ys / fastest_speed))
                        if ob.y != old_y:
                            self.check_collisions(ob, "y", ob.y_direction())
                    if ob.x_direction() != 0:
                        old_x = ob.x
                        ob.move_x(i * (ob.xs / fastest_speed))
                        if ob.x != old_x:
                            self.check_collisions(ob, "x", ob.x_direction())

    def check_collisions(self, ob, axis, direction):
        for ob2 in self.solid_obs:
            if ob.overlaps(ob2):
                if not ob2.is_mover:
                    if axis == "y":
                        ob.ys = settings.gravity_constant
                        if direction == 1:
                            ob.y = ob2.y - ob.h
                            ob.is_on_floor = True
                            ob.xs *= (ob.friction * ob2.friction)
                        if direction == -1:
                            ob.y = ob2.y + ob2.h
                    if axis == "x":
                        ob.xs = 0
                        if direction == 1:
                            ob.x = ob2.x - ob.w
                        if direction == -1:
                            ob.x = ob2.x + ob2.w
                else:
                    if axis == "y":
                        if direction == 1:
                            ob.y = ob2.y - ob.h
                            ob.is_on_floor = True
                            ob.xs *= (ob.friction * ob2.friction)
                        if direction == -1:
                            ob.y = ob2.y + ob2.h
                        initial_ob_ys = ob.ys
                        ob.ys = ((ob.mass - ob2.mass) / (ob.mass + ob2.mass)) * initial_ob_ys
                        ob2.ys = ((2 * ob.mass) / (ob.mass + ob2.mass)) * initial_ob_ys
                    if axis == "x":
                        if direction == 1:
                            ob.x = ob2.x - ob.w
                        if direction == -1:
                            ob.x = ob2.x + ob2.w
                        initial_ob_xs = ob.xs
                        ob.xs = ((ob.mass - ob2.mass) / (ob.mass + ob2.mass)) * initial_ob_xs
                        ob2.xs = ((2 * ob.mass) / (ob.mass + ob2.mass)) * initial_ob_xs

    def render(self):

        def render_image(img, x, y, w, h):
            # if w != img.get_width() or h != img.get_height():
            #     self.surface.blit(pygame.transform.scale(img, (w, h)), (x, y))
            # else:
                self.surface.blit(img, (x, y))

        screen_rectangle = pygame.draw.rect(self.surface, (0, 0, 0), [0, 0, self.screen_width, self.screen_height])

        self.view_x = round(self.resolution_width / 2) - (self.player_ob.get_center_x())
        self.view_y = round(self.resolution_height / 2) - (self.player_ob.get_center_y())

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

        for o in self.visible_obs:

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
                if o.facing == "right":
                    if o.is_on_floor:
                        render_image(self.images[o.img_r], display_x, display_y, display_w, display_h)
                    elif o.ys < 0:
                        render_image(self.images[o.img_r_u], display_x, display_y, display_w, display_h)
                    else:
                        render_image(self.images[o.img_r_d], display_x, display_y, display_w, display_h)
                else:
                    if o.is_on_floor:
                        render_image(self.images[o.img_l], display_x, display_y, display_w, display_h)
                    elif o.ys < 0:
                        render_image(self.images[o.img_l_u], display_x, display_y, display_w, display_h)
                    else:
                        render_image(self.images[o.img_l_d], display_x, display_y, display_w, display_h)
            if type(o).__name__ == "Lettuce":
                render_image(self.images[o.img], display_x, display_y, display_w, display_h)

        pygame.display.update(screen_rectangle)

        self.handle_events()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_running = False

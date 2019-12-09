# PLYTFORM - A platform game engine
# Author: Sam Boulby
import ctypes
import sys
from ctypes import windll

from pygame_gui.elements.ui_label import UILabel
from pygame_gui.ui_manager import UIManager
from pygame.locals import *
import json
from obs import *
from Level import *
import re
import math


class Plytform:

    screen_width = 0
    screen_height = 0
    resolution_width = settings.resolution_width
    resolution_height = settings.resolution_height
    gravity_constant = settings.gravity_constant
    fps = settings.fps
    game_running = False
    obs = []
    movable_obs = []
    visible_obs = []
    solid_obs = []
    remove_from_movable_obs = []
    remove_from_visible_obs = []
    remove_from_solid_obs = []
    bgs = []
    images = {}
    view_x = 0
    view_y = 0
    player_ob = None
    focus_ob = None
    level_width = False
    level_height = False
    current_level_set = []
    current_level = False
    current_level_file_path = ""
    global_frame = 1
    global_frame_max = 32
    is_focussed = False
    level_change_instruction = ""
    frame_count = -1
    victory_frame = 0
    display_mode = "game"
    # keys_held_previous_frame = []
    keys_held_this_frame = []
    keys_down_this_frame = []
    keys_up_this_frame = []

    def __init__(self):
        pygame.init()

        self.resolution_width_ratio = self.screen_width / self.resolution_width
        self.resolution_height_ratio = self.screen_height / self.resolution_height

        # Hack to get round Windows app scaling (thanks Stack Exchange - https://gamedev.stackexchange.com/questions/105750/pygame-fullsreen-display-issue)
        ctypes.windll.user32.SetProcessDPIAware()
        self.screen_width = windll.user32.GetSystemMetrics(0)
        self.screen_height = windll.user32.GetSystemMetrics(1)
        true_res = (self.screen_width, self.screen_height)

        pygame.display.set_mode(true_res, pygame.FULLSCREEN)

        self.surface = pygame.Surface((self.resolution_width, self.resolution_height))
        self.final_surface = pygame.display.get_surface()

        self.up_key = settings.default_up_key
        self.right_key = settings.default_right_key
        self.down_key = settings.default_down_key
        self.left_key = settings.default_left_key
        self.jump_key = settings.default_jump_key
        self.action_key = settings.default_action_key

        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(settings.font_name, settings.font_size)
        self.big_font = pygame.font.Font(settings.big_font_name, settings.big_font_size)

        pygame.mouse.set_visible(settings.cursor_visible)

        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

        # GUI
        self.ui_manager = UIManager((self.resolution_width, self.resolution_height),
                                               "gui_theme.json")
        counter_pos_rect = pygame.Rect(0, 0, 100, 25)
        counter_pos_rect.center = (56, 36)
        self.nugget_counter = UILabel(counter_pos_rect, "", self.ui_manager)

        timer_pos_rect = pygame.Rect(0, 0, 100, 25)
        timer_pos_rect.center = (self.resolution_width - 100, 36)
        self.timer_label = UILabel(timer_pos_rect, "", self.ui_manager)

    def start(self):
        self.game_running = True

        while self.game_running:
            dt = self.clock.tick(self.fps) / self.fps
            if dt < 1:
                dt = 1
            self.handle_events()
            self.cycle_engine(dt)
            self.render()

        pygame.quit()
        sys.exit()

    def add_ob(self, ob):
        self.obs.append(ob)
        if ob.is_mover:
            self.movable_obs.append(ob)
        if ob.is_visible:
            self.visible_obs.append(ob)
        if ob.is_solid:
            self.solid_obs.append(ob)

    def add_obs(self, obs):
        for ob in obs:
            self.add_ob(ob)

    def remove_ob(self, ob):
        if ob.is_mover:
            self.movable_obs.remove(ob)
        if ob.is_visible:
            self.visible_obs.remove(ob)
        if ob in self.solid_obs:
            self.solid_obs.remove(ob)
        for sub_ob in ob.sub_obs:
            ob.remove_sub_ob(sub_ob, self)
        self.obs.remove(ob)

    def load_level_from_file(self, file_path):
        data = json.loads(open(file_path).read())
        self.current_level_file_path = file_path
        self.frame_count = -1

        # Background tiles
        for index, layer in enumerate(data["bg_tile_layers"]):
            for tile_key, tile_value in layer.items():
                if tile_key != "name" and tile_value != False and "img" in tile_value:
                    decoded_img = self.code_to_img(tile_value["img"], data["tile_codes"])
                    tile_value["img"] = decoded_img
                    self.add_image("images/" + tile_value["img"], alpha=True)

        # Objects
        for ob in data["obs"]:
            decoded_type = self.code_to_img(ob["type"], data["ob_type_codes"])
            ob["type"] = decoded_type
            self.add_ob(globals()[ob["type"]](ob["values"]))

        # Foreground tiles
        for layer in data["fg_tile_layers"]:
            for tile_key, tile_value in layer.items():
                if tile_key != "name" and tile_value != False and "img" in tile_value:
                    decoded_img = self.code_to_img(tile_value["img"], data["tile_codes"])
                    tile_value["img"] = decoded_img
                    self.add_image("images/" + tile_value["img"], alpha=True)

        self.current_level = Level(data)
        self.level_width = self.current_level.w * self.current_level.tile_w
        self.level_height = self.current_level.h * self.current_level.tile_h

    def reload_current_level(self):
        self.level_change_instruction = self.current_level_file_path

    def load_next_level(self):
        self.level_change_instruction = self.current_level_set.pop()

    def code_to_img(self, code, lookup_data):
        for data in lookup_data:
            if data["code"] == code:
                if "img" in data:
                    return data["img"]
                elif "type" in data:
                    return data["type"]

    def load_obs_from_file(self, file_path):
        data = json.loads(open(file_path).read())
        for ob in data["obs_to_load"]:
            self.add_ob(globals()[ob["type"]](ob["values"]))

    def add_image(self, path, alpha=False):
        name = path.replace("images/", "")
        if name not in self.images:
            if alpha and "&noalpha" not in name:
                img = pygame.image.load(path).convert_alpha()
            else:
                img = pygame.image.load(path).convert()
            self.images[name] = img
        if re.search("&[0-9]+of[0-9]+", name):
            frames_string = re.findall("&[0-9]+of[0-9]+", name)[0]
            split_string = frames_string.replace("&", "").split("of")
            current_frame = int(split_string[0])
            total_frames = int(split_string[1])
            if current_frame == 1:
                for i in range(2, total_frames + 1):
                    self.add_image(path.replace("1of", str(i) + "of"), alpha=alpha)

    def add_image_set(self, path, number, alpha=False):
        for i in range(1, number + 1):
            self.add_image(path + "-" + str(i) + ".png", alpha)

    def add_bg(self, img, img_w, img_h):
        self.bgs.append({
            "img": img,
            "w": img_w,
            "h": img_h,
        })

    def set_player_ob(self, player):
        if self.player_ob:
            self.player_ob.is_player = False
        self.player_ob = player
        player.is_player = True

    def focus_on(self, ob):
        self.is_focussed = True
        self.focus_ob = ob

    def lose_focus(self):
        self.focus_ob = False
        self.is_focussed = False

    def set_level_dimensions(self, w, h):
        self.level_width = w
        self.level_height = h

    def update_keys(self):
        keys = pygame.key.get_pressed()
        self.keys_held_this_frame = []
        self.keys_down_this_frame = []
        self.keys_up_this_frame = []

        for k in range(len(keys)):
            if keys[k]:
                self.keys_held_this_frame.append(k)

        for k in self.keys_held_this_frame:
            if k not in self.keys_held_previous_frame:
                self.keys_down_this_frame.append(k)

        for k in self.keys_held_previous_frame:
            if k not in self.keys_held_this_frame:
                self.keys_up_this_frame.append(k)

    def cycle_engine(self, dt):
        self.frame_count += 1

        if self.level_change_instruction != "":
            self.obs = []
            self.movable_obs = []
            self.visible_obs = []
            self.solid_obs = []
            self.remove_from_solid_obs = []
            self.remove_from_movable_obs = []
            self.remove_from_visible_obs = []
            self.player_ob = False
            self.lose_focus()
            self.display_mode = "game"
            self.global_frame = 0
            self.frame_count = -1
            self.load_level_from_file(self.level_change_instruction)
            self.level_change_instruction = ""
            self.clean_up_lists()
            return

        self.global_frame += 1
        if self.global_frame > self.global_frame_max:
            self.global_frame = 1
        for ob in self.obs:
            ob.behave(self)

        self.move_and_collide(dt)

        self.clean_up_lists()

        if pygame.K_ESCAPE in self.keys_held_this_frame:
            pygame.quit()

        if self.display_mode == "victory" and self.action_key in self.keys_down_this_frame:
            self.load_next_level()

        # self.keys_held_previous_frame = self.keys_held_this_frame

    def move_and_collide(self, dt):
        if len(self.movable_obs) < 1:
            return

        fastest_speed = 0
        for ob in self.movable_obs:
            ob.is_on_floor = False
            ob.is_in_liquid = False
            ob.is_submerged = False
            ob.has_moved_this_frame = False
            ob.on_slope = ""
            if max(abs(ob.xs), abs(ob.ys)) > fastest_speed:
                fastest_speed = round(max(abs(ob.xs), abs(ob.ys)))

        if fastest_speed < 1:
            fastest_speed = 1

        for i in range(fastest_speed):
            for ob in self.movable_obs:
                if ob.y_direction() != 0:
                    old_y = ob.y
                    ob.move_y(ob.ys / fastest_speed)
                    if ob.y != old_y and not ob.does_not_collide:
                        self.check_collisions(ob, "y", ob.y_direction())
                        ob.has_moved_this_frame = True
                if ob.x_direction() != 0:
                    old_x = ob.x
                    ob.move_x(ob.xs / fastest_speed)
                    if ob.x != old_x and not ob.does_not_collide:
                        self.check_collisions(ob, "x", ob.x_direction())
                        ob.has_moved_this_frame = True

        for ob in self.movable_obs:
            if not ob.has_moved_this_frame and not ob.does_not_collide:
                self.check_collisions(ob, "", 0)

            if ob.cares_about_screen_edges:
                if ob.y < 0:
                    ob.screen_edge_status["top"] = self.current_level.edges["top"]
                    if ob.screen_edge_status["top"] == "impassable":
                        ob.set_y(0)
                        ob.ys = 1
                else:
                    ob.screen_edge_status["top"] = ""

                if ob.x + ob.w > (self.current_level.w * self.current_level.tile_w):
                    ob.screen_edge_status["right"] = self.current_level.edges["right"]
                    if ob.screen_edge_status["right"] == "impassable":
                        ob.set_x(self.current_level.w - ob.w - 1)
                        ob.xs = 1
                else:
                    ob.screen_edge_status["right"] = ""

                if ob.y + ob.h > (self.current_level.h * self.current_level.tile_h):
                    ob.screen_edge_status["bottom"] = self.current_level.edges["bottom"]
                    if ob.screen_edge_status["bottom"] == "impassable":
                        ob.set_y(self.current_level.h - ob.h - 1)
                        ob.ys = 1
                        ob.is_on_floor = True
                else:
                    ob.screen_edge_status["bottom"] = ""

                if ob.x < 0:
                    ob.screen_edge_status["left"] = self.current_level.edges["left"]
                    if ob.screen_edge_status["left"] == "impassable":
                        ob.set_x(0)
                        ob.xs = 0
                else:
                    ob.screen_edge_status["left"] = ""

    def handle_slope_collision(self, ob, ob2):
        if ob2.slope == "UR":
            ob.ys = 2
            ob.set_y(ob2.y + ob2.h - ob.h - ((ob.x + ob.w - ob2.x) * ob2.gradient))
            ob.is_on_floor = True
            ob.xs *= (ob.friction * ob2.friction)
            ob.on_slope = "UR"
        if ob2.slope == "UL":
            ob.ys = 2
            ob.set_y(ob2.y + ob2.h - ob.h - ((ob2.x + ob2.w - ob.x) * ob2.gradient))
            ob.is_on_floor = True
            ob.xs *= (ob.friction * ob2.friction)
            ob.on_slope = "UL"

    def check_collisions(self, ob, axis, direction):
        for ob2 in self.solid_obs:
            if axis != "" and ob.overlaps(ob2):
                special = ob.deal_with_special_collisions(ob2, self)
                if not ob2.is_mover and not special:
                    if not ob2.is_liquid:
                        if axis == "y":
                            if direction == 1:
                                if ob2.slope == "":
                                    ob.ys = 2
                                    ob.set_y(ob2.y - ob.h)
                                    ob.is_on_floor = True
                                    ob.xs *= (ob.friction * ob2.friction)
                                else:
                                    self.handle_slope_collision(ob, ob2)
                            if direction == -1 and not ob2.down_only_collision:
                                if ob2.slope == "":
                                    ob.set_y(ob2.y + ob2.h)
                                    ob.ys = 0
                        if axis == "x" and not ob2.down_only_collision:
                            if direction == 1:
                                if ob2.slope == "":
                                    ob.xs = 0
                                    ob.set_x(ob2.x - ob.w)
                                else:
                                    self.handle_slope_collision(ob, ob2)
                            if direction == -1:
                                if ob2.slope == "":
                                    ob.xs = 0
                                    ob.set_x(ob2.x + ob2.w)
                                else:
                                    self.handle_slope_collision(ob, ob2)
                    elif ob2.is_liquid:
                        ob.xs *= ob2.drag_factor
                        ob.ys *= ob2.drag_factor
                        ob.is_in_liquid = True
                        if ob.y > ob2.y:
                            ob.is_submerged = True
                elif ob.collides_with_movers and ob2.collides_with_movers and not special:
                    if axis == "y":
                        if direction == 1:
                            ob.set_y(ob2.y - ob.h)
                            ob.is_on_floor = True
                            ob.xs *= (ob.friction * ob2.friction)
                        if direction == -1 and not ob2.down_only_collision:
                            ob.set_y(ob2.y + ob2.h)
                        initial_ob_ys = ob.ys
                        ob.ys = ((ob.mass - ob2.mass) / (ob.mass + ob2.mass)) * initial_ob_ys
                        ob2.ys = ((2 * ob.mass) / (ob.mass + ob2.mass)) * initial_ob_ys
                    if axis == "x" and not ob2.down_only_collision:
                        if direction == 1:
                            ob.set_x(ob2.x - ob.w)
                        if direction == -1:
                            ob.set_x(ob2.x + ob2.w)
                        initial_ob_xs = ob.xs
                        ob.xs = ((ob.mass - ob2.mass) / (ob.mass + ob2.mass)) * initial_ob_xs
                        ob2.xs = ((2 * ob.mass) / (ob.mass + ob2.mass)) * initial_ob_xs
            if axis == "" and ob.overlaps(ob2):
                special = ob.deal_with_special_collisions(ob2, self)
                if not special:
                    if ob2.is_liquid:
                        ob.is_in_liquid = True
                        if ob.y > ob2.y:
                            ob.is_submerged = True

    def render(self):

        to_blit = []

        def render_image(img, x, y):
            to_blit.append((img, (x, y)))

        def render_text(text, text_rect):
            to_blit.append((text, text_rect))

        screen_rectangle = pygame.draw.rect(self.final_surface, (0, 0, 0), [0, 0, self.screen_width, self.screen_height])

        if self.is_focussed:
            self.view_x = round(self.resolution_width / 2) - (self.focus_ob.get_center_x())
            self.view_y = round(self.resolution_height / 2) - (self.focus_ob.get_center_y())

        if self.view_x > 0:
            self.view_x = 0
        if self.view_y > 0:
            self.view_y = 0
        if self.level_width and self.view_x < ((self.level_width * -1) + self.resolution_width):
            self.view_x = ((self.level_width * -1) + self.resolution_width)
        if self.level_height and self.view_y < ((self.level_height * -1) + self.resolution_height):
            self.view_y = ((self.level_height * -1) + self.resolution_height)

        # Work out view range for tiles
        tile_view_left = round((self.view_x * - 1) / self.current_level.tile_w) - 2
        tile_view_right = tile_view_left + round(self.resolution_width / self.current_level.tile_w) + 4
        tile_view_top = round((self.view_y * -1) / self.current_level.tile_h) - 2
        tile_view_bottom = tile_view_top + round(self.resolution_height / self.current_level.tile_w) + 4

        # Backgrounds

        for bg in self.bgs:
            w_ratio = (bg["w"] - self.resolution_width) / (self.level_width - self.resolution_width)
            h_ratio = (bg["h"] - self.resolution_height) / (self.level_height - self.resolution_height)

            bg_x = round(self.view_x * w_ratio)
            bg_y = round(self.view_y * h_ratio)
            # bg_w = round(bg["w"] * self.resolution_width_ratio)
            # bg_h = round(bg["h"] * self.resolution_height_ratio)

            render_image(self.images[bg["img"]], bg_x, bg_y)

        # Background tiles

        for bg_layer in self.current_level.bg_tile_layers:
            for tx in range(tile_view_left, tile_view_right):
                for ty in range(tile_view_top, tile_view_bottom):
                    tile_name = str(tx) + "-" + str(ty)
                    if tile_name is not False and tile_name in bg_layer.tiles and bg_layer.tiles[tile_name] is not False:
                        if bg_layer.tiles[tile_name].animated:
                            bg_layer.tiles[tile_name].update_animation(self)
                        render_image(
                            self.images[bg_layer.tiles[tile_name].img],
                            round(self.view_x + (tx * self.current_level.tile_w)),
                            round(self.view_y + (ty * self.current_level.tile_h))
                        )

        # Objects

        for o in self.visible_obs:

            o.animate(self)

            display_x = (self.view_x + o.x - o.offset_x)
            display_y = (self.view_y + o.y - o.offset_y)
            display_w = round(o.w)
            display_h = round(o.h)

            if o.img_w:
                display_w = round(o.img_w)
            if o.img_h:
                display_h = round(o.img_h)

            if display_x + display_w < 0:
                continue
            if display_y + display_h < 0:
                continue
            if display_x > self.resolution_width:
                continue
            if display_y > self.resolution_height:
                continue

            if o.is_visible and o.img in self.images:
                render_image(self.images[o.img], display_x, display_y)

        # Foreground tiles

        for fg_layer in self.current_level.fg_tile_layers:
            for tx in range(tile_view_left, tile_view_right):
                for ty in range(tile_view_top, tile_view_bottom):
                    tile_name = str(tx) + "-" + str(ty)
                    if tile_name is not False and tile_name in fg_layer.tiles and fg_layer.tiles[tile_name] is not False:
                        if fg_layer.tiles[tile_name].animated:
                            fg_layer.tiles[tile_name].update_animation(self)
                        render_image(
                            self.images[fg_layer.tiles[tile_name].img],
                            round(self.view_x + (tx * self.current_level.tile_w)),
                            round(self.view_y + (ty * self.current_level.tile_h))
                        )

        # GUI stuff

        # Normal game GUI
        if self.display_mode == "game" and self.player_ob is not None:

            nugget_count_str = str(self.player_ob.nuggets) + "/" + str(self.current_level.current_nuggets)
            self.nugget_counter.set_text(nugget_count_str)
            # nugget_count_text = self.font.render(
            #     nugget_count_str, True, (255, 255, 255))
            # nugget_count_rect = nugget_count_text.get_rect()
            # nugget_count_rect.center = (56, 36)
            # render_text(nugget_count_text, nugget_count_rect)

            render_image(self.images["nugget-icon.png"], 32, 32)

            if self.player_ob.dandelions > 0:
                render_image(self.images["dandelion-icon-got.png"], 96, 24)
            else:
                render_image(self.images["dandelion-icon-empty.png"], 96, 24)

            if self.is_focussed:
                if hasattr(self.focus_ob, "current_oxygen") and hasattr(self.focus_ob, "total_oxygen"):
                    if self.focus_ob.current_oxygen < self.focus_ob.total_oxygen:
                        air_blocks = math.ceil((self.focus_ob.current_oxygen / self.focus_ob.total_oxygen) * 5)
                        display_x = (self.view_x + self.focus_ob.x - 12)
                        display_y = (self.view_y + self.focus_ob.y - 16)
                        for i in range(0, air_blocks):
                            render_image(self.images["air-unit.png"], display_x + (i * 8), display_y)

            total_millis = (self.frame_count * self.fps)
            total_cents = math.floor(total_millis / 10) % 100
            total_seconds = math.floor(total_millis / 1000) % 60
            total_minutes = math.floor(total_millis / 60000)

            timer_string = (str(total_minutes).zfill(2) + ":" + str(total_seconds).zfill(2)
                            + ":" + str(total_cents).zfill(2))
            self.timer_label.set_text(timer_string)
            # timer_text = self.font.render(
            #     timer_string, True,
            #     (255, 255, 255))
            # timer_text_rect = timer_text.get_rect()
            # timer_text_rect.center = (self.resolution_width - 100, 36)
            # render_text(timer_text, timer_text_rect)

        # Victory GUI
        if self.display_mode == "victory":
            victory_text = self.big_font.render("MASSIVE SUCCESS", True, (255, 255, 255))
            victory_rect = victory_text.get_rect()
            victory_rect.center = (self.resolution_width / 2, self.resolution_height / 4)
            render_text(victory_text, victory_rect)

            total_millis = (self.victory_frame * self.fps)
            total_cents = math.floor(total_millis / 10) % 100
            total_seconds = math.floor(total_millis / 1000) % 60
            total_minutes = math.floor(total_millis / 60000)

            timer_text = self.font.render("Time: " + str(total_minutes).zfill(2) + ":" + str(total_seconds).zfill(2) + ":" + str(total_cents).zfill(2), True, (255, 255, 255))
            timer_text_rect = timer_text.get_rect()
            timer_text_rect.center = (self.resolution_width / 2, self.resolution_height / 2)
            render_text(timer_text, timer_text_rect)

            nugget_percent = math.ceil(((self.current_level.total_nuggets - self.current_level.current_nuggets) / self.current_level.total_nuggets) * 100)

            nuggets_text = self.font.render("Nuggets: " + str(nugget_percent) + "%", True, (255, 255, 255))
            nuggets_text_rect = nuggets_text.get_rect()
            nuggets_text_rect.center = (self.resolution_width / 2, (self.resolution_height / 2) + 32)
            render_text(nuggets_text, nuggets_text_rect)

            injury_text = self.font.render("Injuries: " + str(self.player_ob.injury_count), True, (255, 255, 255))
            injury_text_rect = injury_text.get_rect()
            injury_text_rect.center = (self.resolution_width / 2, (self.resolution_height / 2) + 64)
            render_text(injury_text, injury_text_rect)

            if self.player_ob.dandelions > 0:
                dandelion_text = self.font.render("Dandelion: obtained", True, (255, 255, 255))
            else:
                dandelion_text = self.font.render("Dandelion: no dandelion :(", True, (255, 255, 255))
            dandelion_text_rect = dandelion_text.get_rect()
            dandelion_text_rect.center = (self.resolution_width / 2, (self.resolution_height / 2) + 96)
            render_text(dandelion_text, dandelion_text_rect)

        # Things that just have to happen

        self.surface.blits(to_blit)
        self.ui_manager.update((1.0/max(1.0, self.fps)))
        self.ui_manager.draw_ui(self.surface)
        pygame.transform.scale(self.surface, (self.screen_width, self.screen_height), self.final_surface)
        pygame.display.update(screen_rectangle)

    def handle_events(self):
        self.keys_down_this_frame = []
        self.keys_up_this_frame = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_running = False
            elif event.type == pygame.KEYDOWN:
                self.keys_down_this_frame.append(event.key)
                if event.key not in self.keys_held_this_frame:
                    self.keys_held_this_frame.append(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_up_this_frame.append(event.key)
                while event.key in self.keys_held_this_frame:
                    self.keys_held_this_frame.remove(event.key)

    def clean_up_lists(self):
        for ob in self.remove_from_visible_obs:
            self.visible_obs.remove(ob)
        for ob in self.remove_from_movable_obs:
            self.movable_obs.remove(ob)
        for ob in self.remove_from_solid_obs:
            self.solid_obs.remove(ob)
        self.remove_from_visible_obs = []
        self.remove_from_movable_obs = []
        self.remove_from_solid_obs = []

# Plytform standard object types
from random import *
from Animation import Animation

import pygame
import settings
import datetime


class Ob:
    xs = 0
    ys = 1
    is_mover = True
    is_visible = True
    is_player = False
    is_solid = True
    has_moved_this_frame = False
    friction = 0.95
    is_on_floor = False
    xx = 0.0
    yy = 0.0
    xs_limit = 1000
    ys_limit = 1000
    mass = 1
    buoyancy = 1
    facing = "right"
    img_w = False
    img_h = False
    offset_x = 0
    offset_y = 0
    w = 0
    h = 0
    x = 0
    y = 0
    color = False
    img = False
    slope = ""
    gradient = 0
    on_slope = ""
    is_liquid = False
    has_ai = False
    is_in_liquid = False
    is_submerged = False
    experiences_gravity = False
    down_only_collision = False
    collides_with_movers = True
    can_input = False
    is_animated = False
    animation = False
    does_not_collide = False
    screen_edge_status = {"top": "", "right": "", "bottom": "", "left": ""}
    cares_about_screen_edges = False
    is_victorious = False
    has_failed_off_screen = False
    sub_obs = []

    def __init__(self, values):
        if "x" in values:
            self.set_x(values["x"])
        if "y" in values:
            self.set_y(values["y"])
        if "w" in values:
            self.set_w(values["w"])
        if "h" in values:
            self.set_h(values["h"])
        if "color" in values:
            self.color = values["color"]
        if "img" in values:
            self.img = values["img"]
        if self.slope != "":
            self.gradient = self.h / self.w

    def behave(self, engine):
        if self.experiences_gravity:
            self.apply_gravity()
        if self.is_player and self.can_input:
            self.apply_input(engine)
        if self.has_ai and engine.frame_count > 0:
            self.ai_behave(engine)
        if self.is_animated:
            self.animation.update()
            self.img = self.animation.current_frame
        if self.cares_about_screen_edges:
            self.handle_screen_edges(engine)

    def deal_with_special_collisions(self, other, engine):
        return False

    def ai_behave(self, engine):
        pass

    def handle_screen_edges(self, engine):
        if self.is_player and "victory" in self.screen_edge_status.values() and engine.display_mode != "victory" and engine.frame_count > 0:
            engine.display_mode = "victory"
            engine.victory_frame = engine.frame_count
            self.is_victorious = True
            return
        if self.is_player and "victory" not in self.screen_edge_status and "fail" in self.screen_edge_status.values():
            self.has_failed_off_screen = True

    def set_x(self, x):
        self.x = round(x)
        self.xx = x

    def set_y(self, y):
        self.y = round(y)
        self.yy = y

    def set_xy(self, x, y):
        self.set_x(x)
        self.set_y(y)

    def move_x(self, xs):
        self.set_x(self.xx + xs)

    def move_y(self, ys):
        self.set_y(self.yy + ys)

    def move(self, xs, ys):
        self.move_x(xs)
        self.move_y(ys)

    def set_animation(self, animation):
        self.is_animated = True
        self.animation = animation

    def stop_animation(self):
        self.is_animated = False
        self.animation = False

    def is_moving(self):
        return abs(self.xs) > 0 or abs(self.ys) > 0

    def y_direction(self):
        if self.ys > 0:
            return 1
        if self.ys < 0:
            return -1
        return 0

    def x_direction(self):
        if self.xs > 0:
            return 1
        if self.xs < 0:
            return -1
        return 0

    def get_center_x(self):
        return round(self.x + (self.w / 2))

    def get_center_y(self):
        return round(self.y + (self.h / 2))

    def update_hitbox(self):
        self.offset_x = 0
        self.offset_y = 0
        if self.img_w:
            self.offset_x = round((self.img_w - self.w) / 2)
        if self.img_h:
            self.offset_y = round((self.img_h - self.h) / 2)

    def set_w(self, new_w):
        self.w = new_w
        self.update_hitbox()

    def set_h(self, new_h):
        self.h = new_h
        self.update_hitbox()

    def set_wh(self, new_w, new_h):
        self.w = new_w
        self.h = new_h
        self.update_hitbox()

    def apply_gravity(self):
        if not self.is_in_liquid:
            self.ys += settings.gravity_constant
        else:
            self.ys += (settings.gravity_constant / 2) * self.buoyancy
        if self.ys > settings.terminal_velocity:
            self.ys = settings.terminal_velocity
        # if self.ys < -settings.terminal_velocity:
        #     self.ys = -settings.terminal_velocity

    def apply_input(self, engine):
        pass

    def overlaps(self, other):
        if self is other:
            return False
        if self.x + self.w <= other.x:
            return False
        if self.x >= other.x + other.w:
            return False
        if self.y + self.h <= other.y:
            return False
        if self.y >= other.y + other.h:
            return False
        if other.down_only_collision and self.y + self.h > other.y + other.h:
            return False
        if other.slope == "":
            return True
        else:
            if other.slope == "UL":
                if self.x + 1 <= other.x:
                    return False
                if (self.y + self.h) - (other.y + other.h) < (self.x - (other.x + other.w)) * other.gradient:
                    return False
            if other.slope == "UR":
                if self.x + self.w - 1 >= other.x + other.w:
                    return False
                if (self.y + self.h) - (other.y + other.h) < (other.x - (self.x + self.w)) * other.gradient:
                    return False
        return True

    def animate(self, engine):
        pass

    def become_solid(self, engine):
        self.is_solid = True
        if self not in engine.solid_obs:
            engine.solid_obs.append(self)

    def stop_being_solid(self, engine):
        self.is_solid = False
        if self in engine.solid_obs:
            engine.remove_from_solid_obs.append(self)

    def become_visible(self, engine):
        self.is_visible = True
        if self not in engine.visible_obs:
            engine.visible_obs.append(self)

    def stop_being_visible(self, engine):
        self.is_visible = False
        if self in engine.visible_obs:
            engine.remove_from_visible_obs.append(self)

    def become_mover(self, engine):
        self.is_mover = True
        if self not in engine.movable_obs:
            engine.movable_obs.append(self)

    def stop_being_mover(self, engine):
        self.is_mover = False
        if self in engine.movable_obs:
            engine.remove_from_movables_obs.append(self)

    def add_sub_ob(self, sub_ob, engine):
        if sub_ob not in self.sub_obs:
            engine.add_ob(sub_ob)
            self.sub_obs.append(sub_ob)

    def remove_sub_ob(self, sub_ob, engine):
        if sub_ob in self.sub_obs:
            self.sub_obs.remove(sub_ob)
            engine.remove_ob(sub_ob)


class StaticBlock(Ob):
    is_mover = False
    is_visible = False


class StaticBlockDownOnly(Ob):
    is_mover = False
    is_visible = False
    down_only_collision = True


class StaticSlopeUR(Ob):
    is_mover = False
    is_visible = False
    slope = "UR"


class StaticSlopeUL(Ob):
    is_mover = False
    is_visible = False
    slope = "UL"


class Water(Ob):
    is_mover = False
    is_visible = False
    is_liquid = True
    drag_factor = 0.9


class Fish(Ob):
    w = 8
    h = 8
    img_w = 8
    img_h = 8
    mass = 0.1
    has_ai = True
    img_l = "goldfish-l.png"
    img_r = "goldfish-r.png"
    img = "goldfish-l.png"
    frame_count = 0
    frame_limit = randint(0, 20) + 20
    ys_limit = 4
    experiences_gravity = True

    def animate(self, engine):
        if self.xs > 0:
            self.img = self.img_r
        else:
            self.img = self.img_l

    def ai_behave(self, engine):
        self.frame_count += 1
        if self.is_in_liquid:
            self.experiences_gravity = False
        else:
            self.experiences_gravity = True
        if self.frame_count > self.frame_limit:
            self.frame_count = 0
            self.frame_limit = randint(0, 20) + 20
            self.xs += randint(-4, 4)
            self.ys += randint(-4, 4)


class Goldfish(Fish):
    img_l = "goldfish-l.png"
    img_r = "goldfish-r.png"
    img = "goldfish-l.png"


class Palefish(Fish):
    img_l = "palefish-l.png"
    img_r = "palefish-r.png"
    img = "palefish-l.png"


class Pinkfish(Fish):
    img_l = "pinkfish-l.png"
    img_r = "pinkfish-r.png"
    img = "pinkfish-l.png"


# Not for creation as it is, template for guineas of other flavours
class GenericGuinea(Ob):
    w = 16
    h = 16
    img_folder = ""
    xs_limit = 10
    ys_limit = 10
    is_pancaking = False
    img_w = 64
    img_h = 64
    anim_count = 0
    mass = 0.5
    experiences_gravity = True
    poo_counter = 0
    poo_counter_limit = 400
    left_last_released = datetime.datetime.now() - datetime.timedelta(days=1)
    right_last_released = datetime.datetime.now() - datetime.timedelta(days=1)
    expired_at = datetime.datetime.now() - datetime.timedelta(days=1)
    expire_length = 4000
    invincibility_counter = 0
    is_invincible = True
    is_zooming = False
    anim_speed = 4
    just_hurt = False
    is_hurt = False
    is_expiring = False
    has_expired = False
    is_flying = False
    nuggets = 0
    dandelions = 0
    walk_acceleration = 3
    zoom_acceleration = 9
    jump_acceleration = 20
    friction = 0.94
    cares_about_screen_edges = True
    total_oxygen = 200
    current_oxygen = 200
    buoyancy = 0.5
    injury_count = 0
    has_zoomed_this_jump = False

    def __init__(self, values):
        super(GenericGuinea, self).__init__(values)

        self.img_l = self.img_folder + "/guinea-l.png"
        self.img_l_u = self.img_folder + "/guinea-l-up.png"
        self.img_l_d = self.img_folder + "/guinea-l-down.png"
        self.img_r = self.img_folder + "/guinea-r.png"
        self.img_r_u = self.img_folder + "/guinea-r-up.png"
        self.img_r_d = self.img_folder + "/guinea-r-down.png"
        self.pancake_r = self.img_folder + "/guinea-r-pancake.png"
        self.pancake_l = self.img_folder + "/guinea-l-pancake.png"
        self.hurt_r = self.img_folder + "/guinea-r-hurt.png"
        self.hurt_l = self.img_folder + "/guinea-l-hurt.png"
        self.turning_r = self.img_folder + "/guinea-r-turning.png"
        self.turning_l = self.img_folder + "/guinea-l-turning.png"
        self.swim_r = self.img_folder + "/guinea-r-swim.png"
        self.swim_r_down = self.img_folder + "/guinea-r-swim-down.png"
        self.swim_r_up = self.img_folder + "/guinea-r-swim-up.png"
        self.swim_l = self.img_folder + "/guinea-l-swim.png"
        self.swim_l_down = self.img_folder + "/guinea-l-swim-down.png"
        self.swim_l_up = self.img_folder + "/guinea-l-swim-up.png"

        self.walk_r_animation = Animation(self.img_folder + "/guinea-r-walk-", 8, 2, True)
        self.walk_l_animation = Animation(self.img_folder + "/guinea-l-walk-", 8, 2, True)
        self.zoom_r_animation = Animation(self.img_folder + "/guinea-zoom-r-", 4, 1, True)
        self.zoom_l_animation = Animation(self.img_folder + "/guinea-zoom-l-", 4, 1, True)
        self.expire_r = Animation(self.img_folder + "/guinea-r-hurt-spin-", 4, 1, True)
        self.expire_l = Animation(self.img_folder + "/guinea-l-hurt-spin-", 4, 1, True)
        self.swim_r_animation = Animation(self.img_folder + "/guinea-r-swim-", 4, 4, True)
        self.swim_l_animation = Animation(self.img_folder + "/guinea-l-swim-", 4, 4, True)
        self.swim_r_down_animation = Animation(self.img_folder + "/guinea-r-swim-down-", 4, 4, True)
        self.swim_l_down_animation = Animation(self.img_folder + "/guinea-l-swim-down-", 4, 4, True)
        self.swim_r_up_animation = Animation(self.img_folder + "/guinea-r-swim-up-", 4, 4, True)
        self.swim_l_up_animation = Animation(self.img_folder + "/guinea-l-swim-up-", 4, 4, True)

    def behave(self, engine):
        super().behave(engine)
        if self.is_victorious and not self.has_expired:
            self.behave_victory(engine)
            return
        if self.has_failed_off_screen:
            self.behave_fail_off_screen(engine)
            return
        self.behave_zoom(engine)
        self.behave_poo(engine)
        self.behave_invincibility(engine)
        self.behave_injury(engine)
        self.behave_water(engine)

    def behave_zoom(self, engine):
        if self.is_on_floor:
            self.has_zoomed_this_jump = False

    def behave_victory(self, engine):
        self.experiences_gravity = False
        self.can_input = False
        engine.lose_focus()
        self.xs = self.zoom_acceleration
        self.ys = 0

    def behave_fail_off_screen(self, engine):
        if not self.has_expired:
            self.has_expired = True
            engine.lose_focus()
            self.expired_at = datetime.datetime.now()
        if self.has_expired:
            if datetime.datetime.now() - self.expired_at > datetime.timedelta(milliseconds=self.expire_length / 2):
                engine.reload_current_level()

    def behave_poo(self, engine):
        self.poo_counter += 1
        if self.poo_counter > self.poo_counter_limit:
            self.poo_counter = 0
            if self.facing == "right":
                engine.add_ob(Poo({"x": self.x - 13, "y": self.y + 8, "w": 5, "h": 3}))
            if self.facing == "left":
                engine.add_ob(Poo({"x": self.x + self.w + 8, "y": self.y + 8, "w": 5, "h": 3}))

    def behave_invincibility(self, engine):
        if self.is_invincible:
            self.invincibility_counter += 1
            if self.invincibility_counter > 40:
                self.is_invincible = False

    def behave_injury(self, engine):
        if (self.is_on_floor or self.is_in_liquid) and self.is_hurt:
            self.is_hurt = False
            self.can_input = True
            self.is_invincible = True
            self.invincibility_counter = 0
        if self.just_hurt:
            self.injury_count += 1
            self.just_hurt = False
            self.is_hurt = True
            self.ys = -12
            if self.facing == "right":
                self.xs = -12
            if self.facing == "left":
                self.xs = 12
        if self.is_expiring and not self.has_expired:
            self.ys = -12
            self.has_expired = True
            engine.lose_focus()
            self.expired_at = datetime.datetime.now()
        if self.has_expired:
            if datetime.datetime.now() - self.expired_at > datetime.timedelta(milliseconds=self.expire_length):
                engine.reload_current_level()

    def behave_water(self, engine):
        if self.is_submerged:
            self.current_oxygen -= 1
            if randint(1, 25) == 1:
                bubble_size = pow(2, randint(2, 4))
                engine.add_ob(Bubble({"x": self.x, "y": self.y, "w": bubble_size, "h": bubble_size, "img": "bubble-" + str(bubble_size) + ".png"}))
            if self.current_oxygen < 1 and not self.is_expiring:
                self.expire()
        else:
            self.current_oxygen = self.total_oxygen

    def take_damage(self, engine):
        self.just_hurt = True
        self.can_input = False
        for i in range(0, self.nuggets - 1):
            flying_nugget = FlyingNugget({"x": self.x + randint(-8, 8), "y": self.y + randint(-8, 0)})
            flying_nugget.ys = randint(-20, -5)
            flying_nugget.xs = randint(-10, 10)
            engine.add_ob(flying_nugget)
        self.nuggets = 0

    def expire(self):
        self.can_input = False
        self.collides_with_movers = False
        self.cares_about_screen_edges = False
        self.is_expiring = True
        self.does_not_collide = True
        self.is_invincible = False
        self.is_visible = True

    def expire_other(self, other, engine, particles=20):
        other_l = other.x
        other_r = other.x + other.w
        other_t = other.y
        other_b = other.y + other.h

        engine.remove_ob(other)
        engine.add_ob(BigCircleParticle({
            "x": other.get_center_x() - (BigCircleParticle.w / 2),
            "y": other.get_center_y() - (BigCircleParticle.h / 2)
        }))

        for i in range(1, particles):
            px = randint(other_l, other_r) - 4
            py = randint(other_t, other_b) - 4
            pxs = (self.xs / 2) + randint(-4, 4)
            pys = (self.ys / 2) + randint(-8, 0)
            p = FlyingYellowParticle({"x": px, "y": py})
            engine.add_ob(p)
            p.xs = pxs
            p.ys = pys

    def deal_with_special_collisions(self, other, engine):
        if isinstance(other, Nugget):
            if not other.collected:
                self.nuggets += 1
                engine.current_level.current_nuggets -= 1
                other.collected = True
            return True
        if isinstance(other, Heron) or isinstance(other, SurprisingBird):
            if not self.is_hurt and (abs(self.xs) > 10 or self.ys > 10):
                self.expire_other(other, engine)
            return True
        if isinstance(other, Dandylion):
            if not other.collected:
                self.dandelions += 1
                other.collected = True
            return True
        if isinstance(other, Hazard) and not self.just_hurt and not self.is_hurt and not self.is_invincible:
            if self.nuggets > 0:
                self.take_damage(engine)
            elif not self.is_expiring:
                self.expire()
            return False
        if isinstance(other, SoftHazard):
            if not self.just_hurt and not self.is_hurt and not self.is_invincible:
                if self.nuggets > 0:
                    self.take_damage(engine)
                elif not self.is_expiring:
                    self.expire()
            return True
        if isinstance(other, RicketyBridge) and not other.is_breaking and not other.is_broken:
            other.is_breaking = True
            return False

    def animate(self, engine):
        self.stop_animation()
        self.anim_count += 1

        if self.is_expiring:
            if self.facing == "right":
                self.set_animation(self.expire_r)
            if self.facing == "left":
                self.set_animation(self.expire_l)
        else:
            if self.is_invincible and self.invincibility_counter % 10 < 5:
                self.is_visible = False
            else:
                self.is_visible = True
            if self.is_on_floor:
                if self.facing == "right":
                    if self.xs < -0.1:
                        self.img = self.turning_r
                    else:
                        if self.xs < 1:
                            if self.is_pancaking:
                                self.img = self.pancake_r
                            else:
                                self.img = self.img_r
                        else:
                            if self.is_zooming:
                                self.set_animation(self.zoom_r_animation)
                            else:
                                self.set_animation(self.walk_r_animation)
                if self.facing == "left":
                    if self.xs > 0.1:
                        self.img = self.turning_l
                    else:
                        if self.xs > -1:
                            if self.is_pancaking:
                                self.img = self.pancake_l
                            else:
                                self.img = self.img_l
                        else:
                            if self.is_zooming:
                                self.set_animation(self.zoom_l_animation)
                            else:
                                self.set_animation(self.walk_l_animation)
            else:
                if self.facing == "right":
                    if self.is_flying:
                        if self.xs < -1:
                            self.img = self.turning_l
                        elif self.xs > 4:
                            self.set_animation(self.fly_fast_r_animation)
                        else:
                            self.img = self.flying_r
                    elif self.is_in_liquid:
                        if self.xs > 0.5:
                            self.set_animation(self.swim_r_animation)
                        if self.ys < -0.5:
                            self.set_animation(self.swim_r_up_animation)
                        if self.ys > 0.5:
                            self.set_animation(self.swim_r_down_animation)
                        if self.xs <= 0.5 and -0.5 <= self.ys <= 0.5:
                            self.img = self.img_r_d

                    else:
                        if self.ys < 0:
                            if self.is_hurt:
                                self.img = self.hurt_r
                            else:
                                self.img = self.img_r_u
                        else:
                            self.img = self.img_r_d
                else:
                    if self.is_flying:
                        if self.xs > 1:
                            self.img = self.turning_l
                        elif self.xs < -4:
                            self.set_animation(self.fly_fast_l_animation)
                        else:
                            self.img = self.flying_l
                    elif self.is_in_liquid:
                        if self.xs < -0.5:
                            self.set_animation(self.swim_l_animation)
                        if self.ys < -0.5:
                            self.set_animation(self.swim_l_up_animation)
                        if self.ys > 0.5:
                            self.set_animation(self.swim_l_down_animation)
                        if self.xs >= -0.5 and -0.5 <= self.ys <= 0.5:
                            self.img = self.img_l_d

                    else:
                        if self.ys < 0:
                            if self.is_hurt:
                                self.img = self.hurt_l
                            else:
                                self.img = self.img_l_u
                        else:
                            self.img = self.img_l_d

    def apply_input(self, engine):
        self.is_pancaking = False

        if self.is_on_floor and not self.is_in_liquid:
            if engine.left_key in engine.keys_held_this_frame:
                self.facing = "left"
                if engine.action_key in engine.keys_held_this_frame:
                    self.is_zooming = True
                else:
                    self.is_zooming = False
                if self.is_zooming:
                    self.xs -= self.zoom_acceleration
                else:
                    self.xs -= self.walk_acceleration
            if engine.right_key in engine.keys_held_this_frame:
                self.facing = "right"
                if engine.action_key in engine.keys_held_this_frame:
                    self.is_zooming = True
                else:
                    self.is_zooming = False
                if self.is_zooming:
                    self.xs += self.zoom_acceleration
                else:
                    self.xs += self.walk_acceleration
            if engine.jump_key in engine.keys_down_this_frame:
                if not self.is_in_liquid:
                    self.ys = -self.jump_acceleration

        elif self.is_in_liquid:
            if engine.up_key in engine.keys_held_this_frame:
                self.ys -= self.walk_acceleration
            if engine.right_key in engine.keys_held_this_frame:
                self.facing = "right"
                self.xs += self.walk_acceleration
            if engine.down_key in engine.keys_held_this_frame:
                self.ys += self.walk_acceleration
            if engine.left_key in engine.keys_held_this_frame:
                self.facing = "left"
                self.xs -= self.walk_acceleration

        else:
            if engine.left_key in engine.keys_held_this_frame:
                if self.xs > (self.xs_limit * -1):
                    self.xs -= self.walk_acceleration / 2
            if engine.right_key in engine.keys_held_this_frame:
                if self.xs < self.xs_limit:
                    self.xs += self.walk_acceleration / 2
            if engine.action_key in engine.keys_down_this_frame and not self.has_zoomed_this_jump:
                self.has_zoomed_this_jump = True
                self.ys = 0
                if engine.left_key in engine.keys_held_this_frame:
                    self.facing = "left"
                if engine.right_key in engine.keys_held_this_frame:
                    self.facing = "right"
                if self.facing == "right":
                    self.xs = self.zoom_acceleration * 3
                if self.facing == "left":
                    self.xs = self.zoom_acceleration * -3
                engine.add_ob(BigCircleParticle({"x": self.x - 8, "y": self.y - 8}))

        if engine.down_key in engine.keys_held_this_frame:
            self.is_pancaking = True


class SuperGuinea(GenericGuinea):
    img_folder = "super-guinea"
    can_input = True
    is_flying = False
    fly_star_count = 0
    nugget_use_speed = 20
    nugget_flight_counter = 20
    fly_acceleration = 2.5

    def __init__(self, values):
        super(SuperGuinea, self).__init__(values)
        self.flying_r = self.img_folder + "/guinea-r-fly.png"
        self.flying_l = self.img_folder + "/guinea-l-fly.png"

        self.fly_fast_r_animation = Animation(self.img_folder + "/guinea-r-fly-fast-", 2, 1, True)
        self.fly_fast_l_animation = Animation(self.img_folder + "/guinea-l-fly-fast-", 2, 1, True)

    def behave(self, engine):
        super().behave(engine)
        self.behave_flight(engine)

    def behave_flight(self, engine):
        if self.is_flying and (self.is_in_liquid or self.is_on_floor):
            self.stop_flying()
        if self.is_flying:
            self.nugget_flight_counter += 1
            if self.nugget_flight_counter > self.nugget_use_speed:
                if self.nuggets > 0:
                    self.nuggets -= 1
                    self.nugget_flight_counter = 0
                else:
                    self.stop_flying()
            else:
                self.xs *= 0.85
                self.ys *= 0.85
                self.fly_star_count += 1
                if self.fly_star_count > 4:
                    self.fly_star_count = 0
                    engine.add_ob(YellowParticle({"x": self.x + randint(-10, 10), "y": self.y + randint(-10, 10), "w": 8, "h": 8}))

    def take_damage(self, engine):
        super().take_damage(engine)
        if self.is_flying:
            self.stop_flying()

    def start_flying(self):
        self.is_flying = True
        self.experiences_gravity = False

    def stop_flying(self):
        self.is_flying = False
        self.experiences_gravity = True

    def apply_input(self, engine):
        if engine.jump_key in engine.keys_down_this_frame:
            if not self.is_on_floor and not self.is_in_liquid:
                if self.is_flying:
                    self.stop_flying()
                else:
                    self.start_flying()
        if self.is_flying:
            if engine.up_key in engine.keys_held_this_frame:
                self.ys -= self.fly_acceleration
            if engine.down_key in engine.keys_held_this_frame:
                self.ys += self.fly_acceleration
            if engine.left_key in engine.keys_held_this_frame:
                self.facing = "left"
                self.xs -= self.fly_acceleration
            if engine.right_key in engine.keys_held_this_frame:
                self.facing = "right"
                self.xs += self.fly_acceleration

        super().apply_input(engine)


class ChutneyGuinea(GenericGuinea):
    img_folder = "chutney-guinea"
    can_input = True


class BadGuinea(GenericGuinea):
    img_folder = "bad-guinea"
    can_input = True


class Poo(Ob):
    img = "guinea-poo.png"
    w = 5
    h = 3
    collides_with_movers = False
    experiences_gravity = True
    buoyancy = -0.25


class Lettuce(Ob):
    img = "lettuce"
    xs_limit = 5
    ys_limit = 5
    img_w = 16
    img_h = 16
    experiences_gravity = True


class Dandylion(Ob):
    img = "dandylion.png"
    w = 32
    h = 32
    is_mover = False
    collected = False

    def __init__(self, values):
        super(Dandylion, self).__init__(values)
        self.normal_animation = Animation("dandelion-", 6, 4, True)
        self.collected_animation = Animation("dandelion-collected-", 5, 2, False)
        self.set_animation(self.normal_animation)

    def animate(self, engine):
        if self.collected:
            self.set_animation(self.collected_animation)

    def behave(self, engine):
        super().behave(engine)
        if self.collected and self.collected_animation.is_complete:
            engine.remove_ob(self)


class Nugget(Ob):
    img = "nugget-1.png"
    w = 32
    h = 32
    is_mover = False
    collected = False

    def __init__(self, values):
        super(Nugget, self).__init__(values)
        self.nugget_animation = Animation("nugget-", 4, 2, True)
        self.collected_animation = Animation("yellow-particle-", 4, 1, False)
        self.x -= 4
        self.y -= 4
        self.w = 32
        self.h = 32

    def animate(self, engine):
        if not self.collected:
            self.set_animation(self.nugget_animation)
        else:
            self.set_animation(self.collected_animation)
            if self.collected_animation.is_complete:
                engine.remove_ob(self)


class FlyingNugget(Ob):
    img = "nugget-1.png"
    w = 8
    h = 8
    is_mover = True
    experiences_gravity = True
    collides_with_movers = False
    is_solid = False
    nugget_animation = Animation("nugget-", 4, 2, True)
    does_not_collide = True

    def __init__(self, values):
        super(FlyingNugget, self).__init__(values)
        self.created_at = datetime.datetime.now()

    def behave(self, engine):
        super().behave(engine)
        if datetime.datetime.now() - self.created_at > datetime.timedelta(seconds=5):
            engine.remove_ob(self)

    def animate(self, engine):
        self.set_animation(self.nugget_animation)


class Hazard(StaticBlock):
    is_hazardous = True


class SoftHazard(Ob):
    is_mover = False
    is_visible = False
    is_hazardous = True

    def deal_with_special_collisions(self, other, engine):
        if isinstance(other, SuperGuinea):
            return True


class YellowParticle(Ob):
    is_solid = False
    collides_with_movers = False
    is_mover = False

    def __init__(self, values):
        super(YellowParticle, self).__init__(values)
        self.yellow_particle_animation = Animation("yellow-particle-", 4, 1, False)

    def animate(self, engine):
        self.set_animation(self.yellow_particle_animation)
        if self.yellow_particle_animation.is_complete:
            engine.remove_ob(self)


class FlyingYellowParticle(Ob):
    w = 8
    h = 8
    is_solid = False
    does_not_collide = True
    collides_with_movers = False
    is_mover = True

    def __init__(self, values):
        super(FlyingYellowParticle, self).__init__(values)
        self.yellow_particle_animation = Animation("yellow-particle-", 4, 1, False)

    def animate(self, engine):
        self.set_animation(self.yellow_particle_animation)
        if self.yellow_particle_animation.is_complete:
            engine.remove_ob(self)


class BigCircleParticle(Ob):
    is_solid = False
    collides_with_movers = False
    is_mover = False
    w = 32
    h = 32

    def __init__(self, values):
        super(BigCircleParticle, self).__init__(values)
        self.particle_animation = Animation("big-circle-particle-", 8, 1, False)

    def animate(self, engine):
        self.set_animation(self.particle_animation)
        if self.particle_animation.is_complete:
            engine.remove_ob(self)


class Bubble(Ob):
    is_solid = False
    collides_with_movers = False
    buoyancy = -1
    experiences_gravity = True
    is_submerged = True
    has_ai = True
    counter = 0

    def ai_behave(self, engine):
        self.counter += 1
        if self.counter > 100:
            engine.remove_ob(self)
        if not self.is_submerged:
            engine.remove_ob(self)
        else:
            if randint(1, 4) == 1:
                self.xs += randint(-2, 2)


class GuineaSpawner(Ob):
    is_solid = False
    collides_with_movers = False
    is_mover = False

    def behave(self, engine):
        player = SuperGuinea({"x": self.x + 16, "y": self.y + 16, "w": 16, "h": 16})
        engine.add_ob(player)
        engine.focus_on(player)
        engine.set_player_ob(player)
        engine.remove_ob(self)


class RicketyBridge(Ob):
    is_breaking = False
    is_broken = False
    is_mover = False
    experiences_gravity = False
    breaking_cycles = 5
    break_counter = 0

    def __init__(self, values):
        super(RicketyBridge, self).__init__(values)
        self.img = "gentle-garden/rickety-bridge.png"

    def behave(self, engine):
        super().behave(engine)
        if self.is_breaking and not self.is_broken:
            self.img = "gentle-garden/rickety-bridge-breaking.png"
            self.break_counter += 1
            if self.break_counter > self.breaking_cycles:
                self.img = "gentle-garden/rickety-bridge-broken.png"
                self.is_breaking = False
                self.is_broken = True
                self.become_mover(engine)
                self.stop_being_solid(engine)
                self.experiences_gravity = True
                self.collides_with_movers = False
                self.ys = 1

    def deal_with_special_collisions(self, other, engine):
        if isinstance(other, Nugget) or isinstance(other, Dandylion):
            return True


class Heron(Ob):
    w = 8
    h = 28
    img_w = 80
    img_h = 64
    mass = 2
    has_ai = True
    img_l = "heron/heron-l.png"
    img_l_peck_high = "heron/heron-l-peck-high.png"
    img_l_peck_low = "heron/heron-l-peck-low.png"
    img_r = "heron/heron-r.png"
    img_r_peck_high = "heron/heron-r-peck-high.png"
    img_r_peck_low = "heron/heron-r-peck-low.png"
    img = img_l
    experiences_gravity = True
    strike_ob = False
    last_strike_time = 0

    def __init__(self, values):
        super(Heron, self).__init__(values)
        self.offset_y = 28

    def ai_behave(self, engine):
        player_x_diff = engine.player_ob.get_center_x() - self.get_center_x()
        player_y_diff = engine.player_ob.get_center_y() - self.get_center_y()

        if engine.frame_count - self.last_strike_time > 4:
            if self.strike_ob:
                self.remove_sub_ob(self.strike_ob, engine)
                self.strike_ob = False
            if player_x_diff < 0:
                self.img = self.img_l
            if player_x_diff > 0:
                self.img = self.img_r

        if engine.frame_count - self.last_strike_time > 8:
            if -32 < player_x_diff < 0:
                if 32 > player_y_diff > 0:
                    self.img = self.img_l_peck_low
                    self.strike_ob = SoftHazard({"x": self.get_center_x() - 25, "y": self.get_center_y() - 7, "w": 4, "h": 13})
                    self.add_sub_ob(self.strike_ob, engine)
                    self.last_strike_time = engine.frame_count
                if -32 < player_y_diff < 0:
                    self.img = self.img_l_peck_high
                    self.strike_ob = SoftHazard({"x": self.get_center_x() - 38, "y": self.get_center_y() - 24, "w": 12, "h": 6})
                    self.add_sub_ob(self.strike_ob, engine)
                    self.last_strike_time = engine.frame_count
            elif 32 > player_x_diff > 0:
                if 32 > player_y_diff > 0:
                    self.img = self.img_r_peck_low
                    self.strike_ob = SoftHazard({"x": self.get_center_x() + 21, "y": self.get_center_y() - 7, "w": 4, "h": 13})
                    self.add_sub_ob(self.strike_ob, engine)
                    self.last_strike_time = engine.frame_count
                if -32 < player_y_diff < 0:
                    self.img = self.img_r_peck_high
                    self.strike_ob = SoftHazard({"x": self.get_center_x() + 26, "y": self.get_center_y() - 24, "w": 12, "h": 6})
                    self.add_sub_ob(self.strike_ob, engine)
                    self.last_strike_time = engine.frame_count

    def deal_with_special_collisions(self, other, engine):
        if isinstance(other, SuperGuinea):
            return True


class SurprisingBird(Ob):
    w = 16
    h = 16
    img_w = 64
    img_h = 64
    mass = 1
    has_ai = True
    img_flap_down = "surprising-bird/surprising-bird-flap-down.png"
    img_flap_mid = "surprising-bird/surprising-bird-flap-mid.png"
    img_flap_up = "surprising-bird/surprising-bird-flap-up.png"
    img_standing = "surprising-bird/surprising-bird-standing.png"
    animation_dive_prefix = "surprising-bird/surprising-bird-dive-"
    experiences_gravity = False
    is_hovering = True
    last_flap_frame = 0
    is_hazardous = False
    is_diving = False
    is_flying_back_up = False
    land_frame = 0
    is_swooping = False
    flap_cycle = 0
    xs_limit = 5
    just_landed = False

    def __init__(self, values):
        super(SurprisingBird, self).__init__(values)
        self.dive_animation = Animation(self.animation_dive_prefix, 2, 1, True)
        self.start_x = values["x"]
        self.start_y = values["y"]
        self.hazard_ob = SoftHazard({"y": self.y - 1, "x": self.x - 1, "h": self.h + 2, "w": self.w + 2})

    def animate(self, engine):
        self.stop_animation()
        if self.is_hovering:
            flap_interval = engine.frame_count - self.last_flap_frame
            if flap_interval % 10 == 0:
                self.move_y(1)
            if flap_interval < 40:
                self.img = self.img_flap_up
            elif flap_interval < 44:
                self.img = self.img_flap_mid
            elif flap_interval < 48:
                self.img = self.img_flap_down
                if flap_interval >= 44:
                    self.move_y(-1)
            elif flap_interval < 52:
                self.img = self.img_flap_mid
            elif flap_interval >= 52:
                self.img = self.img_flap_up
                self.last_flap_frame = engine.frame_count
        if self.is_on_floor:
            self.img = self.img_standing
        else:
            if self.is_swooping:
                self.set_animation(self.dive_animation)
            if self.is_flying_back_up:
                self.flap_cycle += 1
                if self.flap_cycle > 4:
                    self.flap_cycle = 0
                    if self.img == self.img_flap_mid:
                        self.img = self.img_flap_down
                    elif self.img == self.img_flap_up:
                        self.img = self.img_flap_mid
                    else:
                        self.img = self.img_flap_up

    def ai_behave(self, engine):
        px = engine.player_ob.get_center_x()
        py = engine.player_ob.get_center_y()

        if self.is_hovering:
            self.ys = 0
            if abs(self.get_center_x() - px) < 64 and 0 < (py - self.y) < 320:
                self.swoop(engine)

        if self.is_swooping:
            if self.x > px and self.xs >= (self.xs_limit * -1):
                self.xs -= 1
            if self.x < px and self.xs <= self.xs_limit:
                self.xs += 1
            self.hazard_ob.set_xy(self.x - 1, self.y - 1)

        if self.just_landed:
            self.just_landed = False
            engine.remove_ob(self.hazard_ob)

        if self.is_on_floor and self.is_swooping:
            self.land(engine)

        if self.is_on_floor and not self.is_swooping and engine.frame_count - self.land_frame > 25:
            self.fly_back_up()

        if self.is_flying_back_up:
            if self.y > self.start_y:
                self.ys = -2
            else:
                self.hover()

    def swoop(self, engine):
        engine.add_ob(self.hazard_ob)
        self.is_swooping = True
        self.experiences_gravity = True
        self.is_hazardous = True
        self.is_flying_back_up = False
        self.is_hovering = False

    def land(self, engine):
        self.xs = 0
        self.is_swooping = False
        self.land_frame = engine.frame_count
        self.experiences_gravity = True
        self.is_hazardous = False
        self.is_flying_back_up = False
        self.is_hovering = False
        self.just_landed = True

    def fly_back_up(self):
        self.is_swooping = False
        self.experiences_gravity = False
        self.is_hazardous = False
        self.is_flying_back_up = True
        self.is_hovering = False

    def hover(self):
        self.is_swooping = False
        self.experiences_gravity = False
        self.is_hazardous = False
        self.is_flying_back_up = False
        self.is_hovering = True

    def deal_with_special_collisions(self, other, engine):
        if isinstance(other, SoftHazard):
            if other == self.hazard_ob:
                return True
        if isinstance(other, Nugget) or isinstance(other, Dandylion):
            return True
        return False



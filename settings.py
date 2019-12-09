import pygame

#screen_width = 640
#screen_height = 480
resolution_width = 640
resolution_height = 360

gravity_constant = 3
fps = 30
terminal_velocity = 20

default_tile_w = 32
default_tile_h = 32

default_level_w = 32
default_level_h = 32

default_level_edges = {"top": "off-screen", "right": "victory", "bottom": "fail", "left": "impassable"}

editor_screen_w = 1366
editor_screen_h = 768

font_name = "freesansbold.ttf"
font_size = 12
big_font_name = "freesansbold.ttf"
big_font_size = 17

cursor_visible = False

default_up_key = pygame.K_UP
default_right_key = pygame.K_RIGHT
default_down_key = pygame.K_DOWN
default_left_key = pygame.K_LEFT
default_jump_key = pygame.K_a
default_action_key = pygame.K_s

from plytform import *


P = Plytform()
img_folder = "images/"


def load_img(ref):
    P.add_image("images/" + ref + ".png", True)


def load_generic_guinea_imgs(folder_name):
    load_img(folder_name + "/guinea-r")
    load_img(folder_name + "/guinea-r-up")
    load_img(folder_name + "/guinea-r-down")
    load_img(folder_name + "/guinea-r-pancake")
    load_img(folder_name + "/guinea-r-hurt")
    load_img(folder_name + "/guinea-r-turning")
    load_img(folder_name + "/guinea-l")
    load_img(folder_name + "/guinea-l-up")
    load_img(folder_name + "/guinea-l-down")
    load_img(folder_name + "/guinea-l-pancake")
    load_img(folder_name + "/guinea-l-hurt")
    load_img(folder_name + "/guinea-l-turning")
    P.add_image_set("images/" + folder_name + "/guinea-r-walk", 8, True)
    P.add_image_set("images/" + folder_name + "/guinea-l-walk", 8, True)
    P.add_image_set("images/" + folder_name + "/guinea-zoom-l", 4, True)
    P.add_image_set("images/" + folder_name + "/guinea-zoom-r", 4, True)
    P.add_image_set("images/" + folder_name + "/guinea-r-hurt-spin", 4, True)
    P.add_image_set("images/" + folder_name + "/guinea-l-hurt-spin", 4, True)
    P.add_image_set("images/" + folder_name + "/guinea-r-swim", 4, True)
    P.add_image_set("images/" + folder_name + "/guinea-l-swim", 4, True)
    P.add_image_set("images/" + folder_name + "/guinea-r-swim-down", 4, True)
    P.add_image_set("images/" + folder_name + "/guinea-l-swim-down", 4, True)
    P.add_image_set("images/" + folder_name + "/guinea-r-swim-up", 4, True)
    P.add_image_set("images/" + folder_name + "/guinea-l-swim-up", 4, True)


#P.load_level_from_file("levels/gg-piglington-mannor-v4.json")
#P.load_level_from_file("levels/gg-flower-garden.json")
#P.load_level_from_file("levels/gg-grounds.json")
#P.load_level_from_file("levels/gg-water-feature.json")
#P.load_level_from_file("levels/gg-main-gate.json")
#P.load_level_from_file("levels/gg-wildlife-reserve.json")
#P.load_level_from_file("levels/gg-rabbit-warren.json")
#P.load_level_from_file("levels/gg-down-dale.json")
#P.load_level_from_file("levels/gg-lakeside.json")

P.current_level_set = [
    "levels/gg-piglington-mannor-v4.json",
    "levels/gg-flower-garden.json",
    "levels/gg-grounds.json",
    "levels/gg-water-feature.json",
    "levels/gg-main-gate.json",
    "levels/gg-wildlife-reserve.json",
    "levels/gg-rabbit-warren.json",
    "levels/gg-down-dale.json",
    "levels/gg-lakeside.json",
]

P.current_level_set.reverse()

P.load_level_from_file(P.current_level_set.pop())

load_generic_guinea_imgs("super-guinea")
load_generic_guinea_imgs("chutney-guinea")
load_generic_guinea_imgs("bad-guinea")

# Super Guinea extras
P.add_image("images/super-guinea/guinea-r-fly.png", True)
P.add_image("images/super-guinea/guinea-l-fly.png", True)
P.add_image_set("images/super-guinea/guinea-r-fly-fast", 2, True)
P.add_image_set("images/super-guinea/guinea-l-fly-fast", 2, True)

P.add_image("images/gentle-garden/sky-bg.png")
P.add_image("images/gentle-garden/sky-bg-16-9.png")
P.add_image("images/gentle-garden/clouds-bg.png", True)
P.add_image("images/gentle-garden/hills-bg.png", True)
P.add_image("images/gentle-garden/wild-trees-bg.png", True)
P.add_image("images/lettuce.gif", True)
P.add_image("images/goldfish-l.png", True)
P.add_image("images/palefish-l.png", True)
P.add_image("images/pinkfish-l.png", True)
P.add_image("images/goldfish-r.png", True)
P.add_image("images/palefish-r.png", True)
P.add_image("images/pinkfish-r.png", True)
P.add_image("images/guinea-poo.png", True)
P.add_image("images/dandylion.png", True)
P.add_image("images/nugget-icon.png", True)
P.add_image("images/gentle-garden/rickety-bridge.png", True)
P.add_image("images/gentle-garden/rickety-bridge-breaking.png", True)
P.add_image("images/gentle-garden/rickety-bridge-broken.png", True)
P.add_image("images/bubble-4.png", True)
P.add_image("images/bubble-8.png", True)
P.add_image("images/bubble-16.png", True)
P.add_image("images/air-unit.png", True)
P.add_image("images/dandelion-icon-got.png", True)
P.add_image("images/dandelion-icon-empty.png", True)
P.add_image("images/heron/heron-l.png", True)
P.add_image("images/heron/heron-r.png", True)
P.add_image("images/heron/heron-l-peck-high.png", True)
P.add_image("images/heron/heron-r-peck-high.png", True)
P.add_image("images/heron/heron-l-peck-low.png", True)
P.add_image("images/heron/heron-r-peck-low.png", True)

# Surprising Bird
P.add_image("images/surprising-bird/surprising-bird-flap-down.png", True)
P.add_image("images/surprising-bird/surprising-bird-flap-mid.png", True)
P.add_image("images/surprising-bird/surprising-bird-flap-up.png", True)
P.add_image("images/surprising-bird/surprising-bird-standing.png", True)
P.add_image_set("images/surprising-bird/surprising-bird-dive", 2, True)

P.add_image_set("images/nugget", 4, True)
P.add_image_set("images/yellow-particle", 4, True)
P.add_image_set("images/dandelion", 6, True)
P.add_image_set("images/dandelion-collected", 5, True)
P.add_image_set("images/big-circle-particle", 8, True)

P.add_bg("gentle-garden/sky-bg-16-9.png", 768, 432)
P.add_bg("gentle-garden/clouds-bg.png", 740, 555)
P.add_bg("gentle-garden/hills-bg.png", 960, 720)
#P.add_bg("gentle-garden/wild-trees-bg.png", 920, 640)

#P.add_ob(GuineaSpawner({"x": 32, "y": 1008}))

P.start()

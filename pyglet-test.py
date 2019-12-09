import pyglet

game_window = pyglet.window.Window(640, 480)
pyglet.resource.path = ['images']
pyglet.resource.reindex()

main_batch = pyglet.graphics.Batch()

guinea_r = pyglet.resource.image("guinea-r.png")
guinea = pyglet.sprite.Sprite(img=guinea_r, x=32, y=32, batch=main_batch)


def rect(x, y, w, h, c):
    wy = game_window.height - y - h
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                         ("v2f", (x, wy, x + w, wy, x + w, wy + h, x, wy + h)),
                         ("c3B", (c[0], c[1], c[2], c[0], c[1], c[2], c[0], c[1], c[2], c[0], c[1], c[2])))


@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()
    rect(0, 0, 32, 32, (100, 200, 100))
    rect(32, 32, 32, 32, (200, 200, 100))
    rect(64, 64, 32, 32, (100, 100, 200))


if __name__ == '__main__':
    pyglet.app.run()

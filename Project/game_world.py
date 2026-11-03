world = []


def add_object(obj):
    world.append(obj)


def remove_object(obj):
    if obj in world:
        world.remove(obj)


def update():
    for obj in world:
        obj.update()


def render():
    for obj in world:
        obj.draw()

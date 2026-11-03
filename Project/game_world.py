MAX_DEPTH = 10
DEFAULT_DEPTH = 0
world = [[] for _ in range(MAX_DEPTH)]


def add_object(obj, depth=DEFAULT_DEPTH):
    if not 0 <= depth < MAX_DEPTH:
        raise ValueError(f"depth must be between 0 and {MAX_DEPTH - 1}")
    world[depth].append(obj)


def remove_object(obj):
    for objects in world:
        if obj in objects:
            objects.remove(obj)
            return


def clear():
    for objects in world:
        objects.clear()


def handle_event(event):
    for objects in world:
        for obj in objects:
            handle_event_method = getattr(obj, "handle_event", None)
            if handle_event_method is not None:
                handle_event_method(event)


def update():
    for objects in world:
        for obj in objects:
            obj.update()


def render():
    for objects in world:
        for obj in objects:
            obj.draw()

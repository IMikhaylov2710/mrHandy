def moveMouse(x, y, mouse):
    return mouse.move(x, y, absolute=True, duration=0, steps_per_second=100.0)

def clickMouse(mouse):
    return mouse.click(button='left')

def doubleClickMouse(mouse):
    mouse.click(button='left')
    mouse.release(button='left')
    mouse.click(button='left')
    mouse.release(button='left')
    return True

def releaseMouse(mouse):
    return mouse.release(button='left')

def pressMouse(mouse):
    return mouse.press(button='left')
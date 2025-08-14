import platform

# Adapters provide a unified interface:
# - move(x, y, absolute=True, duration=0, steps_per_second=100.0)
# - click(button='left')
# - press(button='left')
# - release(button='left')

class MacMouseAdapter:
    def __init__(self):
        import macmouse  # type: ignore
        self._mouse = macmouse

    def move(self, x, y, absolute=True, duration=0, steps_per_second=100.0):
        return self._mouse.move(x, y, absolute=absolute, duration=duration, steps_per_second=steps_per_second)

    def click(self, button='left'):
        return self._mouse.click(button=button)

    def press(self, button='left'):
        return self._mouse.press(button=button)

    def release(self, button='left'):
        return self._mouse.release(button=button)


class PynputMouseAdapter:
    def __init__(self):
        from pynput.mouse import Controller, Button  # type: ignore
        self._controller = Controller()
        self._Button = Button

    def _map_button(self, button: str):
        return self._Button.left if button == 'left' else self._Button.right

    def move(self, x, y, absolute=True, duration=0, steps_per_second=100.0):
        # pynput has no duration/steps. We set absolute position directly.
        self._controller.position = (int(x), int(y))
        return True

    def click(self, button='left'):
        self._controller.click(self._map_button(button))
        return True

    def press(self, button='left'):
        self._controller.press(self._map_button(button))
        return True

    def release(self, button='left'):
        self._controller.release(self._map_button(button))
        return True


def get_mouse_adapter():
    system = platform.system()
    if system == 'Darwin':
        try:
            return MacMouseAdapter()
        except Exception:
            # Fallback if macmouse is unavailable
            return PynputMouseAdapter()
    else:
        # Linux and Windows
        return PynputMouseAdapter()
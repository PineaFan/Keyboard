from razer import RGBColor
import time


def callback(razer):
    """
    Race lights
    > Set each set of function keys to red in turn, until all are red, where they switch to green
    > Wipe across the keyboard to make it all green
    > Specifically highlight the main keys (A-Z) in green, and make the rest dark green
    """
    kbd = [RGBColor(0, 0, 0)] * 22 * 6
    # Set keys 1 to 4, then 1 to 8, then 1 to 12 to red, with 1s between each
    for x in range(0, 3):
        kbd[3:4 * (x + 1) + 3] = [RGBColor(255, 0, 0)] * (4 * (x + 1))
        razer.set_colors(kbd, "KEYBOARD")
        time.sleep(1)
    # Set the function keys all to green, and the mousemat+mouse to green
    kbd[3:22] = [RGBColor(0, 255, 0)] * 19
    razer.set_colors(kbd, "KEYBOARD")
    razer.set_colors(RGBColor(0, 255, 0), "MOUSEMAT")
    razer.set_colors(RGBColor(0, 255, 0), "MOUSE")
    time.sleep(1)
    # Wipe across the keyboard to make it all green
    for x in range(0, 22):
        for y in range(0, 6):
            kbd[x + y * 22] = RGBColor(0, 255, 0)
        razer.set_colors(kbd, "KEYBOARD")
    time.sleep(1)
    # Highlight x 0 to 14, y 1 to 5 in green, and the rest in dark green
    highlight = RGBColor(0, 255, 0)
    current_green = RGBColor(0, 255, 0)
    for l in range(0, 255, 5):
        # Set the keyboard regions to the correct colours
        kbd = [current_green] * 22 * 6
        for x in range(0, 15):
            for y in range(1, 6):
                kbd[x + y * 22] = highlight
        razer.set_colors(kbd, "KEYBOARD")
        # Decrease the green brightness (Full saturation, green hue, decreasing brightness)
        current_green = RGBColor(0, 255 - l, 0)

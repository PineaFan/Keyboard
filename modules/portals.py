from razer import RGBColor
import time

def callback(razer):
    """
    A white ball moves from left to right, and loops back around. The left and right of the keyboard are blue and orange respectively.
    """

    for n in range(0, 22 * 10 + 11):
        ball_x = n % 22
        ball_y = 3
        # Create a list of key indexes which include the 8 keys around the ball
        # The x coordinate should wrap around the keyboard (as the edges are portals)
        ball_pixels = [
            ball_x + ball_y * 22,
            (ball_x - 1) % 22 + ball_y * 22,
            (ball_x + 1) % 22 + ball_y * 22,
            ball_x + (ball_y - 1) * 22,
            (ball_x - 1) % 22 + (ball_y - 1) * 22,
            (ball_x + 1) % 22 + (ball_y - 1) * 22,
            ball_x + (ball_y + 1) * 22,
            (ball_x - 1) % 22 + (ball_y + 1) * 22,
            (ball_x + 1) % 22 + (ball_y + 1) * 22,
        ]
        kbd = []
        k = min(max(0, (n - 100) * 2), 255)
        for key_index in range(0, 22 * 6):
            x = key_index % 22
            y = key_index // 22
            if x < 2:
                kbd.append(RGBColor(0, 0, 255))
            elif x > 19:
                kbd.append(RGBColor(255, 165, 0))
            elif key_index in ball_pixels:
                kbd.append(RGBColor(*[255 - k] * 3))
            else:
                kbd.append(RGBColor(*[k] * 3))
        razer.set_colors(kbd, "KEYBOARD")

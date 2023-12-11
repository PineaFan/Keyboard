import time
import math
from razer import RGBColor
from utils import hsl_to_rgb
import random

distances = []
# The keyboard is 22x6, so we need to calculate the distance from each key to the middle
for n in range(0, 22 * 6):
    distances.append(math.sqrt((n % 22 - 11) ** 2 + (n // 22 - 3) ** 2))


def callback(razer):
    # Cycle through Red-orange-yellow-green-blue-purple-pink, radiating from the middle of the keyboard
    # This should be done in bands - Only solid hues should be used
    hues = [0, 30, 60, 120, 180, 240, 300]
    hues = [RGBColor(*hsl_to_rgb((h, 255, 128))) for h in hues]
    hues.append(RGBColor(0, 0, 0))
    max_distance = max(distances)
    kbd = [RGBColor(0, 0, 0)] * 22 * 6
    for hue in hues:
        for i in range(math.ceil(max_distance) + 1):
            # i is the threshold for the next colour
            # Set all keys with a distance less than i to the current hue
            n = 0
            for x in range(0, 22):
                for y in range(0, 6):
                    if distances[x + y * 22] < i:
                        n += 1
                        kbd[x + y * 22] = hue
            razer.set_colors(kbd, "KEYBOARD")
    # Highlight keys in green
    cutoff = 0  # Increases each frame
    smallest = min(distances)
    furthest = max(distances)
    n = random.randint(1, 6)  # Pick from R/G/B/C/M/Y
    def to_tuple(colour):
        colour = round(colour)
        # Set the red value to colour if the first bit of n is set
        # Set the green value to colour if the second bit of n is set
        # Set the blue value to colour if the third bit of n is set
        return RGBColor(*[colour if n & (1 << i) else 0 for i in range(3)])
    # Set each key to green at {cutoff} brightness, or their distance from the middle, whichever is smaller
    for cutoff in range(10):
        for x in range(0, 22):
            for y in range(0, 6):
                kbd[x + y * 22] = to_tuple(min(cutoff, furthest - distances[x + y * 22]) * 5)
        razer.set_colors(kbd, "KEYBOARD")

        # Set the mousemat and mouse to the colour of the middle key (22 * 6 / 2)
        razer.set_colors(to_tuple(min(cutoff, furthest - distances[11 + 3 * 22]) * 5), "MOUSEMAT")
        razer.set_colors(to_tuple(min(cutoff, furthest - distances[11 + 3 * 22]) * 5), "MOUSE")

import time
from razer import RGBColor
import subprocess

def callback(razer):
    before = [False, False, False]
    colours = [RGBColor(255, 0, 0), RGBColor(255, 0, 255), RGBColor(255, 255, 255)]
    while True:
        # Get if caps lock is on using xset
        subprocess_output = subprocess.check_output(["xset", "-q"]).decode("utf-8")
        # Get only line index 3
        subprocess_output = subprocess_output.split("\n")[3]
        # Do this by splitting by spaces
        now = [x == "on" for x in subprocess_output.split(" ") if x in ["on", "off"]]
        now[1] = not now[1]  # Num lock should be on most of the time
        to_toggle = [x for x in range(len(now)) if now[x] != before[x]]
        for i in to_toggle:
            razer.set_colors(colours[i] if now[i] else RGBColor(0, 0, 0), "MOTHERBOARD")
        before = now
        time.sleep(0.1)

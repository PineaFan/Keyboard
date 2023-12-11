import time
import subprocess
import psutil
import threading

from razer import Client, RGBColor

import opening
from modules import weatherAdaptive
from modules import notifications
from modules import torch


# Create a client object
razer = Client(port=6767)
# Create a blank keyboard list, which is 22*6 long full of RGBColor objects
kbd = [RGBColor(0, 0, 0)] * 22 * 6
razer.set_colors(kbd, "KEYBOARD")
razer.set_colors(RGBColor(0, 0, 0), "MOUSEMAT")
razer.set_colors(RGBColor(0, 0, 0), "MOUSE")
razer.set_colors(RGBColor(0, 0, 0), "MOTHERBOARD")
time.sleep(1)

opening.callback(razer)
time.sleep(3)

threading.Thread(target=weatherAdaptive.callback, args=(razer,)).start()
threading.Thread(target=notifications.callback, args=(razer,)).start()
threading.Thread(target=torch.callback, args=(razer,)).start()

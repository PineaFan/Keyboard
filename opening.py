from modules import race
from modules import radiate
from modules import portals
import random

def callback(razer):
    modules = [race, radiate, portals]
    chosen = random.choice(modules)
    chosen.callback(razer)

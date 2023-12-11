import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gi.repository.GLib
from razer import RGBColor
import time


def callback(razer):
    def notifications(bus, message):
        # Check if it is a notification
        if message.get_member() != "Notify":
            return
        if message.get_args_list()[0] == "discord":
            for b in range(125, 0, -5):
                razer.set_colors(RGBColor(0, 0, b), "MOTHERBOARD")
                razer.set_colors(RGBColor(0, 0, b), "MOUSEMAT")
                time.sleep(0.01)
            razer.set_colors(RGBColor(0, 0, 0), "MOTHERBOARD")
            razer.set_colors(RGBColor(0, 0, 0), "MOUSEMAT")
        else:
            for g in range(125, 0, -5):
                razer.set_colors(RGBColor(0, g, 0), "MOTHERBOARD")
                razer.set_colors(RGBColor(0, g, 0), "MOUSEMAT")
                time.sleep(0.01)
            razer.set_colors(RGBColor(0, 0, 0), "MOTHERBOARD")
            razer.set_colors(RGBColor(0, 0, 0), "MOUSEMAT")

    DBusGMainLoop(set_as_default=True)

    bus = dbus.SessionBus()
    bus.add_match_string_non_blocking("eavesdrop=true, interface='org.freedesktop.Notifications', member='Notify'")
    bus.add_message_filter(notifications)

    mainloop = gi.repository.GLib.MainLoop()
    mainloop.run()

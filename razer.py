import openrgb
import subprocess
import time
from dataclasses import dataclass
from typing import Iterator
import struct


@dataclass
class RGBColor:
    red: int
    green: int
    blue: int
    def pack(self, version: int = 0) -> bytes:
        return struct.pack("BBBx", self.red, self.green, self.blue)
    @classmethod
    def unpack(cls, data: Iterator[int], version: int, *args):
        r = parse_var('B', data)
        g = parse_var('B', data)
        b = parse_var('B', data)
        parse_var('x', data)
        return cls(r, g, b)
    @classmethod
    def fromHSV(cls, hue: int, saturation: int, value: int):
        return cls(*(round(i * 255) for i in colorsys.hsv_to_rgb(hue/360, saturation/100, value/100)))
    @classmethod
    def fromHEX(cls, hex: str):
        return cls(*(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)))


class Client:
    def __init__(self, port=6767):
        self.client = openrgb.OpenRGBClient(port=port)
        self.devices = self.fetch_devices()

    def fetch_devices(self):
        types = [str(x) for x in openrgb.utils.DeviceType.__dict__ if not str(x).startswith("_")]
        devices = {}
        for device_type in types:
            d = self.client.get_devices_by_type(getattr(openrgb.utils.DeviceType, device_type))
            if d:
                devices[device_type] = d
        return devices

    def hexToRGB(self, hex):
        if hex.startswith("#"):
            hex = hex[1:]
        return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))

    def set_colors(self, colours: list | RGBColor, t):
        if isinstance(colours, list):
            for device in self.devices[t]:
                device.set_colors(colours)
        else:
            for device in self.devices[t]:
                device.set_color(colours)

    def close_connection(self):
        self.client.disconnect()

    @property
    def all(self):
        return self.devices

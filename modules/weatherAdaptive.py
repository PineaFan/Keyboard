import requests
import time
import random
from razer import RGBColor


def get_coordinates() -> tuple[float, float, str]:
    """
    Returns the coordinates of the user
    """
    data = requests.get("http://ip-api.com/json").json()
    print("Getting weather for " + data["city"] + ", " + data["country"])
    return data["lat"], data["lon"], data["timezone"]


def get_weather(lat: float, lon: float, timezone: str) -> dict:
    """
    """
    data = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation,cloudcover,visibility,windspeed_10m&current_weather=true&daily=sunrise,sunset&windspeed_unit=ms&forecast_days=1&timezone={timezone}").json()
    return data


def interpolate(input_min, input_max, output_min, output_max, t):
    return round((t - input_min) / (input_max - input_min) * (output_max - output_min) + output_min)


def time_to_seconds(time: str) -> int:
    # Convert a time in the form 2023-09-29T07:06 to seconds since midnight
    h, m = time.split("T")[1].split(":")
    return int(h) * 60 * 60 + int(m) * 60


# https://www.desmos.com/calculator/rixoj53axk

def red_equation(t: int, sr: int, ss: int) -> float:
    # Takes a time in seconds since midnight, and returns a value from 0 to 1 representing the red value
    # Red should spike at sunrise and sunset, and be low at noon
    # Red should be 1 at a difference of 0, and 0 from ± 2 hours (7200 seconds)
    # This gives the equation y = max(0, -1/7200 * x + 1)
    return min(max(-1/7200 * min(abs(t+sr-3600), abs(t-ss-3600)) + 1, 0.1), 1)


def green_equation(t: int, sr: int, ss: int) -> float:
    # Green does not generally go above 0.5, and is 0 at night
    # During the day, it is high at noon, and low at sunrise and sunset
    # This gives the equation y = (-1x10^-9)(x-sr)(x-ss)
    return min(max(-1e-9 * (t - sr) * (t - ss), 0), 0.75)


def blue_equation(t: int, sr: int, ss: int) -> float:
    # Blue is high throughout the day, low at night, and starts at sunrise and ends at sunset
    # This gives the equation y = (-2x10^-9)(x-sr)(x-ss)
    return min(max(-2e-9 * (t - sr) * (t - ss), 0.1), 1)


wind_pixels = [
    [129, 107, 85, 63, 41],  # 0 degrees
    [129, 106, 85, 63, 41],  # 30 degrees
    [129, 106, 85, 65, 43],  # 60 degrees...
    [84, 85, 86, 65],
    [40, 62, 85, 108, 109],
    [40, 62, 85, 10, 130],
    [41, 63, 85, 107, 129],
    [42, 64, 85, 106, 129],
    [43, 64, 85, 106],
    [65, 86, 85, 84],
    [109, 109, 85, 62, 40],
    [130, 107, 85, 63, 40]
]
number_pad_pixels = list(set([pixel for row in wind_pixels for pixel in row]))


def callback(razer):
    lat, lon, timezone = get_coordinates()
    last_weather_read = 0  # Last time the weather was read as a unix timestamp

    frame_count = 0
    keyboard = [RGBColor(0, 0, 0)] * 22 * 6
    raindrops = {}
    lightning_strikes = []

    while True:
        if time.time() - last_weather_read > 60 * 5:  # If it has been more than 5 minutes since the last weather read
            weather = get_weather(lat, lon, timezone)
            last_weather_read = time.time()
            current_hour = time.localtime().tm_hour
            import json
            with open("weather.json", "w") as f:
                json.dump(weather, f, indent=4)
            print("Refreshed weather")
            cloud_cover = weather["hourly"]["cloudcover"][current_hour]
            # cloud_cover = interpolate(0, 60, 0, 100, time.localtime().tm_sec)
            visibility = weather["hourly"]["visibility"][current_hour]
            rain = weather["hourly"]["precipitation"][current_hour]
            lightning = rain > 2.5  # If the rain is more than 2.5mm/h, this counts as heavy rain, and lightning should be shown
            temperature = weather["current_weather"]["temperature"]
            wind_speed = weather["current_weather"]["windspeed"]
            wind_direction = weather["current_weather"]["winddirection"]
            # Wind direction is measured as the direction the wind is coming from, in degrees from the north, clockwise
            # To correct for this, add 180 to the value and take the modulus
            wind_direction = ((wind_direction + 180) % 360) // 30

            # Set the top row of keys to reflect the cloud cover
            # Cloud coverage is a value from 0 to 100. At 0, the keys should be blue, at 100, they should be white
            # Interpolate between the two values
            value = interpolate(0, 100, 50, 175, cloud_cover)
            blue = interpolate(0, 100, 100, 175, cloud_cover)
            keyColour = RGBColor(value, value, 255)
            keyboard[0:22] = [keyColour] * 22

            # Based on the time of day, estimate the colour temperature of the light
            # This should be 0 at sunrise, 100 at noon, and 0 at sunset. At midnight, it should be -100
            sunrise = weather["daily"]["sunrise"][0]
            sunset = weather["daily"]["sunset"][0]
            # Convert both times to seconds since midnight. Both are in the form 2023-09-29T07:06
            sunrise = time_to_seconds(sunrise)
            sunset = time_to_seconds(sunset)

            # The insert/home/page keys should reflect the actual temperature
            # https://www.desmos.com/calculator/kwon2z4olq
            red = interpolate(-10, 0, 0, 1, temperature)
            green = (temperature / (5 if temperature < 0 else -30)) + 1
            blue = interpolate(10, 0, 0, 1, temperature)
            red, green, blue = min(max(round(red * 255), 0), 255), min(max(round(green * 255), 0), 255), min(max(round(blue * 255), 0), 255)
            keys = [37, 38, 39, 59, 60, 61]
            colour = RGBColor(red, green, blue)
            for key in keys:
                keyboard[key] = colour
            arrows = [104, 125, 126, 127]
            for key in arrows:
                keyboard[key] = RGBColor(50, 50, 50)
            keyboard[103] = RGBColor(0, 255, 0)
            keyboard[105] = RGBColor(255, 0, 0)

        if frame_count % 600 == 0: # Every 1 minute
            current_seconds = time.localtime().tm_hour * 60 * 60 + time.localtime().tm_min * 60 + time.localtime().tm_sec
            params = (current_seconds, sunrise, sunset)
            r, g, b = red_equation(*params), green_equation(*params), blue_equation(*params)
            sky_colour = RGBColor(round(r * 255), round(g * 255), round(b * 255))
            # Set the keys from 0 to 15 on rows 2 onwards to the colour temperature
            for row in range(1, 6):
                keyboard[row * 22:row * 22 + 14] = [sky_colour] * 14

            solar_colour = RGBColor(255, 255, 255) if current_seconds < sunrise or current_seconds > sunset else RGBColor(255, 255, 0)
            # Find the position of the sun
            keyboard[interpolate(sunrise, sunset, 0, 21, current_seconds) % 21] = solar_colour

        # The number pad is animated to show the wind speed and direction
        # Show an animation of a blue pixel moving across the number pad at a speed proportional to the wind speed, and a direction proportional to the wind direction
        # Wind speed is m/s, direction is in degrees from the north, clockwise
        # Use the frame count to determine the position of the pixel. The animation will reset every more often the higher the wind speed is
        animation_length = round(40 / wind_speed)
        index = round(frame_count % animation_length)
        for number in number_pad_pixels:
            keyboard[number] = RGBColor(128, 128, 128)
        if index < len(wind_pixels[wind_direction]):
            keyboard[wind_pixels[wind_direction][index]] = RGBColor(50, 50, 255)
        if index - 1 > 0 and index - 1 < len(wind_pixels[wind_direction]):
            keyboard[wind_pixels[wind_direction][index - 1]] = RGBColor(75, 75, 255)
        if index - 2 > 0 and index - 2 < len(wind_pixels[wind_direction]):
            keyboard[wind_pixels[wind_direction][index - 2]] = RGBColor(100, 100, 255)

        # If it is raining, show the rain on the keyboard
        # This should play from keys 0 to 15 on rows 0 to 5
        # Rain is stored in the rain dictionary, which stores the x value as a key, and the y value as a value
        # Every frame, the rain should move down by 1, so the y value should be incremented by 1
        # When the y value reaches 6, it should be removed from the dictionary

        if rain > 0:
            # Increment
            for key in list(raindrops.keys()):
                raindrops[key] += 1
                # Delete
                if raindrops[key] > 5:
                    # Set the key to the colour of the sky
                    keyboard[22*5 + key] = sky_colour
                    del raindrops[key]
            # Create
            if random.randint(0, round(interpolate(0, 5, 5, 1, rain))) == 0:
                raindrops[random.randint(0, 14)] = 0
            # Display
            for k, v in raindrops.items():
                if v > 0:
                    keyboard[k + (v - 1) * 22] = sky_colour
                keyboard[k + v * 22] = RGBColor(0, 0, 255)

        # Do a similar process for lightning, except keep the previous lit pixels, and allow the pixel to move left or right
        # Every frame, the pixel should move down 1, and left or right 1, or stay in the same place
        # There is a 1 in 100 chance of a lightning strike every frame
        # The lightning list contains the x value of the lightning strike

        if lightning:
            indices_to_delete = []
            # Increment
            for i in range(len(lightning_strikes)):
                current_x = lightning_strikes[i][-1]
                new_x = current_x + random.randint(-1, 1)
                lightning_strikes[i].append(min(max(new_x, 0), 14))
                # Delete
                if len(lightning_strikes[i]) > 5:
                    # Set all keys back to the colour of the sky
                    # Also set the keys to either side, if they are in range
                    for y, x in enumerate(lightning_strikes[i]):
                        keyboard[22*y + x] = sky_colour
                        if x > 0:
                            keyboard[22*y + x - 1] = sky_colour
                        if x < 14:
                            keyboard[22*y + x + 1] = sky_colour
                    indices_to_delete.append(i)
            # Delete
            for index in indices_to_delete:
                del lightning_strikes[index]
            # Create
            if random.randint(0, round(interpolate(10, 100, 2.5, 7.5, rain))) == 0:
                lightning_strikes.append([random.randint(0, 14)])
            # Display
            for strike in lightning_strikes:
                big = len(strike) == 6
                for y, x in enumerate(strike):
                    keyboard[22*y + x] = RGBColor(255, 255, 0)
                    # If big, also set the pixels to either side, if they are in range
                    if x > 0:
                        keyboard[22*y + x - 1] = RGBColor(255, 255, 0)
                    if x < 14:
                        keyboard[22*y + x + 1] = RGBColor(255, 255, 0)

        razer.set_colors(keyboard, "KEYBOARD")
        time.sleep(0.1)
        frame_count = (frame_count + 1) % 1e10

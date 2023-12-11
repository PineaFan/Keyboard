def hsl_to_rgb(hsl):
    h, s, l = hsl
    while h < 0:
        h += 360
    while h >= 360:
        h -= 360
    s /= 255
    l /= 255
    c = (1 - abs(2*l - 1)) * s
    x = c * (1 - abs(h/60 % 2 - 1))
    m = l - c/2
    if h < 60:
        r, g, b = c + m, x + m, 0 + m
    elif h < 120:
        r, g, b = x + m, c + m, 0 + m
    elif h < 180:
        r, g, b = 0 + m, c + m, x + m
    elif h < 240:
        r, g, b = 0 + m, x + m, c + m
    elif h < 300:
        r, g, b = x + m, 0 + m, c + m
    else:
        r, g, b = c + m, 0 + m, x + m
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    return (r, g, b)

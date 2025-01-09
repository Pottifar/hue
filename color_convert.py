import math

def convert_color(colortemp_mireds, brightness):
    """
    Converts the light's color temperature (mireds) and brightness to RGB values.
    :param colortemp_mireds: Color temperature in mireds (153-500 typical range for Hue).
    :param brightness: Brightness value (1-254 typical range for Hue).
    :return: Tuple of scaled (R, G, B) values, where each is in the range [0, 255].
    """
    # Convert mireds to Kelvin
    kelvin = 1000000 / colortemp_mireds

    # Ensure Kelvin is within the valid range
    if kelvin < 1000:
        kelvin = 1000
    elif kelvin > 40000:
        kelvin = 40000

    tmp_internal = kelvin / 100.0

    # Red calculation
    if tmp_internal <= 66:
        red = 255
    else:
        tmp_red = 329.698727446 * math.pow(tmp_internal - 60, -0.1332047592)
        red = max(0, min(255, tmp_red))

    # Green calculation
    if tmp_internal <= 66:
        tmp_green = 99.4708025861 * math.log(tmp_internal) - 161.1195681661
        green = max(0, min(255, tmp_green))
    else:
        tmp_green = 288.1221695283 * math.pow(tmp_internal - 60, -0.0755148492)
        green = max(0, min(255, tmp_green))

    # Blue calculation
    if tmp_internal >= 66:
        blue = 255
    elif tmp_internal <= 19:
        blue = 0
    else:
        tmp_blue = 138.5177312231 * math.log(tmp_internal - 10) - 305.0447927307
        blue = max(0, min(255, tmp_blue))

    # Scale RGB by brightness (brightness range is 1-254)
    scale = brightness / 254
    scaled_red = int(red * scale)
    scaled_green = int(green * scale)
    scaled_blue = int(blue * scale)

    return scaled_red, scaled_green, scaled_blue

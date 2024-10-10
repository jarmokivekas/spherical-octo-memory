from dataclasses import dataclass

red = (255,0,0)
blue = (0,128,255)
orange = (255,128,0)
white = (255,255,255)
gray = (200,200,200)
cyan = (0, 255,255)
gpx = orange + (100,)
black = (0,0,0)
green = (128,255,0)
lidar = (0, 255, 128)


@dataclass
class Cyberpunk:
    dark: tuple = (40,40,40)
    gray: tuple = (117, 113,  94)
    white: tuple = (255,255,255)
    pink: tuple = (219, 112, 147)
    orange: tuple = (255, 165, 0)
    green: tuple = (0, 255, 127)
    blue: tuple = (0, 191, 255)
    yellow: tuple = (255, 255, 0)
    purple: tuple = (148, 0, 211)

    cyan: tuple = (0, 255, 255)
    magenta: tuple = (255, 0, 255)
    lime: tuple = (50, 205, 50)
    red: tuple = (255, 36, 0)

@dataclass
class Monokai:
    dark: tuple = (39,  40,   34)
    gray: tuple = (117, 113,  94)
    white: tuple = (248, 248, 242)
    pink: tuple = (249, 38,  114)
    orange: tuple = (253, 151,  31)
    green: tuple = (166, 226,  46)
    blue: tuple = (102, 217, 239)
    yellow: tuple = (230, 219, 116)
    purple: tuple = (174, 129, 255)


def is_ground_color(color):
    if ((color[0] == 0) and
        (color[1] == 0) and
        (color[2] == 0)
    ):
        return True
    else:
        return False

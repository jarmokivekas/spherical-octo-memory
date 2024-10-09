red = (255,0,0)
accent_blue = (0,128,255)
orange = (255,128,0)
white = (255,255,255)
gray = (200,200,200)
cyan = (0, 255,255)
gpx = orange + (100,)
black = (0,0,0)
green = (128,255,0)
lidar = (0, 255, 128)


def is_ground_color(color):
    if ((color[0] == 0) and
        (color[1] == 0) and
        (color[2] == 0)
    ):
        return True
    else:
        return False

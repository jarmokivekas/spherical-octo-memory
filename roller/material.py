import random
from roller.datatypes import Point
HEATMAP = 0
SCATTERMAP = 1

def get_scattering_propability(pixel_color: tuple):
    return 1 - color[SCATTERMAP / 255]

def get_temperature_at(point: Point, world):
    pixel_color = world.surface.get_at((int(point.x),int(point.y)))
    temperature = pixel_color[HEATMAP]
    return temperature

def is_light_scattering(pixel_color: tuple):
    scattering_propability = 1 - pixel_color[SCATTERMAP] / 255
    return random.random() < scattering_propability


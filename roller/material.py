"""
This module defines what materials and properties are represented by different
color pixels in the world raster
"""

import random
from roller.datatypes import Point

HEATMAP = 0
"""The HEATMAP is mapped to the red channel in the world raster.
the value of the red channel directly represents the ambient temperature in celcius.
"""

SCATTERMAP = 1
"""Represents how likely a pixel is to scatter light.
The values is mapped to the green channel of the world raster.
0 means a 100% probability for scattering,
i.e. the pixel is completely opaque to light.
255 means the pixel will never scatter."""

def get_scattering_propability(pixel_color: tuple):
    return (1 - pixel_color[SCATTERMAP] /255) **2

def get_temperature_at(point: Point, world):
    pixel_color = world.surface.get_at((int(point.x),int(point.y)))
    temperature = pixel_color[HEATMAP]
    return temperature

def is_light_scattering(pixel_color: tuple):
    scattering_propability =  get_scattering_propability(pixel_color)
    return random.random() < scattering_propability


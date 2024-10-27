"""
This module defines what materials and properties are represented by different
color pixels in the world raster
"""

from functools import lru_cache
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

@lru_cache(maxsize=None)  # maxsize=None means unlimited cache size. limit it if needed
def get_scattering_probability(scattermap_value: int):
    """Calculates the laser scattering probability based on the pixel color.
    Uses caching to avoid recalculating for the same color values (@lru_cache decorator).
    
    Caching this result reduced profiling time for 0.460 seconds to < 0.000 seconds during 10 seconds of the gameloop
    """
    return (1 - scattermap_value / 255) ** 2

def get_temperature_at(point: Point, world):
    pixel_color = world.surface.get_at((int(point.x),int(point.y)))
    temperature = pixel_color[HEATMAP]
    return temperature

def is_light_scattering(pixel_color: tuple):
    scattering_propability =  get_scattering_probability(pixel_color[SCATTERMAP])
    return random.random() < scattering_propability


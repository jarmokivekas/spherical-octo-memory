from typing import NamedTuple

# Define the named tuple for an xy coordinate
class Point(NamedTuple):
    """A named tuple for representing (x,y) coordinates on world or screen Surface.
    Functions that take a point as an argument can also take any other object with 
    `x` and `y` properties that represent a location. e.g an instance of any Bot class
    counts also as a Point"""
    x: float
    y: float

class Line(NamedTuple):
    """A named tuple for representing a line from (x,y) Points start to end on a world or screen Surface.
    `start` and `end` are expected to conform to the `Point` interface, i.e have `.x` and `.y` attributes
    representing the coordinates of the point."""
    start: Point
    end: Point
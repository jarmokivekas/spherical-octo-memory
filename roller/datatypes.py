from collections import namedtuple


# Define the named tuple for an xy coordinate
Point = namedtuple('Point', ['x', 'y'])
"""A named tuple for representing (x,y) coordinates on world or screen Surface.
Functions that take a point as an argument can also take any other object with 
`x` and `y` properties that represent a location. e.g an instance of any Bot class
counts also as a Point"""



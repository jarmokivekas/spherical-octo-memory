import math
import random
from roller.datatypes import Point
from roller import colors

def scalarProduct(ax, ay, bx, by):
    return ax*bx + ay*by;

def vectorProjection(ax, ay, bx, by):
    coef = scalarProduct(ax, ay, bx, by) / scalarProduct(bx, by, bx, by);
    return [coef * bx, coef * by];


def get_line_pixels(start: Point, end: Point):
    """Returns a list of (x, y) coordinates of all pixels along the line from (x0, y0) to (x1, y1).
    This should be an implementation of Bresenham's algorithm"""
    x0 = start.x
    y0 = start.y
    x1 = end.x
    y1 = end.y

    pixels = []
    
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        pixels.append(Point(int(x0), int(y0)))  # Store the current pixel coordinates
        if (abs(x0 - x1) < 1) and (abs(y0- y1) < 1):
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    
    return pixels

def get_line_endpoint(start: Point, distance:float, angle:float):
    # Calculate new coordinates using trigonometry
    x2 = start.x + distance * math.cos(angle)
    y2 = start.y + distance * math.sin(angle)
    return Point(x2, y2)



def get_first_solid_pixel(origin, max_range, theta, world):
    """function used for sensors. Calculates coordinates for all pixels along 
    the line going from origin, in direction theta all the way to the max_range.
    Then scans trhough and returns the coordinates of the first soil/ground pixel along the line"""
    # the pixel coordinates at max_range from origin in direction theta
    end_point = get_line_endpoint(origin, max_range, theta)
    # coordinates for all pixels along the ray
    ray_points = get_line_pixels(origin, end_point)
    for point in ray_points:
        pixel_color = world.surface.get_at(point)
        if colors.is_ground_color(pixel_color):
            return point
        if colors.is_water_color(pixel_color):
            if random.random() <= 0.10:
                return point
            continue
    return None


def clip(value, min, max):
    """return `value` unless it's outside the min/max boundary. If outside, return the boundary value instead"""
    if value < min:
        value = min
    if value > max:
        value = max

    return value


def screen2world(screen_point:Point, world):
    return Point(screen_point.x - world.x, screen_point.y - world.y)

def world2screen(world_point: Point, world):
    return Point(world_point.x + world.x, world_point.y + world.y)
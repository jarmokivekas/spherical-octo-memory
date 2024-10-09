from roller import color
from collections import namedtuple
import pygame
import numpy as np
import math
# Define the named tuple for an xy coordinate
Point = namedtuple('Point', ['x', 'y'])

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

def is_ground_color(color):
    if ((color[0] < 15) and
        (color[1] < 15) and
        (color[2] < 15)
    ):
        return True
    else:
        return False

def get_line_endpoint(start: Point, distance:float, angle:float):
    # Calculate new coordinates using trigonometry
    x2 = start.x + distance * math.cos(angle)
    y2 = start.y + distance * math.sin(angle)
    return Point(x2, y2)


def passive_sonar():
    pass

def active_sonar():
    pass

def motion_detection():
    pass

def ground_penetrating_radar():
    pass

def gpx_trail(world, screen, player):
    # origin a xy cooridinate in reference to the 0,0 corner of the world surface.
    origin = Point(player.x - world.x, player.y - world.y)
    pygame.draw.circle(world.memory, color.gray, origin, 1) 

def screen2world(screen_point:Point, world):
    return Point(screen_point.x - world.x, screen_point.y - world.y)



def lidar(world, screen, player):
    origin = screen2world(player, world)
    lidar_range = 400
    lidar_samples = 40
    lidar_shows_lines = True
    
    for theta in np.linspace(0, 2*math.pi, num=lidar_samples):
        # We calculat the world coordinate to which the lidat ray will travel
        end_point = get_line_endpoint(origin, lidar_range, theta)
        # origin and endpoint are now in world coordinates
        # pygame.draw.line(world.interpretation, color.accent_blue, origin, end_point, 1)

        # we get a list of coordinate points from the player's position
        # we are operating in world coordinates
        ray_points = get_line_pixels(origin, end_point)

        for point in ray_points:
            pixel_color = world.surface.get_at(point)
            if is_ground_color(pixel_color):
                pygame.draw.circle(world.interpretation, color.lidar, point, 1)  # Clear circle with full transparency
                if lidar_shows_lines:
                    pygame.draw.line(world.interpretation, color.lidar + (30,), origin, point, 1)
                break

    return


def fog_of_war(world, screen, player):

    reveal_radius = 100  # Radius of the revealed area around the player
    # world.interpretation.fill((0, 0, 0, 250))  # Refill fog (reset)
    pygame.draw.circle(world.interpretation, (0, 0, 0, 0), (player.x, player.y), reveal_radius)  # Clear circle with full transparency
    return

from roller import color
import pygame
import numpy as np
import math
from roller.calculations import get_line_pixels, get_line_endpoint, screen2world
from roller.datatypes import Point

class Sensor:
    def __init__(self, power_draw):
        self.power_draw = power_draw        # Power usage of the sensor
        self.is_enabled = True             # Whether the sensor is active
        self.temperature = 20               # Current temperature of the sensor

    def enable(self):
        """Enable the sensor."""
        self.is_enabled = True
        print(f"{self.__class__.__name__} enabled.")

    def toggle(self):
        self.is_enabled = not self.is_enabled
        print(f"{self.__class__.__name__} toggled.")
        
    def disable(self):
        """Disable the sensor."""
        self.is_enabled = False
        print(f"{self.__class__.__name__} disabled.")

    def get_status(self):
        """Return sensor's status."""
        return {
            "power_draw": self.power_draw,
            "is_enabled": self.is_enabled,
            "temperature": self.temperature
        }

    def run(self):
        """This method will be implemented in specific sensor subclasses."""
        raise NotImplementedError("run must be implemented in subclasses.")



# Specific sensor classes inheriting from the base Sensor class
class SingleLaser(Sensor):
    def __init__(self, power_draw=1, range = 1000, color = color.cyan, mount_angle = 0):
            # Call the base class constructor
            super().__init__(power_draw)
            # LIDAR-specific attribute
            self.range = range
            self.color = color
            self.shows_ray = True
            self.mount_angle = mount_angle

    def run(self, player, world):
        if self.is_enabled:

            origin = screen2world(player, world)
            end_point = get_line_endpoint(origin, self.range, self.mount_angle + player.phi)
            ray_points = get_line_pixels(origin, end_point)

            for point in ray_points:
                pixel_color = world.surface.get_at(point)
                if color.is_ground_color(pixel_color):
                    pygame.draw.circle(world.interpretation, self.color, point, 1)  # Clear circle with full transparency
                    if self.shows_ray:
                        pygame.draw.line(world.interpretation, self.color + (30,), origin, point, 1)
                    break


class LIDAR(Sensor):

    def __init__(self, range = 300, laser_count = 30,color = color.green,):
        # Call the base class constructor
        super().__init__(power_draw = laser_count)
        # LIDAR-specific attribute
        self.range = range
        self.color = color
        self.shows_ray = True
        self.laser_count = laser_count

    def run(self, player, world):
        if self.is_enabled:
            origin = screen2world(player, world)
   
            for theta in np.linspace(0, 2*math.pi, num=self.laser_count):
                # We calculat the world coordinate to which the lidat ray will travel
                end_point = get_line_endpoint(origin, self.range, theta)
                # origin and endpoint are now in world coordinates
                # pygame.draw.line(world.interpretation, color.accent_blue, origin, end_point, 1)

                # we get a list of coordinate points from the player's position
                # we are operating in world coordinates
                ray_points = get_line_pixels(origin, end_point)

                for point in ray_points:
                    pixel_color = world.surface.get_at(point)
                    if color.is_ground_color(pixel_color):
                        pygame.draw.circle(world.interpretation, self.color, point, 1)  # Clear circle with full transparency
                        if self.shows_ray:
                            pygame.draw.line(world.interpretation, self.color + (30,), origin, point, 1)
                        break

class GPS_surface_mount(Sensor):
    def run(self, player, world):
        if self.is_enabled:
            origin = screen2world(player, world)
            sensor_location = get_line_endpoint(origin, player.r, player.phi)
            pygame.draw.circle(world.memory, color.cyan, sensor_location, 1) 

class GPS_stabilized(Sensor):
    def run(self, player, world):
        if self.is_enabled:
            origin = screen2world(player, world)
            pygame.draw.circle(world.memory, color.gpx, origin, 1) 

class Sonar(Sensor):
    def run(self, player, world):
        if self.is_enabled:
            print("Sonar is emitting sound waves to detect objects.")
        else:
            print("Sonar is disabled.")

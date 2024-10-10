from roller import colors
import pygame
import numpy as np
import math
from roller.calculations import get_line_pixels, get_line_endpoint, screen2world
from roller.datatypes import Point

class Sensor:
    def __init__(self, power_draw = 1, color = colors.cyan):
        self.power_draw = power_draw        # Power usage of the sensor
        self.is_enabled = True             # Whether the sensor is active
        self.temperature = 20               # Current temperature of the sensor
        self.color = color
    def enable(self):
        """Enable the sensor."""
        self.is_enabled = True
        return self
        print(f"{self.__class__.__name__} enabled.")

    def toggle(self):
        self.is_enabled = not self.is_enabled
        print(f"{self.__class__.__name__} toggled.")
        return self
        
    def disable(self):
        """Disable the sensor."""
        self.is_enabled = False
        print(f"{self.__class__.__name__} disabled.")
        return self

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
    def __init__(self, power_draw=1, range = 1000, color = colors.cyan, mount_angle = 0):
            # Call the base class constructor
            super().__init__(power_draw =power_draw, color = color)
            # LIDAR-specific attribute
            self.range = range
            self.shows_ray = True
            self.mount_angle = mount_angle

    def run(self, player, world):
        if self.is_enabled:

            origin = screen2world(player, world)
            end_point = get_line_endpoint(origin, self.range, self.mount_angle + player.phi)
            ray_points = get_line_pixels(origin, end_point)

            for point in ray_points:
                pixel_color = world.surface.get_at(point)
                if colors.is_ground_color(pixel_color):
                    pygame.draw.circle(world.interpretation, self.color, point, 1)  # Clear circle with full transparency
                    if self.shows_ray:
                        # the range on the single laser if higer than LIDAR, so the ray is more opaque
                        pygame.draw.line(world.interpretation, self.color + (60,), origin, point, 2)
                    break


class LIDAR(Sensor):

    def __init__(self, range = 300, laser_count = 30,color = colors.green,):
        # Call the base class constructor
        super().__init__(power_draw = laser_count, color = color)
        # LIDAR-specific attribute
        self.range = range
        self.shows_ray = True
        self.laser_count = laser_count

    def run(self, player, world):
        if self.is_enabled:
            origin = screen2world(player, world)
   
            for theta in np.linspace(0, 2*math.pi, num=self.laser_count):
                # We calculat the world coordinate to which the lidat ray will travel
                end_point = get_line_endpoint(origin, self.range, theta)
                # origin and endpoint are now in world coordinates
                # pygame.draw.line(world.interpretation, colors.blue, origin, end_point, 1)

                # we get a list of coordinate points from the player's position
                # we are operating in world coordinates
                ray_points = get_line_pixels(origin, end_point)

                for point in ray_points:
                    pixel_color = world.surface.get_at(point)
                    if colors.is_ground_color(pixel_color):
                        pygame.draw.circle(world.interpretation, self.color, point, 1)  # Clear circle with full transparency
                        if self.shows_ray:
                            pygame.draw.line(world.interpretation, self.color + (30,), origin, point, 1)
                        break

class GPS_surface_mount(Sensor):
    def run(self, player, world):
        if self.is_enabled:
            origin = screen2world(player, world)
            sensor_location = get_line_endpoint(origin, player.radius, player.phi)
            pygame.draw.circle(world.memory, self.color, sensor_location, 1) 

class GPS_stabilized(Sensor):
    def run(self, player, world):
        if self.is_enabled:
            origin = screen2world(player, world)
            pygame.draw.circle(world.memory, self.color, origin, 1) 

class Sonar(Sensor):
    def run(self, player, world):
        if self.is_enabled:
            print("Sonar is emitting sound waves to detect objects.")
        else:
            print("Sonar is disabled.")

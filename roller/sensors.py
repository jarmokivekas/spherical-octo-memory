from roller import colors
import pygame
import numpy as np
import math
from roller.calculations import get_line_pixels, get_line_endpoint, screen2world
from roller.datatypes import Point

import random


def get_first_solid_pixel(origin, max_range, theta, world):
    # the pixel coordinates at max_range from origin in direction theta
    end_point = get_line_endpoint(origin, max_range, theta)
    # coordinates for all pixels along the ray
    ray_points = get_line_pixels(origin, end_point)
    for point in ray_points:
        pixel_color = world.surface.get_at(point)
        if colors.is_ground_color(pixel_color):
            return point
    return None


class Sensor:

    # Power and temperature attributes
    temperature = 20     # Current temperature of the sensor
    power_draw = 1       # Watts
    mass = 0.2           # m, Assumed mass in kg
    heat_capacity = 900  # Assumed specific heat capacity in J/(kg*K)
    heat_dissipation_rate = 0.1  # Example dissipation rate

    def __init__(self, color = colors.cyan):
        self.is_enabled = True             # Whether the sensor is active
        self.color = color
        self.model = self.__class__.__name__

    def get_housekeeping(self):
        return dict(
            model = self.model,
            is_enabled = self.is_enabled,
            temperature = round(self.temperature, 1),
        )

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

    def update_temperature(self, ambient_temperature, dt):
        # Calculate heat generated
        
        heat_generated = self.power_draw * dt if self.is_enabled else 0
        
        # Calculate heat loss
        heat_loss = self.heat_dissipation_rate * (self.temperature - ambient_temperature) * dt
        
        # Calculate net heat change
        net_heat_change = heat_generated - heat_loss
        
        # Update sensor temperature
        self.temperature += net_heat_change / (self.mass * self.heat_capacity)


# Specific sensor classes inheriting from the base Sensor class
class SpectraScan_LX1(Sensor):
    
    marketing_copy = """Meet the SpectraScan-LX1, the ultimate single-ray laser range finder, born from a sphere-whacking club-wielding human sport eqpuipment that’s been reverse-engineered, reimagined, and perfected for your everyday robotics sensing needs. 
    """
    power_draw = 2
    def __init__(self, range = 1000, color = colors.cyan, mount_angle = 0):
            # Call the base class constructor
            super().__init__(color = color)
            # SpectraScan_SX30-specific attribute
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
                        # the range on the single laser if higer than SpectraScan_SX30, so the ray is more opaque
                        pygame.draw.line(world.interpretation, self.color + (60,), origin, point, 2)
                    break


class SpectraScan_SX30(Sensor):

    marketing_copy = """Meet the SpectraScan-SX30 - your answer to getting lost and running into things! We took thirty of our trusty LX1 rangefinders, packed them into one powerful sensor array, and called it a day. Well... almost. Turns out, cramming that much tech makes it run a little toasty, we had to dial back the range a bit. But hey, it’s still a game-changer for up-close precision."""

    def __init__(self, range = 300, laser_count = 30,color = colors.green,):
        # Call the base class constructor
        super().__init__(color = color)
        # SpectraScan_SX30-specific attribute
        self.power_draw = laser_count
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



class FOTIRS(Sensor):
    """Introducing the Forward-Emitting Optical Terrain Illumination and Reflectivity Sensor (FOTIRS)—a precision-engineered light-based sensor designed to project a controlled beam forward and downward, scanning the terrain ahead for optimal navigation and environmental awareness."""
    def __init__(self):
        super().__init__()
        self.color = colors.Cyberpunk.white

    def run(self, bot, world):
        if self.is_enabled == False:
            return;

        origin = screen2world(bot, world)

        for theta in np.linspace(0, math.pi, num=100):
            point = get_first_solid_pixel(origin, 200, theta, world)
            if point != None:
                pygame.draw.circle(world.interpretation, self.color, point, 1)



class NAV1_InertiaCore(Sensor):
    def run(self, player, world):
        if self.is_enabled:
            origin = screen2world(player, world)
            sensor_location = get_line_endpoint(origin, player.radius, player.phi)
            pygame.draw.circle(world.memory, self.color, sensor_location, 1) 

class NAV1_GyroSphere(Sensor):
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

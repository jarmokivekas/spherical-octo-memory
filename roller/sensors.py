import numpy as np
import random
import pygame
import math
from dataclasses import dataclass
from roller.datatypes import Point
from roller import colors
from roller.calculations import (
    get_line_pixels, 
    get_first_solid_pixel,
    get_line_endpoint,
    screen2world,
    world2screen
)



@dataclass
class Sensor:

    # Power and temperature attributes
    temperature: float   = 20     # Current temperature of the sensor
    power_draw: float    = 1       # Watts
    mass: float          = 0.2           # m, Assumed mass in kg
    heat_capacity: float = 500  # Assumed specific heat capacity in J/(kg*K)
    heat_dissipation_rate:float = 0.1  # Example dissipation rate
    color: tuple = colors.cyan
    is_enabled:bool = True             # Whether the sensor is active
    mount_angle: float = 0
    #####################################
    ## Methods childred should implement
    #####################################3
    def run(self):
        """This method will be implemented in specific sensor subclasses."""
        raise NotImplementedError("run must be implemented in subclasses.")

    def render(self, bot, world, screen):
        pass

    ######################
    # Common methods for all sensors
    #######################

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
        """Return sensor's status. This is intended for
        user interface programming. """
        return {
            "power_draw": self.power_draw,
            "is_enabled": self.is_enabled,
            "temperature": self.temperature
        }


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
    """Meet the SpectraScan-LX1, the ultimate single-ray laser range finder, born from a sphere-whacking club-wielding human sport eqpuipment that’s been reverse-engineered, reimagined, and perfected for your everyday robotics sensing needs. 
    """
    power_draw = 2
    shows_ray = True

    def __init__(self, range = 1000, *args, **kwargs):
            # Call the base class constructor
            super().__init__(*args, **kwargs)
            # SpectraScan_SX30-specific attribute
            self.range = range
            self.model: str = self.__class__.__name__



    def run(self, bot, world):
            
            end_point = get_line_endpoint(bot, self.range, self.mount_angle + bot.phi)
            ray_points = get_line_pixels(bot, end_point)

            for point in ray_points:
                pixel_color = world.surface.get_at(point)
                if colors.is_ground_color(pixel_color):
                    pygame.draw.circle(world.interpretation, self.color, point, 1)  # Clear circle with full transparency
                    if self.shows_ray:
                        # the range on the single laser if higer than SpectraScan_SX30, so the ray is more opaque
                        pygame.draw.line(world.interpretation, self.color + (60,), (bot.x,bot.y), point, 2)
                    break


class SpectraScan_SX30(Sensor):
    """Meet the SpectraScan-SX30 - your answer to getting lost and running into things! We took thirty of our trusty LX1 rangefinders, packed them into one powerful sensor array, and called it a day. Well... almost. Turns out, cramming that much tech makes it run a little toasty, we had to dial back the range a bit. But hey, it’s still a game-changer for up-close precision."""

    def __init__(self, range = 300, laser_count = 30,color = colors.green,):
        # Call the base class constructor
        super().__init__(color = color)
        # SpectraScan_SX30-specific attribute
        self.power_draw = laser_count
        self.range = range
        self.shows_ray = True
        self.laser_count = laser_count
        self.model: str = self.__class__.__name__

    def run(self, bot, world):

        for theta in np.linspace(0, 2*math.pi, num=self.laser_count):

            point = get_first_solid_pixel(bot, self.range, theta, world)
            if point != None:
                pygame.draw.circle(world.interpretation, self.color, point, 1) 
                if self.shows_ray:
                    pygame.draw.line(world.interpretation, self.color + (30,), bot.xy, point, 1)



class FOTIRS(Sensor):
    """Introducing the Forward-Emitting Optical Terrain Illumination and Reflectivity Sensor (FOTIRS)—a precision-engineered light-based sensor designed to project a controlled beam forward and downward, scanning the terrain ahead for optimal navigation and environmental awareness."""




    def __init__(self, laser_count=100, **kwargs):
        super().__init__(**kwargs)
        self.color = colors.Cyberpunk.white
        self.laser_count = laser_count
        self.power_draw = laser_count
        self.model = self.__class__.__name__


    def render(self, bot, world, screen):
        if is_enabled:
            pygame.draw.circle(world.interpretation, self.color, point, 3)
        

    def run(self, bot, world):

        for theta in np.linspace(0, math.pi, num=self.laser_count):
            point = get_first_solid_pixel(bot, 200, theta, world)
            if point != None:
                pygame.draw.circle(world.interpretation, self.color, point, 1)



class NAV1_InertiaCore(Sensor):
    """ NAV1_InertiaCore – Your Essential Navigation Companion. Need reliable motion tracking without the frills? The NAV1_InertiaCore is built for the everyday robotic explorer. Affordable, simple, and easy to integrate, this unit gives you what you need to get rolling."""

    power_draw = 1
    def __init__(self, laser_count=100, **kwargs):
        super().__init__(**kwargs)
        self.model = self.__class__.__name__

    def run(self, bot, world):

        sensor_location = get_line_endpoint(bot, bot.radius, bot.phi)
        pygame.draw.circle(world.memory, self.color, sensor_location, 1) 

    def render(self, bot, world, screen):
        if not self.is_enabled:
            return
        
        x = bot.x + math.cos(bot.phi)*bot.radius*0.7
        y = bot.y + math.sin(bot.phi)*bot.radius*0.7

        sensor_xy = world2screen(Point(x,y), world)
        pygame.draw.circle(screen, self.color, sensor_xy, bot.radius/5)

        

class NAV1_GyroSphere(Sensor):
    """NAV1_GyroCore – Precision, Perfected. For those who demand pinpoint accuracy, the NAV1_GyroCore is the flagship of the NAV1 line. Designed with advanced calibration to track your robot's center of mass with unmatched precision, this high-end unit ensures smooth, stable motion data for even the most demanding applications. Whether you're navigating complex terrains or fine-tuning every movement. """

    power_draw = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = self.__class__.__name__

    def run(self, bot, world):
            pygame.draw.circle(world.memory, self.color, bot.xy, 1) 

    def render(self, bot, world, screen):
        if not self.is_enabled:
            return
        
        sensor_xy = world2screen(bot, world)
        pygame.draw.circle(screen, self.color, sensor_xy, bot.radius/5)

        

class Sonar(Sensor):
    def run(self, bot, world):
        if self.is_enabled:
            print("Sonar is emitting sound waves to detect objects.")
        else:
            print("Sonar is disabled.")

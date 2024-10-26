import numpy as np
import random
import pygame
import math
from dataclasses import dataclass, field
from roller.datatypes import Point, Line
from roller.places import places
from roller.config import g_config
from roller import colors
from roller.calculations import (
    get_line_pixels, 
    get_lidar_return,
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

    # Other attributes
    color: tuple = colors.cyan
    is_enabled:bool = True             # Whether the sensor is active
    mount_angle: float = 0

    data: list = field(default_factory=list)
    """Each sensor subclass can determine themselves how to interact with the
    data buffer that has been provided for them. It may store Point's, """
    dataindex:int = 0


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

    def toggle(self):
        self.is_enabled = not self.is_enabled
        return self
        
    def disable(self):
        """Disable the sensor."""
        self.is_enabled = False
        return self

    def get_status(self):
        """Return sensor's status. This is intended for
        user interface programming. """
        return {
            "power_draw": self.power_draw,
            "is_enabled": self.is_enabled,
            "temperature": self.temperature
        }


    def update_temperature(self, ambient_temperature:float, dt:float):
        # Calculate heat generated
        
        heat_generated = self.power_draw * dt if self.is_enabled else 0
        
        # Calculate heat loss
        heat_loss = self.heat_dissipation_rate * (self.temperature - ambient_temperature) * dt
        
        # Calculate net heat change
        net_heat_change = heat_generated - heat_loss
        
        # Update sensor temperature
        self.temperature += net_heat_change / (self.mass * self.heat_capacity)

    def draw_data(self, world):
        raise NotImplementedError

    def delete_data(self, index:int, world):
        raise NotImplementedError

    def random_dataindex(self):
        """choose the next index where lidar data will be written. How this is chosen
        as a effect on how old data gets overwritten, which has aestethic importance"""
        return random.randint(0, len(self.data)-1)

    def next_dataindex(self):
        """returns the incremented data index, and ensures that it wraps correctly when reaching maximum.
        This indexing strategy always overwrites the oldest data entry, which can make the bot appear
        "snake like", as the data is deleted at the same pace that the bot is moving."""
        return (self.dataindex + 1) % len(self.data)




class Lidar(Sensor):
    """(at risk of too much abstraction)
    This is a Sensor class that implements methods common to all Lidar style laser sensors. 
    """

    shows_rays: bool = True
    """Whether to draw a line from the bot's location to the sensed point, or just the point sensed by the laser.
    This is mostly a aesthetic choice. Having the lines visible makes the world seem more illuminated/bighter"""
    data: list[Line] = field(default_factory=list)
    """The sensor's data buffer. Sensor reading are stored in this fixed-size buffer that
    represents the sensor's built-in memory. For Lidars each data entry is a tuple of two points that represent a line: (ray_start, ray_end)"""

    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def draw_data(self, world):
        """Draw the visual prepresentation of the data in the sensor's data buffer
        onto the world interpretation surface"""
        for line in self.data:
            if not line:
                continue
            pygame.draw.circle(world.interpretation, self.color, line.end, 1)
            if self.shows_rays:
                pygame.draw.line(world.interpretation, self.color + (30,), line.start, line.end, 1)

    
# Specific sensor classes inheriting from the base Sensor class
class SpectraScan_LX1(Lidar):
    """Meet the SpectraScan-LX1, the ultimate single-ray laser range finder, born from a sphere-whacking club-wielding human sport eqpuipment that’s been reverse-engineered, reimagined, and perfected for your everyday robotics sensing needs. 
    """
    power_draw = 2

    def __init__(self, range = 1000, **kwargs):
        # Call the base class constructor
        super().__init__(**kwargs)
        # SpectraScan_SX30-specific attribute
        self.range = range
        self.model: str = self.__class__.__name__
        self.data = [None] * g_config.fps * 10

    def run(self, bot, world):
        point = get_lidar_return(bot, self.range, self.mount_angle+bot.phi, world)
        if point:
            self.data[self.dataindex] = Line(Point(bot.x,bot.y), point)
            self.dataindex = self.next_dataindex()

class SpectraScan_SX30(Lidar):
    """Meet the SpectraScan-SX30 - your answer to getting lost and running into things! We took thirty of our trusty LX1 rangefinders, packed them into one powerful sensor array, and called it a day. Well... almost. Turns out, cramming that much tech makes it run a little toasty, we had to dial back the range a bit. But hey, it’s still a game-changer for up-close precision."""


    def __init__(self, range = 300, is_stabilized=True,laser_count = 17, **kwargs):
        # Call the base class constructor
        super().__init__(**kwargs)
        # SpectraScan_SX30-specific attribute
        self.power_draw = laser_count
        self.range = range
        self.laser_count = laser_count
        self.model: str = self.__class__.__name__
        self.is_stabilized = is_stabilized
        self.data = [None] * g_config.fps* 2 * self.laser_count
        #move to base class

    def run(self, bot, world):
        for theta in np.linspace(0, 2*math.pi, num=self.laser_count):
            # is the sensor does not have a stabilizer, it will
            # be co-rotating with with the body of the bot
            if not self.is_stabilized:
                theta += bot.phi          
            point = get_lidar_return(bot, self.range, theta, world)
            if point:
                self.data[self.dataindex] = Line(Point(bot.x,bot.y),point)
                self.dataindex = self.random_dataindex()

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
            point = get_lidar_return(bot, 200, theta, world)
            if point != None:
                pygame.draw.circle(world.interpretation, self.color, point, 1)

class NAV1_InertiaCore(Sensor):
    """ NAV1_InertiaCore – Your Essential Navigation Companion. Need reliable motion tracking without the frills? The NAV1_InertiaCore is built for the everyday robotic explorer. Affordable, simple, and easy to integrate, this unit gives you what you need to get rolling."""

    power_draw = 1

    data: list[Point] 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = self.__class__.__name__
        self.data = [None]*g_config.fps *20

    def run(self, bot, world):
        """The Inertia Core measures the location it is mounted it, which co-rotates with the bot"""
        self.dataindex = self.next_dataindex()
        self.delete_data(self.dataindex, world)
        sensor_location = get_line_endpoint(bot, bot.radius*4/5, bot.phi + self.mount_angle)
        self.data[self.dataindex] = Point(int(sensor_location.x), int(sensor_location.y))

    def delete_data(self, index, world):
        if self.data[index] is None:
            return
        world.interpretation.set_at(self.data[index], colors.black) 
        self.data[index] = None

    def draw_data(self, world):
        world.interpretation.set_at(self.data[self.dataindex], self.color) 


    def render(self, bot, world, screen):
        if not self.is_enabled:
            return
        
        # the sensor size is radium/5 so scale appropriatly to the size of the bot
        # we add the mount angle to bot.phi so the sensor spins with the spherebot
        sensor_xy = get_line_endpoint(bot, bot.radius*4/5, bot.phi + self.mount_angle)
        sensor_xy = world2screen(sensor_xy, world)
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

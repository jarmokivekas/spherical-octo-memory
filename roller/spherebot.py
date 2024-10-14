import math

from typing import List, Dict
from dataclasses import dataclass, field

from roller.datatypes import Point
from roller import colors
from roller.calculations import vectorProjection, screen2world, clip
from roller.sensors import SpectraScan_SX30, Sensor
from roller.conditions import g_player_conditions
from roller.config import g_config
from roller.behaviours import Behaviour
import pygame

@dataclass
class Bot():
    x: float
    y: float
    has_camera: bool = False
    color: tuple = (60,60,60)
    vy: float = 0
    vx: float = 0
    omega: float = 0 # speed of rotation (radian/time (frame or second?))
    phi: float = 0   # the angle of rotation
    sensors: List[Sensor] = field(default_factory=list)
    keybinds: Dict[str,int] = field(default_factory=dict)
    joystick: pygame.joystick.Joystick = None
    behaviours: List[Behaviour] = field(default_factory=list)

    def get_xy(self):
        return (self.x, self.y)

    def add_behaviour(self, behaviour):
        self.behaviours.append(behaviour)

    def add_sensor(self, sensor: Sensor):
        # TODO: add logic to set the mount_angle for sensors so that they
        # are placed in a satisfying way. Maybe implemented in the subclasses
        self.sensors.append(sensor)

    def run_physics(self, world):
        raise NotImplementedError()

    def run_behaviours(self):
        for behaviour in self.behaviours:
            behaviour.run()

    def run_sensors(self, world, screen):
        raise NotImplementedError()



class Spherebot(Bot):
    """Introducing the SphereBot-1000 - Your go-to spherical robotics platform that gets the job done, no frills attached. Whether you're mapping caves, patrolling perimeters, or just rolling around, the SphereBot-1000 delivers reliable performance for all your basic robotics needs. Built to last, easy to maintain, and ready to tackle whatever task you throw at it (within reason, of course)."""
    
    radius: float = 20
    collisionDirectionX: float = 1  # collision direction provides direction of the collision force vector
    collisionDirectionY: float = 0
    closest_pixel_distance: float = 20
    accent_color: tuple = colors.blue
    friction: float = 1
    accelerating:bool  = False    # wether the bot is currently accelerating or coasting

    def __init__(self, radius=20, *args, **kwargs):
        # this passess all other arguments given to this initializer to the 
        # parent calss to take care of
        super().__init__(*args, **kwargs)
        self.radius = radius

    def get_housekeeping(self):
        housekeeping = dict(
            x = round(self.x, 1),
            y = round(self.y, 1),
            vy = round(self.vy, 1),
            vx = round(self.vx, 1),
            omega = round(self.omega, 1),
            phi = round(self.phi, 1),
            # input = {
            #     "joystick0": self.joystick.get_axis(0),
            # },
        )
        housekeeping['sensors'] = []
        for sensor in self.sensors:
            housekeeping['sensors'].append(sensor.get_housekeeping())

        return housekeeping

    @property
    def xy(self):
        """just to easily access the xy position for pygame functions"""
        return (self.x, self.y)


    def accelerate_left(self, gain):
        self.accelerating = True
        self.omega += gain * (-1 - self.omega) * 0.1
        return
    def accelerate_right(self, gain):
        self.accelerating = True
        self.omega += gain * ( 1 - self.omega) * 0.1
        return


    def move(self):
        """Move the bot in the world according to it current velocities
        Also apply friction to slow down velocities, and apply
        rotational velocity if the bot has keybinds attached to it"""

        previous_omega = self.omega

        if self.joystick is not None:
            # axis_value is between 1.0...-1.0
            axis_value = self.joystick.get_axis(0)
            if axis_value < 0:  # Move left
                self.accelerate_left(gain=2.0*abs(axis_value))
            elif axis_value > 0:  # Move right
                self.accelerate_right(gain=2.0*abs(axis_value))
    
        # Keyboard input for movement
        keys = pygame.key.get_pressed()
        if self.keybinds:
            if keys[self.keybinds['left']]:
                self.accelerate_left(gain=1.0)

            elif keys[self.keybinds['right']]:
                self.accelerate_right(gain=1.0)

 
        # friction
        self.vy *= 0.99;
        self.vx *= 0.99;
        self.omega *= 0.95;

        # Gravity
        self.vy += g_config.gravity_acceleration 

        # Rotate and move
        self.phi += self.omega;
        self.x += self.vx;
        self.y += self.vy;


    def touch(self, world):
        """Check if the sphere bot is touching ground pixels in the world
        This function makes sure the bot is not too deep inside the ground,
        and saves the information needed to determine the direction
        of any possible bounces after a collision.
        """

        # Loop through the pixels around the self

        origin = Point(self.x, self.y)
        
        radius = math.floor(self.radius)
        x = math.floor(origin.x)
        y = math.floor(origin.y)
        pixelSumX = 0
        pixelSumY =  0
        pixelsHit = 0
        self.closest_pixel_distance = self.radius
        self.collisionDirectionX = 0
        self.collisionDirectionY = 0 
        for dx in range(-radius, radius+1):
            for dy in range(-radius, radius+1):
                pixel_x = x + dx
                pixel_y = y + dy
                pixelDistance = math.sqrt(dx**2 + dy**2) # pythagoras

                # check pixel values from the world surface itself
                color = world.surface.get_at((pixel_x, pixel_y))
                if colors.is_ground_color(color) and pixelDistance <= self.radius:
                    pixelsHit += 1
                    pixelSumX += dx
                    pixelSumY += dy
                    # we store the closes distance to a pixel as a metric
                    # of how hard we have collided (how far into the terrain the player is)
                    if pixelDistance < self.closest_pixel_distance:
                        self.closest_pixel_distance = pixelDistance

        
        if(pixelsHit != 0):
            # this is the kind of average "center" location of all the pixels we hit. 
            weightMedX = pixelSumX / pixelsHit;
            weightMedY = pixelSumY / pixelsHit;

            # The deeper into the player hitbox the hit pixel center is, the harder the collision
            weightMedDist = math.sqrt(weightMedX*weightMedX + weightMedY*weightMedY);
            # a unit vector to define the direction of the collision
            self.collisionDirectionX = weightMedX / weightMedDist;
            self.collisionDirectionY = weightMedY / weightMedDist;
            return True;
        else:
            return False;

    
    def collide(self, world):
        """Changes the direction of the velocity vector based on 
        the collisionDirection[XY] attributes (the the bot collides with ground)"""
        #pop player onto surface
        self.x -= self.collisionDirectionX * (self.radius - self.closest_pixel_distance);
        self.y -= self.collisionDirectionY * (self.radius - self.closest_pixel_distance);

        # change velocity direction
        velocity_change = vectorProjection(self.vx, self.vy, self.collisionDirectionX, self.collisionDirectionY);
        # for a fully elastic bounce, use the multiplication factor 2
        # values over 2: increases velocity on bounce
        # values near 1: fully dampened collision
        self.vx -= (1.5 * velocity_change[0]);
        self.vy -= (1.5 * velocity_change[1]);



    def rotate(self):
        

        # Get the state of all keys
        keys = pygame.key.get_pressed()

        friction = self.friction;

        # this needs to be complicated like this, so it doesn't brake for 
        # entities that don't have keybinds
        if self.accelerating == True:
            # this is the rotation physics for when the bot is "in gear"
            # and driving more momentum into the rotation
            speedMean = 0;
            scalar = self.vx*self.collisionDirectionY - self.vy*self.collisionDirectionX;
            scalar2 = self.vx*self.collisionDirectionX + self.vy*self.collisionDirectionY;

            # if the contact to round is along the x-axis
            self.vx = scalar2 * self.collisionDirectionX;
            self.vy = scalar2 * self.collisionDirectionY;

            speedMean = (scalar + self.radius*self.omega)/2;
            self.vy += friction*speedMean * (-self.collisionDirectionX);
            self.vx += friction*speedMean * (self.collisionDirectionY);
            self.omega = friction*speedMean/self.radius;
        
        else: # The bot is coasting
            # This is a cross product. It is used to measure how much of the bot's linear
            # velocity is contributing to rotation (tangential velocity) around the contact point.
            scalar = self.vx*self.collisionDirectionY - self.vy*self.collisionDirectionX;
            # Higher friction means more rotational velocity is generated from the same linear velocity (rolling vs. skidding)
            # Larger spheres will rotate more slowly for the same amount of linear velocity.
            self.omega = friction*scalar/self.radius;
        pass


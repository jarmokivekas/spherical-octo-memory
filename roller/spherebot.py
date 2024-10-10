import math

from typing import List, Dict
from dataclasses import dataclass, field

from roller.datatypes import Point
from roller.colors import is_ground_color
from roller import colors
from roller.calculations import vectorProjection, screen2world
from roller.sensors import LIDAR, Sensor
import pygame

@dataclass
class Spherebot:
    x: float # world coordinates
    y: float # world coordinates
    vy: float = 0
    vx: float = 0
    radius: float = 20
    omega: float = 0
    phi: float = 0   # the angle of rotation in radians
    collisionDirectionX: float = 1  # collision direction provides direction of the collision force vector
    collisionDirectionY: float = 0
    closest_pixel_distance: float = 20
    color: tuple = (60,60,60)
    accent_color: tuple = colors.blue
    friction: float = 1
    sensors: List[Sensor] = field(default_factory=list)
    keybinds: Dict[str,int] = field(default_factory=dict)
    has_camera: bool = False


    def move(self):
        """Move the bot in the world according to it current velocities
        Also apply friction to slow down velocities, and apply
        rotational velocity if the bot has keybinds attached to it"""

        if len(self.keybinds) == 2:
            # Get the state of all keys
            keys = pygame.key.get_pressed()

            if keys[self.keybinds['left']]:
                self.omega += (-1 - self.omega) * 0.1
            if keys[self.keybinds['right']]:
                self.omega += (1-self.omega) * 0.1

        # friction
        self.vy *= 0.99;
        self.vx *= 0.99;
        self.omega *= 0.95;

        # Gravity
        self.vy += 0.2 # TODO read this from config

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
        origin = Point(0,0)
        if self.has_camera: 
            origin = screen2world(self, world)
        else:
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
                if is_ground_color(color) and pixelDistance <= self.radius:
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
        if(keys[self.keybinds['left']] or keys[self.keybinds['right']]):
            speedMean = 0;
            scalar = self.vx*self.collisionDirectionY - self.vy*self.collisionDirectionX;
            scalar2 = self.vx*self.collisionDirectionX + self.vy*self.collisionDirectionY;

            self.vx = scalar2 * self.collisionDirectionX;
            self.vy = scalar2 * self.collisionDirectionY;

            speedMean = (scalar + self.radius*self.omega)/2;
            self.vy += friction*speedMean * (-self.collisionDirectionX);
            self.vx += friction*speedMean * (self.collisionDirectionY);
            self.omega = friction*speedMean/self.radius;
        
        else:
            scalar = self.vx*self.collisionDirectionY - self.vy*self.collisionDirectionX;
            self.omega = friction*scalar/self.radius;
        pass


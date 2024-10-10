import pygame
from pygame.locals import *
from dataclasses import dataclass
import math
import numpy as np
from roller import sensors
from roller.sensors import Point
from roller.calculations import vectorProjection, scalarProduct, world2screen
from roller.spherebot import Spherebot
from roller.overlay import Overlay
from roller import colors
from typing import List
from roller.conditions import g_player_conditions


config = {
    "fps": 60,
    "gravity_acceleration": 0.2, # acceleration in pixels / second^2
    "height": 0,
    "width": 0,
    "debug": False,
}



@dataclass
class World:
    surface: pygame.surface.Surface
    interpretation: pygame.surface.Surface
    memory: pygame.surface.Surface
    x: float = 0  # screen coordinates of the top-right corner
    y: float = 0



"""checks the location of the player and moves the view
of the wold accordingly"""
def worldEdgeCheck(player):
    x_pad = 20
    y_pad = 100
    center_x = config['width']/2
    center_y = config['height']/2
    ##x-axis - follows constantly
    if(player.x > (center_x + x_pad)):
        world.x -= player.x - (center_x + x_pad);
        player.x = (center_x + x_pad);
    
    elif(player.x < (center_x - x_pad)):
        world.x -= player.x - (center_x - x_pad);
        player.x = (center_x - x_pad);
    
    ##--y-axis - moves at treshhold
    if(player.y > (center_y + y_pad)):
        world.y -= player.y - (center_y + y_pad);
        player.y = (center_y + y_pad);
    
    elif(player.y < (center_y-y_pad)):
        world.y -= player.y - (center_y-y_pad);
        player.y = (center_y-y_pad);
    

LAST_MEMORY_UPDATE_TIME = 0
LAST_INTERPRETATION_UPDATE_TIME = 0

def drawWorld():
    # Drawing
    global LAST_MEMORY_UPDATE_TIME
    global LAST_INTERPRETATION_UPDATE_TIME

    screen.fill(colors.black)

    if config['debug']:
        screen.blit(world.surface, (world.x, world.y))

    if g_player_conditions["you have a memory bank for sensor data"]:
            
        if g_current_tick_ms - LAST_INTERPRETATION_UPDATE_TIME > 1000:
            LAST_INTERPRETATION_UPDATE_TIME = g_current_tick_ms
            # Get the pixel array from the surface
            # and apply brightness reduction to "forget" past sensor data
            pixels = pygame.surfarray.pixels3d(world.interpretation)  # For RGB surfaces
            pixels >>= 1
            del pixels

        if g_current_tick_ms - LAST_MEMORY_UPDATE_TIME > 20000:
            LAST_MEMORY_UPDATE_TIME = g_current_tick_ms
            # Get the pixel array from the surface
            # and apply brightness reduction to "forget" past sensor data
            pixels = pygame.surfarray.pixels3d(world.memory)  # For RGB surfaces
            pixels >>= 1
            del pixels
    else:
        world.interpretation.fill((0,0,0,0))

    for sensor in player.sensors:
        sensor.run(player, world)
    
    # for sensor in friend.sensors:
    #     sensor.run(friend, world)
    if g_player_conditions["you have a memory bank for sensor data"]:
        screen.blit(world.memory, (world.x, world.y))
    screen.blit(world.interpretation, (world.x, world.y))



def drawSpherebot(bot: Spherebot):
    # main body of the bot
    if bot.has_camera and not g_player_conditions['you are aware you are a robot']:
        # we don't render the bot until it has become aware that it is a bot
        return

    origin = Point(0,0)

    if bot.has_camera:
        origin = Point(bot.x,bot.y)
    else:
        origin = world2screen(bot, world)

    pygame.draw.circle(screen, bot.color, origin, bot.radius)

    # Accent dot to make the rotation of the bot visible
    # we divide by 4 so the dot is 
    accent_xy = (
        origin.x + math.cos(bot.phi)*bot.radius*0.7,
        origin.y + math.sin(bot.phi)*bot.radius*0.7
    )
    pygame.draw.circle(screen, bot.accent_color, accent_xy, bot.radius/5)

    if config['debug']:
        # draw the center of the bot position
        pygame.draw.circle(screen, bot.accent_color, origin, 2)

    if config['debug']:
        collsion_center_xy = (
            origin.x + bot.collisionDirectionX * bot.closest_pixel_distance,
            origin.y + bot.collisionDirectionY * bot.closest_pixel_distance
        )
        pygame.draw.circle(screen, (255,128,0), collsion_center_xy, 2)


def handle_events(player):
    global RUNNING
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            RUNNING = False

        # Check for key presses to toggle sensors

        if event.type == pygame.KEYDOWN:
        
            sensor_count = len(player.sensors)
            if event.key == pygame.K_1 and sensor_count > 0:
                player.sensors[0].toggle()
            elif event.key == pygame.K_2 and sensor_count > 1:
                player.sensors[1].toggle()
            elif event.key == pygame.K_3 and sensor_count > 2:
                player.sensors[2].toggle()
            elif event.key == pygame.K_4 and sensor_count > 3:
                player.sensors[3].toggle()
            elif event.key == pygame.K_5 and sensor_count > 4:
                player.sensors[4].toggle()
            elif event.key == pygame.K_6 and sensor_count > 5:
                player.sensors[5].toggle()
            elif event.key == pygame.K_7 and sensor_count > 6:
                player.sensors[6].toggle()
            elif event.key == pygame.K_8 and sensor_count > 7:
                player.sensors[7].toggle()
            elif event.key == pygame.K_9 and sensor_count > 8:
                player.sensors[8].toggle()
            elif event.key == pygame.K_0 and sensor_count > 9:
                player.sensors[9].toggle()
    

            elif event.key == pygame.K_ESCAPE:  # Exit fullscreen on ESC key press
                RUNNING = False


def execute_tick():
    handle_events(player)
    worldEdgeCheck(player)
    drawWorld()
    if (player.touch(world)):
        player.collide(world);
        player.rotate();

    if (friend.touch(world)):
        friend.collide(world);
        friend.rotate();
    player.move();
    friend.move()
    
    for entity in g_entities:
        for sensor in entity.sensors:
            sensor.update_temperature(
                g_ambient_temperature,
                (g_current_tick_ms - g_previous_tick_ms) / 1000
            )
    
    if ["you are aware you are a robot"] == True:
        drawSpherebot(player);
        drawSpherebot(friend);
    else:
        drawSpherebot(Spherebot(radius= 5, color= colors.Cyberpunk.white, x=player.x, y = player.y))

    for entity in g_entities:
        if entity.has_camera:
            overlay.render_housekeeping(entity.get_housekeeping())





if __name__ == "__main__":


    # Initialize Pygame
    pygame.init()

    # Set up the game window
    # screen = pygame.display.set_mode((config['width'], config['height']))
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    config['width'] = pygame.display.Info().current_w
    config['height'] = pygame.display.Info().current_h

    # Set up the game clock
    clock = pygame.time.Clock()


    world_surface = pygame.image.load('roller/assets/map4.png').convert()

    world = World(
        x=700, 
        y=400,
        surface = world_surface,
        interpretation = pygame.Surface(world_surface.get_size(), pygame.SRCALPHA),
        memory = pygame.Surface(world_surface.get_size(), pygame.SRCALPHA),
    )

    world.memory.fill((0,0,0,0))


    # Create the overlay object jor displaying robot housekeeping
    # data
    overlay = Overlay(screen)

    # Create playble characters and other entities

    palette = colors.Cyberpunk
    player = Spherebot(
        x = config['width']/2,  # screen coordinates
        y = config['height']/2, 
        radius = 20,
        friction = 1,
        color = palette.dark,
        sensors = [
            sensors.FOTIRS(),
            sensors.SpectraScan_SX30(color = palette.blue).disable() ,
            sensors.SpectraScan_LX1(color = palette.blue).disable() ,
            sensors.NAV1_InertiaCore(color = palette.pink).disable() ,
            sensors.NAV1_GyroSphere(color = palette.yellow).disable(),

        ],
        keybinds = {
            'left': pygame.K_LEFT, 
            'right': pygame.K_RIGHT
        },
        has_camera = True
    );

    friend = Spherebot(
        x = 800,
        y = 1000,
        keybinds = {
            'left': pygame.K_a, 
            'right': pygame.K_d
        },
        sensors = [sensors.SpectraScan_SX30(color=colors.orange)]
    )

    g_entities = [player, friend]
    g_ambient_temperature = 25

    g_current_tick_ms = 0
    g_previous_tick_ms = 0
    # Game loop
    RUNNING = True
    while RUNNING:
        # Event handling

        g_previous_tick_ms = g_current_tick_ms
        g_current_tick_ms = pygame.time.get_ticks()

        # (draw your game objects here)
        execute_tick()

        pygame.display.flip()  # Update the display

        # Cap the frame rate
        clock.tick(config['fps'])

    # Clean up
    pygame.quit()
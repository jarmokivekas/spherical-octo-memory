import pygame
import math
import numpy as np
import json

from pygame.locals import *
from dataclasses import dataclass
from typing import List

from roller.calculations import vectorProjection, scalarProduct, world2screen
from roller.spherebot import Spherebot, Bot
from roller.overlay import Overlay
from roller.conditions import g_player_conditions
from roller.datatypes import Point
from roller.config import g_config
from roller import colors
from roller import sensors
from roller import characters
from roller import camera
from roller import material




@dataclass
class World:
    surface: pygame.surface.Surface
    interpretation: pygame.surface.Surface
    memory: pygame.surface.Surface
    x: float = 0  # screen coordinates of the top-right corner
    y: float = 0



LAST_MEMORY_UPDATE_TIME = 0
LAST_INTERPRETATION_UPDATE_TIME = 0

def drawWorld(world):
    # Drawing
    global LAST_MEMORY_UPDATE_TIME
    global LAST_INTERPRETATION_UPDATE_TIME

    screen.fill(colors.black)

    if g_config.debug:
        screen.blit(world.surface, (world.x, world.y))

    if g_player_conditions["you have a memory bank for sensor data"]:
            
        # if g_current_tick_ms - LAST_INTERPRETATION_UPDATE_TIME > 1000:
        #     LAST_INTERPRETATION_UPDATE_TIME = g_current_tick_ms
        #     # Get the pixel array from the surface
        #     # and apply brightness reduction to "forget" past sensor data
        #     pixels = pygame.surfarray.pixels3d(world.interpretation)  # For RGB surfaces
        #     pixels >>= 1
        #     del pixels

        if g_current_tick_ms - LAST_MEMORY_UPDATE_TIME > 20000:
            LAST_MEMORY_UPDATE_TIME = g_current_tick_ms
            # Get the pixel array from the surface
            # and apply brightness reduction to "forget" past sensor data
            pixels = pygame.surfarray.pixels3d(world.memory)  # For RGB surfaces
            pixels >>= 1
            del pixels
    else:
        world.interpretation.fill((0,0,0,0))

    for entity in g_entities:
        for sensor in entity.sensors:
            if sensor.is_enabled == False:
                continue
            sensor.run(entity, world)
    
    # for sensor in friend.sensors:
    #     sensor.run(friend, world)
    if g_player_conditions["you have a memory bank for sensor data"]:
        screen.blit(world.memory, (world.x, world.y))
    screen.blit(world.interpretation, (world.x, world.y))



def drawSpherebot(bot: Bot):
    # main body of the bot
    if bot.has_camera and not g_player_conditions['you are aware you are a robot']:
        # we don't render the bot until it has become aware that it is a bot
        return

 
    #TODO: if this is outside the screen (by some buffer, just return and don't render)
    origin = world2screen(bot, world)
    
    pygame.draw.circle(screen, bot.color, origin, bot.radius)

    for sensor in bot.sensors:
        sensor.render(bot, world, screen)

    if g_config.debug:
        # draw the center of the bot position
        pygame.draw.circle(screen, bot.accent_color, origin, 2)

    if g_config.debug:
        collsion_center_xy = (
            origin.x + bot.collisionDirectionX * bot.closest_pixel_distance,
            origin.y + bot.collisionDirectionY * bot.closest_pixel_distance
        )
        pygame.draw.circle(screen, (255,128,0), collsion_center_xy, 2)


def handle_events(bot):
    global RUNNING
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            RUNNING = False

        # Check for key presses to toggle sensors

        elif event.type == pygame.KEYDOWN:
        
            print(event.key)

            sensor_count = len(bot.sensors)
            if event.key == pygame.K_1 and sensor_count > 0:
                bot.sensors[0].toggle()
            elif event.key == pygame.K_2 and sensor_count > 1:
                bot.sensors[1].toggle()
            elif event.key == pygame.K_3 and sensor_count > 2:
                bot.sensors[2].toggle()
            elif event.key == pygame.K_4 and sensor_count > 3:
                bot.sensors[3].toggle()
            elif event.key == pygame.K_5 and sensor_count > 4:
                bot.sensors[4].toggle()
            elif event.key == pygame.K_6 and sensor_count > 5:
                bot.sensors[5].toggle()
            elif event.key == pygame.K_7 and sensor_count > 6:
                bot.sensors[6].toggle()
            elif event.key == pygame.K_8 and sensor_count > 7:
                bot.sensors[7].toggle()
            elif event.key == pygame.K_9 and sensor_count > 8:
                bot.sensors[8].toggle()
            elif event.key == pygame.K_0 and sensor_count > 9:
                bot.sensors[9].toggle()

            elif event.key == pygame.K_ESCAPE:  # Exit fullscreen on ESC key press
                RUNNING = False

        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"Button {event.button} pressed.")
            sensor_count = len(bot.sensors)
            if event.button == 0 and sensor_count > 0:
                bot.sensors[0].toggle()
            elif event.button == 1 and sensor_count > 1:
                bot.sensors[1].toggle()
            elif event.button == 2 and sensor_count > 2:
                bot.sensors[2].toggle()
            elif event.button == 2 and sensor_count > 2:
                bot.sensors[3].toggle()

            # Note that this does not take into account
            # which controller presses the button. all palyers
            # will be able to move the camera. 
            # TODO: the current implementation will always keep the same 
            # joystick for the entiry that has camera focus.
            # TODO: bug don't overrrite the joystic attribute of an entiry that already has 
            # a joystick assigned to it.
            elif event.button == 4:
                g_camera.focus_next_target()
            elif event.button == 5:
                g_camera.focus_previous_target()



def execute_tick(world, screen):

    # We move the world on it's own, so the world is not moving between processing
    # one entity and the next
    g_camera.set_goal(g_camera.targets[g_camera.target_index])
    g_camera.update_pid((g_current_tick_ms - g_previous_tick_ms)/1000)
    g_camera.move(world, screen)

    handle_events(characters.player1)
    drawWorld(world)

    for entity in g_entities:
        # TODO: This should be a more generic "physics tick"
        # for entities. Not all of them need collide and rotate physics

        ## Run physics
        if (entity.touch(world)):
            entity.collide(world);
            entity.rotate();
        entity.move();
        
        entity.run_behaviours()
        
        ambient_temperature = material.get_temperature_at(entity, world)
        for sensor in entity.sensors:
            sensor.update_temperature(
                ambient_temperature,
                (g_current_tick_ms - g_previous_tick_ms) / 1000
            )

        drawSpherebot(entity)

    for entity in g_entities:
        if entity.has_camera:
            overlay.render_housekeeping(entity.get_housekeeping())





if __name__ == "__main__":


    # Initialize Pygame
    pygame.init()


    # Set up the game window
    if g_config.fullscreen:
        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((g_config.width, g_config.height))
    g_config.width = pygame.display.Info().current_w
    g_config.height = pygame.display.Info().current_h

    # Set up the game clock
    clock = pygame.time.Clock()

    # Create playble characters and other entities
    g_entities = [
        characters.player1,
        # characters.player2,
        characters.Aros,
        characters.Skiv,
    ]

    # Game pad/controller support
    pygame.joystick.init()

    # Check for connected joysticks/controllers
    for joystick_index in range(0, pygame.joystick.get_count()):
        # if there are 0 controllers, this loop will not be executed.
        joystick = pygame.joystick.Joystick(joystick_index)  # 0 represents the first connected joystick
        joystick.init()
        # assign the controller to one of the character entities 
        # starting in order of appearance
        g_entities[joystick_index].joystick = joystick
        print(json.dumps(dict(
            name = joystick.get_name(),
            instance_id = joystick.get_instance_id(),
        ), indent = 4))


    world_surface = pygame.image.load('roller/assets/map5.png').convert()

    world = World(
        x=0, 
        y=0,
        surface = world_surface,
        interpretation = pygame.Surface(world_surface.get_size(), pygame.SRCALPHA),
        memory = pygame.Surface(world_surface.get_size(), pygame.SRCALPHA),
    )

    world.memory.fill((0,0,0,0))

    # Create the overlay object jor displaying robot housekeeping
    overlay = Overlay(screen)

    # contols which part of the world is rendered on screen


    g_camera = camera.Camera()
    g_camera.add_target(characters.player1)
    g_camera.add_target(characters.Aros)
    g_camera.add_target(characters.Skiv)

    g_current_tick_ms = 0
    g_previous_tick_ms = 0
    # Game loop
    RUNNING = True
    while RUNNING:
        # Event handling

        g_previous_tick_ms = g_current_tick_ms
        g_current_tick_ms = pygame.time.get_ticks()
        world.y +=1
        # characters.player1.x += 1
        # (draw your game objects here)
        execute_tick(world, screen)

        pygame.display.flip()  # Update the display

        # Cap the frame rate
        clock.tick(g_config.fps)

    # Clean up
    pygame.quit()
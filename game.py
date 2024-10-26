import pygame
import math
import numpy as np
import json
import random
from pygame.locals import *
from dataclasses import dataclass
from typing import List

from roller.calculations import vectorProjection, scalarProduct, world2screen
from roller.bots import Spherebot, Bot
from roller.overlay import Overlay
from roller.conditions import g_player_conditions
from roller.datatypes import Point
from roller.config import g_config
from roller import colors
from roller import sensors
from roller import characters
from roller import camera
from roller import material
from roller import sounds



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
        if g_current_tick_ms - LAST_MEMORY_UPDATE_TIME > 20000:
            LAST_MEMORY_UPDATE_TIME = g_current_tick_ms
            # Get the pixel array from the surface
            # and apply brightness reduction to "forget" past sensor data
            pixels = pygame.surfarray.pixels3d(world.memory)  # For RGB surfaces
            pixels >>= 1
            del pixels

    world.interpretation.fill((0,0,0,0))

    for entity in g_entities:
        for sensor in entity.sensors:
            if sensor.is_enabled:
                sensor.run(entity, world)
            sensor.draw_data(world)
    
    # for sensor in friend.sensors:
    #     sensor.run(friend, world)
    if g_player_conditions["you have a memory bank for sensor data"]:
        screen.blit(world.memory, (world.x, world.y))
    screen.blit(world.interpretation, (world.x, world.y))





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
            elif event.button == 3 and sensor_count > 3:
                bot.sensors[3].toggle()

            # Note that this does not take into account
            # which controller presses the button. all palyers
            # will be able to move the camera. 
            # TODO: the current implementation will always keep the same 
            # joystick for the entity that has camera focus.
            # TODO: bug don't overrrite the joystick attribute of an entity that already has 
            # a joystick assigned to it.
            elif event.button == 5:
                g_camera.focus_next_target()
                new_target = g_camera.get_target()
                if new_target.joystick == None:
                    transfer_control(new_target, event.instance_id)

            elif event.button == 4:
                g_camera.focus_previous_target()
                new_target = g_camera.get_target()
                if new_target.joystick == None:
                    transfer_control(new_target, event.instance_id)


def transfer_control(destination: Bot, joystick_instance_id: int):
    """Sets the joystick object matching the instance id to control the given bot.
    Also ensures the joystick object is not left controlling any other bots"""

    for entity in g_entities:
        if entity.joystick == None:
            continue
        if entity.joystick.get_instance_id() == joystick_instance_id:
            destination.joystick = entity.joystick
            entity.joystick = None
            assert(entity != destination, "Trying to move joystick control from an entity to itself")
            return
    assert(False, "joystick instance id is not assocciated with any playable entity")

def trasfer_joystick(source: Bot, destination: Bot):
    """Moves joystick control from one bot to an other.
    The source bot will be left with no joystick object to control it."""

    assert(destination.joystick == None, "attempting to steal bot contol for  other player")
    destination.joystick = source.joystick
    source.joystick = None


def execute_tick(world, screen):
    """runs and controls calls to all the main submodules of the game,
    implementing the logic for each game tick. intended to be call
    once per frame to run the game."""
    # We move the world on it's own, so the world is not moving between processing
    # one entity and the next
    g_camera.set_goal(g_camera.targets[g_camera.target_index])
    g_camera.update_pid((g_current_tick_ms - g_previous_tick_ms)/1000)
    g_camera.move(world, screen)

    handle_events(g_camera.targets[g_camera.target_index])
    drawWorld(world)

    for entity in g_entities:
        # TODO: This should be a more generic "physics tick"
        # for entities. Not all of them need collide and rotate physics

        entity.run_physics(world)

        entity.run_behaviours()
        
        ambient_temperature = material.get_temperature_at(entity, world)
        for sensor in entity.sensors:
            sensor.update_temperature(
                ambient_temperature,
                (g_current_tick_ms - g_previous_tick_ms) / 1000
            )

        if entity.joystick != None:
            entity.run_player_input()


        entity.render(world,screen)

    overlay.render_housekeeping(g_camera.targets[g_camera.target_index].get_housekeeping())



SAMPLE_RATE = 44100  # Standard sample rate for audio (44.1 kHz)
DURATION = 5  # Duration of each note in seconds
VOLUME = 0.5  # Volume for output

# Generate a sine wave for a given frequency
def generate_sine_wave(freq, duration, sample_rate=SAMPLE_RATE, volume=VOLUME):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * freq * t) * volume
    return wave.astype(np.float32)



if __name__ == "__main__":


    # Initialize Pygame and the mixer for sound output
    # 44.1kHz, 16-bit signed, mono sound
    pygame.mixer.pre_init(g_config.mixer_sample_frequency, -16, 1, 1024)

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
        characters.Aros,
        characters.Skiv,
        characters.elevator1,
    ]

    g_camera = camera.Camera()
    g_camera.add_target(characters.player1)
    g_camera.add_target(characters.Aros)
    g_camera.add_target(characters.Skiv)
    g_camera.add_target(characters.elevator1)


    # Game pad/controller support
    pygame.joystick.init()

    # Check for connected joysticks/controllers
    # if there are 0 controllers, this loop will not be executed.
    for joystick_index in range(0, pygame.joystick.get_count()):
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

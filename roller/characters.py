"""The characters module initializes a number of different Bot objects with various sensors and starting locations.

Many of these Bots are mean't to be playable characters that the player can choose with the camera focus mechanic
"""

import pygame
import math
import numpy as np
from roller.bots import Spherebot, Elevator
from roller.places import places
from roller import sensors
from roller import colors
from roller import behaviours
from roller import colors
palette = colors.Cyberpunk

player1 = Spherebot(
    x = 800,  # world coordinates
    y = 200, 
    radius = 20,
    color = palette.dark,
    sensors = [
        sensors.NAV1_InertiaCore(color = palette.yellow),
        sensors.SpectraScan_LX1(color = palette.blue).disable() ,
        sensors.SpectraScan_SX30(color = palette.blue, laser_count = 16) ,
        # sensors.FOTIRS(),
        # sensors.NAV1_InertiaCore(color = palette.pink).disable() ,

    ],
    keybinds = {
        'left': pygame.K_LEFT, 
        'right': pygame.K_RIGHT
    },
    has_camera = True
);

player2 = Spherebot(
    x = 700,
    y = 700,
    keybinds = {
        'left': pygame.K_a, 
        'right': pygame.K_d
    },
    sensors = [
        # sensors.SpectraScan_SX30(color=colors.orange),
        sensors.SpectraScan_LX1(mount_angle=0),
        sensors.SpectraScan_LX1(mount_angle=math.pi * 1/3),
        sensors.SpectraScan_LX1(mount_angle=math.pi * 2/3),
    ]
)

Aros  = Spherebot(
    x = 700,
    y = 700,
    radius = 30,
    color = (10,10,10),
    sensors = [
        sensors.SpectraScan_SX30(color=colors.orange, laser_count = 16),
        sensors.NAV1_InertiaCore(color=colors.orange),
    ],
    keybinds = {
        'left': pygame.K_q, 
        'right': pygame.K_e
    },
)

Aros.add_behaviour(
    behaviours.Blinking(
        bot = Aros,               # Aros is controlling itself
        sensor_index = 0,
        duty_cycle = 0.2,
        period = 0.5,
    )
)


Skiv  = Spherebot(
    x = places['map5.png']['scrap_yard_exit'][0],
    y = places['map5.png']['scrap_yard_exit'][1],
    radius = 10,
    color = (20,20,20),
    sensors = [
        sensors.NAV1_InertiaCore(color=colors.Cyberpunk.pink),
        sensors.NAV1_InertiaCore(color=colors.Cyberpunk.pink, mount_angle=math.pi),
        sensors.SpectraScan_LX1(color=colors.Cyberpunk.pink, mount_angle=math.pi/2),
        sensors.SpectraScan_LX1(color=colors.Cyberpunk.pink, mount_angle=3*math.pi/2),
    ],

)

elevator1 = Elevator(
    x = places['map5.png']['elevator'][0],
    y = places['map5.png']['elevator'][1],
    color = (50,50,50),
    sensors = [
        sensors.SpectraScan_LX1(color=colors.Cyberpunk.yellow, retension_period = 0.5, mount_angle=math.pi/2),
        sensors.SpectraScan_LX1(color=colors.Cyberpunk.yellow, retension_period = 0.5, mount_angle=3*math.pi/2),
    ]
)
elevator1.add_behaviour(
    behaviours.OscillateSensor(
        bot = elevator1,
        sensor_index = 0,
        period = 2,
        phi_min = np.radians(90-20),
        phi_max = np.radians(90+20),
    )
)
elevator1.add_behaviour(
    behaviours.OscillateSensor(
        bot = elevator1,
        sensor_index = 1,
        period = 2,
        phi_min = np.radians(270-20),
        phi_max = np.radians(270+20),
    )
)
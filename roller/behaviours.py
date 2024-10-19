"""Behaviours are classes that implement interface of the Behaviour class. 
One or more behaviours can be associated with a bot to give it autonomous behaviour
when not controlled by a player Joystick
"""

import numpy as np
import math
import random
import pygame


class Behaviour:
    """Base class for bot behaviours. Inherit from this class when
    wirting new behaviour classes.

    :param bot: The Bot object that this behaviour will control. Note that a bot can have behaviours that don't control itself.
    """

    def __init__(self, bot):
        self.bot = bot

    def run(self):
        """Execute one game tick of the behaviour. This method is automatically called
        by the Bot object to which your behaviour object is associated with. 
        Raises NotImplementedError is not implemented by a Behaviour subclass."""
        raise NotImplementedError()

class Blinking(Behaviour):
    """:param sensor_index: index of the Bot.sensors array to blink
    :param period: The speed at which the the sensor is toggled (seconds)
    :param duty_cycle: How many percent of the time the sensor is enabled (0...1)""" 

    def __init__(self, bot, sensor_index: int, period:float, duty_cycle:float, **kwargs):
        super().__init__(bot, **kwargs)
        assert(0 <= duty_cycle <= 1)
        self.sensor_index = sensor_index
        self.period = period
        self.duty_cycle = duty_cycle

    def run(self):
        """Simulates a square wave determined by `period` and `duty_cycle`.
        The sensor is disabled when the square wave is 0, and enabled when 1"""
        is_enabled = square_wave(
            t = pygame.time.get_ticks()/1000,
            period = self.period,
            duty_cycle = self.duty_cycle
        )

        if is_enabled:
            self.bot.sensors[self.sensor_index].enable()
        else:
            self.bot.sensors[self.sensor_index].disable()


class OscillateSensor(Behaviour):
    """Oscillate the mount_angle of a sensor between the angles phi_min ... phi_max.
    
    :param sensor_index: index to the Bot.sensors array indicating which sensor to oscillate
    :param period: the time period of one oscillation in seconds
    :param phi_min: one end of the oscillation in radians
    :param phi_max: the other end of the oscillation in radians
    """ 

    def __init__(self, bot, sensor_index: int, period:float, phi_min:float, phi_max:float, **kwargs):
        super().__init__(bot, **kwargs)
        self.sensor_index = sensor_index
        assert(len(self.bot.sensors) > sensor_index)
        self.period = period
        self.phi_min = phi_min
        self.phi_max = phi_max
        self.period = period

    def run(self):
        """Updates the `mount_angle` of the specified sensor on the specified bot to execute the oscillation"""
        t = pygame.time.get_ticks()/1000
        phase = np.sin(t* 2*np.pi* (1/self.period))
        # we map the values -1.0 ... +1.0 to match phi_min ... phi_max
        phi = self.phi_min + (phase + 1) * (self.phi_max - self.phi_min) / 2
        self.bot.sensors[self.sensor_index].mount_angle = phi

def square_wave(t, period, duty_cycle, terms=8):
    """
    Approximates square wave with the given duty cycle square wave using a Fourier series.
    (yeah this might be overly complicated, but it was fun to implement)
    :param t: Time (can be an array of time values, or the current time, e.g game tick)
    
    :param terms: Number of terms in the Fourier series to sum
    :return: Approximate 75% duty cycle square wave
    """
    T = period  # Period of the square wave
    D = duty_cycle  # Duty cycle (75%)
    
    # Initial offset to approximate 75% duty cycle square wave
    f_t = D  # Starting at the average value for the duty cycle
    
    # Sum the Fourier series up to the number of specified terms
    for n in range(1, terms + 1, 2):  # Use only odd terms to approximate the wave
        f_t += (4 * np.sin(n * np.pi * D) / (n * np.pi)) * np.cos(2 * np.pi * n * t / T)
    
    
    return f_t > 1
import numpy as np
import math
import random
import pygame


class Behaviour:

    def __init__(self, bot):
        self.bot = bot

class Blinking(Behaviour):


    def __init__(self, bot, sensor_index: int, period, duty_cycle, **kwargs):
        """@param sensor_index: index of the Bot.sensors array to blink""" 
        super().__init__(bot, **kwargs)
        self.sensor_index = sensor_index
        self.period = period
        self.duty_cycle = duty_cycle

    def run(self):
        is_enabled = square_wave(
            t = pygame.time.get_ticks()/1000,
            period = self.period,
            duty_cycle = self.duty_cycle
        )

        if is_enabled:
            self.bot.sensors[self.sensor_index].enable()
        else:
            self.bot.sensors[self.sensor_index].disable()


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
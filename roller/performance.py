import pygame
import json
import psutil
from roller.config import g_config

class Perfomance():

    tick_period_s: float
    """The amount of time between the current game tick and the previous game tick"""
    fps: float = 0
    """The actual FPS the game is running at. Equal to 1/tick_period_s"""
    fps_max: float = 0
    fps_min: float = 10000
    current_tick_ms: float = 0
    previous_tick_ms: float = 0

    cpu_percent: float = psutil.cpu_percent()


    def start_tick(self):
        # Update the timestamp for the current and previous ticks
        self.previous_tick_ms = self.current_tick_ms
        self.current_tick_ms = pygame.time.get_ticks()

        # Update the measured performance of FPS
        self.tick_period_s = (self.current_tick_ms - self.previous_tick_ms) / 1000
        self.fps = 1/self.tick_period_s

        # Keep track of the minumum and maximum FPS performance
        self.fps_max = self.fps if self.fps > self.fps_max else self.fps_max
        self.fps_min = self.fps if self.fps < self.fps_min else self.fps_min

        self.cpu_percent = psutil.cpu_percent()

    def __str__(self):
        """represents the data fields in the Performance object as a json string of the self.get_housekeeping() dict"""
        return json.dumps(self.get_housekeeping(), indent=4)
    def get_housekeeping(self):

        return dict(
            fps = int(self.fps),
            fps_max = int(self.fps_max),
            fps_min = int(self.fps_min),
            cpu_percent = int(self.cpu_percent),
        )

g_performance = Perfomance()
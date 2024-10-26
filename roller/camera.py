"""The Camera class controls what part of the current game world is shown
of the screen. The class takes care of keeping track of the screen coordinates of the world surface"""

from roller.datatypes import Point
from roller.config import g_config
from roller.bots import Bot

class Camera:
    """
    :param initial_x: The x coordinate of the point in the world surface that will be rendered ay the center of the screen
    :param initial_y: The y coordinate of the point in the world surface that will be rendered at the center of the screen
    """

    targets = []
    """A list of Bot of Point objects that can be chosen by the player to be in camera focus and tracked by the camera"""
    target_index = 0
    """An index to the `self.targets` list that points to the Bot object that is currently being tracked by the camera"""

    def __init__(self, initial_x:int = 0, initial_y:int=0):
        # world coordinates of the camera position.
        self.x = initial_x
        self.y = initial_y
        # The camera will eventually move here, using the PID loop
        self.target_x = initial_x
        self.target_y = initial_y

        # PID parameters
        self.kp = g_config.camera_kp   # Proportional gain
        self.ki = g_config.camera_ki   # Integral gain
        self.kd = g_config.camera_kd   # Derivative gain

        # Error tracking
        self.previous_error_x = 0
        self.previous_error_y = 0
        self.integral_x = 0
        self.integral_y = 0

    def move(self, world, screen):
        """Updates the coordinates of the world object so that the camera's (x,y) coordiantes are int the middle of the screen
        (Since there is no such thing as moving the camera, we just move the world raster in reference to the screen)"""
        world.x = - self.x + screen.get_width()/2
        world.y = - self.y + screen.get_height()/2

    def update_pid(self, dt):
        """
        PID controlled motion to move the camera (x,y) toward (target_x, target_y) in a smooth motion.
        :param dt: Time step. This is the time since the last update in seconds (time between game ticks)
        """
        # Compute errors for both axes
        error_x = self.goal_x - self.x
        error_y = self.goal_y - self.y

        # Update integral (cumulative error)
        self.integral_x += error_x * dt
        self.integral_y += error_y * dt

        # Compute derivative (rate of change of error)
        derivative_x = (error_x - self.previous_error_x) / dt
        derivative_y = (error_y - self.previous_error_y) / dt

        # PID control for x and y axes
        control_x = (self.kp * error_x) + (self.ki * self.integral_x) + (self.kd * derivative_x)
        control_y = (self.kp * error_y) + (self.ki * self.integral_y) + (self.kd * derivative_y)

        # Update camera position
        self.x += control_x * dt
        self.y += control_y * dt

        # Store the current error for the next derivative calculation
        self.previous_error_x = error_x
        self.previous_error_y = error_y

    def set_goal(self, goal: Point|Bot):
        """
        Sets a new goal position for the camera. The PID controller will try to make the camera (x,y) coords match this goal.

        :param goal: An object with .x and .y attributes representing coordinates on the world raster.
        """
        self.goal_x = goal.x
        self.goal_y = goal.y
    
    def add_target(self, target: Point|Bot):
        """Add an Point of Bot to the list of selectable targets that the player can choose the camera to track"""
        assert(hasattr(target, "x"))
        assert(hasattr(target, "y"))
        self.targets.append(target)

    def get_target(self):
        """Returns the instance of the Point of Bot object that the camera is currently tracking"""
        return self.targets[self.target_index]

    def focus_next_target(self):
        """Select the next tracking target to focus on from the `self.targets` list"""
        # increment the target inxex, but loop back to 0 if index overdlows
        # TODO: this should later make check if the entities have a data link
        # to determine if focus can be moved due to lore reasons.
        self.target_index = (self.target_index + 1) % len(self.targets)
        self.set_goal(self.targets[self.target_index])

    def focus_previous_target(self):
        """Select the previous tracking target to focus on from the `self.targets` list"""
        # select the previous target
        self.target_index = self.target_index - 1
        # handle underflow for indexes < 0
        self.target_index = len(self.targets) - 1 if self.target_index < 0 else self.target_index 
        self.set_goal(self.targets[self.target_index])
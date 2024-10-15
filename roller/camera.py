
from roller.datatypes import Point
from roller.config import g_config
from roller.spherebot import Bot

class Camera:

    targets = []
    target_index = 0

    def __init__(self, x=0, y=0, target_x=0, target_y=0):
        # world coordinates of the camera position.
        # This point will be rendered in the middle of the screen
        self.x = x
        self.y = y
        # The camera will eventually move here, using the PID loop
        self.target_x = target_x
        self.target_y = target_y

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
        """Moves the world coordinates so that the cameras (x,y) coordiantes are int the middle of the screen"""
        world.x = - self.x + screen.get_width()/2
        world.y = - self.y + screen.get_height()/2

    def update_pid(self, dt):
        """
        PID controlled motion to move the camera toward target_x and target_y.
        :param dt: Time step (time since the last update, seconds)
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

    def set_goal(self, goal: Point):
        """
        Sets a new goal position for the camera.
        """
        self.goal_x = goal.x
        self.goal_y = goal.y
    
    def add_target(self, target: Point|Bot):
        assert(hasattr(target, "x"))
        assert(hasattr(target, "y"))
        self.targets.append(target)

    def get_target(self):
        return self.targets[self.target_index]

    def focus_next_target(self):
        # increment the target inxex, but loop back to 0 if index overdlows
        # TODO: this should later make check if the entities have a data link
        # to determine if focus can be moved due to lore reasons.
        self.target_index = (self.target_index + 1) % len(self.targets)
        self.set_goal(self.targets[self.target_index])

    def focus_previous_target(self):
        # select the previous target
        self.target_index = self.target_index - 1
        # handle underflow for indexes < 0
        self.target_index = len(self.targets) - 1 if self.target_index < 0 else self.target_index 
        self.set_goal(self.targets[self.target_index])
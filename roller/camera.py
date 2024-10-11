



    class Camera:
    def __init__(self, x=0, y=0, target_x=0, target_y=0):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y

        # PID parameters
        self.kp = 0.1  # Proportional gain
        self.ki = 0.01  # Integral gain
        self.kd = 0.05  # Derivative gain

        # Error tracking
        self.previous_error_x = 0
        self.previous_error_y = 0
        self.integral_x = 0
        self.integral_y = 0

    def update_camera(self, dt):
        """
        PID controlled motion to move the camera toward target_x and target_y.
        :param dt: Time step (time since the last update, seconds)
        """
        # Compute errors for both axes
        error_x = self.target_x - self.x
        error_y = self.target_y - self.y

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

    def set_target(self, target_x, target_y):
        """
        Sets a new target position for the camera.
        """
        self.target_x = target_x
        self.target_y = target_y
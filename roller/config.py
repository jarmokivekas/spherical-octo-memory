
class GameConfig:
    gravity_acceleration: float = 0.4
    """The acceleration for free gravity. Used in physics simulations. This should be meter/s, but is now still in pixels per frame"""

    ambient_temperature: float = 25
    fps: int = 60
    """Target frames-per-second of the game tick. This is now a little bit hard-coded, since much of the physics is done per-frame.
    That means that the in the game time appears to slow down if you lower the FPS"""

    debug: bool = False
    """When set to True, certain functions will behave differently. E.g. the world surface will be visible at all times"""

    camera_kp: float = 1.0     # Camera movement PID proportional gain
    camera_ki: float = 0.1   # Camera movement PID integral gain
    # derivative gain set to 0 to prevent "derivative kick" when the camera setpoint
    # is changed from on bot to another. If you need derivative, then temporarily
    # set the derivative gain to 0 while changing the bot in camera focus.
    camera_kd: float = 0.0   # Camera movement PID derivative gain

    fullscreen: bool = False
    """Wether the game starts in fullscreen mode or windowed mode"""
    height: int = 900
    """Window size in pixels if not in full screen mode"""
    width: int = 1600
    """Window size in pixels if not in full screen mode"""

    mixer_sample_frequency = 44100 
    """The sample frequency used by pygame.mixer audio output and other audio processing subsystems"""
    mixer_datatype = -16
    """The datatype argument for pygame.mixer. -16 means audio signals are represented by int16_t (signed 16 bit int)"""

g_config = GameConfig()

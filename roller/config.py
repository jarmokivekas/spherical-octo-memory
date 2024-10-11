
class GameConfig:
    gravity_acceleration: float = 0.4 # should be meter/s, but is now pixels per frame
    ambient_temperature: float = 25
    fps: int = 60
    debug: bool = False

    camera_kp: float = 1     # Camera movement PID proportional gain
    camera_ki: float = 0.1   # Camera movement PID integral gain
    camera_kd: float = 0.2   # Camera movement PID derivative gain


g_config = GameConfig()


class GameConfig:
    gravity_acceleration: float = 0.4 # should be meter/s, but is now pixels per frame
    ambient_temperature: float = 25
    fps: int = 60
    debug: bool = False


config = GameConfig()

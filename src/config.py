from pydantic import BaseModel

config_path: str = 'config.json'


def load_config_from_disc():
    global config

    config = Config.parse_file(config_path)
    print(config)


class MinimapConfig(BaseModel):
    bounds: tuple[int, int, int, int]
    mark_size: int


class WorldConfig(BaseModel):
    size: int
    start_wood: int
    start_money: int
    start_meat: int
    base_meat: int


class ScreenConfig(BaseModel):
    size: tuple[int, int]


class CameraConfig(BaseModel):
    min_speed: int
    max_speed: int
    step_slower: float
    step_faster: float


class ServerConfig(BaseModel):
    ip: str
    port: int


class Config(BaseModel):
    minimap: MinimapConfig
    world: WorldConfig
    screen: ScreenConfig
    camera: CameraConfig
    server: ServerConfig


config: Config

load_config_from_disc()

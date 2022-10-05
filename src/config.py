import pathlib

from pydantic import BaseModel

config_path: str = 'config.json'


def load_config_from_disc():
    global config

    if pathlib.Path(config_path).exists():
        config = Config.parse_file(config_path)
    else:
        config = Config(
            minimap=MinimapConfig(),
            world=WorldConfig(),
            screen=ScreenConfig(),
            camera=CameraConfig(),
            server=ServerConfig(),
        )
    print(config)


def upload_config_to_disc():
    with open(config_path, mode='w', encoding='UTF8') as config_file:
        config_file.write(config.json())


class MinimapConfig(BaseModel):
    bounds: tuple[int, int, int, int] = (45, 142,
                                         249, 247)
    mark_size: int = 10


class WorldConfig(BaseModel):
    size: int = 2400
    start_wood: int = 1500
    start_money: int = 2500
    start_meat: int = 0
    base_meat: int = 25


class ScreenConfig(BaseModel):
    size: tuple[int, int] = (1280, 720)
    fullscreen: bool = False

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]


class CameraConfig(BaseModel):
    min_speed: int = 1
    max_speed: int = 10
    step_slower: float = 0.05
    step_faster: float = 0.05


class ServerConfig(BaseModel):
    ip: str = ""
    port: int = 9090


class Config(BaseModel):
    minimap: MinimapConfig
    world: WorldConfig
    screen: ScreenConfig
    camera: CameraConfig
    server: ServerConfig


config: Config

load_config_from_disc()

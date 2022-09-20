from json import JSONEncoder, JSONDecoder

from pydantic import BaseModel

from src.core.types import PlayerInfo


class PydanticEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            return o.dict() | {'__model': 'PlayerInfo'}
        return o


class PydanticDecoder(JSONDecoder):
    custom_models = {
        'PlayerInfo': PlayerInfo
    }

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if '__model' in dct:
            return self.custom_models[dct['__model']](**dct)
        return dct

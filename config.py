import json

from pygame import Color


class Config:
    def __init__(self, filepath):
        self.filepath = 'config.json'
        self.json = {}
        self.reload()

    def __getitem__(self, item):
        return self.json[item]

    def reload(self):
        def decode_json(dct):
            if value := dct.get('__color__'):
                return Color(*value)
            return dct

        with open(self.filepath, mode='r', encoding='utf8') as config_file:
            self.json = json.loads(config_file.read(), object_hook=decode_json)


config = Config('config.json')

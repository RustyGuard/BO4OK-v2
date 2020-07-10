import json


class Config:
    def __init__(self, filepath):
        self.filepath = 'config.json'
        self.json = {}
        self.reload()

    def __getitem__(self, item):
        return self.json[item]

    def reload(self):
        with open(self.filepath, mode='r', encoding='utf8') as config_file:
            self.json = json.loads(config_file.read())


config = Config('config.json')

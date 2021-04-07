import yaml
import os
import json


CONFIG_DIR='/configurations/'


class Catalyst:
    def __init__(self, entries):
        self.files: list[str]
        self.syscalls: list[str]
        self.sockets: list[str]
        self.__dict__.update(entries)


class Product:
    def __init__(self):
        self.init: list[str]
        self.kernel: list[str]

    def __init__(self, entries):
        self.init: list[str]
        self.kernel: list[str]
        self.__dict__.update(entries)


class Config:
    def __init__(self, entries):
        self.catalyst: Catalyst
        self.product: Product
        self.__dict__.update(entries)


def get_options(file_name: str) -> Config:
    with open(os.path.dirname(os.path.realpath(__file__)) + file_name, 'r') as file:
        config: Config = json.loads(json.dumps((yaml.load(file, Loader=yaml.Loader))), object_hook=Config)
        return config


def get_all_options(dir=os.path.dirname(os.path.realpath(__file__)) + CONFIG_DIR) -> list[Config]:
    opts: list[Config] = []

    for file in os.listdir(dir):
        opts.append(get_options(CONFIG_DIR + file))

    return opts
import yaml
import os
import json


CONFIG_DIR='/configurations/'

class SysArg:
    def __init__(self, entries):
        self.call: str = entries.get('call')
        self.arg_pos: int = entries.get('arg_pos')
        self.arg_vals: list[str or int] = entries.get('arg_vals')


class Catalyst:
    def __init__(self, entries):
        self.files: list[str] = entries.get('files')
        self.syscalls: list[str] = entries.get('syscalls')
        self.sys_args: list[SysArg] = list(map(lambda x: SysArg(x), entries.get('sys_args'))) if entries.get('sys_args') is not None else None


class Product:
    def __init__(self, entries):
        self.init: list[str] = entries.get('init')
        self.kernel: list[str] = entries.get('kernel')


class Config:
    def __init__(self, entries):
        self.catalyst: Catalyst = Catalyst(entries.get('catalyst'))
        self.product: Product = Product(entries.get('product'))


def get_options(file_name: str) -> Config:
    with open(os.path.dirname(os.path.realpath(__file__)) + file_name, 'r') as file:
        config: Config = Config(yaml.load(file, Loader=yaml.Loader))
        return config


def get_all_options(dir=os.path.dirname(os.path.realpath(__file__)) + CONFIG_DIR) -> list[Config]:
    opts: list[Config] = []

    for file in os.listdir(dir):
        opts.append(get_options(CONFIG_DIR + file))

    return opts
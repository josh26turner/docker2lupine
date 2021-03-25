class LinuxConf:
    def __init__(self):
        self.options: list[str]
        self.kml: bool

class Runtime:
    def __init__(self):
        self.entry_command: str
        self.envs: list[str]
        self.working_directory: str
        self.enabled_init_options: list[str]

class Manifest:
    def __init__(self):
        self.linux_configuration = LinuxConf()
        self.runtime = Runtime()
        self.filesystem: str
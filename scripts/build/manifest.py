class LinuxConf:
    def __init__(self):
        self.options: list[str]
        self.kml: bool


    @classmethod
    def from_dict(cls, entries):
        conf = cls()

        conf.options = entries['options']
        conf.kml = entries['kml']

        return conf

class Runtime:
    def __init__(self):
        self.entry_command: str
        self.entry: [str]
        self.envs: list[str]
        self.working_directory: str
        self.enabled_init_options: list[str]


    @classmethod
    def from_dict(cls, entries):
        run = cls()

        run.entry_command = entries['entry_command']
        run.entry = entries['entry']
        run.envs = entries['envs']
        run.working_directory = entries['working_directory']
        run.enabled_init_options = entries['enabled_init_options']

        return run

class Manifest:
    def __init__(self):
        self.linux_configuration = LinuxConf()
        self.runtime = Runtime()
        self.filesystem: str


    @classmethod
    def from_dict(cls, entries):
        manifest = cls()

        manifest.linux_configuration = LinuxConf.from_dict(entries['linux_configuration'])
        manifest.runtime = Runtime.from_dict(entries['runtime'])
        manifest.filesystem = entries['filesystem']

        return manifest
from configparser import ConfigParser


class Config():
    def __init__(self, config_file):
        parser = ConfigParser()

        parser.read(config_file)



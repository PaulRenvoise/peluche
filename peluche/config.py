from configparser import ConfigParser


class Config:
    """
    TODO
    """
    def __init__(self, config_file):
        """
        TODO
        """
        parser = ConfigParser()

        parser.read(config_file)

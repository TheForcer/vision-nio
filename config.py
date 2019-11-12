import logging
import re
import os
import yaml
import sys
from errors import ConfigError

logger = logging.getLogger()


class Config(object):
    def __init__(self, filepath):
        """
        Args:
            filepath (str): Path to config file
        """
        if not os.path.isfile(filepath):
            raise ConfigError(f"Config file '{filepath}' does not exist")

        # Load in the config file at the given filepath
        with open(filepath) as file_stream:
            config = yaml.full_load(file_stream.read())

        # Logging setup
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s [%(levelname)s] %(message)s"
        )

        log_dict = config.get("logging", {})
        log_level = log_dict.get("level", "INFO")
        logger.setLevel(log_level)

        file_logging = log_dict.get("file_logging", {})
        file_logging_enabled = file_logging.get("enabled", False)
        file_logging_filepath = file_logging.get("filepath", "bot.log")
        if file_logging_enabled:
            handler = logging.FileHandler(file_logging_filepath)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        console_logging = log_dict.get("console_logging", {})
        console_logging_enabled = console_logging.get("enabled", True)
        if console_logging_enabled:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # Database setup
        database_dict = config.get("database", {})
        self.database_filepath = database_dict.get("filepath")

        # Whitelist setups
        self.invite_whitelist = config.get("invite_whitelist")
        if not type(self.invite_whitelist) == list:
            raise ConfigError(
                "Leave the list empty if the invite whitelist should be disabled."
            )
        elif not self.invite_whitelist:
            self.invite_whitelist_enabled = False
        else:
            self.invite_whitelist_enabled = True

        self.admin_whitelist = config.get("admin_whitelist")
        if not type(self.admin_whitelist) == list:
            raise ConfigError(
                "Leave the list empty if the admin whitelist should be disabled."
            )
        elif not self.admin_whitelist:
            self.admin_whitelist_enabled = False
        else:
            self.admin_whitelist_enabled = True

        # Matrix bot account setup
        matrix = config.get("matrix", {})

        self.user_id = matrix.get("user_id")
        if not self.user_id:
            raise ConfigError("matrix.user_id is a required field")
        elif not re.match("@.*:.*", self.user_id):
            raise ConfigError("matrix.user_id must be in the form @name:domain")

        self.access_token = matrix.get("access_token")
        if not self.access_token:
            raise ConfigError("matrix.access_token is a required field")

        self.device_id = matrix.get("device_id")
        if not self.device_id:
            logger.warning(
                "matrix.device_id is not provided, which means "
                "that encryption won't work correctly"
            )

        self.homeserver_url = matrix.get("homeserver_url")
        if not self.homeserver_url:
            raise ConfigError("matrix.homeserver_url is a required field")

        self.command_prefix = config.get("command_prefix", "!c") + " "

        # PiHole Setup
        pihole = config.get("pihole", {})
        self.pihole_url = pihole.get("url")

        # UptimeRobot Setup
        utrobot = config.get("uptimerobot", {})
        self.utrobot_apikey = utrobot.get("apikey")
        if not len(self.utrobot_apikey) == 33:
            raise ConfigError("uptimerobot.apikey has the wrong length")

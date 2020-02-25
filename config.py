import logging
import re
import os
import yaml
import sys
from typing import List, Any
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
            self.config = yaml.safe_load(file_stream.read())

        # Logging setup
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s [%(levelname)s] %(message)s"
        )

        log_level = self._get_cfg(["logging", "level"], default="INFO")
        logger.setLevel(log_level)

        file_logging_enabled = self._get_cfg(
            ["logging", "file_logging", "enabled"], default=False
        )
        file_logging_filepath = self._get_cfg(
            ["logging", "file_logging", "filepath"], default="bot.log"
        )
        if file_logging_enabled:
            handler = logging.FileHandler(file_logging_filepath)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        console_logging_enabled = self._get_cfg(
            ["logging", "console_logging", "enabled"], default=True
        )
        if console_logging_enabled:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        # Storage setup
        self.database_filepath = self._get_cfg(
            ["storage", "database_filepath"], required=True
        )
        self.store_filepath = self._get_cfg(
            ["storage", "store_filepath"], required=True
        )

        # Create the store folder if it doesn't exist
        if not os.path.isdir(self.store_filepath):
            if not os.path.exists(self.store_filepath):
                os.mkdir(self.store_filepath)
            else:
                raise ConfigError(
                    f"storage.store_filepath '{self.store_filepath}' is not a directory"
                )

        # Matrix bot account setup
        self.user_id = self._get_cfg(["matrix", "user_id"], required=True)
        if not re.match("@.*:.*", self.user_id):
            raise ConfigError("matrix.user_id must be in the form @name:domain")

        self.user_password = self._get_cfg(["matrix", "user_password"], required=True)
        self.device_id = self._get_cfg(["matrix", "device_id"], required=True)
        self.device_name = self._get_cfg(
            ["matrix", "device_name"], default="nio-template"
        )
        self.homeserver_url = self._get_cfg(["matrix", "homeserver_url"], required=True)
        self.enable_encryption = self._get_cfg(
            ["matrix", "enable_encryption"], default=False
        )

        # Matrix invite whitelist setup
        self.invite_whitelist = self._get_cfg(
            ["matrix", "invite_whitelist"], required=False
        )
        if not type(self.invite_whitelist) == list:
            raise ConfigError(
                "Leave the list empty if the invite whitelist should be disabled."
            )
        elif not self.invite_whitelist:
            self.invite_whitelist_enabled = False
        else:
            self.invite_whitelist_enabled = True

        # Matrix admin whitelist setup
        self.admin_whitelist = self._get_cfg(
            ["matrix", "admin_whitelist"], required=False
        )
        if not type(self.admin_whitelist) == list:
            raise ConfigError(
                "Leave the list empty if the admin whitelist should be disabled."
            )
        elif not self.admin_whitelist:
            self.admin_whitelist_enabled = False
        else:
            self.admin_whitelist_enabled = True

        # AdGuard Home Setup
        self.adguard_url = self._get_cfg(["adguard", "url"], required=False)
        self.adguard_port = self._get_cfg(["adguard", "port"], default=3000)
        self.adguard_tls = self._get_cfg(["adguard", "tls"], default=False)
        self.adguard_username = self._get_cfg(["adguard", "username"], required=False)
        self.adguard_password = self._get_cfg(["adguard", "password"], required=False)

        self.command_prefix = self._get_cfg(["command_prefix"], default="!c") + " "

    def _get_cfg(
        self, path: List[str], default: Any = None, required: bool = True
    ) -> Any:
        """Get a config option from a path and option name, specifying whether it is
        required.

        Raises:
            ConfigError: If required is specified and the object is not found
                (and there is no default value provided), this error will be raised
        """
        # Sift through the the config until we reach our option
        config = self.config
        for name in path:
            config = config.get(name)

            # If at any point we don't get our expected option...
            if config is None:
                # Raise an error if it was required
                if required or not default:
                    raise ConfigError(f"Config option {'.'.join(path)} is required")

                # or return the default value
                return default

        # We found the option. Return it
        return config

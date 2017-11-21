from time import sleep

import requests
from requests.exceptions import RequestException
from simple_container_runtime.modules.Module import HealthCheckModule
from simple_container_runtime.util import get_logger


class LocalHttpHealthCheck(HealthCheckModule):
    def __init__(self, config: dict):
        super().__init__(config)

        self.logger = get_logger()
        self.port = int(config["port"])
        self.path = config.get("path", "").lstrip("/")
        self.encrypted = bool(config.get("encrypted", False))
        self.expected_string = config.get("expected_string")
        self.timeout = int(config.get("timeout", 300))
        self.interval = int(config.get("interval", 2))

    def run(self):
        if self.encrypted:
            protocol = "https"
        else:
            protocol = "http"

        for i in range(0, max(int(self.timeout / self.interval), 1)):
            try:
                url = "{}://localhost:{}/{}".format(protocol, self.port, self.path)
                response = requests.get(url, timeout=1)
                response.raise_for_status()

                if self.expected_string:
                    if response.text == self.expected_string:
                        return True
                    else:
                        self.logger.error("Response was ok but expected string: '{}' was not found in: '{}'".format(
                            self.expected_string, response.text))
                        return False

                return True

            except RequestException:
                sleep(self.interval)

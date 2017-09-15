import os
import signal as os_signal
import tempfile

import yaml
from typing import List, Dict

from simple_container_runtime.modules.AwsEcrLogin import AwsEcrLogin
from simple_container_runtime.util import get_logger
from simple_container_runtime.exceptions import ScrBaseException
from simple_container_runtime.file_reader import FileLoader
from simple_container_runtime.docker import DockerCompose
from simple_container_runtime.modules.Http import HttpHealthCheck
from simple_container_runtime.modules.AwsElbHealthCheck import AwsElbHealthCheck
from simple_container_runtime.modules.AwsCfnSignal import AwsCfnSignal

work_dir = tempfile.mkdtemp()


class Runnable(object):
    def __init__(self, config_file=None, config_dict=None):
        self.logger = get_logger(name="Run")

        if config_file:
            base_dir = os.path.dirname(os.path.realpath(config_file))
            self.config = FileLoader.get_yaml_or_json_file(config_file, base_dir)
        elif config_dict:
            self.config = config_dict
        else:
            raise ScrBaseException("Runnable must be initialized with either config_file or config_dict")

    def run(self) -> None:
        try:
            self._register_stop_callbacks()

            self._execute_pre_start_modules()

            self._write_compose_config(self.config, work_dir)
            DockerCompose(work_dir).up()

            self._execute_health_checks()
        except Exception as e:
            self.logger.error("Start process failed")
            self._send_signals(successful=False)
            raise e

        self._send_signals(successful=True)
        self.logger.info("Startup finished")
        os_signal.pause()

    def _execute_pre_start_modules(self):
        pre_start_config = self.config.get("pre_start")
        pre_start_modules = {"AwsEcrLogin": AwsEcrLogin}

        if pre_start_config:
            self._execute_modules(pre_start_modules, pre_start_config, execution_args={}, kind="PreStartModule")
            self.logger.info("All pre-start modules executed successfully!")
        else:
            self.logger.info("No pre-start modules configured")

    def _send_signals(self, successful: bool):
        signal_config = self.config.get("signals")
        signal_modules = {"AwsCfn": AwsCfnSignal}

        if signal_config:
            self._execute_modules(signal_modules, signal_config,
                                  execution_args={"successful": successful},
                                  kind="Signal")

            self.logger.info("All signals sent successfully!")
        else:
            self.logger.info("No signals configured")

    def _execute_health_checks(self):
        healthcheck_config = self.config.get("healthchecks")
        healthcheck_modules = {
            "AwsElb": AwsElbHealthCheck,
            "http": HttpHealthCheck
        }

        if healthcheck_config:
            self._execute_modules(healthcheck_modules, healthcheck_config, execution_args={}, kind="HealthCheck")
            self.logger.info("All health checks completed successfully!")
        else:
            self.logger.info("No health checks configured")

    def _execute_modules(self, known_modules: dict, config: List[dict], execution_args: dict, kind: str):
        for module_config in config:
            assert isinstance(module_config, dict), \
                "Config value for {} must be a dictionary, not {}".format(kind, type(module_config))

            name = list(module_config.keys())[0]
            config = module_config[name]
            self.logger.info("Executing {}".format(name))
            executable = known_modules.get(name)

            if executable:
                result = executable(config).run(**execution_args)
                if result:
                    self.logger.info("{} {} succeeded".format(kind, name))
                else:
                    raise ScrBaseException("{} {} failed".format(kind, name))
            else:
                raise ScrBaseException("Could not find {} module for {}".format(kind, name))

    @staticmethod
    def _write_compose_config(config: dict, work_dir: str):
        with open("{}/docker-compose.yaml".format(work_dir), "w") as f:
            f.write(yaml.safe_dump(config["docker-compose"]))

    @staticmethod
    def _handle_stop(signum, frame) -> None:
        DockerCompose(work_dir).down()

    @classmethod
    def _register_stop_callbacks(cls) -> None:
        os_signal.signal(os_signal.SIGINT, cls._handle_stop)
        os_signal.signal(os_signal.SIGTERM, cls._handle_stop)


if __name__ == '__main__':
    Runnable(
        config_file="/Users/mhoyer/IdeaProjects/simple-container-runtime/src/unittest/resources/test-config.yaml").run()

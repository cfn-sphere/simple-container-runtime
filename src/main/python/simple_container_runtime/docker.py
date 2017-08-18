import sh

from simple_container_runtime.exceptions import ScrBaseException
from simple_container_runtime.util import get_logger


class DockerCompose(object):
    docker_compose = sh.Command("/usr/local/bin/docker-compose")
    output_logger = get_logger(name="DockerComposeOutput")

    def __init__(self, work_dir):
        self.logger = get_logger(name="DockerCompose")
        self.work_dir = work_dir

    def up(self) -> None:
        self.logger.info("Starting containers")
        try:
            p = self.docker_compose("up", "-d", _cwd=self.work_dir, _bg=True, _out=self._process_output,
                                    _err=self._process_output)
            p.wait()
        except sh.ErrorReturnCode as e:
            raise ScrBaseException(e.stderr)

        self.logger.info("Containers started")

    def down(self):
        self.logger.info("Stopping containers")
        try:
            p = self.docker_compose("down", _cwd=self.work_dir, _bg=True, _out=self._process_output,
                                    _err=self._process_output)
            p.wait()
        except sh.ErrorReturnCode as e:
            raise ScrBaseException(e.stderr)

        self.logger.info("Containers stopped")

    @classmethod
    def _process_output(cls, line):
        cls.output_logger.info(line.strip("\r\n").strip("\n"))

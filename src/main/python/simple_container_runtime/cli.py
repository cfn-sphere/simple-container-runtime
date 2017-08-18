import sys
import click
import logging
from simple_container_runtime import __version__
from simple_container_runtime.exceptions import ScrBaseException
from simple_container_runtime.util import get_logger
from simple_container_runtime.api import run_from_config_path

LOGGER = get_logger(root=True)


@click.group(help="Simple container runtime is intended to be a really simple solution to run docker containers.")
@click.version_option(version=__version__)
def cli():
    pass


@cli.command(help="Run")
@click.argument('url', type=click.STRING)
@click.option('--debug', '-d', is_flag=True, default=False, envvar='SCR_DEBUG', help="Debug output")
def run(url, debug):
    if debug:
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.INFO)

    try:
        run_from_config_path(config_path=url)
    except ScrBaseException as e:
        LOGGER.error(e)
        if debug:
            LOGGER.exception(e)
        sys.exit(1)
    except Exception as e:
        LOGGER.error("Failed with unexpected error")
        LOGGER.exception(e)
        sys.exit(1)


def main():
    cli()

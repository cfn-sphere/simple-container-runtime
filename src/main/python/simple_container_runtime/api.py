from simple_container_runtime.runnable import Runnable


def run_from_config_path(config_path: str) -> None:
    Runnable(config_file=config_path).run()


def run_from_config_dict(config: dict) -> None:
    Runnable(config_dict=config).run()

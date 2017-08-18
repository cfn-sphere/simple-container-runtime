from abc import ABCMeta, abstractmethod


class Module(object, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, config: dict):
        pass


class PreStartModule(Module):
    @abstractmethod
    def run(self):
        pass

class HealthCheckModule(Module):
    @abstractmethod
    def run(self):
        pass


class SignalModule(Module):
    @abstractmethod
    def run(self, successful: bool):
        pass

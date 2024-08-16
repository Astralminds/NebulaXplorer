import time
from contextlib import contextmanager
import sys
import loguru


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        key = (cls, args, frozenset(kwargs.items()))
        if key not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[key] = instance
        return cls._instances[key]


loguru.logger.remove()


class Logger(metaclass=Singleton):
    def __init__(self, name, log_dir=None):
        super().__init__()
        format = (
            "<d><green>[{extra[name]:^15}]</green>"
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<cyan>{file}</cyan>:<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<cyan>{process}</cyan> {elapsed} </d> "
            "\n \u2514\u2500\u2500\u2500\u2500 <level>{level}</level>: "
            "<level>{message}</level>"
        )
        self.logger = loguru.logger.bind(name=name)
        self.logger.add(sys.stderr, format=format,
                        filter=lambda record: record["extra"].get("name") == name)
        if log_dir is not None:
            log_file = f"{log_dir}/{name}.log"
            self.logger.add(log_file, format=format,
                            filter=lambda record: record["extra"].get("name") == name, level="INFO")

    def __getattr__(self, name: str):
        return getattr(self.logger, name)


class Timer:
    time_logger = Logger("Timer")

    @classmethod
    @contextmanager
    def timeit(cls, message="operation"):
        start = time.time()
        cls.time_logger.info(f"{message} started.")
        yield
        cls.time_logger.info(
            f"{message} finished in {time.time()-start:.2f} seconds.")

    @classmethod
    def timer(cls, func):
        def wrapper(*args, **kwargs):
            start = time.time()
            res = func(*args, **kwargs)
            cls.time_logger.info(
                f"{func.__name__} finished in {time.time()-start:.2f} seconds.")
            return res
        return wrapper

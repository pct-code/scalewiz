"""A logger class for the program."""

import logging
from logging.handlers import QueueHandler
from queue import Queue


class Logger:
    """Sets default logging behavior for the program.

    Holds a ref to a queue. The LogFrame depends on access to this.

    Use from anywhere by calling logging.getLogger('scalewiz')
    """

    def __init__(self) -> None:
        """The LogWindow depends on access to the .loq_queue attribute."""
        self.log_queue = Queue()
        logging.basicConfig(level=logging.DEBUG)
        queue_handler = QueueHandler(self.log_queue)
        # this one is for inspecting the multithreading
        # fmt = "%(asctime)s - %(func)s - %(thread)d - %(levelname)s - %(name)s - %(message)s"  # noqa: E501
        fmt = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        date_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            fmt,
            date_fmt,
        )
        queue_handler.setFormatter(formatter)
        queue_handler.setLevel(logging.INFO)
        logging.getLogger("scalewiz").addHandler(queue_handler)

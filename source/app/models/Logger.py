import logging
from logging.handlers import QueueHandler
import queue

class Logger:
    """Sets default logging behavior for the program.

    Holds a ref to a queue. The LogFrame depends on access to this.

    Use from anywhere by calling logging.getLogger('scalewiz')
    """ 

    def __init__(self):
        """The LogWindow depends on access to the .loq_queue attribute."""
        self.log_queue = queue.Queue()
        # set default logging behavior. could be moved to json. see dictConfig
        logging.basicConfig(level=logging.DEBUG)
        queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s - %(thread)d - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        queue_handler.setFormatter(formatter)
        queue_handler.setLevel(logging.DEBUG)
        logging.getLogger('scalewiz').addHandler(queue_handler)
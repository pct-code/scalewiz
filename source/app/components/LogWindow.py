import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import logging
import queue


# https://github.com/beenje/tkinter-logging-text-widget/blob/master/main.py
class QueueHandler(logging.Handler):
    """Class to send logging records to a queue
    It can be used from different threads
    The ConsoleUi class polls this queue to display records in a ScrolledText widget
    """
    # Example from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06
    # (https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget) is not thread safe!
    # See https://stackoverflow.com/questions/43909849/tkinter-python-crashes-on-new-thread-trying-to-log-on-main-thread

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    # this method is defined but not called -- used internally 
    def emit(self, record):
        self.log_queue.put(record)

class LogWindow(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.build()

    def build(self):
        self.parent.winfo_toplevel().title('Log Window')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.scrolled_text = ScrolledText(self, state='disabled')
        self.scrolled_text.grid(row=0, column=0, sticky='nsew')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        
        # Create a logging handler using a queue
        logging.basicConfig(level=logging.DEBUG)
        # todo need to make custom logger to stay rid of all those matplotlib debug logs
        logger = logging.getLogger('scalewiz')

        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s - %(thread)d - %(levelname)s - %(message)s')
        self.queue_handler.setFormatter(formatter)
        self.queue_handler.setLevel(logging.DEBUG)
        logger.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.after(100, self.poll_log_queue)

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        # i think this last arg is for the tag
        self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.after(100, self.poll_log_queue)


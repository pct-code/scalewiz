import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import logging
from logging.handlers import QueueHandler, QueueListener
import queue


# # https://github.com/beenje/tkinter-logging-text-widget/blob/master/main.py
# class QueueHandler(logging.Handler):
#     """Class to send logging records to a queue
#     It can be used from different threads
#     The ConsoleUi class polls this queue to display records in a ScrolledText widget
#     """
#     # Example from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06
#     # (https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget) is not thread safe!
#     # See https://stackoverflow.com/questions/43909849/tkinter-python-crashes-on-new-thread-trying-to-log-on-main-thread

#     def __init__(self, log_queue):
#         super().__init__()
#         self.log_queue = log_queue

#     # this method is defined but not called -- used internally 
#     def emit(self, record):
#         self.log_queue.put(record)

class LogWindow(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.build()

    def build(self):
        self.parent.winfo_toplevel().title('Log Window')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.scrolled_text = ScrolledText(self, state='disabled', width=70)
        self.scrolled_text.grid(row=0, column=0, sticky='nsew')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        
        # Create a logging handler using a queue
        logging.basicConfig(level=logging.DEBUG)

        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s - %(thread)d - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        self.queue_handler.setFormatter(formatter)
        self.queue_handler.setLevel(logging.DEBUG)
        # listener = QueueListener(self.log_queue, self.queue_handler, respect_handler_level=True)
        # listener.start()
        logger = logging.getLogger('scalewiz')
        # logger.propagate = False
        logger.addHandler(self.queue_handler)

        # Start polling messages from the queue
        self.after(100, self.poll_log_queue)

    def display(self, record):
        msg = record.getMessage()
        self.scrolled_text.configure(state='normal')
        # last arg is for the tag
        self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # scroll to bottom
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


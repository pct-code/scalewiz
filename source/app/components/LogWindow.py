import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import logging
from logging.handlers import QueueHandler, QueueListener
import queue


class LogWindow(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.build()

    def build(self):
        self.parent.winfo_toplevel().title('Log Window')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.scrolled_text = ScrolledText(self, state='disabled', width=80)
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


"""The entry point for the program."""

import tkinter as tk

from pct_scalewiz.components.scalewiz import ScaleWiz

def main() -> None:
    """The Tkinter entry point of the program; enters mainloop."""
    root = tk.Tk()
    ScaleWiz(root).grid()
    root.mainloop()

if __name__ == "__main__":
    main()

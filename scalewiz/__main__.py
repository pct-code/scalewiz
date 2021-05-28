"""The entry point for the program."""

import tkinter as tk

import scalewiz
from scalewiz.components.scalewiz import ScaleWiz


def main() -> None:
    """The Tkinter entry point of the program; enters mainloop."""
    root = tk.Tk()
    scalewiz.ROOT = root
    ScaleWiz(root).grid(sticky="nsew")
    root.mainloop()


if __name__ == "__main__":
    main()

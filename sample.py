import tkinter as tk
from time import time


class App(tk.Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.count = tk.IntVar()
        self.delay = tk.DoubleVar()
        tk.Label(self, textvariable=self.delay).pack(padx=20, pady=20)
        tk.Label(self, textvariable=self.count).pack(padx=20, pady=20)
        self.cycle(1000)

    def cycle(self, interval_ms: int, start=None, count=0) -> None:
        print("count is", count)
        if start is None:
            start = time()
        if count < 100:
            self.count.set(count)
            x = [i for i in range(1 * 10 ** 6)]
            [i + 1 for i in x]
            [i * 2 for i in x]
            # this is approximate
            self.delay.set(interval_ms - (((time() - start) * 1000) % interval_ms))
            print("delay is", self.delay.get())
            self.after(
                round(interval_ms - (((time() - start) * 1000) % interval_ms)),
                self.cycle,
                interval_ms,
                start,
                count + 1,
            )


if __name__ == "__main__":
    root = tk.Tk()
    App(root).pack()
    root.mainloop()

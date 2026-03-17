import random
import tkinter as tk

from app_legacy import App
from cdad.platform.dpi import enable_windows_dpi_awareness


def run() -> None:
    random.seed()
    enable_windows_dpi_awareness()
    root = tk.Tk()
    App(root)
    root.mainloop()


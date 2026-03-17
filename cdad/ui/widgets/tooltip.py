import tkinter as tk


class Tooltip:
    def __init__(self, widget: tk.Widget, text: str, theme: dict, image: tk.PhotoImage | None = None) -> None:
        self.widget = widget
        self.text = text
        self.theme = theme
        self.image = image
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
        widget.bind("<ButtonPress>", self.hide, add="+")

    def show(self, _event=None) -> None:
        if not self.text:
            return
        if self.tip:
            self.tip.destroy()
            self.tip = None
        x = self.widget.winfo_pointerx() + 12
        y = self.widget.winfo_pointery() + 12
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        self.tip.bind("<Leave>", self.hide)
        self.tip.bind("<ButtonPress>", self.hide)
        container = tk.Frame(self.tip, bg=self.theme["panel"], relief="solid", borderwidth=1)
        container.pack()
        if self.image:
            image_label = tk.Label(container, image=self.image, bg=self.theme["panel"])
            image_label.image = self.image
            image_label.pack(padx=6, pady=(6, 2))
        label = tk.Label(
            container,
            text=self.text,
            justify="left",
            font=self.theme["body_font"],
            bg=self.theme["panel"],
            fg=self.theme["text"],
        )
        label.pack(padx=6, pady=(0, 6))
        self.tip.update_idletasks()
        tip_w = self.tip.winfo_width()
        tip_h = self.tip.winfo_height()
        root = self.widget.winfo_toplevel()
        root.update_idletasks()
        root_x = root.winfo_rootx()
        root_y = root.winfo_rooty()
        root_w = root.winfo_width()
        root_h = root.winfo_height()
        if x + tip_w > root_x + root_w - 6:
            x = self.widget.winfo_pointerx() - tip_w - 12
        if y + tip_h > root_y + root_h - 6:
            y = self.widget.winfo_pointery() - tip_h - 12
        max_x = root_x + root_w - tip_w - 6
        max_y = root_y + root_h - tip_h - 6
        x = max(root_x + 6, min(x, max_x))
        y = max(root_y + 6, min(y, max_y))
        self.tip.wm_geometry(f"+{x}+{y}")

    def hide(self, _event=None) -> None:
        if self.tip:
            self.tip.destroy()
            self.tip = None


# ui.py
import tkinter as tk
from tkinter import ttk

# --- Constants (partagés) ---
WHITE = "#FFFFFF"
UI_FONT      = ("Segoe UI", 9)
UI_FONT_BOLD = ("Segoe UI", 9, "bold")
PADX_S, PADY_S = 6, 2
PADY_SEC       = 4
GRID_PAD       = 2

def apply_theme(root: tk.Tk | tk.Widget):
    """
    Thème compact tout blanc pour TTK (labels, frames, boutons, combobox, checkboxes, entries).
    À appeler UNE SEULE FOIS (dans main.py) pour tout l’app.
    """
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Couleurs & polices par défaut (fond blanc)
    base = {
        "background": WHITE,
        "foreground": "#000000",
        "font": UI_FONT,
        "padding": 0,
    }
    for elem in ("TFrame","TLabelframe","TLabelframe.Label","TLabel","TButton","TCheckbutton","TRadiobutton"):
        style.configure(elem, **base)

    style.configure("Bold.TLabel", background=WHITE, foreground="#000000", font=UI_FONT_BOLD)
    style.configure("TEntry", fieldbackground=WHITE, background=WHITE)
    style.configure("Compact.TCombobox", fieldbackground=WHITE, background=WHITE, arrowsize=14, padding=0)

    # Fond window / containers (tk natif)
    try:
        root.configure(bg=WHITE)
    except Exception:
        pass


def force_white_bg(widget: tk.Widget):
    """Force le fond blanc récursivement pour les widgets Tk 'classiques' (Frames, LabelFrames, Text, etc.)."""
    try:
        widget.configure(bg=WHITE)
    except Exception:
        pass
    for child in widget.winfo_children():
        force_white_bg(child)


class ScrollFrame(tk.Frame):
    """
    Conteneur scrollable vertical prêt à l'emploi (fond blanc).
    Utilisation:
        sf = ScrollFrame(parent)
        form_parent = sf.interior  # mettre vos widgets ici
    """
    def __init__(self, parent):
        super().__init__(parent, bg=WHITE)

        self.canvas  = tk.Canvas(self, highlightthickness=0, bg=WHITE)
        self.vscroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vscroll.pack(side="right", fill="y")

        self.interior = tk.Frame(self.canvas, bg=WHITE)
        self._win_id = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")

        # Ajuste la surface scrollable
        self.interior.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",  lambda e: self.canvas.itemconfig(self._win_id, width=e.width))

        # Mouse wheel (Windows/Mac/Linux)
        self._bind_mousewheel(self.canvas)

    def _bind_mousewheel(self, widget):
        widget.bind_all("<MouseWheel>", self._on_mousewheel, add="+")  # Win/Mac
        widget.bind_all("<Button-4>",  lambda e: self.canvas.yview_scroll(-1, "units"), add="+")  # Linux up
        widget.bind_all("<Button-5>",  lambda e: self.canvas.yview_scroll( 1, "units"), add="+")  # Linux down

    def _on_mousewheel(self, event):
        delta = getattr(event, "delta", 0)
        self.canvas.yview_scroll(-1 if delta > 0 else 1, "units")

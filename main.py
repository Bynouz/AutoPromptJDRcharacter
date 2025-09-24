import tkinter as tk
from tkinter import ttk, messagebox
import traceback

from solocharacter import CharacterForm
from groupcharacter import GroupForm
from monsters import MonsterForm


# ---------- Shared Prompt Bus ----------
class PromptBus:
    """
    Shared in-memory roster for group mixing.
    Characters/Monsters push prompts here via 'Add to Group'.
    Duplicates allowed. Max 12 items.
    Each item: {"type": "character"|"monster", "label": str, "text": str, "weight": int}
    """
    MAX_ITEMS = 12

    def __init__(self):
        self.items = []
        self.listeners = []

    def register(self, callback):
        """Register a listener; immediately notify with current items."""
        self.listeners.append(callback)
        callback(list(self.items))

    def _notify(self):
        for cb in self.listeners:
            cb(list(self.items))

    def add(self, item):
        if len(self.items) >= self.MAX_ITEMS:
            raise RuntimeError(f"Roster is full (max {self.MAX_ITEMS}).")
        self.items.append(item)
        self._notify()

    def add_character(self, label, text, weight=3):
        self.add({"type": "character", "label": label or "Character", "text": text, "weight": int(weight)})

    def add_monster(self, label, text, weight=3):
        self.add({"type": "monster", "label": label or "Monster", "text": text, "weight": int(weight)})

    # Mutations for Group UI
    def move_up(self, idx):
        if 0 < idx < len(self.items):
            self.items[idx-1], self.items[idx] = self.items[idx], self.items[idx-1]
            self._notify()

    def move_down(self, idx):
        if 0 <= idx < len(self.items) - 1:
            self.items[idx+1], self.items[idx] = self.items[idx], self.items[idx+1]
            self._notify()

    def remove(self, idx):
        if 0 <= idx < len(self.items):
            self.items.pop(idx)
            self._notify()

    def clear(self):
        self.items.clear()
        self._notify()

    def set_weight(self, idx, w):
        if 0 <= idx < len(self.items):
            self.items[idx]["weight"] = int(w)
            self._notify()


# ---------- Scrollable container ----------
class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.vscroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vscroll.pack(side="right", fill="y")

        self.interior = tk.Frame(self.canvas)
        self._win_id = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")

        self.interior.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._win_id, width=e.width))

        self._bind_mousewheel(self.canvas)

    def _bind_mousewheel(self, widget):
        # Windows / Mac
        widget.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        # Linux/X11
        widget.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"), add="+")
        widget.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"), add="+")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 if getattr(event, "delta", 0) > 0 else 1, "units")


# ---------- App ----------
class App:
    def __init__(self, root):
        root.title("Simplified Character Generation")
        root.minsize(1000, 680)

        styles_map = {
            "Dark Fantasy (B/W)": "A black-and-white, highly detailed portrait in dark fantasy or gothic style, charcoal or ink rendering.",
            "Heroic Fantasy (color)": "A vibrant, full-color heroic fantasy character portrait, painted illustration.",
            "Photorealistic": "A photorealistic portrait with shallow depth of field (85mm lens), high dynamic range.",
            "Anime / Manga": "An anime-style character portrait with clean lineart and cel shading.",
            "Soft Watercolor": "A soft watercolor illustration with light washes and paper texture.",
            "Oil Painting": "An oil painting portrait with rich brush strokes and dramatic lighting.",
            "Steampunk": "A steampunk character portrait with brass fittings, gears, and Victorian aesthetics.",
            "Neon Cyberpunk": "A neon-lit cyberpunk portrait with moody atmosphere and futuristic city glow.",
            "Etching": "A monochrome copperplate etching style with fine cross-hatching.",
            "Cinematic Concept Art": "A cinematic concept art portrait, painterly and high detail."
        }

        # Shared bus for group mixing
        self.bus = PromptBus()

        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True)

        # Character tab
        tab1 = ScrollFrame(nb)
        nb.add(tab1, text="Character")
        self.char_form = CharacterForm(tab1.interior, styles_map, prompt_bus=self.bus)
        self.char_form.frame.pack(anchor="w", fill="x", padx=8, pady=8)

        # Group tab (mixer)
        tab2 = ScrollFrame(nb)
        nb.add(tab2, text="Group")
        self.group_form = GroupForm(tab2.interior, styles_map, prompt_bus=self.bus)
        self.group_form.frame.pack(anchor="w", fill="x", padx=8, pady=8)

        # Monsters tab
        tab3 = ScrollFrame(nb)
        nb.add(tab3, text="Monsters")
        self.monster_form = MonsterForm(tab3.interior, styles_map, prompt_bus=self.bus)
        self.monster_form.frame.pack(anchor="w", fill="x", padx=8, pady=8)


# ---------- Safe launch ----------
if __name__ == "__main__":
    try:
        root = tk.Tk()
        App(root)
        root.mainloop()
    except Exception:
        err = traceback.format_exc()
        print(err)
        try:
            messagebox.showerror("Error", err)
        except Exception:
            pass

# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import traceback

from solocharacter import CharacterForm
from groupcharacter import GroupForm
from monsters import MonsterForm

# UI partagé
from ui import apply_theme, ScrollFrame, WHITE

# ---------- Shared Prompt Bus ----------
class PromptBus:
    """
    In-memory roster for group mixing (characters + monsters).
    Each item: {"type": "character"|"monster", "label": str, "text": str, "weight": int}
    """
    MAX_ITEMS = 12

    def __init__(self):
        self.items = []
        self.listeners = []

    def register(self, callback):
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


# ---------- App ----------
class App:
    def __init__(self, root):
        root.title("Simplified Character Generation")
        root.minsize(1000, 680)

        # 1) Appliquer le thème blanc compact UNE SEULE FOIS
        apply_theme(root)

        # 2) Styles d’image partagés
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

        # Bus partagé pour l’onglet Groupe
        self.bus = PromptBus()

        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True)

        # Onglet Character
        tab1 = ScrollFrame(nb)
        nb.add(tab1, text="Character")
        self.char_form = CharacterForm(tab1.interior, styles_map, prompt_bus=self.bus)
        self.char_form.frame.pack(anchor="w", fill="x", padx=8, pady=8)

        # Onglet Group (mixer)
        tab2 = ScrollFrame(nb)
        nb.add(tab2, text="Group")
        self.group_form = GroupForm(tab2.interior, styles_map, prompt_bus=self.bus)
        self.group_form.frame.pack(anchor="w", fill="x", padx=8, pady=8)

        # Onglet Monsters
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

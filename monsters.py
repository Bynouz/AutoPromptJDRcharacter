import tkinter as tk
from tkinter import ttk, messagebox
import unicodedata

from ui import WHITE, PADX_S, PADY_S, PADY_SEC, GRID_PAD

# --- utils ---
def unaccent(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if not unicodedata.combining(ch))
def sorted_en(items): return sorted(items, key=lambda s: unaccent(s).lower())
def parse_custom_list(text: str):
    if not text: return []
    out = []
    for token in text.replace(";", ",").replace("\n", ",").split(","):
        t = token.strip()
        if t: out.append(t)
    return out

# --- vocab ---
SPECIES = sorted_en([
    "Undead","Vampire","Zombie","Skeleton","Wraith","Ghost",
    "Demon","Devil","Imp","Gargoyle",
    "Dragon","Wyvern","Basilisk","Hydra",
    "Giant","Troll","Ogre",
    "Goblin","Orc","Kobold","Lizardfolk",
    "Werewolf","Lycanthrope",
    "Giant Spider","Giant Scorpion","Kraken","Leviathan",
    "Slime","Ooze",
    "Golem (Stone)","Golem (Iron)","Golem (Clay)","Golem (Flesh)",
    "Elemental (Fire)","Elemental (Ice)","Elemental (Air)","Elemental (Earth)",
    "Plant Monster","Treant","Vine Horror"
])
SIZE_CLASS = ["Tiny","Small","Medium","Large","Huge","Colossal"]
TEMPER = ["Ferocious","Territorial","Cunning","Mindless","Predatory","Brooding","Malevolent","Savage","Stalking"]

ANATOMY = sorted_en([
    "Claws","Talons","Fangs","Tusks","Horns","Antlers","Spikes","Bony Plates","Scales","Chitin","Fur","Feathers",
    "Exposed Bone","Tentacles","Wings","Multiple Eyes","Single Eye","Extra Arms","Tail","Stinger",
    "Venom","Acidic Saliva","Fire Breath","Ice Breath","Poison Cloud"
])
LOCOMOTION = ["Biped","Quadruped","Serpentine","Aerial","Burrowing","Aquatic","Amphibious","Ooze-like"]
BEHAVIOR = sorted_en([
    "Ambush Hunter","Pack Tactics","Solitary Stalker","Territorial Roar","Fear Aura",
    "Regeneration","Camouflage","Invisibility","Shadow Step","Teleport",
    "Magic Resistant","Necrotic Aura","Psychic Scream","Web Spinning","Stone Gaze","Charm Gaze"
])
BIOOME = sorted_en([
    "Cave","Ancient Ruins","Swamp","Mire","Shadowy Forest","Mountain Pass","Desert Dunes","Snowy Tundra","City Sewer",
    "Cathedral Ruin","Cemetery","Volcanic Crater","Abandoned Mine","Stormy Coast","Ship Graveyard"
])
COLORS = sorted_en([
    "Black","Charcoal","Grey","White","Bone","Green","Olive","Dark Green","Brown","Umber","Rust","Crimson",
    "Purple","Violet","Blue","Teal","Copper","Bronze","Gold","Silver"
])
LIGHTING = ["Moonlit","Torchlit","Volumetric Rays","Overcast","Backlit silhouette","Lightning flashes"]
FRAMING = sorted_en([
    "Head Only","Bust","Torso","Half Body","Three-Quarter View","Full Body","Low Angle","High Angle","Wide Shot"
])
POSES = sorted_en([
    "Roaring","Lunging","Stalking","Coiled to strike","Spreading wings","Perched and glaring","Emerging from shadows",
    "Breaking through wall","Bursting from water","Crushing debris underfoot"
])

class MonsterForm:
    def __init__(self, parent, styles_map, title_text="Monster generator", prompt_bus=None):
        self.styles_map = styles_map
        self.prompt_bus = prompt_bus

        self.frame = tk.LabelFrame(parent, text=title_text, bg=WHITE)
        self.frame.configure(padx=PADX_S, pady=PADY_S)

        self.style_var = tk.StringVar(value=list(styles_map.keys())[0])

        # singles
        self.single_vars = {}
        self.multi_blocks = {}
        self.energy_var = tk.BooleanVar(value=True)
        self._last_prompt = ""

        self._build_ui()

    # ---- grid helpers ----
    _grid_rows = {}
    def _make_grid(self, parent):
        f = tk.Frame(parent, bg=WHITE)
        f.grid_columnconfigure(0, minsize=140, weight=0)
        f.grid_columnconfigure(1, minsize=200, weight=0)
        f.grid_columnconfigure(2, weight=1)
        f.grid_columnconfigure(3, minsize=46,  weight=0)
        self._grid_rows[f] = 0
        return f

    def _add_single_row(self, grid_parent, label, options, key, width=20):
        r = self._grid_rows[grid_parent]
        ttk.Label(grid_parent, text=label, style="Bold.TLabel").grid(row=r, column=0, sticky="w", padx=(0,8), pady=(PADY_S, PADY_S))
        var = tk.StringVar(value="— (leave empty) —")
        ttk.Combobox(grid_parent, textvariable=var, values=["— (leave empty) —"]+list(options),
                     state="readonly", width=width, style="Compact.TCombobox").grid(row=r, column=1, sticky="w", pady=(PADY_S, PADY_S))
        other = tk.StringVar()
        ttk.Entry(grid_parent, textvariable=other).grid(row=r, column=2, sticky="ew", padx=(8,0), pady=(PADY_S, PADY_S))
        ttk.Label(grid_parent, text="Other").grid(row=r, column=3, sticky="w", padx=(6,0), pady=(PADY_S, PADY_S))
        self.single_vars[key] = (var, other)
        self._grid_rows[grid_parent] = r + 1

    def _add_multi_block(self, parent, title, options, key, columns=2, grid=False, grid_rc=(0,0)):
        block = tk.LabelFrame(parent, text=title, bg=WHITE)
        items = []
        rows = max(1, (len(options) + columns - 1)//columns)
        for idx, opt in enumerate(options):
            v = tk.BooleanVar()
            cb = ttk.Checkbutton(block, text=opt, variable=v)
            r, c = idx % rows, idx // rows
            block.grid_columnconfigure(c, weight=1, uniform=f"{key}_cols")
            cb.grid(row=r, column=c, sticky="w", padx=(4,4), pady=(GRID_PAD, GRID_PAD))
            items.append((opt, v))
        bottom = tk.Frame(block, bg=WHITE)
        bottom.grid(row=rows, column=0, columnspan=columns, sticky="ew")
        other_var = tk.StringVar()
        ttk.Entry(bottom, textvariable=other_var).grid(row=0, column=0, sticky="ew", padx=(4,4), pady=(4,2))
        ttk.Label(bottom, text="Other (comma separated)").grid(row=0, column=1, sticky="w", padx=(6,0))
        bottom.grid_columnconfigure(0, weight=1)
        self.multi_blocks[key] = {"frame": block, "items": items, "other_var": other_var}
        if grid:
            r, c = grid_rc; block.grid(row=r, column=c, sticky="nsew", padx=4, pady=PADY_SEC)
        else:
            block.pack(anchor="w", fill="x", pady=PADY_SEC)
        return block

    # ---- UI ----
    def _build_ui(self):
        header = tk.Frame(self.frame, bg=WHITE); header.pack(anchor="w", fill="x", pady=PADY_SEC)
        ttk.Label(header, text="Render style", style="Bold.TLabel").pack(side="left")
        ttk.Combobox(header, textvariable=self.style_var, values=list(self.styles_map.keys()),
                     state="readonly", width=30, style="Compact.TCombobox").pack(side="left", padx=(8,0))

        sec_id = tk.LabelFrame(self.frame, text="Identity", bg=WHITE); sec_id.pack(fill="x", pady=PADY_SEC)
        grid_id = self._make_grid(sec_id); grid_id.pack(fill="x")
        self._add_single_row(grid_id, "Species", SPECIES, "Species", width=24)
        self._add_single_row(grid_id, "Size class", SIZE_CLASS, "Size class", width=18)
        self._add_single_row(grid_id, "Temperament", TEMPER, "Temperament", width=20)

        sec_an = tk.LabelFrame(self.frame, text="Anatomy & Abilities", bg=WHITE); sec_an.pack(fill="x", pady=PADY_SEC)
        row_an = tk.Frame(sec_an, bg=WHITE); row_an.pack(fill="x")
        for i in range(3): row_an.grid_columnconfigure(i, weight=1, uniform="anrow")
        self._add_multi_block(row_an, "Anatomy", ANATOMY, "Anatomy", columns=2, grid=True, grid_rc=(0,0))
        self._add_multi_block(row_an, "Locomotion", LOCOMOTION, "Locomotion", columns=1, grid=True, grid_rc=(0,1))
        self._add_multi_block(row_an, "Behaviors / Powers", BEHAVIOR, "Behaviors", columns=2, grid=True, grid_rc=(0,2))

        sec_color = tk.LabelFrame(self.frame, text="Colors & Look (optional)", bg=WHITE); sec_color.pack(fill="x", pady=PADY_SEC)
        grid_col = self._make_grid(sec_color); grid_col.pack(fill="x")
        self._add_single_row(grid_col, "Dominant color", COLORS, "Dominant color", width=18)
        self._add_single_row(grid_col, "Secondary color", COLORS, "Secondary color", width=18)

        sec_scene = tk.LabelFrame(self.frame, text="Scene & Framing", bg=WHITE); sec_scene.pack(fill="x", pady=PADY_SEC)
        grid_sc = self._make_grid(sec_scene); grid_sc.pack(fill="x")
        self._add_single_row(grid_sc, "Biome / Background", BIOOME, "Background", width=26)
        self._add_single_row(grid_sc, "Lighting", LIGHTING, "Lighting", width=20)
        self._add_single_row(grid_sc, "Pose / Action", POSES, "Pose", width=22)
        self._add_single_row(grid_sc, "Framing", FRAMING, "Framing", width=22)
        ttk.Checkbutton(sec_scene, text="Inject motion (debris, dust, water spray, cloth)", variable=self.energy_var).pack(anchor="w", padx=6, pady=(2,0))

        btns = tk.Frame(self.frame, bg=WHITE); btns.pack(pady=(6,4))
        ttk.Button(btns, text="🧟 Generate monster prompt", command=self.generate_prompt).pack(side="left", padx=6)
        ttk.Button(btns, text="📋 Copy", command=self.open_copy).pack(side="left", padx=6)
        if self.prompt_bus:
            ttk.Button(btns, text="➕ Add to Group", command=self.add_to_group).pack(side="left", padx=6)

        self.output = tk.Text(self.frame, height=8, wrap="word", bg=WHITE)
        self.output.pack(fill="both", expand=True, padx=6, pady=(2,8))

    # ---- data helpers ----
    def get_single_choice(self, key):
        var, other = self.single_vars.get(key, (None, None))
        if not var: return None
        txt = other.get().strip()
        if txt: return txt
        v = var.get()
        return None if v.startswith("—") else v

    def gather_multi(self, key):
        block = self.multi_blocks.get(key)
        if not block: return []
        vals = [opt for opt, var in block["items"] if var.get()]
        vals += parse_custom_list(block["other_var"].get())
        return [v for v in vals if v]

    # ---- prompt ----
    def build_monster_lines(self):
        intro = self.styles_map.get(self.style_var.get(), next(iter(self.styles_map.values())))
        lines = [intro]

        sp = self.get_single_choice("Species")
        size = self.get_single_choice("Size class")
        temp = self.get_single_choice("Temperament")
        parts = [sp, size, temp]
        lines.append("Monster: " + ", ".join([p for p in parts if p]) + ".")

        ana = self.gather_multi("Anatomy")
        loco = self.gather_multi("Locomotion")
        beh  = self.gather_multi("Behaviors")
        if ana:  lines.append(f"Anatomy: {', '.join(ana)}.")
        if loco: lines.append(f"Locomotion: {', '.join(loco)}.")
        if beh:  lines.append(f"Behaviors and powers: {', '.join(beh)}.")

        # colors
        dom = self.get_single_choice("Dominant color")
        sec = self.get_single_choice("Secondary color")
        cols = []
        if dom: cols.append(f"dominant — {dom}")
        if sec: cols.append(f"secondary — {sec}")
        if cols:
            if "black-and-white" in intro.lower() or "monochrome" in intro.lower():
                lines.append("Color cues (for tonal accents): " + "; ".join(cols) + ".")
            else:
                lines.append("Color palette: " + "; ".join(cols) + ".")

        bg  = self.get_single_choice("Background")
        lit = self.get_single_choice("Lighting")
        pose= self.get_single_choice("Pose")
        frm = self.get_single_choice("Framing")
        if bg:   lines.append(f"Background: {bg}.")
        if lit:  lines.append(f"Lighting: {lit}.")
        if pose: lines.append(f"Pose: {pose}.")
        if frm:  lines.append(f"Shown from {frm}.")

        if self.energy_var.get():
            lines.append("Add motion cues: debris, dust, splashes or drifting particles appropriate to the biome.")

        return lines

    # ---- actions ----
    def generate_prompt(self):
        text = " ".join(self.build_monster_lines())
        self._last_prompt = text
        self.output.delete("1.0","end")
        self.output.insert("1.0", text)

    def build_label(self):
        return self.get_single_choice("Species") or "Monster"

    def add_to_group(self):
        if not self._last_prompt.strip():
            messagebox.showwarning("No prompt", "Generate a monster prompt first.")
            return
        try:
            label = self.build_label()
            self.prompt_bus.add_monster(label, self._last_prompt, weight=3)
            messagebox.showinfo("Added", f"Monster added to Group:\n{label}")
        except RuntimeError as e:
            messagebox.showerror("Roster full", str(e))

    def open_copy(self):
        txt = self.output.get("1.0","end-1c").strip()
        if not txt:
            messagebox.showwarning("No prompt", "Generate the monster prompt first.")
            return
        win = tk.Toplevel(self.frame); win.title("Copy"); win.configure(bg=WHITE); win.geometry("760x420")
        t = tk.Text(win, wrap="word", bg=WHITE); t.pack(fill="both", expand=True, padx=8, pady=8)
        t.insert("1.0", txt); t.focus_set(); t.tag_add("sel","1.0","end")
        ttk.Button(win, text="Copy to clipboard",
                   command=lambda: (self.frame.clipboard_clear(), self.frame.clipboard_append(t.get("1.0","end-1c")),
                                    messagebox.showinfo("Copied","Monster prompt copied."))).pack(pady=6)

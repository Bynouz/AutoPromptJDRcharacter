import tkinter as tk
from tkinter import messagebox
import unicodedata

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

class MonsterForm:
    def __init__(self, parent, styles_map, prompt_bus=None):
        self.styles_map = styles_map
        self.prompt_bus = prompt_bus
        self._last_prompt = ""
        self.frame = tk.Frame(parent)

        tk.Label(self.frame, text="Render style", font=("Arial",10,"bold")).pack(anchor="w", padx=10, pady=(8,0))
        self.style_var = tk.StringVar(value=list(styles_map.keys())[0])
        tk.OptionMenu(self.frame, self.style_var, *styles_map.keys()).pack(anchor="w", padx=20, pady=(0,8))

        box = tk.Frame(self.frame); box.pack(anchor="w", fill="x", padx=10, pady=(0,6))
        tk.Label(box, text="Count", font=("Arial",10,"bold")).pack(side="left")
        self.count_var = tk.IntVar(value=1); tk.Spinbox(box, from_=1, to=50, textvariable=self.count_var, width=5).pack(side="left", padx=8)
        self.horde_var = tk.BooleanVar(value=False); tk.Checkbutton(box, text="Horde (single scene)", variable=self.horde_var).pack(side="left", padx=12)

        self.singles = {
            "Creature Type": sorted_en(["Aberration","Beast","Demon","Devil","Dragon","Elemental","Fey","Giant","Horror","Undead","Plant","Ooze","Insectoid","Aquatic","Celestial","Nightmare","Construct","Lycanthrope"]),
            "Size": ["Tiny","Small","Medium","Large","Huge","Gargantuan"],
            "Biome / Environment": sorted_en(["Forest","Jungle","Swamp","Desert","Tundra","Mountains","Underground","Coast/Sea","Cave","Ruins","Sewers","Volcanic","Sky/Aerial","Shadowfell","Feywild","Ruined Temple"]),
            "Behavior": sorted_en(["Aggressive","Ambush","Pack Hunter","Territorial","Guardian","Parasitic","Stalker","Apex Predator"]),
            "Threat Level": ["Low","Moderate","High","Deadly","Apocalyptic"],
            "Background / Ambience": sorted_en(["Dark Lab","Shadowy Forest","Foggy Graveyard","Collapsed Cathedral","Ritual Chamber","Ancient Ruins","Sewers","Swamp","Desert","Tundra","Volcano","Dungeon","Cave","Nocturnal Plains"])
        }
        self.single_vars = {}
        sblock = tk.LabelFrame(self.frame, text="Primary descriptors", font=("Arial",10,"bold"))
        sblock.pack(anchor="w", fill="x", padx=10, pady=6)
        for cat, opts in self.singles.items():
            cell = tk.Frame(sblock); cell.pack(anchor="w", fill="x", pady=4)
            tk.Label(cell, text=cat, font=("Arial",10,"bold")).pack(anchor="w")
            var = tk.StringVar(value="— (leave empty) —")
            tk.OptionMenu(cell, var, "— (leave empty) —", *opts).pack(anchor="w", fill="x", pady=(2,2))
            other = tk.StringVar(); tk.Entry(cell, textvariable=other).pack(fill="x")
            tk.Label(cell, text="Other (free text)", fg="#666").pack(anchor="w")
            self.single_vars[cat] = (var, other)

        self.multis = {
            "Anatomy / Morphology": sorted_en(["Horns","Tusks","Fangs","Claws","Wings","Tail","Carapace","Chitin","Tentacles","Multiple Eyes","Extra Limbs","Spines","Bioluminescent","Crystals","Bone Plates","Barbed"]),
            "Surface / Texture": sorted_en(["Scaly","Slimy","Furry","Shadowy","Translucent","Smoky","Charred","Frozen","Rocky","Liquid","Putrid","Skeletal","Moldy"]),
            "Abilities / Attacks": sorted_en(["Poison","Acid","Fire Breath","Frost Breath","Lightning","Necrotic Aura","Psychic Scream","Web/Entangle","Burrowing","Flight/Glide","Regeneration","Invisibility","Camouflage","Shadow Step"])
        }
        self.multi_blocks = {}
        for cat, opts in self.multis.items():
            block = tk.LabelFrame(self.frame, text=cat, font=("Arial",10,"bold"))
            block.pack(anchor="w", fill="x", padx=10, pady=6)
            vars_ = []
            for o in opts:
                v = tk.BooleanVar(); tk.Checkbutton(block, text=o, variable=v, anchor="w").pack(anchor="w"); vars_.append((o,v))
            other = tk.StringVar(); bottom = tk.Frame(block); bottom.grid_columnconfigure(0, weight=1)
            tk.Entry(bottom, textvariable=other).grid(row=0, column=0, sticky="ew", padx=8, pady=(8,4))
            tk.Label(bottom, text="Other (comma separated)", fg="#666").grid(row=1, column=0, sticky="w", padx=8, pady=(0,6))
            bottom.pack(fill="x"); self.multi_blocks[cat] = {"items": vars_, "other_var": other}

        self.cadrage_opts = sorted_en(["Head Only","Bust","Chest-up","Half Body","Full Body","Three-Quarter View","Profile View","Front View","Back View","Slight High Angle","Low Angle","Over-the-Shoulder","Includes mouth and jaw"])
        self.cadr_vars = []
        cblock = tk.LabelFrame(self.frame, text="Framing", font=("Arial",10,"bold")); cblock.pack(anchor="w", fill="x", padx=10, pady=6)
        for c in self.cadrage_opts:
            v = tk.BooleanVar(); tk.Checkbutton(cblock, text=c, variable=v, anchor="w").pack(anchor="w"); self.cadr_vars.append((c,v))
        self.cadr_other = tk.StringVar(); cbottom = tk.Frame(cblock); cbottom.grid_columnconfigure(0, weight=1)
        tk.Entry(cbottom, textvariable=self.cadr_other).grid(row=0, column=0, sticky="ew", padx=8, pady=(8,4))
        tk.Label(cbottom, text="Other framing (commas)", fg="#666").grid(row=1, column=0, sticky="w", padx=8, pady=(0,6))
        cbottom.pack(fill="x")

        btns = tk.Frame(self.frame); btns.pack(pady=10)
        tk.Button(btns, text="🎨 Generate", command=self.generate).pack(side="left", padx=6)
        tk.Button(btns, text="📋 Copy window", command=self.copy_win).pack(side="left", padx=6)
        if self.prompt_bus:
            tk.Button(btns, text="➕ Add to Group", command=self.add_to_group).pack(side="left", padx=6)

        self.out = tk.Text(self.frame, height=8, wrap="word"); self.out.pack(padx=10, pady=10, fill="both", expand=True)

    def _get_single(self, cat):
        pair = self.single_vars.get(cat)
        if not pair: return None
        var, other = pair
        o = other.get().strip()
        if o: return o
        v = var.get()
        return None if v.startswith("—") else v
    def _gather_multi(self, cat):
        data = self.multi_blocks.get(cat)
        if not data: return []
        vals = [k for k,v in data["items"] if v.get()]
        vals += parse_custom_list(data["other_var"].get())
        return [x for x in vals if x]
    def _gather_cadr(self):
        vals = [k for k,v in self.cadr_vars if v.get()]
        vals += parse_custom_list(self.cadr_other.get())
        return [x for x in vals if x]

    def _build_monster_lines(self):
        intro = self.styles_map.get(self.style_var.get(), next(iter(self.styles_map.values())))
        lines = [intro]
        typ=self._get_single("Creature Type"); size=self._get_single("Size"); biome=self._get_single("Biome / Environment")
        behav=self._get_single("Behavior"); threat=self._get_single("Threat Level"); bg=self._get_single("Background / Ambience")
        parts=[]; 
        if typ: parts.append(typ)
        if size: parts.append(size)
        if biome: parts.append(f"from a {biome} biome")
        lines.append(f"A monstrous creature: {', '.join(parts)}." if parts else "A monstrous creature.")
        anatomy=self._gather_multi("Anatomy / Morphology"); surface=self._gather_multi("Surface / Texture"); abil=self._gather_multi("Abilities / Attacks")
        if anatomy: lines.append(f"Anatomy/features: {', '.join(anatomy)}.")
        if surface: lines.append(f"Surface/texture: {', '.join(surface)}.")
        if behav: lines.append(f"Behavior: {behav}.")
        if abil: lines.append(f"Abilities/attacks: {', '.join(abil)}.")
        if threat: lines.append(f"Overall threat level: {threat}.")
        if bg: lines.append(f"Set against a {bg} background.")
        cadr=self._gather_cadr()
        if cadr: lines.append(f"Shown from {', '.join(cadr)}.")
        return lines

    def generate(self):
        n=max(1,int(self.count_var.get()))
        if self.horde_var.get() and n>1:
            lines=self._build_monster_lines(); lines.append(f"Depict a horde of approximately {n} creatures, with size and detail variation.")
            txt=" ".join(lines)
        else:
            base=self._build_monster_lines(); txt="\n\n---\n\n".join([f"[Monster {i}] "+" ".join(base) for i in range(1,n+1)])
        self._last_prompt = txt
        self.out.delete("1.0", tk.END); self.out.insert(tk.END, txt)

    def build_label(self):
        typ = self._get_single("Creature Type") or "Creature"
        size = self._get_single("Size")
        return f"{typ}{' ('+size+')' if size else ''}"

    def add_to_group(self):
        if not self._last_prompt.strip():
            messagebox.showwarning("No prompt","Generate a monster prompt first."); return
        try:
            label = self.build_label()
            self.prompt_bus.add_monster(label, self._last_prompt, weight=3)
            messagebox.showinfo("Added", f"Monster added to Group:\n{label}")
        except RuntimeError as e:
            messagebox.showerror("Roster full", str(e))

    def copy_win(self):
        txt=self.out.get("1.0","end-1c").strip()
        if not txt: messagebox.showwarning("No prompt","Generate a prompt before opening the copy window."); return
        win=tk.Toplevel(self.frame); win.title("Copy"); win.geometry("760x420")
        t=tk.Text(win, wrap="word"); t.pack(fill="both", expand=True, padx=10, pady=10)
        t.insert("1.0", txt); t.focus_set(); t.tag_add("sel","1.0","end")
        tk.Button(win,text="Copy to clipboard",
                  command=lambda:(self.frame.clipboard_clear(), self.frame.clipboard_append(t.get("1.0","end-1c")),
                                  messagebox.showinfo("Copied","Prompt copied to clipboard."))).pack(pady=6)

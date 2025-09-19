import tkinter as tk
from tkinter import messagebox, ttk
import unicodedata, math, random, traceback

# ---------------- utilities ----------------
def unaccent(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if not unicodedata.combining(ch))

def sorted_en(items):
    return sorted(items, key=lambda s: unaccent(s).lower())

def parse_custom_list(text: str):
    if not text:
        return []
    out = []
    for token in text.replace(";", ",").replace("\n", ",").split(","):
        t = token.strip()
        if t:
            out.append(t)
    return out

# ---------------- scrollable frame ----------------
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
        self.interior.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self._bind_mousewheel(self.canvas)

    def _on_content_configure(self, _e=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self.canvas.itemconfig(self._win_id, width=e.width)

    def _bind_mousewheel(self, widget):
        widget.bind_all("<MouseWheel>", self._on_mousewheel, add="+")   # Windows/macOS
        widget.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"), add="+")  # Linux
        widget.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"), add="+")

    def _on_mousewheel(self, event):
        move = -1 if getattr(event, "delta", 0) > 0 else 1
        self.canvas.yview_scroll(move, "units")

# ---------------- race presets ----------------
RACE_PRESETS = {
    "Human": {
        "lines": ["Neutral human craniofacial proportions; subtle asymmetry; natural pores and minor blemishes."],
        "avoid": ""
    },
    "Elf": {
        "lines": ["Long pointed ears clearly visible; slender angular features, high cheekbones, almond-shaped eyes; fine smooth hair."],
        "avoid": "Avoid human round ears and heavy jaw."
    },
    "Dark Elf": {
        "lines": ["Long pointed ears; onyx/dark skin values rendered in grayscale; white or silver hair; luminous eyes (light or pale)."],
        "avoid": "Avoid tan human skin and short rounded ears."
    },
    "High Elf": {
        "lines": ["Long pointed ears; elegant, refined features; luminous pale or golden skin values (grayscale rendition)."],
        "avoid": "Avoid coarse human jaw and small ears."
    },
    "Half-Elf": {
        "lines": ["Subtle short pointed ears; blend of human and elven features; slightly angular cheekbones with softer jawline."],
        "avoid": "Avoid fully human ears or full-length elven ears."
    },
    "Kobold": {
        "lines": ["Small draconic/reptilian head; slender muzzle; small horns or head spines; scaled skin; slit pupils."],
        "avoid": "Avoid human nose and lips."
    },
    "Goblin": {
        "lines": ["Large expressive ears; long hooked or bulbous nose; sharp teeth; wiry features; mischievous, sinewy face."],
        "avoid": "Avoid elven elegance and human beauty portrait."
    },
    "Tiefling": {
        "lines": ["Prominent horns (shape can vary); slight fangs; narrow pupils; subtle tail implied; unusual skin values interpreted in grayscale."],
        "avoid": "Avoid human ears without horns."
    },
    "Orc": {
        "lines": ["Large lower tusks clearly visible; massive jaw; heavy brow ridge; broad flat nose; rough textured skin, visible pores and scars."],
        "avoid": "Avoid human or elven facial proportions, no delicate beauty look."
    },
    "Half-Orc": {
        "lines": ["Small lower tusks clearly visible; pronounced jawline; heavy brow ridge; broad nose; slightly pointed ears; rough textured skin.",
                  "Olive/ashen grey-green skin tone (rendered in grayscale)."],
        "avoid": "Avoid human or elven facial proportions, no delicate beauty look."
    },
    "Undead": {
        "lines": ["Gaunt, sunken features; desaturated mottled skin; visible bone hints or tendon shadows; cracked lips; cold dead gaze."],
        "avoid": "Avoid warm healthy skin and lively eyes."
    },
    "Vampire": {
        "lines": ["Very pale skin; elongated upper fangs; sharp elegant features with predatory undertone; subtle under-eye darkness."],
        "avoid": "Avoid tanned skin and daylight cues."
    },
    "Dhampir": {
        "lines": ["Alive yet pale; short fangs visible only when lips part; subtly predatory eyes; mix of human vitality and vampiric elegance."],
        "avoid": "Avoid full vampire gauntness or human warmth only."
    },
    "Fae": {
        "lines": ["Ethereal delicate features; slightly otherworldly eyes; faint freckles or leaf-like motifs; hair with airy flow."],
        "avoid": "Avoid heavy human jaw or brutish orcish traits."
    },
    "Golem": {
        "lines": ["Material body (stone/metal/clay/wood); carved seams and runic cracks; joints implied by plates; non-fleshy surface."],
        "avoid": "Avoid soft human skin and pores."
    },
    "Dwarf": {
        "lines": ["Broad face; prominent nose; thick neck; heavy brow; full beard or stout facial hair texture."],
        "avoid": "Avoid slender elven proportions."
    },
    "Gnome": {
        "lines": ["Small round face; button nose; lively eyes; fine short beard or whiskers optional; playful expression lines."],
        "avoid": "Avoid tall elongated elven features."
    },
    "Halfling": {
        "lines": ["Soft round features; gentle nose; curly hair texture; warm approachable expression lines."],
        "avoid": "Avoid elven long ears and orcish tusks."
    },
    "Dragonborn": {
        "lines": ["Draconic head with muzzle; layered scales; visible horn ridges or frills; slit or reptilian pupils; no human nose or lips."],
        "avoid": "Avoid human facial structure."
    },
    "Aasimar": {
        "lines": ["Subtle halo or radiant rim light; serene noble features; faint luminous skin values (grayscale glow)."],
        "avoid": ""
    },
    "Werewolf": {
        "lines": ["Lupine muzzle; layered fur; bestial ears; elongated canines; transitioning anatomy across cheeks and brow."],
        "avoid": "Avoid clean human facial features."
    },
    "Lycanthrope": {
        "lines": ["Hybrid bestial traits (wolf/bear/boar variation); coarse fur; pronounced muzzle; predatory eyes; visible fangs."],
        "avoid": "Avoid neat human portrait proportions."
    },
    "Demon": {
        "lines": ["Horns; ridged or scarred skin; predatory teeth; infernal eyes; smoke/soot patina on skin (grayscale)."],
        "avoid": "Avoid cute human look."
    },
    "Angel": {
        "lines": ["Subtle halo; soft yet defined features; feather textures implied on shoulders or edges; luminous highlights."],
        "avoid": ""
    },
    "Lizardfolk": {
        "lines": ["Reptilian head; scales of varied size; broad jaw; slit pupils; small cranial frill or spines."],
        "avoid": "Avoid human nose/lips and round ears."
    },
    "Satyr": {
        "lines": ["Goat-like curled horns; pointed ears; playful, sly expression; faint fur texture at jawline/temples."],
        "avoid": ""
    },
    "Minotaur": {
        "lines": ["Bovine head; large horns; strong muzzle; short fur; heavy neck musculature."],
        "avoid": "Avoid human/elf hints."
    },
    "Triton": {
        "lines": ["Aquatic facial traits; finned ears or cheek fins; wet sheen highlights; subtle scales or gill lines."],
        "avoid": "Avoid dry human skin."
    },
    "Giant": {
        "lines": ["Massive craniofacial proportions; heavy bone structure; thick neck; oversized features emphasized by lighting."],
        "avoid": ""
    },
}

# ---------------- Character form ----------------
class CharacterForm:
    def __init__(self, parent, styles_map, title_text=None, columns_mode=True):
        self.styles_map = styles_map
        self.columns_mode = columns_mode
        self.frame = tk.LabelFrame(parent, text=title_text or "Character settings", font=("Arial", 10, "bold"))
        self.style_var = tk.StringVar(value=list(styles_map.keys())[0])

        # categories
        self.single_categories = {
            "Race": sorted_en(list(RACE_PRESETS.keys())),
            "Gender": sorted_en(["Male", "Female", "Androgynous", "Unknown"]),
            "Role / Class": sorted_en(["Alchemist","Apothecary","Archer","Artificer","Assassin","Barbarian","Bard",
                                       "Berserker","Captain","Cleric","Commander","Commoner","Criminal","Cultist",
                                       "Druid","Engineer","Hunter","Inquisitor","Knight","Mage","Merchant",
                                       "Monk","Necromancer","Noble","Occultist","Paladin","Pirate","Priest",
                                       "Ranger","Rogue","Scholar","Seer","Soldier","Sorcerer","Witch"]),
            "Age": ["Childlike","Teenager","Young Adult","Adult","Mature (50-60)","Elderly (70+)","Ageless"],
            "Facial Expression": sorted_en(["Calm","Compassionate","Confident","Cruel","Desperate","Determined","Angry",
                                            "Playful","Frightened","Feral","Proud","Cold","Haunted","Worried","Mischievous",
                                            "Wary","Mocking","Thoughtful","Wrinkled","Brooding","Smiling","Stoic","Stern",
                                            "Sad","Hollow-eyed","Tired"]),
            "Background / Ambience": sorted_en(["Dark Lab","Shadowy Forest","Foggy Graveyard","Collapsed Cathedral",
                                                "Ritual Chamber","Broken Throne Room","Sewer Tunnel","Underground Market",
                                                "City Alley","Ruined Battlefield","Torch-lit Dungeon","Alchemist Explosion",
                                                "Moonlit Rooftop","Plain Dark Background","Stone Wall","Cave","Library",
                                                "Workshop","Market","Temple","Throne Room","Forest Clearing","Snowy Landscape",
                                                "Desert Dunes","Rainy Street","Cliff Edge","Mountain Pass","Night Seashore",
                                                "Laboratory","Dungeon","Ancient Ruins"])
        }
        self.multi_categories = {
            "Hair / Beard": sorted_en(["Long and Braided","Short and Military","Messy and Burnt","Tied in a Bun","Shaved","Half Bald",
                                       "Horned","Matted","No Beard","Goatee","Mustache Only","Thick Beard","Hooded",
                                       "Long Hair","Short Hair","Curly Hair","Wavy Hair","Straight Hair","Ponytail",
                                       "Multiple Braids","White Streak","Graying Temples","Stubble Beard","Groomed Beard","Sideburns"]),
            "Notable Traits": sorted_en([
                "Heterochromia","Scar","Missing Eye","Burn Marks","Soot-covered","Blood Spatter","Veins Visible",
                "Runes Etched in Skin","Cracked Skin","Blindfolded","Blind Eye","Skeletal Features","Tattooed Face",
                "Facial Piercings","Tattoos","Multiple Scars","Pale Skin","Dried Blood","Glowing Eyes","Tribal Markings",
                "Facial Jewelry","Multiple Ear Rings",
                # orcish markers
                "Small lower tusks clearly visible","Pronounced jawline","Heavy brow ridge","Broad nose",
                "Slightly pointed ears","Rough textured skin with visible pores",
                "Mouth slightly open, lower tusks visible",
            ]),
            "Clothing / Armor": sorted_en(["Victorian Jacket","Surgical Coat","Plague Doctor Outfit","Tattered Cloak",
                                           "Engraved Plate Armor","Runed Robes","Scorched Leather Armor","Merchant's Vest",
                                           "Heavy Fur Coat","Tactical Gear","Military Uniform","Embroidered Ritual Garb",
                                           "Simple Tunic","Hooded Cloak","Cloak","Leather Armor","Chainmail","Plate Armor",
                                           "Robes","Tattered Robes","Rags","Noble Attire","Commoner's Clothes","Long Coat",
                                           "Leather Gloves","High Boots","Hood","Apron","Alchemist's Coat"]),
            "Accessories": sorted_en(["Flask","Beaker","Smoking Pipe","Ancient Book","Mechanical Eye","Ring","Amulet","Skull","Dagger",
                                      "Staff","Cane","Scroll","Crystal Ball","Chain","Broken Mask","Medal","Exploding Vial",
                                      "Belt Pouch","Pouches","Necklace","Earrings","Bracelets","Gloves","Lantern","Torch",
                                      "Coiled Rope","Satchel","Backpack","Quiver","Bow","Crossbow","Sword","Shield","Axe",
                                      "Mace","Spear","Crown","Diadem","Mechanical Gauntlet","Keys","Vials","Bottle","Jeweled Ring"]),
            "Framing": sorted_en(["Head Only","Bust","Chest-up","Half Body","Square Portrait","Tight Portrait","Asymmetrical Frame",
                                  "Medium Long Shot","Full Body","Three-Quarter View","Profile View","Front View","Back View",
                                  "Slight High Angle","Low Angle","Over-the-Shoulder","Includes mouth and jaw"])
        }

        self._race_auto_lines = []
        self._race_avoid_line = ""

        self._build_ui()

    def _build_ui(self):
        tk.Label(self.frame, text="Render style", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(8,0))
        tk.OptionMenu(self.frame, self.style_var, *self.styles_map.keys()).pack(anchor="w", padx=20, pady=(0,8))

        self.single_vars = {}
        self.single_block = tk.LabelFrame(self.frame, text="Main characteristics", font=("Arial", 10, "bold"))
        self.single_block.pack(anchor="w", fill="x", padx=10, pady=6)
        self._single_cells = []

        for cat, options in self.single_categories.items():
            cell = tk.Frame(self.single_block)
            tk.Label(cell, text=cat, font=("Arial", 10, "bold"), anchor="w").pack(anchor="w")
            var = tk.StringVar(value="— (leave empty) —")
            if cat == "Race":
                # FIX: capture the right variable for this cell
                var.trace_add("write", lambda *_a, v=var: self._apply_race_preset(v.get()))
            tk.OptionMenu(cell, var, "— (leave empty) —", *options).pack(fill="x", pady=(2,2))
            other = tk.StringVar()
            tk.Entry(cell, textvariable=other).pack(fill="x")
            tk.Label(cell, text="Other (free text)", fg="#666").pack(anchor="w")
            self.single_vars[cat] = (var, other)
            self._single_cells.append(cell)

            if cat == "Race":
                self.race_hint = tk.Label(cell, text="", fg="#666", wraplength=420, justify="left")
                self.race_hint.pack(anchor="w", pady=(6,0))

        self.check_blocks = {}
        for category, options in self.multi_categories.items():
            block = tk.LabelFrame(self.frame, text=category, font=("Arial", 10, "bold"))
            block.pack(anchor="w", fill="x", padx=10, pady=6)
            items, labels = [], []
            for opt in options:
                v = tk.BooleanVar()
                cb = tk.Checkbutton(block, text=opt, variable=v, anchor="w", justify="left")
                labels.append(cb); items.append((opt, v))
            bottom = tk.Frame(block); other_var = tk.StringVar()
            ent = tk.Entry(bottom, textvariable=other_var); lab = tk.Label(bottom, text="Other (comma separated)", fg="#666")
            bottom.grid_columnconfigure(0, weight=1)
            ent.grid(row=0, column=0, sticky="ew", padx=8, pady=(8,4))
            lab.grid(row=1, column=0, sticky="w", padx=8, pady=(0,6))
            self.check_blocks[category] = {"frame": block, "labels": labels, "items": items, "bottom": bottom, "other_var": other_var}

        tk.Button(self.frame, text="🎨 Generate prompt", command=self.generate_prompt).pack(pady=10)
        self.output = tk.Text(self.frame, height=8, wrap="word")
        self.output.pack(padx=10, pady=10, fill="both", expand=True)
        tk.Button(self.frame, text="📋 Copy window", command=self.open_copy_window).pack(pady=(0,10))

        self._last_cols = None
        self.frame.bind("<Configure>", self._on_resize)
        self._relayout()

    def _apply_race_preset(self, race_value: str):
        if race_value.startswith("—"):
            self._race_auto_lines = []; self._race_avoid_line = ""
            self.race_hint.configure(text="")
            return
        preset = RACE_PRESETS.get(race_value)
        if preset:
            self._race_auto_lines = list(preset.get("lines", []))
            self._race_avoid_line = preset.get("avoid", "")
            hint = "Race preset added: " + " ".join(self._race_auto_lines)
            if self._race_avoid_line:
                hint += f"  [Avoid: {self._race_avoid_line}]"
            self.race_hint.configure(text=hint)
        else:
            self._race_auto_lines = []; self._race_avoid_line = ""
            self.race_hint.configure(text="")

    def _columns_for_width(self, w):
        if not self.columns_mode:
            return 1
        if w < 520: return 1
        if w < 760: return 2
        if w < 1000: return 3
        if w < 1240: return 4
        return 5

    def _relayout(self):
        w = self.frame.winfo_width() or 1000
        cols = self._columns_for_width(w)
        if cols == self._last_cols: return
        self._last_cols = cols
        for wdg in self.single_block.grid_slaves(): wdg.grid_forget()
        n = len(self._single_cells)
        rows = max(1, math.ceil(n/cols))
        for i, cell in enumerate(self._single_cells):
            r, c = i % rows, i // rows
            self.single_block.grid_columnconfigure(c, weight=1, uniform="singcols")
            cell.grid(row=r, column=c, sticky="nsew", padx=8, pady=6)
        for cat, data in self.check_blocks.items():
            block = data["frame"]; labels = data["labels"]; bottom = data["bottom"]
            for wdg in block.grid_slaves(): wdg.grid_forget()
            rows = max(1, math.ceil(len(labels)/cols))
            for c in range(cols):
                block.grid_columnconfigure(c, weight=1, uniform=f"{cat}_cols")
            for idx, cb in enumerate(labels):
                r, c = idx % rows, idx // rows
                cb.grid(row=r, column=c, sticky="w", padx=8, pady=2)
            bottom.grid(row=rows, column=0, columnspan=cols, sticky="ew")

    def _on_resize(self, _e=None): self._relayout()

    def get_single_choice(self, cat):
        var, other = self.single_vars[cat]
        txt = other.get().strip()
        if txt: return txt
        v = var.get()
        return None if v.startswith("—") else v

    def gather_multi(self, cat):
        vals = [opt for opt, var in self.check_blocks[cat]["items"] if var.get()]
        vals += parse_custom_list(self.check_blocks[cat]["other_var"].get())
        return [v for v in vals if v]

    def build_character_lines(self):
        intro = self.styles_map.get(self.style_var.get(), next(iter(self.styles_map.values())))
        lines = [intro]

        race = self.get_single_choice("Race")
        gender = self.get_single_choice("Gender")
        role   = self.get_single_choice("Role / Class")

        # Robustness: ensure race preset is applied even if trace didn't fire
        if race:
            self._apply_race_preset(race)

        parts = [x for x in [race, gender, role] if x]
        lines.append(f"The subject is a {' '.join(parts)}." if parts else "The subject is a character.")

        if self._race_auto_lines:
            lines.extend(self._race_auto_lines)

        age = self.get_single_choice("Age")
        expr= self.get_single_choice("Facial Expression")
        segs=[]
        if age: segs.append(f"approximately {age}")
        if expr: segs.append(f"with {expr}")
        if segs: lines.append(", ".join(segs) + ".")

        traits = self.gather_multi("Notable Traits")
        if traits: lines.append(f"Notable features include {', '.join(traits)}.")
        hair = self.gather_multi("Hair / Beard")
        if hair: lines.append(f"Their {', '.join(hair)} adds character to their appearance.")
        clothes = self.gather_multi("Clothing / Armor")
        acc     = self.gather_multi("Accessories")
        if clothes and acc: lines.append(f"They wear {', '.join(clothes)}, along with {', '.join(acc)}.")
        elif clothes:       lines.append(f"They wear {', '.join(clothes)}.")
        elif acc:           lines.append(f"They carry {', '.join(acc)}.")
        bg = self.get_single_choice("Background / Ambience")
        if bg: lines.append(f"The scene is set against a {bg} background.")
        cadr = self.gather_multi("Framing")
        if cadr: lines.append(f"Shown from {', '.join(cadr)}.")
        if self._race_avoid_line:
            lines.append(f"Avoid: {self._race_avoid_line}")
        return lines

    def generate_prompt(self):
        text = " ".join(self.build_character_lines())
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)

    def open_copy_window(self):
        txt = self.output.get("1.0","end-1c").strip()
        if not txt:
            messagebox.showwarning("No prompt", "Generate a prompt before opening the copy window.")
            return
        win = tk.Toplevel(self.frame); win.title("Copy"); win.geometry("760x420")
        t = tk.Text(win, wrap="word"); t.pack(fill="both", expand=True, padx=10, pady=10)
        t.insert("1.0", txt); t.focus_set(); t.tag_add("sel","1.0","end")
        tk.Button(win, text="Copy to clipboard",
                  command=lambda: (self.frame.clipboard_clear(), self.frame.clipboard_append(t.get("1.0","end-1c")),
                                   messagebox.showinfo("Copied","Prompt copied to clipboard."))).pack(pady=6)

# ---------------- Monster form (English) ----------------
class MonsterForm:
    def __init__(self, parent, styles_map):
        self.styles_map = styles_map
        self.frame = tk.Frame(parent)

        tk.Label(self.frame, text="Render style", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(8, 0))
        self.style_var = tk.StringVar(value=list(styles_map.keys())[0])
        tk.OptionMenu(self.frame, self.style_var, *styles_map.keys()).pack(anchor="w", padx=20, pady=(0, 8))

        box = tk.Frame(self.frame); box.pack(anchor="w", fill="x", padx=10, pady=(0,6))
        tk.Label(box, text="Count", font=("Arial", 10, "bold")).pack(side="left")
        self.count_var = tk.IntVar(value=1)
        tk.Spinbox(box, from_=1, to=50, textvariable=self.count_var, width=5).pack(side="left", padx=8)
        self.horde_var = tk.BooleanVar(value=False)
        tk.Checkbutton(box, text="Horde (single scene)", variable=self.horde_var).pack(side="left", padx=12)

        self.singles = {
            "Creature Type": sorted_en(["Aberration","Beast","Demon","Devil","Dragon","Elemental","Fey","Giant",
                                        "Horror","Undead","Plant","Ooze","Insectoid","Aquatic","Celestial","Nightmare",
                                        "Construct","Lycanthrope"]),
            "Size": ["Tiny","Small","Medium","Large","Huge","Gargantuan"],
            "Biome / Environment": sorted_en(["Forest","Jungle","Swamp","Desert","Tundra","Mountains","Underground",
                                              "Coast/Sea","Cave","Ruins","Sewers","Volcanic","Sky/Aerial",
                                              "Shadowfell","Feywild","Ruined Temple"]),
            "Behavior": sorted_en(["Aggressive","Ambush","Pack Hunter","Territorial","Guardian","Parasitic","Stalker","Apex Predator"]),
            "Threat Level": ["Low","Moderate","High","Deadly","Apocalyptic"],
            "Background / Ambience": sorted_en(["Dark Lab","Shadowy Forest","Foggy Graveyard","Collapsed Cathedral",
                                                "Ritual Chamber","Ancient Ruins","Sewers","Swamp","Desert","Tundra",
                                                "Volcano","Dungeon","Cave","Nocturnal Plains"])
        }
        self.single_vars = {}
        sblock = tk.LabelFrame(self.frame, text="Primary descriptors", font=("Arial", 10, "bold"))
        sblock.pack(anchor="w", fill="x", padx=10, pady=6)
        for cat, opts in self.singles.items():
            cell = tk.Frame(sblock); cell.pack(anchor="w", fill="x", pady=4)
            tk.Label(cell, text=cat, font=("Arial",10,"bold")).pack(anchor="w")
            var = tk.StringVar(value="— (leave empty) —")
            tk.OptionMenu(cell, var, "— (leave empty) —", *opts).pack(anchor="w", fill="x", pady=(2,2))
            other = tk.StringVar()
            tk.Entry(cell, textvariable=other).pack(fill="x")
            tk.Label(cell, text="Other (free text)", fg="#666").pack(anchor="w")
            self.single_vars[cat] = (var, other)

        self.multis = {
            "Anatomy / Morphology": sorted_en(["Horns","Tusks","Fangs","Claws","Wings","Tail","Carapace","Chitin",
                                               "Tentacles","Multiple Eyes","Extra Limbs","Spines","Bioluminescent",
                                               "Crystals","Bone Plates","Barbed"]),
            "Surface / Texture": sorted_en(["Scaly","Slimy","Furry","Shadowy","Translucent","Smoky","Charred",
                                            "Frozen","Rocky","Liquid","Putrid","Skeletal","Moldy"]),
            "Abilities / Attacks": sorted_en(["Poison","Acid","Fire Breath","Frost Breath","Lightning",
                                              "Necrotic Aura","Psychic Scream","Web/Entangle","Burrowing",
                                              "Flight/Glide","Regeneration","Invisibility","Camouflage","Shadow Step"])
        }
        self.multi_blocks = {}
        for cat, opts in self.multis.items():
            block = tk.LabelFrame(self.frame, text=cat, font=("Arial", 10, "bold"))
            block.pack(anchor="w", fill="x", padx=10, pady=6)
            vars_ = []
            for o in opts:
                v = tk.BooleanVar(); tk.Checkbutton(block, text=o, variable=v, anchor="w").pack(anchor="w")
                vars_.append((o,v))
            other = tk.StringVar()
            bottom = tk.Frame(block); bottom.grid_columnconfigure(0, weight=1)
            tk.Entry(bottom, textvariable=other).grid(row=0, column=0, sticky="ew", padx=8, pady=(8,4))
            tk.Label(bottom, text="Other (comma separated)", fg="#666").grid(row=1, column=0, sticky="w", padx=8, pady=(0,6))
            bottom.pack(fill="x")
            self.multi_blocks[cat] = {"items": vars_, "other_var": other}

        self.cadrage_opts = sorted_en(["Head Only","Bust","Chest-up","Half Body","Full Body","Three-Quarter View",
                                       "Profile View","Front View","Back View","Slight High Angle","Low Angle","Over-the-Shoulder",
                                       "Includes mouth and jaw"])
        self.cadr_vars = []
        cblock = tk.LabelFrame(self.frame, text="Framing", font=("Arial",10,"bold")); cblock.pack(anchor="w", fill="x", padx=10, pady=6)
        for c in self.cadrage_opts:
            v = tk.BooleanVar(); tk.Checkbutton(cblock, text=c, variable=v, anchor="w").pack(anchor="w"); self.cadr_vars.append((c,v))
        self.cadr_other = tk.StringVar()
        cbottom = tk.Frame(cblock); cbottom.grid_columnconfigure(0, weight=1)
        tk.Entry(cbottom, textvariable=self.cadr_other).grid(row=0, column=0, sticky="ew", padx=8, pady=(8,4))
        tk.Label(cbottom, text="Other framing (commas)", fg="#666").grid(row=1, column=0, sticky="w", padx=8, pady=(0,6))
        cbottom.pack(fill="x")

        btns = tk.Frame(self.frame); btns.pack(pady=10)
        tk.Button(btns, text="🎨 Generate", command=self.generate).pack(side="left", padx=6)
        tk.Button(btns, text="📋 Copy window", command=self.copy_win).pack(side="left", padx=6)
        self.out = tk.Text(self.frame, height=8, wrap="word"); self.out.pack(padx=10, pady=10, fill="both", expand=True)

    def _get_single(self, cat):
        var, other = self.single_vars[cat]
        o = other.get().strip()
        if o: return o
        v = var.get()
        return None if v.startswith("—") else v

    def _gather_multi(self, cat):
        data = self.multi_blocks[cat]
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
        typ   = self._get_single("Creature Type")
        size  = self._get_single("Size")
        biome = self._get_single("Biome / Environment")
        behav = self._get_single("Behavior")
        threat= self._get_single("Threat Level")
        bg    = self._get_single("Background / Ambience")

        subject = "A monstrous creature"
        parts = []
        if typ:   parts.append(typ)
        if size:  parts.append(size)
        if biome: parts.append(f"from a {biome} biome")
        if parts: lines.append(f"{subject}: " + ", ".join(parts) + ".")
        else:     lines.append(f"{subject}.")

        anatomy = self._gather_multi("Anatomy / Morphology")
        surface = self._gather_multi("Surface / Texture")
        abil    = self._gather_multi("Abilities / Attacks")
        if anatomy: lines.append(f"Anatomy/features: {', '.join(anatomy)}.")
        if surface: lines.append(f"Surface/texture: {', '.join(surface)}.")
        if behav:   lines.append(f"Behavior: {behav}.")
        if abil:    lines.append(f"Abilities/attacks: {', '.join(abil)}.")
        if threat:  lines.append(f"Overall threat level: {threat}.")
        if bg:      lines.append(f"Set against a {bg} background.")

        cadr = self._gather_cadr()
        if cadr: lines.append(f"Shown from {', '.join(cadr)}.")
        return lines

    def generate(self):
        n = max(1, int(self.count_var.get()))
        if self.horde_var.get() and n > 1:
            lines = self._build_monster_lines()
            lines.append(f"Depict a horde of approximately {n} creatures, with size and detail variation.")
            txt = " ".join(lines)
        else:
            prompts = []
            base = self._build_monster_lines()
            for i in range(1, n+1):
                prompts.append(f"[Monster {i}] " + " ".join(base))
            txt = "\n\n---\n\n".join(prompts)
        self.out.delete("1.0", tk.END); self.out.insert(tk.END, txt)

    def copy_win(self):
        txt = self.out.get("1.0","end-1c").strip()
        if not txt:
            messagebox.showwarning("No prompt", "Generate a prompt before opening the copy window.")
            return
        win = tk.Toplevel(self.frame); win.title("Copy"); win.geometry("760x420")
        t = tk.Text(win, wrap="word"); t.pack(fill="both", expand=True, padx=10, pady=10)
        t.insert("1.0", txt); t.focus_set(); t.tag_add("sel","1.0","end")
        tk.Button(win, text="Copy to clipboard",
                  command=lambda: (self.frame.clipboard_clear(), self.frame.clipboard_append(t.get("1.0","end-1c")),
                                   messagebox.showinfo("Copied","Prompt copied to clipboard."))).pack(pady=6)

# ---------------- Group form ----------------
class GroupForm:
    def __init__(self, parent, styles_map):
        self.styles_map = styles_map
        self.frame = tk.Frame(parent)

        self.base_form = CharacterForm(self.frame, styles_map, title_text="Group base profile", columns_mode=False)
        self.base_form.frame.pack(anchor="w", fill="x", padx=6, pady=6)

        box = tk.LabelFrame(self.frame, text="Group parameters", font=("Arial",10,"bold"))
        box.pack(anchor="w", fill="x", padx=10, pady=6)

        left = tk.Frame(box); left.pack(anchor="w", fill="x")
        tk.Label(left, text="Members", font=("Arial", 10, "bold")).pack(side="left")
        self.count_var = tk.IntVar(value=4)
        tk.Spinbox(left, from_=2, to=20, textvariable=self.count_var, width=5).pack(side="left", padx=8)

        self.sep_var = tk.BooleanVar(value=True)
        tk.Checkbutton(left, text="Separate prompts", variable=self.sep_var).pack(side="left", padx=8)
        self.scene_var = tk.BooleanVar(value=False)
        tk.Checkbutton(left, text="Team scene prompt", variable=self.scene_var).pack(side="left", padx=8)

        varf = tk.Frame(box); varf.pack(anchor="w", fill="x", pady=(6,0))
        tk.Label(varf, text="Auto variations:", font=("Arial",10,"bold")).pack(anchor="w")
        self.var_expr = tk.BooleanVar(value=True)
        self.var_hair = tk.BooleanVar(value=True)
        self.var_traits = tk.BooleanVar(value=True)
        self.var_acc = tk.BooleanVar(value=True)
        for txt, v in [("Expression", self.var_expr), ("Hair/Beard", self.var_hair),
                       ("Notable Traits", self.var_traits), ("Accessories", self.var_acc)]:
            tk.Checkbutton(varf, text=txt, variable=v).pack(side="left", padx=6)

        seedf = tk.Frame(box); seedf.pack(anchor="w", fill="x", pady=(6,0))
        tk.Label(seedf, text="Seed (optional)", font=("Arial",10,"bold")).pack(side="left")
        self.seed_var = tk.StringVar(value="")
        tk.Entry(seedf, textvariable=self.seed_var, width=16).pack(side="left", padx=8)

        ov = tk.LabelFrame(self.frame, text="Per-member overrides (one line per member)", font=("Arial",10,"bold"))
        ov.pack(anchor="w", fill="both", padx=10, pady=6)
        tk.Label(ov, text="Free format, e.g.: Name: Kael, Role: Ranger, Extra: scar across eye", fg="#666").pack(anchor="w", padx=6, pady=(4,2))
        self.overrides = tk.Text(ov, height=5, wrap="word"); self.overrides.pack(fill="both", expand=True, padx=6, pady=6)

        btns = tk.Frame(self.frame); btns.pack(pady=10)
        tk.Button(btns, text="🎨 Generate", command=self.generate).pack(side="left", padx=6)
        tk.Button(btns, text="📋 Copy window", command=self.copy_win).pack(side="left", padx=6)
        self.out = tk.Text(self.frame, height=10, wrap="word"); self.out.pack(padx=10, pady=10, fill="both", expand=True)

    def _choice(self, arr, rnd):
        return rnd.choice(arr) if arr else None

    def generate(self):
        n = max(2, int(self.count_var.get()))
        seed = self.seed_var.get().strip()
        rnd = random.Random(seed) if seed else random.Random()

        base_lines = self.base_form.build_character_lines()

        exprs = list(self.base_form.single_categories["Facial Expression"])
        hairs = list(self.base_form.multi_categories["Hair / Beard"])
        traits= list(self.base_form.multi_categories["Notable Traits"])
        accs  = list(self.base_form.multi_categories["Accessories"])

        ov_lines = [l for l in self.overrides.get("1.0","end-1c").split("\n") if l.strip()]

        prompts = []
        for i in range(n):
            lines = list(base_lines)
            if self.var_expr.get():
                v = self._choice(exprs, rnd)
                if v: lines.append(f"Additional facial expression nuance: {v}.")
            if self.var_hair.get():
                v = self._choice(hairs, rnd)
                if v: lines.append(f"Hair/facial hair variation: {v}.")
            if self.var_traits.get():
                v = self._choice(traits, rnd)
                if v: lines.append(f"Additional notable feature: {v}.")
            if self.var_acc.get():
                v = self._choice(accs, rnd)
                if v: lines.append(f"Additional prop/accessory: {v}.")
            if i < len(ov_lines) and ov_lines[i].strip():
                lines.append(f"Member-specific notes: {ov_lines[i].strip()}.")
            prompts.append(" ".join(lines))

        bundle = []
        if self.sep_var.get():
            for i,p in enumerate(prompts, start=1):
                bundle.append(f"[Character {i}] {p}")
        if self.scene_var.get():
            scene = list(base_lines)
            scene.append(f"Group composition: {n} adventurers standing together with varied heights and stances; coherent lighting and perspective.")
            bundle.append("[Team Scene] " + " ".join(scene))
        if not bundle:
            bundle = [f"[Character {i+1}] {p}" for i,p in enumerate(prompts)]

        text = "\n\n---\n\n".join(bundle)
        self.out.delete("1.0", tk.END); self.out.insert(tk.END, text)

    def copy_win(self):
        txt = self.out.get("1.0","end-1c").strip()
        if not txt:
            messagebox.showwarning("No prompt", "Generate a prompt before opening the copy window.")
            return
        win = tk.Toplevel(self.frame); win.title("Copy"); win.geometry("760x420")
        t = tk.Text(win, wrap="word"); t.pack(fill="both", expand=True, padx=10, pady=10)
        t.insert("1.0", txt); t.focus_set(); t.tag_add("sel","1.0","end")
        tk.Button(win, text="Copy to clipboard",
                  command=lambda: (self.frame.clipboard_clear(), self.frame.clipboard_append(t.get("1.0","end-1c")),
                                   messagebox.showinfo("Copied","Prompt copied to clipboard."))).pack(pady=6)

# ---------------- App ----------------
class App:
    def __init__(self, root):
        root.title("Simplified Character Generation")
        root.minsize(900, 650)

        self.styles_map = {
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

        nb = ttk.Notebook(root); nb.pack(fill="both", expand=True)

        tab1 = ScrollFrame(nb); nb.add(tab1, text="Character")
        self.char_form = CharacterForm(tab1.interior, self.styles_map)
        self.char_form.frame.pack(anchor="w", fill="x", padx=8, pady=8)

        tab2 = ScrollFrame(nb); nb.add(tab2, text="Group")
        self.group_form = GroupForm(tab2.interior, self.styles_map)
        self.group_form.frame.pack(anchor="w", fill="x", padx=8, pady=8)

        tab3 = ScrollFrame(nb); nb.add(tab3, text="Monsters")
        self.monster_form = MonsterForm(tab3.interior, self.styles_map)
        self.monster_form.frame.pack(anchor="w", fill="x", padx=8, pady=8)

# -------------- safe launch --------------
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

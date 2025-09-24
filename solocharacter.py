import tkinter as tk
from tkinter import messagebox
import unicodedata, math

# -------- utils --------
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

# -------- race presets --------
RACE_PRESETS = {
    "Human":{"lines":["Neutral human craniofacial proportions; subtle asymmetry; natural pores and minor blemishes."],"avoid":""},
    "Elf":{"lines":["Long pointed ears clearly visible; slender angular features, high cheekbones, almond-shaped eyes; fine smooth hair."],"avoid":"Avoid human round ears and heavy jaw."},
    "Dark Elf":{"lines":["Long pointed ears; onyx/dark skin values rendered in grayscale; white or silver hair; luminous pale eyes."],"avoid":"Avoid tan human skin and short rounded ears."},
    "High Elf":{"lines":["Long pointed ears; elegant, refined features; luminous pale or golden skin values (grayscale rendition)."],"avoid":"Avoid coarse human jaw and small ears."},
    "Half-Elf":{"lines":["Subtle short pointed ears; blend of human and elven features; slightly angular cheekbones with softer jawline."],"avoid":"Avoid fully human ears or full-length elven ears."},
    "Kobold":{"lines":["Small draconic/reptilian head; slender muzzle; small horns or head spines; scaled skin; slit pupils."],"avoid":"Avoid human nose and lips."},
    "Goblin":{"lines":["Large expressive ears; long hooked or bulbous nose; sharp teeth; wiry features; mischievous, sinewy face."],"avoid":"Avoid elven elegance and human beauty portrait."},
    "Tiefling":{"lines":["Prominent horns (shape can vary); slight fangs; narrow pupils; subtle tail implied; unusual skin values in grayscale."],"avoid":"Avoid human ears without horns."},
    "Orc":{"lines":["Large lower tusks clearly visible; massive jaw; heavy brow ridge; broad flat nose; rough textured skin, visible pores and scars."],"avoid":"Avoid human or elven facial proportions, no delicate beauty look."},
    "Half-Orc":{"lines":["Small lower tusks clearly visible; pronounced jawline; heavy brow ridge; broad nose; slightly pointed ears; rough textured skin.","Olive/ashen grey-green skin tone (rendered in grayscale)."],"avoid":"Avoid human or elven facial proportions, no delicate beauty look."},
    "Undead":{"lines":["Gaunt, sunken features; desaturated mottled skin; bone hints or tendon shadows; cracked lips; cold dead gaze."],"avoid":"Avoid warm healthy skin and lively eyes."},
    "Vampire":{"lines":["Very pale skin; elongated upper fangs; sharp elegant features with predatory undertone; subtle under-eye darkness."],"avoid":"Avoid tanned skin and daylight cues."},
    "Dhampir":{"lines":["Alive yet pale; short fangs visible when lips part; subtly predatory eyes; human vitality + vampiric elegance."],"avoid":"Avoid full vampire gauntness or purely human warmth."},
    "Fae":{"lines":["Ethereal delicate features; slightly otherworldly eyes; faint freckles or leaf-like motifs; airy hair flow."],"avoid":"Avoid heavy human jaw or brutish orcish traits."},
    "Golem":{"lines":["Material body (stone/metal/clay/wood); carved seams and runic cracks; plate-like joints; non-fleshy surface."],"avoid":"Avoid soft human skin and pores."},
    "Dwarf":{"lines":["Broad face; prominent nose; thick neck; heavy brow; full beard or stout facial hair texture."],"avoid":"Avoid slender elven proportions."},
    "Gnome":{"lines":["Small round face; button nose; lively eyes; short beard/whiskers optional; playful expression lines."],"avoid":"Avoid tall elongated elven features."},
    "Halfling":{"lines":["Soft round features; gentle nose; curly hair texture; warm approachable expression lines."],"avoid":"Avoid long elven ears and orcish tusks."},
    "Dragonborn":{"lines":["Draconic head with muzzle; layered scales; horn ridges or frills; slit/reptilian pupils; no human nose or lips."],"avoid":"Avoid human facial structure."},
    "Aasimar":{"lines":["Subtle halo or radiant rim light; serene noble features; faint luminous skin values (grayscale glow)."],"avoid":""},
    "Werewolf":{"lines":["Lupine muzzle; layered fur; bestial ears; elongated canines; transitioning anatomy across cheeks and brow."],"avoid":"Avoid clean human facial features."},
    "Lycanthrope":{"lines":["Hybrid bestial traits (wolf/bear/boar); coarse fur; pronounced muzzle; predatory eyes; visible fangs."],"avoid":"Avoid neat human portrait proportions."},
    "Demon":{"lines":["Horns; ridged or scarred skin; predatory teeth; infernal eyes; smoke/soot patina (grayscale)."],"avoid":"Avoid cute human look."},
    "Angel":{"lines":["Subtle halo; soft yet defined features; feather textures implied; luminous highlights."],"avoid":""},
    "Lizardfolk":{"lines":["Reptilian head; scales of varied size; broad jaw; slit pupils; small cranial frill/spines."],"avoid":"Avoid human nose/lips and round ears."},
    "Satyr":{"lines":["Goat-like curled horns; pointed ears; playful sly expression; faint fur at jawline/temples."],"avoid":""},
    "Minotaur":{"lines":["Bovine head; large horns; strong muzzle; short fur; heavy neck musculature."],"avoid":"Avoid human/elf hints."},
    "Triton":{"lines":["Aquatic facial traits; finned ears or cheek fins; wet sheen highlights; subtle scales or gill lines."],"avoid":"Avoid dry human skin."},
    "Giant":{"lines":["Massive craniofacial proportions; heavy bone structure; thick neck; oversized features emphasized by lighting."],"avoid":""},
}

class CharacterForm:
    def __init__(self, parent, styles_map, title_text=None, columns_mode=True, prompt_bus=None):
        self.styles_map = styles_map
        self.columns_mode = columns_mode
        self.prompt_bus = prompt_bus
        self.frame = tk.LabelFrame(parent, text=title_text or "Character settings", font=("Arial", 10, "bold"))
        self.style_var = tk.StringVar(value=list(styles_map.keys())[0])

        # single-select categories
        self.single_categories = {
            "Race": sorted_en(list(RACE_PRESETS.keys())),
            "Gender": sorted_en(["Male","Female","Androgynous","Unknown"]),
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
            "Stature": ["Very Short","Short","Average Height","Tall","Very Tall"],
            "Build / Body Type": ["Underweight","Slim","Lean","Average","Athletic","Muscular","Stocky","Heavyset","Plus-size","Bulky"],
            "Attractiveness": ["Plain (1)","Average (2)","Attractive (3)","Striking (4)","Ethereal (5)"],
            "Background / Ambience": sorted_en(["Dark Lab","Shadowy Forest","Foggy Graveyard","Collapsed Cathedral",
                                                "Ritual Chamber","Broken Throne Room","Sewer Tunnel","Underground Market",
                                                "City Alley","Ruined Battlefield","Torch-lit Dungeon","Alchemist Explosion",
                                                "Moonlit Rooftop","Plain Dark Background","Stone Wall","Cave","Library",
                                                "Workshop","Market","Temple","Throne Room","Forest Clearing","Snowy Landscape",
                                                "Desert Dunes","Rainy Street","Cliff Edge","Mountain Pass","Night Seashore",
                                                "Laboratory","Dungeon","Ancient Ruins"])
        }

        # multi-select categories (checkboxes)
        self.multi_categories = {
            "Head Hair": sorted_en(["Long Hair","Short Hair","Curly Hair","Wavy Hair","Straight Hair","Ponytail",
                                    "Multiple Braids","Long and Braided","Messy","Shaved","Half Bald","White Streak",
                                    "Graying Temples","Hooded"]),
            "Facial Hair": sorted_en(["No Beard","Stubble Beard","Goatee","Mustache Only","Full/Thick Beard",
                                      "Groomed Beard","Sideburns","Handlebar Mustache","Chevron Mustache"]),
            "Body Hair": sorted_en(["No body hair","Light body hair","Moderate body hair","Heavy body hair",
                                    "Chest hair","Arm hair","Leg hair","Back hair","Armpit hair","Happy trail",
                                    "Well-groomed","Unkempt"]),
            "Notable Traits": sorted_en([
                "Heterochromia","Scar","Missing Eye","Burn Marks","Soot-covered","Blood Spatter","Veins Visible",
                "Runes Etched in Skin","Cracked Skin","Blindfolded","Blind Eye","Skeletal Features","Tattooed Face",
                "Facial Piercings","Tattoos","Multiple Scars","Pale Skin","Dried Blood","Glowing Eyes","Tribal Markings",
                "Facial Jewelry","Multiple Ear Rings",
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

        self._race_auto_lines, self._race_avoid_line = [], ""
        self.gritty_var = tk.BooleanVar(value=True)  # global toggle
        self._last_prompt = ""

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
            tk.Label(cell, text=cat, font=("Arial",10,"bold"), anchor="w").pack(anchor="w")
            var = tk.StringVar(value="— (leave empty) —")
            if cat == "Race":
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

        grit_box = tk.Frame(self.frame); grit_box.pack(anchor="w", fill="x", padx=10, pady=(0,8))
        tk.Checkbutton(grit_box, text="Gritty realism (no beauty retouching)", variable=self.gritty_var).pack(anchor="w")

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

        btns = tk.Frame(self.frame); btns.pack(pady=10)
        tk.Button(btns, text="🎨 Generate prompt", command=self.generate_prompt).pack(side="left", padx=6)
        tk.Button(btns, text="📋 Copy window", command=self.open_copy_window).pack(side="left", padx=6)

        # Add-to-group
        if self.prompt_bus:
            tk.Button(btns, text="➕ Add to Group", command=self.add_to_group).pack(side="left", padx=6)

        self.output = tk.Text(self.frame, height=8, wrap="word")
        self.output.pack(padx=10, pady=10, fill="both", expand=True)

        self._last_cols = None
        self.frame.bind("<Configure>", self._on_resize)
        self._relayout()

    # layout helpers
    def _columns_for_width(self, w):
        if not self.columns_mode: return 1
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
        import math as _m
        rows = max(1, _m.ceil(n/cols))
        for i, cell in enumerate(self._single_cells):
            r, c = i % rows, i // rows
            self.single_block.grid_columnconfigure(c, weight=1, uniform="singcols")
            cell.grid(row=r, column=c, sticky="nsew", padx=8, pady=6)
        for cat, data in self.check_blocks.items():
            block = data["frame"]; labels = data["labels"]; bottom = data["bottom"]
            for wdg in block.grid_slaves(): wdg.grid_forget()
            rows = max(1, _m.ceil(len(labels)/cols))
            for c in range(cols):
                block.grid_columnconfigure(c, weight=1, uniform=f"{cat}_cols")
            for idx, cb in enumerate(labels):
                r, c = idx % rows, idx // rows
                cb.grid(row=r, column=c, sticky="w", padx=8, pady=2)
            bottom.grid(row=rows, column=0, columnspan=cols, sticky="ew")
    def _on_resize(self, _e=None): self._relayout()

    # data helpers
    def _apply_race_preset(self, race_value: str):
        if race_value.startswith("—"):
            self._race_auto_lines, self._race_avoid_line = [], ""
            if hasattr(self, "race_hint"): self.race_hint.configure(text="")
            return
        p = RACE_PRESETS.get(race_value)
        if p:
            self._race_auto_lines = list(p.get("lines", []))
            self._race_avoid_line = p.get("avoid", "")
            if hasattr(self, "race_hint"):
                hint = "Race preset added: " + " ".join(self._race_auto_lines)
                if self._race_avoid_line: hint += f"  [Avoid: {self._race_avoid_line}]"
                self.race_hint.configure(text=hint)
        else:
            self._race_auto_lines, self._race_avoid_line = [], ""
            if hasattr(self, "race_hint"): self.race_hint.configure(text="")

    def get_single_choice(self, cat):
        pair = self.single_vars.get(cat)
        if not pair: return None
        var, other = pair
        txt = other.get().strip()
        if txt: return txt
        v = var.get()
        return None if v.startswith("—") else v

    def gather_multi(self, cat):
        block = self.check_blocks.get(cat)
        if not block: return []
        vals = [opt for opt, var in block["items"] if var.get()]
        vals += parse_custom_list(block["other_var"].get())
        return [v for v in vals if v]

    def build_character_lines(self):
        intro = self.styles_map.get(self.style_var.get(), next(iter(self.styles_map.values())))
        lines = [intro]

        race = self.get_single_choice("Race"); gender = self.get_single_choice("Gender"); role = self.get_single_choice("Role / Class")
        if race: self._apply_race_preset(race)
        parts = [x for x in [race, gender, role] if x]
        lines.append(f"The subject is a {' '.join(parts)}." if parts else "The subject is a character.")

        if self._race_auto_lines: lines.extend(self._race_auto_lines)

        age = self.get_single_choice("Age"); expr = self.get_single_choice("Facial Expression")
        segs = []
        if age: segs.append(f"approximately {age}")
        if expr: segs.append(f"with {expr}")
        if segs: lines.append(", ".join(segs) + ".")

        stat = self.get_single_choice("Stature"); build = self.get_single_choice("Build / Body Type")
        sb = []
        if stat: sb.append(f"stature: {stat}")
        if build: sb.append(f"build: {build}")
        if sb: lines.append("Body: " + ", ".join(sb) + ".")

        beauty = self.get_single_choice("Attractiveness")
        if beauty: lines.append(f"Overall attractiveness: {beauty}.")
        if beauty and (beauty.startswith("Attractive") or beauty.startswith("Striking") or beauty.startswith("Ethereal")):
            lines.append("Avoid losing racial markers due to beautification.")
        if self.gritty_var.get():
            lines.append("Use gritty realism; avoid beauty portrait, glam makeup, and skin smoothing.")

        head_hair = self.gather_multi("Head Hair")
        facial_hair = self.gather_multi("Facial Hair")
        body_hair = self.gather_multi("Body Hair")
        if head_hair: lines.append(f"Head hair: {', '.join(head_hair)}.")
        if facial_hair: lines.append(f"Facial hair: {', '.join(facial_hair)}.")
        if body_hair: lines.append(f"Body hair: {', '.join(body_hair)}.")

        traits = self.gather_multi("Notable Traits")
        if traits: lines.append(f"Notable features include {', '.join(traits)}.")
        clothes = self.gather_multi("Clothing / Armor"); acc = self.gather_multi("Accessories")
        if clothes and acc: lines.append(f"They wear {', '.join(clothes)}, along with {', '.join(acc)}.")
        elif clothes: lines.append(f"They wear {', '.join(clothes)}.")
        elif acc: lines.append(f"They carry {', '.join(acc)}.")

        bg = self.get_single_choice("Background / Ambience")
        if bg: lines.append(f"The scene is set against a {bg} background.")
        cadr = self.gather_multi("Framing")
        if cadr: lines.append(f"Shown from {', '.join(cadr)}.")

        if self._race_avoid_line: lines.append(f"Avoid: {self._race_avoid_line}")
        return lines

    def generate_prompt(self):
        text = " ".join(self.build_character_lines())
        self._last_prompt = text
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)

    def build_label(self):
        race = self.get_single_choice("Race") or ""
        gender = self.get_single_choice("Gender") or ""
        role = self.get_single_choice("Role / Class") or ""
        parts = [p for p in [race, gender, role] if p]
        return " ".join(parts) if parts else "Character"

    def add_to_group(self):
        if not self._last_prompt.strip():
            messagebox.showwarning("No prompt", "Generate a character prompt first.")
            return
        try:
            label = self.build_label()
            self.prompt_bus.add_character(label, self._last_prompt, weight=3)
            messagebox.showinfo("Added", f"Character added to Group:\n{label}")
        except RuntimeError as e:
            messagebox.showerror("Roster full", str(e))

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

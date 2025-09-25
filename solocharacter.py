import tkinter as tk
from tkinter import ttk, messagebox
import unicodedata

# Thème/constantes partagées
from ui import WHITE, UI_FONT_BOLD, PADX_S, PADY_S, PADY_SEC, GRID_PAD

# ---------- utils ----------
def unaccent(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if not unicodedata.combining(ch))

def sorted_en(items):
    return sorted(items, key=lambda s: unaccent(s).lower())

def parse_custom_list(text: str):
    if not text: return []
    out = []
    for token in text.replace(";", ",").replace("\n", ",").split(","):
        t = token.strip()
        if t: out.append(t)
    return out

# ---------- race presets ----------
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

HEAD_FACE_TRAITS = sorted_en([
    "Heterochromia","Scar","Missing Eye","Blind Eye","Blindfolded","Tattooed Face","Facial Piercings",
    "Multiple Ear Rings","Glowing Eyes","Wrinkled","Soot-covered","Blood Spatter","Runes Etched in Skin",
    "Cracked Skin","Skeletal Features"
])
BODY_TRAITS = sorted_en([
    "Tattoos","Multiple Scars","Pale Skin","Dried Blood","Tribal Markings","Veins Visible","Burn Marks",
    "Rough textured skin with visible pores","Mouth slightly open, lower tusks visible",
    "Small lower tusks clearly visible","Pronounced jawline","Heavy brow ridge","Broad nose","Slightly pointed ears"
])

HAIR_COLORS = sorted_en(["Black","Dark Brown","Brown","Chestnut","Auburn","Blonde","Platinum Blonde","Silver/White","Grey","Red","Salt-and-pepper","Dyed Blue","Dyed Green","Dyed Purple","Streaked"])
EYE_COLORS  = sorted_en(["Brown","Dark Brown","Amber","Hazel","Green","Blue","Grey","Violet","Pale/Almost White","Heterochromia"])
SKIN_TONES  = sorted_en(["Porcelain","Pale","Light","Olive","Tan","Brown","Dark Brown","Ebony","Ashen","Sallow","Freckled","Weathered","Scarred"])
CLOTHING_PALETTES = sorted_en(["Monochrome","Muted earth tones","Black & silver","Black & gold","Crimson accents","Emerald accents","Sapphire accents","Royal purple","White & gold","Leather browns","Cold greys","Warm rust"])
ACCENT_METALS = sorted_en(["Iron","Steel","Silver","Gold","Bronze","Copper","Brass","Blackened steel","Gunmetal","Gilded","Antique"])

class CharacterForm:
    def __init__(self, parent, styles_map, title_text=None, prompt_bus=None):
        self.styles_map = styles_map
        self.prompt_bus = prompt_bus

        # container
        self.frame = tk.LabelFrame(parent, text=title_text or "Character settings", bg=WHITE)
        self.frame.configure(padx=PADX_S, pady=PADY_S)

        self.style_var = tk.StringVar(value=list(styles_map.keys())[0])
        self.single_vars = {}
        self.multi_blocks = {}
        self._race_auto_lines, self._race_avoid_line = [], ""
        self.gritty_var = tk.BooleanVar(value=True)
        self.energy_var = tk.BooleanVar(value=True)
        self._last_prompt = ""
        self._race_hint_label = None

        self._build_ui()

    # ---------- aligned grid helpers ----------
    _grid_rows = {}
    def _make_grid(self, parent):
        f = tk.Frame(parent, bg=WHITE)
        f.grid_columnconfigure(0, minsize=140, weight=0)
        f.grid_columnconfigure(1, minsize=180, weight=0)
        f.grid_columnconfigure(2, weight=1)
        f.grid_columnconfigure(3, minsize=46,  weight=0)
        self._grid_rows[f] = 0
        return f

    def _add_single_row(self, grid_parent, label, options, key, race_preset=False, width=20):
        r = self._grid_rows[grid_parent]
        ttk.Label(grid_parent, text=label, style="Bold.TLabel").grid(row=r, column=0, sticky="w", padx=(0,8), pady=(PADY_S, PADY_S))
        var = tk.StringVar(value="— (leave empty) —")
        if race_preset:
            var.trace_add("write", lambda *_a, v=var: self._apply_race_preset(v.get()))
        combo = ttk.Combobox(grid_parent, textvariable=var, values=["— (leave empty) —"]+list(options),
                             state="readonly", width=width, style="Compact.TCombobox")
        combo.grid(row=r, column=1, sticky="w", pady=(PADY_S, PADY_S))
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

    # ---------- UI ----------
    def _build_ui(self):
        header = tk.Frame(self.frame, bg=WHITE); header.pack(anchor="w", fill="x", pady=PADY_SEC)
        ttk.Label(header, text="Render style", style="Bold.TLabel").pack(side="left")
        ttk.Combobox(header, textvariable=self.style_var, values=list(self.styles_map.keys()),
                     state="readonly", width=28, style="Compact.TCombobox").pack(side="left", padx=(8,0))

        # Identity
        sec_identity = tk.LabelFrame(self.frame, text="Identity & Core", bg=WHITE)
        sec_identity.pack(anchor="w", fill="x", pady=PADY_SEC)
        grid_id = self._make_grid(sec_identity); grid_id.pack(fill="x")
        self._add_single_row(grid_id, "Race", sorted_en(list(RACE_PRESETS.keys())), "Race", race_preset=True, width=20)
        self._add_single_row(grid_id, "Gender", sorted_en(["Male","Female","Androgynous","Unknown"]), "Gender", width=18)
        self._add_single_row(grid_id, "Role / Class", sorted_en([
            "Alchemist","Apothecary","Archer","Artificer","Assassin","Barbarian","Bard","Berserker","Captain",
            "Cleric","Commander","Commoner","Criminal","Cultist","Druid","Engineer","Hunter","Inquisitor",
            "Knight","Mage","Merchant","Monk","Necromancer","Noble","Occultist","Paladin","Pirate","Priest",
            "Ranger","Rogue","Scholar","Seer","Soldier","Sorcerer","Witch"
        ]), "Role / Class", width=22)
        self._add_single_row(grid_id, "Age", ["Childlike","Teenager","Young Adult","Adult","Mature (50-60)","Elderly (70+)","Ageless"], "Age", width=18)
        self._add_single_row(grid_id, "Facial Expression", sorted_en([
            "Calm","Compassionate","Confident","Cruel","Desperate","Determined","Angry","Playful","Frightened","Feral",
            "Proud","Cold","Haunted","Worried","Mischievous","Wary","Mocking","Thoughtful","Wrinkled","Brooding",
            "Smiling","Stoic","Stern","Sad","Hollow-eyed","Tired"
        ]), "Facial Expression", width=22)

        # Head & Face (3 colonnes côte à côte)
        sec_head = tk.LabelFrame(self.frame, text="Head & Face", bg=WHITE); sec_head.pack(anchor="w", fill="x", pady=PADY_SEC)
        row_head = tk.Frame(sec_head, bg=WHITE); row_head.pack(fill="x")
        for i in range(3): row_head.grid_columnconfigure(i, weight=1, uniform="headrow")

        self._add_multi_block(row_head, "Head Hair", sorted_en([
            "Long Hair","Short Hair","Curly Hair","Wavy Hair","Straight Hair","Ponytail","Multiple Braids",
            "Long and Braided","Messy","Shaved","Half Bald","White Streak","Graying Temples","Hooded"
        ]), "Head Hair", columns=2, grid=True, grid_rc=(0,0))
        self._add_multi_block(row_head, "Facial Hair", sorted_en([
            "No Beard","Stubble Beard","Goatee","Mustache Only","Full/Thick Beard","Groomed Beard",
            "Sideburns","Handlebar Mustache","Chevron Mustache"
        ]), "Facial Hair", columns=2, grid=True, grid_rc=(0,1))
        self._add_multi_block(row_head, "Head/Face Traits", HEAD_FACE_TRAITS, "Head/Face Traits", columns=2, grid=True, grid_rc=(0,2))

        # Body & Build
        sec_body = tk.LabelFrame(self.frame, text="Body & Build", bg=WHITE); sec_body.pack(anchor="w", fill="x", pady=PADY_SEC)
        grid_body = self._make_grid(sec_body); grid_body.pack(fill="x")
        self._add_single_row(grid_body, "Stature", ["Very Short","Short","Average Height","Tall","Very Tall"], "Stature", width=16)
        self._add_single_row(grid_body, "Build / Body Type", ["Underweight","Slim","Lean","Average","Athletic","Muscular","Stocky","Heavyset","Plus-size","Bulky"], "Build / Body Type", width=20)
        self._add_single_row(grid_body, "Attractiveness", ["Plain (1)","Average (2)","Attractive (3)","Striking (4)","Ethereal (5)"], "Attractiveness", width=16)

        row_body = tk.Frame(sec_body, bg=WHITE); row_body.pack(fill="x")
        for i in range(2): row_body.grid_columnconfigure(i, weight=1, uniform="bodyrow")
        self._add_multi_block(row_body, "Body Hair", sorted_en([
            "No body hair","Light body hair","Moderate body hair","Heavy body hair","Chest hair","Arm hair",
            "Leg hair","Back hair","Armpit hair","Happy trail","Well-groomed","Unkempt"
        ]), "Body Hair", columns=2, grid=True, grid_rc=(0,0))
        self._add_multi_block(row_body, "Body Traits", BODY_TRAITS, "Body Traits", columns=2, grid=True, grid_rc=(0,1))

        # Outfit & Gear
        sec_outfit = tk.LabelFrame(self.frame, text="Outfit & Gear", bg=WHITE); sec_outfit.pack(anchor="w", fill="x", pady=PADY_SEC)
        row_out = tk.Frame(sec_outfit, bg=WHITE); row_out.pack(fill="x")
        for i in range(2): row_out.grid_columnconfigure(i, weight=1, uniform="outrow")
        self._add_multi_block(row_out, "Clothing / Armor", sorted_en([
            "Victorian Jacket","Surgical Coat","Plague Doctor Outfit","Tattered Cloak","Engraved Plate Armor","Runed Robes",
            "Scorched Leather Armor","Merchant's Vest","Heavy Fur Coat","Tactical Gear","Military Uniform",
            "Embroidered Ritual Garb","Simple Tunic","Hooded Cloak","Cloak","Leather Armor","Chainmail","Plate Armor",
            "Robes","Tattered Robes","Rags","Noble Attire","Commoner's Clothes","Long Coat","Leather Gloves",
            "High Boots","Hood","Apron","Alchemist's Coat"
        ]), "Clothing / Armor", columns=2, grid=True, grid_rc=(0,0))
        self._add_multi_block(row_out, "Accessories", sorted_en([
            "Flask","Beaker","Smoking Pipe","Ancient Book","Mechanical Eye","Ring","Amulet","Skull","Dagger","Staff","Cane",
            "Scroll","Crystal Ball","Chain","Broken Mask","Medal","Exploding Vial","Belt Pouch","Pouches","Necklace",
            "Earrings","Bracelets","Gloves","Lantern","Torch","Coiled Rope","Satchel","Backpack","Quiver","Bow",
            "Crossbow","Sword","Shield","Axe","Mace","Spear","Crown","Diadem","Mechanical Gauntlet","Keys","Vials","Bottle","Jeweled Ring"
        ]), "Accessories", columns=2, grid=True, grid_rc=(0,1))

        # Colors
        sec_colors = tk.LabelFrame(self.frame, text="Colors (optional)", bg=WHITE); sec_colors.pack(anchor="w", fill="x", pady=PADY_SEC)
        grid_col = self._make_grid(sec_colors); grid_col.pack(fill="x")
        self._add_single_row(grid_col, "Hair Color", HAIR_COLORS, "Hair Color", width=16)
        self._add_single_row(grid_col, "Eye Color", EYE_COLORS, "Eye Color", width=16)
        self._add_single_row(grid_col, "Skin Tone", SKIN_TONES, "Skin Tone", width=16)
        self._add_single_row(grid_col, "Clothing Palette", CLOTHING_PALETTES, "Clothing Palette", width=18)
        self._add_single_row(grid_col, "Accents / Metals", ACCENT_METALS, "Accents / Metals", width=16)

        # Scene & Framing
        sec_scene = tk.LabelFrame(self.frame, text="Scene & Framing", bg=WHITE); sec_scene.pack(anchor="w", fill="x", pady=PADY_SEC)
        grid_sc = self._make_grid(sec_scene); grid_sc.pack(fill="x")
        self._add_single_row(grid_sc, "Background / Ambience", sorted_en([
            "Dark Lab","Shadowy Forest","Foggy Graveyard","Collapsed Cathedral","Ritual Chamber","Broken Throne Room",
            "Sewer Tunnel","Underground Market","City Alley","Ruined Battlefield","Torch-lit Dungeon","Alchemist Explosion",
            "Moonlit Rooftop","Plain Dark Background","Stone Wall","Cave","Library","Workshop","Market","Temple",
            "Throne Room","Forest Clearing","Snowy Landscape","Desert Dunes","Rainy Street","Cliff Edge","Mountain Pass",
            "Night Seashore","Laboratory","Dungeon","Ancient Ruins"
        ]), "Background / Ambience", width=26)
        self._add_multi_block(sec_scene, "Framing", sorted_en([
            "Head Only","Bust","Chest-up","Half Body","Square Portrait","Tight Portrait","Asymmetrical Frame",
            "Medium Long Shot","Full Body","Three-Quarter View","Profile View","Front View","Back View",
            "Slight High Angle","Low Angle","Over-the-Shoulder","Includes mouth and jaw"
        ]), "Framing", columns=4)

        # Motion & Camera
        sec_motion = tk.LabelFrame(self.frame, text="Motion & Camera", bg=WHITE); sec_motion.pack(anchor="w", fill="x", pady=PADY_SEC)
        grid_mo = self._make_grid(sec_motion); grid_mo.pack(fill="x")
        self._add_single_row(grid_mo, "Pose / Action Beat", [
            "Subtle torso twist","Head turned mid-motion","Leaning forward","Looking back over shoulder",
            "Shoulder drop + neck tilt","Looming toward camera","Hand entering frame","Mid-step shift of weight"
        ], "Pose / Action Beat", width=26)
        self._add_single_row(grid_mo, "Gaze Direction", [
            "Off-camera (left)","Off-camera (right)","Downcast","Upward glance","Eyes to camera","Half-lidded squint"
        ], "Gaze Direction", width=24)
        self._add_single_row(grid_mo, "Camera / Lens", [
            "85mm portrait calm","50mm cinematic","35mm close dynamic","24mm wide slight distortion","Low angle","Slight Dutch angle"
        ], "Camera / Lens", width=26)
        toggles = tk.Frame(sec_motion, bg=WHITE); toggles.pack(anchor="w", fill="x", pady=(PADY_S,0))
        ttk.Checkbutton(toggles, text="Gritty realism (no beauty retouching)", variable=self.gritty_var).pack(side="left")
        ttk.Checkbutton(toggles, text="Inject motion & energy", variable=self.energy_var).pack(side="left", padx=(12,0))

        # actions & output
        btns = tk.Frame(self.frame, bg=WHITE); btns.pack(pady=(6,4))
        ttk.Button(btns, text="🎨 Generate prompt", command=self.generate_prompt).pack(side="left", padx=6)
        ttk.Button(btns, text="📋 Copy window", command=self.open_copy_window).pack(side="left", padx=6)
        if self.prompt_bus:
            ttk.Button(btns, text="➕ Add to Group", command=self.add_to_group).pack(side="left", padx=6)

        self.output = tk.Text(self.frame, height=7, wrap="word", bg=WHITE)
        self.output.pack(padx=PADX_S, pady=(4,8), fill="both", expand=True)

    # ---------- helpers / prompt ----------
    def _apply_race_preset(self, race_value: str):
        if race_value.startswith("—"):
            self._race_auto_lines, self._race_avoid_line = [], ""
            if self._race_hint_label: self._race_hint_label.destroy(); self._race_hint_label = None
            return
        p = RACE_PRESETS.get(race_value)
        if p:
            self._race_auto_lines = list(p.get("lines", []))
            self._race_avoid_line = p.get("avoid", "")
            hint = "Race preset added: " + " ".join(self._race_auto_lines)
            if self._race_avoid_line: hint += f"  [Avoid: {self._race_avoid_line}]"
            if not self._race_hint_label:
                for w in self.frame.winfo_children():
                    if isinstance(w, tk.LabelFrame) and w.cget("text") == "Identity & Core":
                        self._race_hint_label = ttk.Label(w, text=hint, wraplength=700)
                        self._race_hint_label.pack(anchor="w", pady=(2,0))
                        break
            else:
                self._race_hint_label.configure(text=hint)
        else:
            self._race_auto_lines, self._race_avoid_line = [], ""
            if self._race_hint_label: self._race_hint_label.destroy(); self._race_hint_label = None

    def get_single_choice(self, key):
        pair = self.single_vars.get(key)
        if not pair: return None
        var, other = pair
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

        pose = self.get_single_choice("Pose / Action Beat")
        gaze = self.get_single_choice("Gaze Direction")
        cam  = self.get_single_choice("Camera / Lens")
        if pose: lines.append(f"Pose/action: {pose}.")
        if gaze: lines.append(f"Gaze: {gaze}.")
        if cam:  lines.append(f"Camera/lens: {cam}.")

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

        head_hair   = self.gather_multi("Head Hair")
        facial_hair = self.gather_multi("Facial Hair")
        body_hair   = self.gather_multi("Body Hair")
        if head_hair:   lines.append(f"Head hair: {', '.join(head_hair)}.")
        if facial_hair: lines.append(f"Facial hair: {', '.join(facial_hair)}.")
        if body_hair:   lines.append(f"Body hair: {', '.join(body_hair)}.")

        head_traits = self.gather_multi("Head/Face Traits")
        body_traits = self.gather_multi("Body Traits")
        traits = head_traits + body_traits
        if traits: lines.append(f"Notable features include {', '.join(traits)}.")

        clothes = self.gather_multi("Clothing / Armor"); acc = self.gather_multi("Accessories")
        if clothes and acc: lines.append(f"They wear {', '.join(clothes)}, along with {', '.join(acc)}.")
        elif clothes: lines.append(f"They wear {', '.join(clothes)}.")
        elif acc: lines.append(f"They carry {', '.join(acc)}.")

        # Colors
        col_parts = []
        for key, label in [("Hair Color","hair"),("Eye Color","eyes"),("Skin Tone","skin"),
                           ("Clothing Palette","clothing"),("Accents / Metals","accents/metals")]:
            val = self.get_single_choice(key)
            if val: col_parts.append(f"{label} — {val}")
        if col_parts:
            if "black-and-white" in intro.lower() or "monochrome" in intro.lower():
                lines.append("Color cues (use as tonal accents in monochrome): " + "; ".join(col_parts) + ".")
            else:
                lines.append("Color palette: " + "; ".join(col_parts) + ".")

        bg = self.get_single_choice("Background / Ambience")
        if bg: lines.append(f"The scene is set against a {bg} background.")
        cadr = self.gather_multi("Framing")
        if cadr: lines.append(f"Shown from {', '.join(cadr)}.")

        if self.energy_var.get():
            if not pose: lines.append("Pose/action: subtle torso twist with asymmetrical shoulders.")
            lines.append("Motion cues: strands of hair in motion, cloak flutter.")
            lines.append("Environmental motion: drifting dust motes / faint embers in air.")

        if self._race_avoid_line: lines.append(f"Avoid: {self._race_avoid_line}")
        return lines

    # ---------- actions ----------
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
        return "Character" if not parts else " ".join(parts)

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
        win = tk.Toplevel(self.frame); win.title("Copy"); win.configure(bg=WHITE); win.geometry("760x420")
        t = tk.Text(win, wrap="word", bg=WHITE); t.pack(fill="both", expand=True, padx=8, pady=8)
        t.insert("1.0", txt); t.focus_set(); t.tag_add("sel","1.0","end")
        ttk.Button(win, text="Copy to clipboard",
                   command=lambda: (self.frame.clipboard_clear(), self.frame.clipboard_append(t.get("1.0","end-1c")),
                                    messagebox.showinfo("Copied","Prompt copied to clipboard."))).pack(pady=6)

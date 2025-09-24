import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random

class GroupForm:
    def __init__(self, parent, styles_map, prompt_bus):
        self.styles_map = styles_map
        self.bus = prompt_bus
        self.frame = tk.Frame(parent)

        # ===== Group render style (override) =====
        style_box = tk.Frame(self.frame); style_box.pack(anchor="w", fill="x", padx=10, pady=(8,2))
        tk.Label(style_box, text="Group Render Style (overrides individuals)", font=("Arial",10,"bold")).pack(anchor="w")
        self.group_style_var = tk.StringVar(value=list(styles_map.keys())[0])
        tk.OptionMenu(style_box, self.group_style_var, *styles_map.keys()).pack(anchor="w", padx=10, pady=(2,6))

        # ===== Scene header: Action / Location / Theme =====
        scene_box = tk.LabelFrame(self.frame, text="Scene header", font=("Arial",10,"bold"))
        scene_box.pack(anchor="w", fill="x", padx=10, pady=6)

        self.action_var = tk.StringVar(value="Combat")
        actions = ["Combat","Ambush","Chase","Stealth infiltration","Negotiation/Parley","Ritual/Incantation",
                   "Exploration/Scouting","Camping/Rest","Marching/Travel","Training/Drill","Tavern gathering",
                   "Siege assault","Siege defense","Rescue/Extraction"]
        tk.Label(scene_box, text="Action").grid(row=0, column=0, sticky="w", padx=6)
        tk.OptionMenu(scene_box, self.action_var, *actions).grid(row=1, column=0, sticky="ew", padx=6)

        self.location_var = tk.StringVar(value="Ruined Battlefield")
        locations = sorted(["Collapsed Cathedral","Foggy Graveyard","Shadowy Forest","Sewer Tunnel","Underground Market",
                            "Ruined Battlefield","Torch-lit Dungeon","Ancient Library","Throne Room","City Alley","Mountain Pass",
                            "Cliff Edge","Desert Dunes","Snowy Landscape","Rainy Street","Moonlit Rooftop","Cave","Temple",
                            "Workshop","Market","Plain Dark Background"])
        tk.Label(scene_box, text="Location").grid(row=0, column=1, sticky="w", padx=6)
        tk.OptionMenu(scene_box, self.location_var, *locations).grid(row=1, column=1, sticky="ew", padx=6)

        self.theme_var = tk.StringVar(value="Grimdark")
        themes = ["Heroic","Grimdark","Gothic Horror","Hopeful Resistance","Noble Sacrifice",
                  "Mystery / Investigation","Steampunk","High Magic","Low Magic",
                  "Necromancy","Corruption","Redemption","Survival","Cosmic Horror","Political Intrigue"]
        tk.Label(scene_box, text="Theme").grid(row=0, column=2, sticky="w", padx=6)
        tk.OptionMenu(scene_box, self.theme_var, *themes).grid(row=1, column=2, sticky="ew", padx=6)

        for c in range(3):
            scene_box.grid_columnconfigure(c, weight=1)

        # ===== Composition toggles =====
        comp = tk.LabelFrame(self.frame, text="Composition & constraints", font=("Arial",10,"bold"))
        comp.pack(anchor="w", fill="x", padx=10, pady=6)
        self.unified_light = tk.BooleanVar(value=True)
        self.eye_level = tk.BooleanVar(value=True)
        self.three_quarter = tk.BooleanVar(value=True)
        self.depth_layering = tk.BooleanVar(value=True)
        self.include_mouth = tk.BooleanVar(value=False)
        for txt, var in [("Unified lighting", self.unified_light),
                         ("Eye-level camera", self.eye_level),
                         ("Three-quarter arrangement", self.three_quarter),
                         ("Depth layering", self.depth_layering),
                         ("Include mouth and jaw", self.include_mouth)]:
            tk.Checkbutton(comp, text=txt, variable=var).pack(side="left", padx=6)

        varf = tk.LabelFrame(self.frame, text="Auto-variations in scene", font=("Arial",10,"bold"))
        varf.pack(anchor="w", fill="x", padx=10, pady=6)
        self.var_pose = tk.BooleanVar(value=True)
        self.var_facing = tk.BooleanVar(value=True)
        self.var_height = tk.BooleanVar(value=True)
        self.var_distance = tk.BooleanVar(value=True)
        self.var_weapon = tk.BooleanVar(value=True)
        for txt, var in [("Poses", self.var_pose), ("Facing direction", self.var_facing), ("Height offsets", self.var_height),
                         ("Distance to camera", self.var_distance), ("Weapon readiness", self.var_weapon)]:
            tk.Checkbutton(varf, text=txt, variable=var).pack(side="left", padx=6)

        # Harmonization & negatives
        guard = tk.Frame(self.frame); guard.pack(anchor="w", fill="x", padx=10, pady=(2,6))
        self.harmonize_scale = tk.BooleanVar(value=True)
        self.keep_racial_markers = tk.BooleanVar(value=True)
        self.gritty_var = tk.BooleanVar(value=True)
        for txt, var in [("Consistent subject scale", self.harmonize_scale),
                         ("Avoid losing racial markers due to beautification", self.keep_racial_markers),
                         ("Gritty realism (no glam retouching)", self.gritty_var)]:
            tk.Checkbutton(guard, text=txt, variable=var).pack(side="left", padx=6)

        # ===== Roster table =====
        roster_box = tk.LabelFrame(self.frame, text="Roster (mix characters & monsters)", font=("Arial",10,"bold"))
        roster_box.pack(anchor="w", fill="both", padx=10, pady=6)

        self.tree = ttk.Treeview(roster_box, columns=("type","label","weight"), show="headings", height=8)
        self.tree.heading("type", text="Type"); self.tree.column("type", width=100, anchor="w")
        self.tree.heading("label", text="Label"); self.tree.column("label", width=520, anchor="w")
        self.tree.heading("weight", text="Weight"); self.tree.column("weight", width=80, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True, padx=(6,0), pady=6)

        yscroll = ttk.Scrollbar(roster_box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side="left", fill="y", padx=(0,6), pady=6)

        controls = tk.Frame(roster_box); controls.pack(side="left", fill="y", padx=6, pady=6)
        tk.Button(controls, text="▲ Up", command=self.move_up).pack(fill="x", pady=2)
        tk.Button(controls, text="▼ Down", command=self.move_down).pack(fill="x", pady=2)
        tk.Button(controls, text="✖ Remove", command=self.remove_sel).pack(fill="x", pady=6)
        tk.Button(controls, text="🧹 Clear", command=self.clear_all).pack(fill="x")

        self.w_frame = tk.LabelFrame(self.frame, text="Selected item weight (1-5)", font=("Arial",10,"bold"))
        self.w_frame.pack(anchor="w", fill="x", padx=10, pady=(0,6))
        self.weight_var = tk.IntVar(value=3)
        tk.Scale(self.w_frame, from_=1, to=5, orient="horizontal", variable=self.weight_var,
                 command=lambda _v: self.apply_weight()).pack(fill="x", padx=10, pady=6)

        # Condense monsters option
        cond = tk.Frame(self.frame); cond.pack(anchor="w", fill="x", padx=10, pady=(0,6))
        self.condense_monsters = tk.BooleanVar(value=False)
        tk.Checkbutton(cond, text="Condense multiple monsters into a single horde description", variable=self.condense_monsters).pack(anchor="w")

        # ===== Output & buttons =====
        btns = tk.Frame(self.frame); btns.pack(pady=10)
        tk.Button(btns, text="🎨 Generate Team Scene", command=self.generate_scene).pack(side="left", padx=6)
        tk.Button(btns, text="📋 Copy Team Scene only", command=self.copy_scene_only).pack(side="left", padx=6)
        tk.Button(btns, text="📋 Copy All (scene + items)", command=self.copy_all).pack(side="left", padx=6)
        tk.Button(btns, text="💾 Export .txt", command=self.export_txt).pack(side="left", padx=6)

        self.out = tk.Text(self.frame, height=12, wrap="word"); self.out.pack(padx=10, pady=10, fill="both", expand=True)

        # subscribe to bus
        self.bus.register(self._refresh_from_bus)
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._sync_weight_from_selection())

        self._last_scene = ""
        self._last_all = ""

    # ---- roster ops ----
    def _refresh_from_bus(self, items):
        # rebuild tree preserving selection index if possible
        sel = self._selected_index()
        for iid in self.tree.get_children(): self.tree.delete(iid)
        for i, it in enumerate(items):
            self.tree.insert("", "end", iid=str(i), values=(it["type"].capitalize(), it["label"], it["weight"]))
        # restore selection
        if sel is not None and sel < len(items):
            self.tree.selection_set(str(sel))
            self._sync_weight_from_selection()

    def _selected_index(self):
        sel = self.tree.selection()
        if not sel: return None
        try: return int(sel[0])
        except Exception: return None

    def move_up(self):
        idx = self._selected_index()
        if idx is None: return
        self.bus.move_up(idx)
        self.tree.selection_set(str(max(0, idx-1)))

    def move_down(self):
        idx = self._selected_index()
        if idx is None: return
        self.bus.move_down(idx)
        self.tree.selection_set(str(min(len(self.bus.items)-1, idx+1)))

    def remove_sel(self):
        idx = self._selected_index()
        if idx is None: return
        self.bus.remove(idx)

    def clear_all(self):
        if messagebox.askyesno("Clear roster", "Remove all items from the roster?"):
            self.bus.clear()

    def _sync_weight_from_selection(self):
        idx = self._selected_index()
        if idx is None or idx >= len(self.bus.items): return
        self.weight_var.set(self.bus.items[idx]["weight"])

    def apply_weight(self):
        idx = self._selected_index()
        if idx is None: return
        self.bus.set_weight(idx, self.weight_var.get())

    # ---- generation helpers ----
    def _scene_header_lines(self):
        lines = []
        lines.append(self.styles_map.get(self.group_style_var.get(), next(iter(self.styles_map.values()))))
        lines.append(f"Group theme: {self.theme_var.get()}.")
        lines.append(f"Location: {self.location_var.get()}.")
        lines.append(f"Group action: {self.action_var.get()}.")
        if self.unified_light.get(): lines.append("Use unified lighting across subjects.")
        if self.eye_level.get(): lines.append("Eye-level camera.")
        if self.three_quarter.get(): lines.append("Three-quarter arrangement.")
        if self.depth_layering.get(): lines.append("Depth layering to separate planes.")
        if self.include_mouth.get(): lines.append("Include mouth and jaw.")
        if self.var_pose.get(): lines.append("Vary poses naturally among subjects.")
        if self.var_facing.get(): lines.append("Vary facing direction subtly.")
        if self.var_height.get(): lines.append("Introduce slight height offsets.")
        if self.var_distance.get(): lines.append("Vary distance to camera for depth.")
        if self.var_weapon.get(): lines.append("Vary weapon readiness among subjects.")
        if self.harmonize_scale.get(): lines.append("Maintain consistent relative scale among subjects.")
        if self.keep_racial_markers.get(): lines.append("Avoid losing racial markers due to beautification.")
        if self.gritty_var.get(): lines.append("Use gritty realism; avoid glam makeup and skin smoothing.")
        return lines

    def _summarize_members(self, items):
        # produce compact list with weight marks
        if not items: return []
        members = [f"[{it['weight']}] {it['label']}" for it in items]
        return ["Members (weighted focus): " + ", ".join(members) + "."]

    def _summarize_monsters(self, items):
        if not items: return []
        if self.condense_monsters.get() and len(items) > 1:
            # condense into a single horde line
            labels = [it["label"] for it in items]
            return [f"Monsters: a horde comprising {', '.join(labels)}."]
        else:
            mons = [f"[{it['weight']}] {it['label']}" for it in items]
            return ["Monsters (weighted focus): " + ", ".join(mons) + "."]

    def _combat_hint(self, has_char, has_mon):
        if has_char and has_mon and self.action_var.get() in ("Combat","Ambush","Siege assault","Siege defense","Rescue/Extraction","Chase"):
            return ["Depict active engagement between characters and monsters with readable silhouettes."]
        return []

    def generate_scene(self):
        items = list(self.bus.items)
        chars = [it for it in items if it["type"] == "character"]
        mons  = [it for it in items if it["type"] == "monster"]

        if not items:
            messagebox.showwarning("Empty roster","Add characters or monsters from their tabs first.")
            return

        # Build team scene
        lines = []
        lines.extend(self._scene_header_lines())
        lines.extend(self._summarize_members(chars))
        lines.extend(self._summarize_monsters(mons))
        lines.extend(self._combat_hint(bool(chars), bool(mons)))

        # Final framing
        lines.append("Coherent perspective and composition; avoid chaotic overlap of key facial features.")
        scene_text = " ".join(lines)

        # Full output = Team Scene + (optional) list of individual prompts
        blocks = ["[Team Scene] " + scene_text]
        # include the individual items after the scene
        for i, it in enumerate(items, start=1):
            blocks.append(f"[{it['type'].capitalize()} {i}] {it['text']}")

        full_text = "\n\n---\n\n".join(blocks)
        self._last_scene = scene_text
        self._last_all = full_text

        self.out.delete("1.0", tk.END)
        self.out.insert(tk.END, full_text)

    def copy_scene_only(self):
        if not self._last_scene:
            self.generate_scene()
        self.frame.clipboard_clear()
        self.frame.clipboard_append(self._last_scene)
        messagebox.showinfo("Copied", "Team Scene prompt copied to clipboard.")

    def copy_all(self):
        if not self._last_all:
            self.generate_scene()
        self.frame.clipboard_clear()
        self.frame.clipboard_append(self._last_all)
        messagebox.showinfo("Copied", "Full output (scene + items) copied to clipboard.")

    def export_txt(self):
        if not self._last_all:
            self.generate_scene()
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text file","*.txt")],
                                            title="Export prompts as .txt")
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._last_all)
            messagebox.showinfo("Exported", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

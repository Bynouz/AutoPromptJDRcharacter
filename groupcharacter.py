import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Thème/constantes partagées
from ui import WHITE, UI_FONT_BOLD, PADX_S, PADY_S, PADY_SEC, GRID_PAD

def sorted_en(items): 
    return sorted(items, key=lambda s: str(s).lower())

class GroupForm:
    """
    Mixer d'équipe : agrège les prompts arrivant via PromptBus
    (add_character/add_monster depuis les autres onglets),
    permet de réordonner, pondérer et générer un prompt de scène.
    """
    def __init__(self, parent, styles_map, title_text="Group mixer", prompt_bus=None):
        self.styles_map = styles_map
        self.prompt_bus = prompt_bus
        if not prompt_bus:
            raise ValueError("GroupForm requires a prompt_bus")

        self.frame = tk.LabelFrame(parent, text=title_text, bg=WHITE)
        self.frame.configure(padx=PADX_S, pady=PADY_S)

        # state
        self.style_var = tk.StringVar(value=list(styles_map.keys())[-1])  # Cinematic Concept Art par défaut
        self.action_var = tk.StringVar(value="Idle pose")
        self.location_var = tk.StringVar(value="Plain Dark Background")
        self.theme_var = tk.StringVar(value="Epic")
        self.camera_var = tk.StringVar(value="Wide shot (24–35mm)")
        self.light_var = tk.StringVar(value="Volumetric rays")
        self.allow_conflict = tk.BooleanVar(value=True)
        self.depth_var = tk.BooleanVar(value=True)
        self.motion_var = tk.BooleanVar(value=True)

        self._last_prompt = ""

        self._build_ui()

        # subscribe to bus
        self.prompt_bus.register(self._refresh_roster)

    # ------- small builders -------
    _grid_rows = {}
    def _make_grid(self, parent):
        f = tk.Frame(parent, bg=WHITE)
        f.grid_columnconfigure(0, minsize=140, weight=0)
        f.grid_columnconfigure(1, minsize=240, weight=0)
        f.grid_columnconfigure(2, weight=1)
        self._grid_rows[f] = 0
        return f

    def _add_single_row(self, grid_parent, label, values, var):
        r = self._grid_rows[grid_parent]
        ttk.Label(grid_parent, text=label, style="Bold.TLabel").grid(row=r, column=0, sticky="w", padx=(0,8), pady=(PADY_S, PADY_S))
        ttk.Combobox(grid_parent, textvariable=var, values=list(values), state="readonly",
                     width=28, style="Compact.TCombobox").grid(row=r, column=1, sticky="w", pady=(PADY_S, PADY_S))
        self._grid_rows[grid_parent] = r + 1

    # ------- UI -------
    def _build_ui(self):
        # Settings
        sec = tk.LabelFrame(self.frame, text="Group scene settings", bg=WHITE); sec.pack(fill="x", pady=PADY_SEC)
        grid = self._make_grid(sec); grid.pack(fill="x")

        self._add_single_row(grid, "Render style", self.styles_map.keys(), self.style_var)
        self._add_single_row(grid, "Action", [
            "Idle pose","Marching","Negotiation / Parley","Celebration","Tracking / Scouting","Ambush set-up",
            "Combat — melee","Combat — ranged","Duel","Boss battle","Casting ritual","Aftermath / wounded"
        ], self.action_var)
        self._add_single_row(grid, "Location", sorted_en([
            "Plain Dark Background","City Alley","Collapsed Cathedral","Dungeon","Ancient Ruins","Forest Clearing",
            "Foggy Graveyard","Shadowy Forest","Broken Throne Room","Torch-lit Dungeon","Snowy Pass","Desert Canyon",
            "Moonlit Rooftop","Cliff Edge","Mountain Pass","Night Seashore","Marketplace","Temple","Workshop","Cave"
        ]), self.location_var)
        self._add_single_row(grid, "Theme / Tone", [
            "Epic","Heroic","Grimdark","Tragic","Hopeful","Mysterious","Survival","Political Intrigue"
        ], self.theme_var)
        self._add_single_row(grid, "Camera", [
            "Wide shot (24–35mm)","Medium group (35–50mm)","Telephoto compressed (85mm)","Low angle","Slight Dutch angle"
        ], self.camera_var)
        self._add_single_row(grid, "Lighting", [
            "Volumetric rays","Moonlit","Torchlit","Overcast soft light","Harsh backlight","Flickering firelight","Lantern glow"
        ], self.light_var)

        toggles = tk.Frame(sec, bg=WHITE); toggles.pack(anchor="w", fill="x", pady=(2,0))
        ttk.Checkbutton(toggles, text="Allow monsters vs characters conflict", variable=self.allow_conflict).pack(side="left")
        ttk.Checkbutton(toggles, text="Depth cues (overlaps, foreground/background)", variable=self.depth_var).pack(side="left", padx=12)
        ttk.Checkbutton(toggles, text="Motion cues (cloth, hair, particles)", variable=self.motion_var).pack(side="left", padx=12)

        # Roster (list + controls)
        roster = tk.LabelFrame(self.frame, text="Roster (order = composition priority)", bg=WHITE)
        roster.pack(fill="both", expand=True, pady=PADY_SEC)

        left = tk.Frame(roster, bg=WHITE); left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(roster, bg=WHITE); right.pack(side="right", fill="y", padx=6)

        self.listbox = tk.Listbox(left, height=10, activestyle="dotbox")
        self.listbox.pack(fill="both", expand=True, padx=6, pady=6)

        # weight control for selected
        weight_box = tk.Frame(left, bg=WHITE); weight_box.pack(fill="x", padx=6, pady=(0,6))
        ttk.Label(weight_box, text="Weight (selected):").pack(side="left")
        self.weight_var = tk.IntVar(value=3)
        ttk.Spinbox(weight_box, from_=1, to=9, textvariable=self.weight_var, width=4,
                    command=self._apply_weight).pack(side="left", padx=(6,0))
        ttk.Button(weight_box, text="Apply", command=self._apply_weight).pack(side="left", padx=6)

        # buttons
        ttk.Button(right, text="▲ Up", command=lambda: self._move(-1)).pack(fill="x", pady=2)
        ttk.Button(right, text="▼ Down", command=lambda: self._move(+1)).pack(fill="x", pady=2)
        ttk.Button(right, text="Remove", command=self._remove).pack(fill="x", pady=(8,2))
        ttk.Button(right, text="Clear all", command=self.prompt_bus.clear).pack(fill="x", pady=2)

        # Output
        btns = tk.Frame(self.frame, bg=WHITE); btns.pack(pady=(8,4))
        ttk.Button(btns, text="🎬 Generate group prompt", command=self.generate_prompt).pack(side="left", padx=6)
        ttk.Button(btns, text="📋 Copy", command=self.open_copy).pack(side="left", padx=6)
        ttk.Button(btns, text="💾 Export .txt", command=self.export_txt).pack(side="left", padx=6)

        self.output = tk.Text(self.frame, height=10, wrap="word", bg=WHITE)
        self.output.pack(fill="both", expand=True, padx=6, pady=(2,8))

        # update weight field on selection
        self.listbox.bind("<<ListboxSelect>>", lambda e: self._sync_weight_from_selection())

    # ------- roster ops -------
    def _refresh_roster(self, items):
        self.listbox.delete(0, "end")
        for i, it in enumerate(items):
            tag = "CHAR" if it["type"] == "character" else "MONS"
            self.listbox.insert("end", f"{i+1:02d} | {tag} | w{it['weight']} | {it['label']}")

    def _current_index(self):
        sel = self.listbox.curselection()
        return int(sel[0]) if sel else None

    def _sync_weight_from_selection(self):
        idx = self._current_index()
        if idx is None: return
        self.weight_var.set(self.prompt_bus.items[idx]["weight"])

    def _apply_weight(self):
        idx = self._current_index()
        if idx is None: return
        self.prompt_bus.set_weight(idx, self.weight_var.get())
        self._refresh_roster(self.prompt_bus.items)

    def _move(self, delta):
        idx = self._current_index()
        if idx is None: return
        if delta < 0: self.prompt_bus.move_up(idx)
        else:         self.prompt_bus.move_down(idx)
        self._refresh_roster(self.prompt_bus.items)
        new_idx = max(0, min(len(self.prompt_bus.items)-1, idx+delta))
        self.listbox.selection_clear(0, "end"); self.listbox.selection_set(new_idx); self.listbox.activate(new_idx)
        self._sync_weight_from_selection()

    def _remove(self):
        idx = self._current_index()
        if idx is None: return
        self.prompt_bus.remove(idx)
        self._refresh_roster(self.prompt_bus.items)

    # ------- prompt build -------
    def _build_group_lines(self):
        intro = self.styles_map.get(self.style_var.get(), next(iter(self.styles_map.values())))
        lines = [intro]

        lines.append(f"Group scene: {self.action_var.get()} at {self.location_var.get()}, theme {self.theme_var.get().lower()}.")
        lines.append(f"Camera: {self.camera_var.get()}. Lighting: {self.light_var.get()}.")

        if self.depth_var.get():  lines.append("Use strong depth cues: foreground/midground/background layers and tasteful overlaps.")
        if self.motion_var.get(): lines.append("Add subtle motion: cloth/hair in motion, drifting dust or embers.")

        if self.allow_conflict.get():
            lines.append("If monsters and characters are present, allow direct conflict and clear opposing body language.")

        # Individuals
        if not self.prompt_bus.items:
            lines.append("No individuals selected.")
            return lines

        lines.append("Individuals (in composition order; higher weight = more visual priority):")
        for i, it in enumerate(self.prompt_bus.items, 1):
            role = "Character" if it["type"] == "character" else "Monster"
            lines.append(f"{i:02d}. [{role}] weight {it['weight']} — {it['label']}.")
        # Append their prompts (full text) after a separator
        lines.append("—— Individual detailed prompts ——")
        for i, it in enumerate(self.prompt_bus.items, 1):
            lines.append(f"[{it['label']}] {it['text']}")

        return lines

    def generate_prompt(self):
        text = " ".join(self._build_group_lines())
        self._last_prompt = text
        self.output.delete("1.0", "end")
        self.output.insert("1.0", text)

    def open_copy(self):
        txt = self.output.get("1.0","end-1c").strip()
        if not txt:
            messagebox.showwarning("No prompt", "Generate the group prompt first.")
            return
        win = tk.Toplevel(self.frame); win.title("Copy"); win.configure(bg=WHITE); win.geometry("900x480")
        t = tk.Text(win, wrap="word", bg=WHITE); t.pack(fill="both", expand=True, padx=8, pady=8)
        t.insert("1.0", txt); t.focus_set(); t.tag_add("sel","1.0","end")
        ttk.Button(win, text="Copy to clipboard",
                   command=lambda: (self.frame.clipboard_clear(), self.frame.clipboard_append(t.get("1.0","end-1c")),
                                    messagebox.showinfo("Copied","Group prompt copied."))).pack(pady=6)

    def export_txt(self):
        txt = self.output.get("1.0","end-1c").strip()
        if not txt:
            messagebox.showwarning("No prompt", "Generate the group prompt first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text file","*.txt")],
                                            title="Export group prompt")
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            f.write(txt)
        messagebox.showinfo("Exported", f"Saved to:\n{path}")

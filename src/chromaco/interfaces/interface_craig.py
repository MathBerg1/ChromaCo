import tkinter as tk
from tkinter import messagebox
import numpy as np

# --- Color Palette (Matching InterfaceHauteur) ---
BG       = "#0f1117"
SURFACE  = "#1a1d27"
SURFACE2 = "#20243a"
BORDER   = "#2a2d3e"
ACCENT   = "#4f9cf9"
TEXT_PRI = "#e8eaf2"
TEXT_SEC = "#7b80a0"
SUCCESS  = "#68d391"
WARNING  = "#f6ad55"
DANGER   = "#f7706a"

def _dpi_scale(win):
    try:
        scale = win.winfo_fpixels("1i") / 72
        if scale > 1.25:
            win.tk.call("tk", "scaling", scale)
    except Exception:
        pass

def _section_label(parent, text):
    tk.Label(parent, text=text.upper(), font=("Segoe UI", 8, "bold"),
             fg=ACCENT, bg=BG).pack(anchor="w", pady=(0, 4))

def _styled_entry(parent, width=10):
    return tk.Entry(parent, width=width, font=("Segoe UI", 10),
                    bg=SURFACE2, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                    relief="flat", highlightbackground=BORDER,
                    highlightthickness=1, highlightcolor=ACCENT)

def _action_btn(parent, text, cmd, color, large=False):
    def lighten(h):
        r, g, b = int(h[1:3],16), int(h[3:5],16), int(h[5:7],16)
        return f"#{min(255,r+30):02x}{min(255,g+30):02x}{min(255,b+30):02x}"
    btn = tk.Label(parent, text=text, font=("Segoe UI", 10, "bold"),
                   fg=BG, bg=color, cursor="hand2",
                   padx=20, pady=10 if large else 7)
    btn.bind("<Button-1>", lambda e: cmd())
    btn.bind("<Enter>",    lambda e: btn.config(bg=lighten(color)))
    btn.bind("<Leave>",    lambda e: btn.config(bg=color))
    return btn

def _labelled_entry_row(parent, label_text, width=10):
    row = tk.Frame(parent, bg=SURFACE)
    row.pack(fill="x", padx=14, pady=6)
    tk.Label(row, text=label_text, font=("Segoe UI", 10),
             fg=TEXT_SEC, bg=SURFACE, anchor="w").pack(side="left", fill="x", expand=True)
    e = _styled_entry(row, width=width)
    e.pack(side="right")
    return e

def _scrollable_text(parent, height=8):
    frame = tk.Frame(parent, bg=SURFACE2, highlightbackground=BORDER,
                     highlightthickness=1)
    sb = tk.Scrollbar(frame, orient="vertical")
    sb.pack(side="right", fill="y")
    t = tk.Text(frame, height=height, font=("Segoe UI Mono", 10),
                bg=SURFACE2, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                relief="flat", highlightthickness=0,
                selectbackground=ACCENT, selectforeground=BG,
                wrap="none", padx=8, pady=6,
                yscrollcommand=sb.set)
    t.pack(side="left", fill="both", expand=True)
    sb.config(command=t.yview)
    return frame, t

class InterfaceCraigBattery:
    def __init__(self, parent):
        self.fenetre = tk.Toplevel(parent)
        self.fenetre.title("Craig Battery Simulation")
        self.fenetre.geometry("800x900")
        self.fenetre.resizable(True, True)
        self.fenetre.config(bg=BG)
        _dpi_scale(self.fenetre)

        # Header
        hdr = tk.Frame(self.fenetre, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(24, 0))
        tk.Label(hdr, text="C H R O M A C O", font=("Segoe UI", 8, "bold"),
                 fg=ACCENT, bg=BG).pack(anchor="w")
        tk.Label(hdr, text="Craig Counter-Current Distribution",
                 font=("Segoe UI", 20, "bold"), fg=TEXT_PRI, bg=BG).pack(anchor="w", pady=(2,1))
        tk.Label(hdr, text="H = L / N via partition coefficient (K) and stepwise transfers",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=BG).pack(anchor="w")
        tk.Frame(self.fenetre, bg=ACCENT, height=2).pack(fill="x", padx=28, pady=(12, 0))

        # Scrollable Container
        scroll_outer = tk.Frame(self.fenetre, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=28, pady=(14, 0))

        self._canvas = tk.Canvas(scroll_outer, bg=BG, highlightthickness=0, bd=0)
        gsb = tk.Scrollbar(scroll_outer, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=gsb.set)
        gsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        sf = tk.Frame(self._canvas, bg=BG)
        self._sf_win = self._canvas.create_window((0, 0), window=sf, anchor="nw")
        sf.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._sf_win, width=e.width))

        self._canvas.bind("<MouseWheel>", lambda e: self._canvas.yview_scroll(int(-e.delta/120), "units"))
        self._canvas.bind("<Button-4>",   lambda e: self._canvas.yview_scroll(-1, "units"))
        self._canvas.bind("<Button-5>",   lambda e: self._canvas.yview_scroll(1,  "units"))
        self._canvas.bind("<Enter>", lambda e: self._canvas.focus_set())

        PAD = {"padx": 0, "pady": 8, "fill": "x"}

        # --- Section 1: Configuration ---
        wrap1 = tk.Frame(sf, bg=BG)
        wrap1.pack(**PAD)
        _section_label(wrap1, "Simulation Parameters")
        card1 = tk.Frame(wrap1, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        card1.pack(fill="x")

        self.ent_n_tubes = _labelled_entry_row(card1, "Number of Tubes (0 to n-1)", width=6)
        self.ent_n_steps = _labelled_entry_row(card1, "Number of Steps", width=6)
        
        tk.Frame(card1, bg=BORDER, height=1).pack(fill="x", padx=14, pady=4)
        
        tk.Label(card1, text="Partition Coefficients (K = C_stat / C_mob)",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=SURFACE, anchor="w").pack(anchor="w", padx=14, pady=(8, 2))
        self.text_k_values = _scrollable_text(card1, height=4)[1]
        # Updated default text to be clearer and easier to parse
        self.text_k_values.insert("1.0", "A: 0.5\nB: 2.0\nC: 5.0")
        
        tk.Frame(card1, bg=BORDER, height=1).pack(fill="x", padx=14, pady=4)
        
        self.ent_initial_load = _labelled_entry_row(card1, "Initial Load (optional, comma separated)", width=20)
        self.ent_initial_load.insert(0, "A:1.0, B:1.0")

        tk.Frame(card1, bg=BORDER, height=1).pack(fill="x", padx=14, pady=12)
        btn_row = tk.Frame(card1, bg=SURFACE)
        btn_row.pack(fill="x", padx=14, pady=8)
        _action_btn(btn_row, "  Initialize Data", self._validate_input, WARNING).pack(side="left")

        # --- Section 2: Visualization Controls ---
        wrap2 = tk.Frame(sf, bg=BG)
        wrap2.pack(**PAD)
        _section_label(wrap2, "Visualization")
        card2 = tk.Frame(wrap2, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        card2.pack(fill="x")

        self.chk_visualize = tk.Checkbutton(card2, text="Enable Step-by-Step Console Output",
                                            bg=SURFACE, fg=TEXT_PRI, selectcolor=SURFACE,
                                            activebackground=SURFACE2, activeforeground=TEXT_PRI)
        self.chk_visualize.pack(anchor="w", padx=14, pady=(8, 2))

        self.ent_visual_interval = _labelled_entry_row(card2, "Update Interval (steps)", width=6)
        self.ent_visual_interval.insert(0, "5")

        tk.Frame(card2, bg=BORDER, height=1).pack(fill="x", padx=14, pady=12)
        _action_btn(card2, "  Start Simulation", self._run_simulation, ACCENT, large=True).pack(pady=4)

        # --- Section 3: Output ---
        wrap3 = tk.Frame(sf, bg=BG)
        wrap3.pack(**PAD)
        _section_label(wrap3, "Simulation Output")
        card3 = tk.Frame(wrap3, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        card3.pack(fill="x", pady=(12, 0))

        tk.Label(card3, text="Console Log / Summary", font=("Segoe UI", 8),
                 fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=14, pady=(8, 2))
        
        log_frame, self.text_log = _scrollable_text(card3, height=15)
        log_frame.pack(fill="x", padx=14, pady=(0, 12))
        
        self.text_log.config(state="disabled")

        # --- Section 4: Results Summary ---
        wrap4 = tk.Frame(sf, bg=BG)
        wrap4.pack(**PAD)
        _section_label(wrap4, "Final Distribution Summary")
        card4 = tk.Frame(wrap4, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        card4.pack(fill="x", pady=(12, 0))

        self.label_final_summary = tk.Label(card4, text="Run simulation to see results.",
                                            font=("Segoe UI", 11), fg=TEXT_SEC, bg=SURFACE, anchor="w", padx=14, pady=12)
        self.label_final_summary.pack(fill="x")

    def _safe_float(self, s):
        if not s or not s.strip():
            return None
        s = s.strip().replace(",", ".")
        try:
            return float(s)
        except ValueError:
            raise ValueError(f"Invalid number: '{s}'")

    def _append_log(self, text, color=TEXT_PRI):
        self.text_log.config(state="normal")
        self.text_log.insert("end", text + "\n")
        self.text_log.see("end")
        self.text_log.config(state="disabled")

    def _validate_input(self):
        try:
            # Validate Integers
            n_tubes_val = self._safe_float(self.ent_n_tubes.get())
            n_steps_val = self._safe_float(self.ent_n_steps.get())
            
            if n_tubes_val is None or n_steps_val is None:
                raise ValueError("Tubes and steps cannot be empty.")

            n_tubes = int(n_tubes_val)
            n_steps = int(n_steps_val)
            
            if n_tubes <= 0 or n_steps <= 0:
                raise ValueError("Tubes and steps must be positive integers.")
            
            # Parse K values
            raw_k = self.text_k_values.get("1.0", "end").strip()
            k_values = {}
            for line in raw_k.splitlines():
                line = line.strip()
                # Skip empty lines, comments, and lines that look like instructions (e.g., starting with 'Example' or 'A:')
                if not line or line.startswith("#") or line.lower().startswith("example"):
                    continue
                
                if ":" in line:
                    name, val = line.split(":", 1)
                    k_val = self._safe_float(val)
                    if k_val is None:
                        raise ValueError(f"Invalid K value for '{name.strip()}' (value: '{val.strip()}')")
                    k_values[name.strip()] = k_val
                else:
                    # Skip lines without a colon
                    continue
            
            if not k_values:
                raise ValueError("No valid K values found. Use format 'Name: Value' (e.g., A: 0.5).")
            
            # Parse Initial Load
            raw_load = self.ent_initial_load.get().strip()
            initial_load = {}
            if raw_load:
                for item in raw_load.split(","):
                    if ":" in item:
                        name, val = item.split(":", 1)
                        load_val = self._safe_float(val)
                        if load_val is None:
                            raise ValueError(f"Invalid load value for '{name.strip()}'")
                        initial_load[name.strip()] = load_val
            
            # Store valid data for simulation
            self.sim_params = {
                "n_tubes": int(n_tubes),
                "n_steps": int(n_steps),
                "k_values": k_values,
                "initial_load": initial_load if initial_load else None,
                "visualize": self.chk_visualize.select() == 1,
                "interval": int(self._safe_float(self.ent_visual_interval.get())) if self.chk_visualize.select() == 1 else 0
            }
            
            self.label_final_summary.config(text="Configuration Valid. Click 'Start Simulation'.", fg=SUCCESS)
            self._append_log("✓ Configuration validated successfully.")
            self._append_log(f"  Loaded {len(k_values)} compounds: {', '.join(k_values.keys())}")
            
        except ValueError as e:
            self.label_final_summary.config(text=f"Input Error: {str(e)}", fg=DANGER)
            self._append_log(f"✗ Validation Error: {str(e)}")
            return False
        except Exception as e:
            self.label_final_summary.config(text=f"Unexpected Error: {str(e)}", fg=DANGER)
            self._append_log(f"✗ Unexpected Error: {str(e)}")
            return False
        
        return True

    def _run_simulation(self):
        if not hasattr(self, 'sim_params'):
            if not self._validate_input():
                return

        p = self.sim_params
        n_tubes = p["n_tubes"]
        n_steps = p["n_steps"]
        k_values = p["k_values"]
        initial_load = p["initial_load"]
        visualize = p["visualize"]
        interval = p["interval"]

        self._append_log(f"Starting Simulation: {n_tubes} tubes, {n_steps} steps.")
        self._append_log(f"Compounds: {', '.join(k_values.keys())}")
        
        # Ensure initial load matches keys and is never None
        if initial_load is None:
            initial_load = {name: 1.0 for name in k_values}
        
        if set(initial_load.keys()) != set(k_values.keys()):
            # Auto-fill missing with 1.0
            for name in k_values:
                if name not in initial_load:
                    initial_load[name] = 1.0
        
        # CRITICAL FIX: Ensure no None values exist in initial_load
        for name in k_values:
            if initial_load.get(name) is None:
                initial_load[name] = 1.0

        try:
            history = self._simulate_craig(n_tubes, n_steps, k_values, initial_load, visualize, interval)
            
            # Generate Summary
            summary_lines = []
            for name in k_values:
                profile = history[name][n_steps-1, :]
                max_pos = np.argmax(profile)
                max_val = np.max(profile)
                summary_lines.append(f"  {name}: Peak at Tube {max_pos} (Val: {max_val:.2f})")
            
            self.label_final_summary.config(text="\n".join(summary_lines), fg=SUCCESS)
            self._append_log("Simulation Complete.")
            
        except Exception as e:
            self.label_final_summary.config(text=f"Simulation Error: {str(e)}", fg=DANGER)
            self._append_log(f"✗ Simulation Failed: {str(e)}")

    def _simulate_craig(self, n_tubes, n_steps, k_values, initial_load, visualize, interval):
        history = {name: np.zeros((n_steps, n_tubes)) for name in k_values}
        current_state = {name: np.zeros(n_tubes) for name in k_values}
        
        # Initial load
        for name, amount in initial_load.items():
            current_state[name][0] = amount
            history[name][0, :] = current_state[name].copy()
            
        if visualize:
            self._append_log(f"Visualization active (every {interval} steps).\n")
            header = f"{'Step':>4} | " + " | ".join([f"T{i:>2}" for i in range(min(n_tubes, 10))])
            if n_tubes > 10: header += " | ..."
            self._append_log(header)
            self._append_log("-" * len(header))

        for step in range(1, n_steps):
            for name, K in k_values.items():
                q_tot = current_state[name]
                p = 1.0 / (1.0 + K) 
                q = K / (1.0 + K)   
                
                c_mobile = q_tot * p
                c_stationary = q_tot * q
                
                new_mobile = np.zeros(n_tubes)
                if n_tubes > 1:
                    new_mobile[1:] = c_mobile[:-1]
                
                current_state[name] = new_mobile + c_stationary
                history[name][step, :] = current_state[name].copy()
            
            if visualize and (step % interval == 0 or step == n_steps - 1):
                summary = f"{step:>4} | "
                for name in k_values.keys():
                    profile = history[name][step, :]
                    max_pos = np.argmax(profile)
                    max_val = np.max(profile)
                    summary += f"{name.split()[0]}:{max_pos}({max_val:.2f}) | "
                self._append_log(summary)
                
                # Optional: Mini-bar for first compound
                if step % (interval * 2) == 0:
                    first_compound = list(k_values.keys())[0]
                    profile = history[first_compound][step, :]
                    max_val = np.max(profile)
                    if max_val > 0:
                        line = ""
                        limit = min(n_tubes, 30)
                        for i in range(limit):
                            if profile[i] > max_val * 0.1: line += "#"
                            elif profile[i] > 0: line += "."
                            else: line += " "
                        self._append_log(f"       Profile ({first_compound}): [{line}]")

        return history
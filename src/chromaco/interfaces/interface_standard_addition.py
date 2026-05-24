import tkinter as tk
import sys
import os
from tkinter import messagebox
from chromaco.interfaces.fonctions_colonnes import plot_standard_addition

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

def _styled_entry(parent, width=14):
    return tk.Entry(parent, width=width, font=("Segoe UI", 10),
                    bg=SURFACE2, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                    relief="flat", highlightbackground=BORDER,
                    highlightthickness=1, highlightcolor=ACCENT)

def _action_btn(parent, text, cmd, color, large=False):
    def lighten(h):
        r,g,b = int(h[1:3],16), int(h[3:5],16), int(h[5:7],16)
        return f"#{min(255,r+30):02x}{min(255,g+30):02x}{min(255,b+30):02x}"
    btn = tk.Label(parent, text=text, font=("Segoe UI", 10, "bold"),
                   fg=BG, bg=color, cursor="hand2",
                   padx=20, pady=10 if large else 7)
    btn.bind("<Button-1>", lambda e: cmd())
    btn.bind("<Enter>",    lambda e: btn.config(bg=lighten(color)))
    btn.bind("<Leave>",    lambda e: btn.config(bg=color))
    return btn

def _labelled_entry_row(parent, label_text, width=14):
    row = tk.Frame(parent, bg=SURFACE)
    row.pack(fill="x", padx=14, pady=6)
    tk.Label(row, text=label_text, font=("Segoe UI", 10),
             fg=TEXT_SEC, bg=SURFACE).pack(side="left", fill="x", expand=True)
    e = _styled_entry(row, width=width)
    e.pack(side="right")
    return e

def _scrollable_text(parent, height=5):
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

def _scrollable_listbox(parent, height=5):
    frame = tk.Frame(parent, bg=SURFACE2, highlightbackground=BORDER,
                     highlightthickness=1)
    sb = tk.Scrollbar(frame, orient="vertical")
    sb.pack(side="right", fill="y")
    lb = tk.Listbox(frame, height=height, font=("Segoe UI Mono", 10),
                    bg=SURFACE2, fg=TEXT_PRI,
                    selectbackground=ACCENT, selectforeground=BG,
                    relief="flat", highlightthickness=0,
                    activestyle="none", selectmode="single",
                    borderwidth=0, yscrollcommand=sb.set)
    lb.pack(side="left", fill="both", expand=True)
    sb.config(command=lb.yview)
    return frame, lb

def _back_button_to_menu(win, label="← Back to menu"):
    bar = tk.Frame(win, bg=BG)
    bar.pack(fill="x", padx=28, pady=(8, 0))
    btn = tk.Label(bar, text=label, font=("Segoe UI", 9),
                   fg=TEXT_SEC, bg=BG, cursor="hand2")
    btn.pack(side="right")
    btn.bind("<Button-1>", lambda e: win.destroy())
    btn.bind("<Enter>",    lambda e: btn.config(fg=TEXT_PRI))
    btn.bind("<Leave>",    lambda e: btn.config(fg=TEXT_SEC))

class StandardAdditionInterface:
    def __init__(self, parent):

        self.window = tk.Toplevel(parent)
        self.window.title("Standard Addition Method")
        self.window.geometry("620x780")
        self.window.resizable(True, True)
        self.window.config(bg=BG)
        _back_button_to_menu(self.window)
        _dpi_scale(self.window)

        header = tk.Frame(self.window, bg=BG)
        header.pack(fill="x", padx=28, pady=(24, 0))
        tk.Label(header, text="C H R O M A C O", font=("Segoe UI", 8, "bold"),
                 fg=ACCENT, bg=BG).pack(anchor="w")
        tk.Label(header, text="Standard Addition Method",
                 font=("Segoe UI", 20, "bold"), fg=TEXT_PRI, bg=BG).pack(anchor="w")
        tk.Label(header, text="y = a·x + b  →  C_unknown = −b / a",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=BG).pack(anchor="w")
        tk.Frame(self.window, bg=ACCENT, height=2).pack(fill="x", padx=28, pady=(12, 0))

        scroll_outer = tk.Frame(self.window, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=28, pady=(14, 0))

        self.canvas = tk.Canvas(scroll_outer, bg=BG, highlightthickness=0, bd=0)
        gsb = tk.Scrollbar(scroll_outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=gsb.set)
        gsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        sf = tk.Frame(self.canvas, bg=BG)
        self.sf_window = self.canvas.create_window((0, 0), window=sf, anchor="nw")
        sf.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.sf_window, width=e.width))

        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-e.delta/120), "units"))
        self.canvas.bind("<Button-4>",   lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>",   lambda e: self.canvas.yview_scroll(1,  "units"))
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())

        PAD = {"padx": 0, "pady": 8, "fill": "x"}

        wrap = tk.Frame(sf, bg=BG)
        wrap.pack(**PAD)
        _section_label(wrap, "Manual Input")
        card = tk.Frame(wrap, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x")

        self.entry_conc = _labelled_entry_row(card, "Concentration added")
        self.entry_area = _labelled_entry_row(card, "Peak area")

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=14)
        btn_row = tk.Frame(card, bg=SURFACE)
        btn_row.pack(fill="x", padx=14, pady=12)

        _action_btn(btn_row, "  Add Point", self._add_point, WARNING).pack(side="left")
        _action_btn(btn_row, "  Remove Last", self._remove_last_point, DANGER).pack(side="left", padx=6)
        _action_btn(btn_row, "  Clear All", self._clear_all, DANGER).pack(side="left")

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=14)

        wrap_units = tk.Frame(sf, bg=BG)
        wrap_units.pack(**PAD)
        _section_label(wrap_units, "Units")
        card_units = tk.Frame(wrap_units, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        card_units.pack(fill="x")

        self.entry_unit = _labelled_entry_row(card_units, "Concentration unit")
        self.entry_unit.insert(0, "mg/L")

        wrap2 = tk.Frame(sf, bg=BG)
        wrap2.pack(**PAD)
        _section_label(wrap2, "Paste from Excel")
        card2 = tk.Frame(wrap2, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        card2.pack(fill="x")

        tk.Label(card2,
                 text="Paste two columns: concentration added | peak area\nInclude the blank row (concentration = 0).",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=14, pady=(10,4))

        tk.Frame(card2, bg=BORDER, height=1).pack(fill="x", padx=14, pady=(4,0))

        tk.Label(card2, text="Paste area", font=("Segoe UI", 8),
                 fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=14, pady=(8, 2))
        paste_frame, self.text_paste = _scrollable_text(card2, height=5)
        paste_frame.pack(fill="x", padx=14, pady=(0, 6))

        self.text_paste.bind("<MouseWheel>", lambda e: self.text_paste.yview_scroll(int(-e.delta/120), "units"))
        self.text_paste.bind("<Button-4>",   lambda e: self.text_paste.yview_scroll(-1, "units"))
        self.text_paste.bind("<Button-5>",   lambda e: self.text_paste.yview_scroll(1,  "units"))

        self.text_paste.bind("<Control-v>", self._on_paste)
        self.text_paste.bind("<<Paste>>",   self._on_paste)

        parse_row = tk.Frame(card2, bg=SURFACE)
        parse_row.pack(fill="x", padx=14, pady=(0, 10))
        _action_btn(parse_row, "  Parse Data", self._parse_paste, WARNING).pack(side="left")

        tk.Frame(card2, bg=BORDER, height=1).pack(fill="x", padx=14)

        tk.Label(card2, text="Data points", font=("Segoe UI", 8),
                 fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=14, pady=(8,2))
        list_frame, self.listbox = _scrollable_listbox(card2, height=6)
        list_frame.pack(fill="x", padx=14, pady=(0,12))

        self.listbox.bind("<MouseWheel>", lambda e: self.listbox.yview_scroll(int(-e.delta/120), "units"))
        self.listbox.bind("<Button-4>",   lambda e: self.listbox.yview_scroll(-1, "units"))
        self.listbox.bind("<Button-5>",   lambda e: self.listbox.yview_scroll(1,  "units"))

        self.points = []

        _action_btn(sf, "  Calculate Unknown Concentration", self._calculate, SUCCESS, large=True).pack(pady=(4, 0))

        self.label_result = tk.Label(sf, text="", font=("Segoe UI", 11, "bold"),
                                     fg=SUCCESS, bg=BG)
        self.label_result.pack(pady=(10, 0))

        self.label_details = tk.Label(sf, text="", font=("Segoe UI", 9),
                                      fg=TEXT_SEC, bg=BG)
        self.label_details.pack()

        self.label_error = tk.Label(sf, text="", font=("Segoe UI", 9),
                                    fg=DANGER, bg=BG)
        self.label_error.pack(pady=(2,16))

    def _add_point(self):
        try:
            c = float(self.entry_conc.get().replace(",", "."))
            a = float(self.entry_area.get().replace(",", "."))
        except ValueError:
            self.label_error.config(text="Please enter valid numbers.")
            return
        self.points.append((c, a))
        self._refresh_listbox()
        self.entry_conc.delete(0, "end")
        self.entry_area.delete(0, "end")
        self.label_error.config(text="")

    def _remove_last_point(self):
        if self.points:
            self.points.pop()
            self._refresh_listbox()

    def _clear_all(self):
        self.points = []
        self._refresh_listbox()
        self.label_result.config(text="")
        self.label_details.config(text="")
        self.label_error.config(text="")

    def _refresh_listbox(self):
        self.listbox.delete(0, "end")
        for i, (c, a) in enumerate(self.points):
            self.listbox.insert("end", f"  {i+1:>2}.   {c:>20.4f}   {a:>16.4f}")

    def _on_paste(self, event=None):
        self.window.after(100, self._parse_paste)

    def _parse_paste(self):
        raw = self.text_paste.get("1.0", "end").strip()
        if not raw:
            self.label_error.config(text="Nothing to parse.")
            return

        new_points = []
        for line in raw.splitlines():
            parts = line.replace(";", "\t").split("\t")
            if len(parts) < 2:
                parts = line.split()
            if len(parts) < 2:
                continue
            try:
                c = float(parts[0].replace(",", "."))
                a = float(parts[1].replace(",", "."))
                new_points.append((c, a))
            except ValueError:
                continue

        if not new_points:
            self.label_error.config(text="No valid rows found.")
            return

        self.points = new_points
        self._refresh_listbox()
        self.label_error.config(text=f"{len(self.points)} point(s) loaded successfully.")

    def _calculate(self):
        if len(self.points) < 2:
            messagebox.showwarning("Not enough points", "Please enter at least 2 data points.", parent=self.window)
            return

        concentrations = [p[0] for p in self.points]
        areas = [p[1] for p in self.points]
        unit = self.entry_unit.get().strip()

        try:
            result = plot_standard_addition(concentrations, areas, show_plot=False)
        except ValueError as e:
            self.label_error.config(text=str(e))
            self.label_result.config(text="")
            self.label_details.config(text="")
            return

        C = abs(result["C_unknown"])
        a = result["a"]
        b = result["b"]
        r2 = result["r2"]

        sign = "+" if b >= 0 else "-"

        self.label_result.config(text=f"Unknown concentration: {C:.6f} {unit}")
        self.label_details.config(text=f"y = {a:.4f}x {sign} {abs(b):.4f}    R² = {r2:.4f}")
        self.label_error.config(text="")

        plot_standard_addition(concentrations, areas, show_plot=True)

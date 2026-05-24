import tkinter as tk
from tkinter import messagebox
from chromaco.interfaces.fonctions_colonnes import calculate_selectivity_factor, calculate_retention_factor

# ── Palette (identical to InterfaceHauteur) ──────────────────────────────────
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


# ── Helpers (copied verbatim from the shared UI toolkit) ─────────────────────

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
        r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
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
             fg=TEXT_SEC, bg=SURFACE, anchor="w").pack(side="left", fill="x", expand=True)
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

# ── Main interface ────────────────────────────────────────────────────────────

class InterfaceSelectivity:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Selectivity Factor")
        self.window.geometry("650x820")
        self.window.resizable(True, True)
        self.window.config(bg=BG)
        _back_button_to_menu(self.window)
        _dpi_scale(self.window)

        # ── Header ────────────────────────────────────────────────────────────
        header = tk.Frame(self.window, bg=BG)
        header.pack(fill="x", padx=28, pady=(24, 0))
        tk.Label(header, text="C H R O M A C O", font=("Segoe UI", 8, "bold"),
                 fg=ACCENT, bg=BG).pack(anchor="w")
        tk.Label(header, text="Selectivity Factor",
                 font=("Segoe UI", 20, "bold"), fg=TEXT_PRI, bg=BG).pack(anchor="w", pady=(2, 1))
        tk.Label(header, text="α = k₂ / k₁   where   k = (tᵣ − t₀) / t₀",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=BG).pack(anchor="w")
        tk.Frame(self.window, bg=ACCENT, height=2).pack(fill="x", padx=28, pady=(12, 0))

        # ── Scrollable canvas ─────────────────────────────────────────────────
        scroll_outer = tk.Frame(self.window, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=28, pady=(14, 0))

        self.canvas = tk.Canvas(scroll_outer, bg=BG, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(scroll_outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        inner_frame = tk.Frame(self.canvas, bg=BG)
        self.window_id = self.canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        inner_frame.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(
            self.window_id, width=e.width))

        for seq, fn in (("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units")),
                        ("<Button-4>",   lambda e: self.canvas.yview_scroll(-1, "units")),
                        ("<Button-5>",   lambda e: self.canvas.yview_scroll(1,  "units"))):
            self.canvas.bind(seq, fn)
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())

        PAD = {"padx": 0, "pady": 8, "fill": "x"}

        # ── Card 1 – Manual input ─────────────────────────────────────────────
        wrapper = tk.Frame(inner_frame, bg=BG)
        wrapper.pack(**PAD)
        _section_label(wrapper, "Manual Input")
        card = tk.Frame(wrapper, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x")

        self.entry_tr1 = _labelled_entry_row(card, "Retention time peak 1  tᵣ₁ (min)")
        self.entry_tr2 = _labelled_entry_row(card, "Retention time peak 2  tᵣ₂ (min)")
        self.entry_t0  = _labelled_entry_row(card, "Dead time  t₀ (min)")

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=14)
        btn_row = tk.Frame(card, bg=SURFACE)
        btn_row.pack(fill="x", padx=14, pady=12)
        _action_btn(btn_row, "  Calculate", self._calculate_manual, ACCENT).pack(side="left")

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=14)
        result_row = tk.Frame(card, bg=SURFACE)
        result_row.pack(fill="x", padx=14, pady=14)

        self.label_manual_result = tk.Label(
            result_row, text="—", font=("Segoe UI", 13, "bold"),
            fg=TEXT_SEC, bg=SURFACE, anchor="w")
        self.label_manual_result.pack(fill="x")

        # sub-labels for k1, k2
        self.label_manual_k = tk.Label(
            result_row, text="", font=("Segoe UI", 9),
            fg=TEXT_SEC, bg=SURFACE, anchor="w")
        self.label_manual_k.pack(fill="x")

        self.label_manual_error = tk.Label(
            result_row, text="", font=("Segoe UI", 9),
            fg=DANGER, bg=SURFACE, anchor="w")
        self.label_manual_error.pack(fill="x")

        # ── Card 2 – Paste from Excel ─────────────────────────────────────────
        wrapper2 = tk.Frame(inner_frame, bg=BG)
        wrapper2.pack(**PAD)
        _section_label(wrapper2, "Paste from Excel")
        card2 = tk.Frame(wrapper2, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        card2.pack(fill="x")

        tk.Label(card2,
                 text="Paste two columns: tᵣ₁  |  tᵣ₂\n"
                      "Select a row then click 'Calculate selected row'.",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=SURFACE,
                 justify="left").pack(anchor="w", padx=14, pady=(10, 4))

        self.entry_t0_paste = _labelled_entry_row(card2, "Dead time  t₀ (min)")

        tk.Frame(card2, bg=BORDER, height=1).pack(fill="x", padx=14, pady=(4, 0))

        tk.Label(card2, text="Paste area", font=("Segoe UI", 8),
                 fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=14, pady=(8, 2))
        paste_frame, self.text_paste = _scrollable_text(card2, height=5)
        paste_frame.pack(fill="x", padx=14, pady=(0, 6))

        for seq, fn in (("<MouseWheel>", lambda e: self.text_paste.yview_scroll(int(-e.delta / 120), "units")),
                        ("<Button-4>",   lambda e: self.text_paste.yview_scroll(-1, "units")),
                        ("<Button-5>",   lambda e: self.text_paste.yview_scroll(1,  "units"))):
            self.text_paste.bind(seq, fn)

        self.text_paste.bind("<Control-v>", self._on_paste)
        self.text_paste.bind("<<Paste>>",   self._on_paste)

        parse_row = tk.Frame(card2, bg=SURFACE)
        parse_row.pack(fill="x", padx=14, pady=(0, 10))
        _action_btn(parse_row, "  Parse Data", self._parse_paste, WARNING).pack(side="left")

        tk.Frame(card2, bg=BORDER, height=1).pack(fill="x", padx=14)
        tk.Label(card2, text="Parsed rows — click to select",
                 font=("Segoe UI", 8), fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=14, pady=(8, 2))
        list_frame, self.listbox = _scrollable_listbox(card2, height=5)
        list_frame.pack(fill="x", padx=14, pady=(0, 12))

        for seq, fn in (("<MouseWheel>", lambda e: self.listbox.yview_scroll(int(-e.delta / 120), "units")),
                        ("<Button-4>",   lambda e: self.listbox.yview_scroll(-1, "units")),
                        ("<Button-5>",   lambda e: self.listbox.yview_scroll(1,  "units"))):
            self.listbox.bind(seq, fn)

        self.rows = []

        # ── Bottom calculate button + result labels ───────────────────────────
        _action_btn(inner_frame, "  Calculate Selected Row", self._calculate_row,
                    SUCCESS, large=True).pack(pady=(4, 0))

        self.label_result = tk.Label(inner_frame, text="", font=("Segoe UI", 11, "bold"),
                                     fg=SUCCESS, bg=BG)
        self.label_result.pack(pady=(10, 0))

        self.label_detail = tk.Label(inner_frame, text="", font=("Segoe UI", 9),
                                     fg=TEXT_SEC, bg=BG)
        self.label_detail.pack(pady=(2, 0))

        self.label_error = tk.Label(inner_frame, text="", font=("Segoe UI", 9),
                                    fg=DANGER, bg=BG)
        self.label_error.pack(pady=(2, 16))

    # ── Calculation helpers ───────────────────────────────────────────────────

    def _run_calculation(self, t_r1, t_r2, t_0):
        """Return (alpha, k1, k2) or raise."""
        k1 = calculate_retention_factor(t_r1, t_0)
        k2 = calculate_retention_factor(t_r2, t_0)
        alpha = (k2 / k1) if k2 >= k1 else (k1 / k2)
        return alpha, k1, k2

    # ── Manual section ────────────────────────────────────────────────────────

    def _calculate_manual(self):
        try:
            t_r1 = float(self.entry_tr1.get().replace(",", "."))
            t_r2 = float(self.entry_tr2.get().replace(",", "."))
            t_0  = float(self.entry_t0.get().replace(",", "."))
            alpha, k1, k2 = self._run_calculation(t_r1, t_r2, t_0)
            self.label_manual_result.config(text=f"α  =  {alpha:.6f}", fg=SUCCESS)
            self.label_manual_k.config(
                text=f"k₁ = {k1:.4f}   k₂ = {k2:.4f}", fg=TEXT_SEC)
            self.label_manual_error.config(text="")
        except ValueError as exc:
            self.label_manual_error.config(text=str(exc))
            self.label_manual_result.config(text="—", fg=TEXT_SEC)
            self.label_manual_k.config(text="")

    # ── Paste section ─────────────────────────────────────────────────────────

    def _on_paste(self, event=None):
        self.window.after(100, self._parse_paste)

    def _parse_paste(self):
        raw = self.text_paste.get("1.0", "end").strip()
        if not raw:
            self.label_error.config(text="Nothing to parse.")
            return

        self.rows = []
        self.listbox.delete(0, "end")

        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.replace(";", "\t").split("\t")
            if len(parts) < 2:
                parts = line.split()
            if len(parts) < 2:
                continue
            try:
                t_r1 = float(parts[0].replace(",", "."))
                t_r2 = float(parts[1].replace(",", "."))
                self.rows.append((t_r1, t_r2))
                self.listbox.insert(
                    "end",
                    f"  tᵣ₁ = {t_r1:>10.4f}    tᵣ₂ = {t_r2:>10.4f}")
            except ValueError:
                continue

        if not self.rows:
            self.label_error.config(text="No valid rows found (need 2 columns per row).")
        else:
            self.label_error.config(text=f"✔  {len(self.rows)} row(s) parsed.")
            self.label_result.config(text="")
            self.label_detail.config(text="")

    def _calculate_row(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No selection",
                                   "Please click a row in the list first.",
                                   parent=self.window)
            return

        idx = selection[0]
        t_r1, t_r2 = self.rows[idx]
        try:
            t_0 = float(self.entry_t0_paste.get().replace(",", "."))
        except ValueError:
            self.label_error.config(text="Please enter a valid dead time t₀.")
            return
        try:
            alpha, k1, k2 = self._run_calculation(t_r1, t_r2, t_0)
            self.label_result.config(text=f"α = {alpha:.6f}")
            self.label_detail.config(text=f"k₁ = {k1:.4f}   k₂ = {k2:.4f}")
            self.label_error.config(text="")
        except Exception as exc:
            self.label_error.config(text=f"Calculation error: {exc}")
            self.label_result.config(text="")
            self.label_detail.config(text="")


# ── Standalone launcher ───────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()          # hide the dummy root
    app = InterfaceSelectivity(root)
    app.window.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
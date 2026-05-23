import tkinter as tk
import sys
from tkinter import messagebox
from chromaco.interfaces.fonctions_colonnes import compare_two_columns_advanced

# ── Shared design tokens ─────────────────────────────────────────────────────
BG       = "#0f1117"
SURFACE  = "#1a1d27"
SURFACE2 = "#20243a"
BORDER   = "#2a2d3e"
ACCENT   = "#b794f4"
ACCENT2  = "#4f9cf9"
TEXT_PRI = "#e8eaf2"
TEXT_SEC = "#7b80a0"
DANGER   = "#f7706a"
SUCCESS  = "#68d391"
WARNING  = "#f6ad55"


# ── Reusable widget builders ───────────────────────────────────────────────────

def styled_label_frame(parent, text):
    wrapper = tk.Frame(parent, bg=BG)
    tk.Label(wrapper, text=text.upper(), font=("Segoe UI", 8, "bold"),
             fg=ACCENT, bg=BG).pack(anchor="w", pady=(0, 4))
    inner = tk.Frame(wrapper, bg=SURFACE, highlightbackground=BORDER,
                     highlightthickness=1)
    inner.pack(fill="x")
    return wrapper, inner


def styled_entry(parent, default="", width=12):
    e = tk.Entry(parent, width=width, font=("Segoe UI", 10),
                 bg=SURFACE2, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                 relief="flat", highlightbackground=BORDER,
                 highlightthickness=1, highlightcolor=ACCENT)
    e.insert(0, default)
    return e


def scrollable_text(parent, height=5):
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


def scrollable_listbox(parent, height=6):
    frame = tk.Frame(parent, bg=SURFACE2, highlightbackground=BORDER,
                     highlightthickness=1)
    sb = tk.Scrollbar(frame, orient="vertical")
    sb.pack(side="right", fill="y")
    lb = tk.Listbox(frame, height=height, font=("Segoe UI Mono", 10),
                    bg=SURFACE2, fg=TEXT_PRI,
                    selectbackground=ACCENT, selectforeground=BG,
                    relief="flat", highlightthickness=0,
                    activestyle="none", selectmode="multiple",
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


# ───────────────────────────────────────────────────────────────────────────────
#                           INTERFACE COMPARE COLUMNS
# ───────────────────────────────────────────────────────────────────────────────

class InterfaceCompareColumns:
    def __init__(self, parent):
        self.fenetre = tk.Toplevel(parent)
        _back_button_to_menu(self.fenetre)
        self.fenetre.title("Compare Columns")
        self.fenetre.geometry("700x760")
        self.fenetre.resizable(True, True)
        self.fenetre.config(bg=BG)

        # DPI scaling
        try:
            scale = self.fenetre.winfo_fpixels("1i") / 72
            if scale > 1.25:
                self.fenetre.tk.call("tk", "scaling", scale)
        except Exception:
            pass

        # ── Header ───────────────────────────────────────────────────────────
        hdr = tk.Frame(self.fenetre, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(24, 0))
        tk.Label(hdr, text="C H R O M A C O", font=("Segoe UI", 8, "bold"),
                 fg=ACCENT, bg=BG).pack(anchor="w")
        tk.Label(hdr, text="Compare Columns", font=("Segoe UI", 20, "bold"),
                 fg=TEXT_PRI, bg=BG).pack(anchor="w", pady=(2, 2))
        tk.Label(hdr, text="Side-by-side chromatographic column analysis",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=BG).pack(anchor="w")
        tk.Frame(self.fenetre, bg=ACCENT, height=2).pack(fill="x", padx=28, pady=(12, 0))

        # ── Scrollable canvas ─────────────────────────────────────────────────
        scroll_outer = tk.Frame(self.fenetre, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=28, pady=(14, 0))

        self.canvas = tk.Canvas(scroll_outer, bg=BG, highlightthickness=0, bd=0)
        gsb = tk.Scrollbar(scroll_outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=gsb.set)
        gsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        sf = tk.Frame(self.canvas, bg=BG)
        self._sf_win = self.canvas.create_window((0, 0), window=sf, anchor="nw")

        sf.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(
            self._sf_win, width=e.width))

        self._enable_canvas_scroll()

        PAD = {"padx": 0, "pady": 8, "fill": "x"}

        # ── Column length ─────────────────────────────────────────────────────
        wrap, card = styled_label_frame(sf, "Column Configuration")
        wrap.pack(**PAD)
        row = tk.Frame(card, bg=SURFACE)
        row.pack(fill="x", padx=14, pady=12)
        tk.Label(row, text="Column length (m)", font=("Segoe UI", 10),
                 fg=TEXT_SEC, bg=SURFACE).pack(side="left")
        self.entry_length = styled_entry(row, default="0.25", width=10)
        self.entry_length.pack(side="left", padx=(12, 0))

        # ── Column A ──────────────────────────────────────────────────────────
        wrap, card = styled_label_frame(sf, "Column A — Data Input")
        wrap.pack(**PAD)
        tk.Label(card, text="Paste two columns: retention time | peak width",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=14, pady=(10, 4))
        boxA_frame, self.boxA = scrollable_text(card, height=5)
        boxA_frame.pack(fill="x", padx=14, pady=(0, 12))
        self._enable_widget_scroll(self.boxA)

        # ── Column B ──────────────────────────────────────────────────────────
        wrap, card = styled_label_frame(sf, "Column B — Data Input")
        wrap.pack(**PAD)
        tk.Label(card, text="Paste two columns: retention time | peak width",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=14, pady=(10, 4))
        boxB_frame, self.boxB = scrollable_text(card, height=5)
        boxB_frame.pack(fill="x", padx=14, pady=(0, 12))
        self._enable_widget_scroll(self.boxB)

        # ── Parse button ──────────────────────────────────────────────────────
        self._make_action_btn(sf, "  Parse Data", self._parse_all, WARNING).pack(pady=(4, 0))

        # ── Peak selection ────────────────────────────────────────────────────
        wrap, card = styled_label_frame(sf, "Peak Selection")
        wrap.pack(**PAD)
        tk.Label(card, text="If no peak is selected, all peaks will be compared.",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=14, pady=(10, 4))
        lb_frame, self.listbox_peaks = scrollable_listbox(card, height=6)
        lb_frame.pack(fill="x", padx=14, pady=(0, 12))
        self._enable_widget_scroll(self.listbox_peaks)

        # ── Compare button ────────────────────────────────────────────────────
        self._make_action_btn(sf, "  Compare Columns", self._compare, SUCCESS, large=True).pack(pady=(4, 0))

        # ── Status label ──────────────────────────────────────────────────────
        self.label_status = tk.Label(sf, text="", font=("Segoe UI", 9),
                                     fg=WARNING, bg=BG)
        self.label_status.pack(pady=(4, 0))

        # ── Results ───────────────────────────────────────────────────────────
        wrap, card = styled_label_frame(sf, "Results")
        wrap.pack(pady=(8, 16), fill="x")
        res_frame, self.text = scrollable_text(card, height=16)
        self.text.config(state="disabled", padx=12, pady=10,
                         font=("Segoe UI Mono", 9))
        res_frame.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self._enable_widget_scroll(self.text)

        self.text.tag_config("heading", foreground=ACCENT,  font=("Segoe UI", 10, "bold"))
        self.text.tag_config("col_hdr", foreground=ACCENT2, font=("Segoe UI Mono", 9, "bold"))
        self.text.tag_config("verdict", foreground=SUCCESS)
        self.text.tag_config("warning", foreground=WARNING)
        self.text.tag_config("muted",   foreground=TEXT_SEC)

        self.columnA = {}
        self.columnB = {}

    # ── Scroll management ──────────────────────────────────────────────────────

    def _scroll_delta(self, event):
        if sys.platform == "darwin":
            return -event.delta
        return int(-event.delta / 120)

    def _enable_canvas_scroll(self):
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(self._scroll_delta(e), "units"))
        self.canvas.bind("<Button-4>",   lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>",   lambda e: self.canvas.yview_scroll(1,  "units"))
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())

    def _enable_widget_scroll(self, widget):
        widget.bind("<MouseWheel>", lambda e: widget.yview_scroll(self._scroll_delta(e), "units"))
        widget.bind("<Button-4>",   lambda e: widget.yview_scroll(-1, "units"))
        widget.bind("<Button-5>",   lambda e: widget.yview_scroll(1,  "units"))

    # ── Action button ──────────────────────────────────────────────────────────

    def _make_action_btn(self, parent, text, cmd, color, large=False):
        btn = tk.Label(parent, text=text, font=("Segoe UI", 10, "bold"),
                       fg=BG, bg=color, cursor="hand2",
                       padx=20, pady=10 if large else 7)
        btn.bind("<Button-1>", lambda e: cmd())
        btn.bind("<Enter>",    lambda e: btn.config(bg=self._lighten(color)))
        btn.bind("<Leave>",    lambda e: btn.config(bg=color))
        return btn

    @staticmethod
    def _lighten(hex_color):
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        return f"#{min(255,r+30):02x}{min(255,g+30):02x}{min(255,b+30):02x}"

    # ── Parsing ────────────────────────────────────────────────────────────────

    def _parse_box(self, box):
        raw = box.get("1.0", "end").strip()
        peaks, idx = {}, 1
        for line in raw.splitlines():
            parts = line.strip().replace(",", ".").replace(";", "\t").split()
            if len(parts) < 2:
                continue
            try:
                peaks[idx] = [float(parts[0]), float(parts[1])]
                idx += 1
            except Exception:
                continue
        return peaks

    def _parse_all(self):
        self.columnA = self._parse_box(self.boxA)
        self.columnB = self._parse_box(self.boxB)
        self.listbox_peaks.delete(0, "end")
        n = min(len(self.columnA), len(self.columnB))
        for i in range(1, n + 1):
            self.listbox_peaks.insert("end", f"  Peak {i}")
        self.label_status.config(
            text=f"✔  {n} peak{'s' if n != 1 else ''} detected.", fg=SUCCESS)

    # ── Comparison ─────────────────────────────────────────────────────────────

    def _compare(self):
        selection = self.listbox_peaks.curselection()
        selected_peaks = (
            [int(self.listbox_peaks.get(i).split()[1]) for i in selection]
            if selection else None
        )
        mode = "subset" if selected_peaks else "global"

        try:
            length = float(self.entry_length.get().replace(",", "."))
        except Exception:
            messagebox.showerror("Error", "Invalid column length.")
            return

        result = compare_two_columns_advanced(
            columnA=self.columnA, columnB=self.columnB,
            column_length=length, selected_peaks=selected_peaks, mode=mode)

        self.text.config(state="normal")
        self.text.delete("1.0", "end")

        self.text.insert("end", "COMPARISON RESULTS\n", "heading")
        self.text.insert("end", "─" * 48 + "\n\n", "muted")

        self.text.insert("end", "VERDICT\n", "col_hdr")
        for key, winner in result["verdict"].items():
            param = key.replace("Best_", "").replace("_", " ").title()
            self.text.insert("end", f"  {param}: ", "muted")
            self.text.insert("end", f"Column {winner}\n", "verdict")

        for col, label in (("A", "COLUMN A"), ("B", "COLUMN B")):
            self.text.insert("end", f"\n{label}\n", "col_hdr")
            for k, v in result[col].items():
                self.text.insert("end", f"  {k}: ", "muted")
                self.text.insert("end", f"{v}\n")
            if result["warnings"][col]:
                self.text.insert("end", "\n  Warnings\n", "warning")
                for msg in result["warnings"][col]:
                    self.text.insert("end", f"    ⚠  {msg}\n", "warning")

        self.text.config(state="disabled")
        self.label_status.config(text="✔  Comparison complete.", fg=SUCCESS)
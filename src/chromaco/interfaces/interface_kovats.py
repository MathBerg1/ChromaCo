"""
chromaco_kovats.py
─────────────────────────────────────────────────────────────────────
Standalone Tkinter UI for two Kovats chromatography calculations:
  • Dead time (t_M) via the Kovats triplet method
  • Kovats Retention Index (I) via Van den Dool & Kratz

Drop this file next to your existing chromaco project and import the
two functions, or paste the stubs below for quick testing.
"""

import math
import tkinter as tk
from tkinter import messagebox
from chromaco.interfaces.fonctions_colonnes import calculate_kovats_index, calculate_dead_time_kovats

# ── colour palette (matches InterfacePlateau) ────────────────────────
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
PURPLE   = "#b57bee"


def _calculate_net_times(all_gross, alkane_data):
    tm = calculate_dead_time_kovats(alkane_data)
    return [t - tm for t in all_gross], tm


# ══════════════════════════════════════════════════════════════════════
#  Shared UI helpers  (identical API to InterfacePlateau helpers)
# ══════════════════════════════════════════════════════════════════════

def _all_widgets(widget):
    """Return widget and all its descendants."""
    yield widget
    for child in widget.winfo_children():
        yield from _all_widgets(child)


def _dpi_scale(win):
    try:
        scale = win.winfo_fpixels("1i") / 72
        if scale > 1.25:
            win.tk.call("tk", "scaling", scale)
    except Exception:
        pass


def _section_label(parent, text, color=ACCENT):
    tk.Label(parent, text=text.upper(), font=("Segoe UI", 8, "bold"),
             fg=color, bg=BG).pack(anchor="w", pady=(0, 4))


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
    frame = tk.Frame(parent, bg=SURFACE2, highlightbackground=BORDER, highlightthickness=1)
    sb = tk.Scrollbar(frame, orient="vertical")
    sb.pack(side="right", fill="y")
    t = tk.Text(frame, height=height, font=("Segoe UI Mono", 10),
                bg=SURFACE2, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                relief="flat", highlightthickness=0,
                selectbackground=ACCENT, selectforeground=BG,
                wrap="none", padx=8, pady=6, yscrollcommand=sb.set)
    t.pack(side="left", fill="both", expand=True)
    sb.config(command=t.yview)
    return frame, t


def _make_scrollable_window(win):
    """Return (canvas, scrollframe) – content goes into scrollframe."""
    outer = tk.Frame(win, bg=BG)
    outer.pack(fill="both", expand=True, padx=28, pady=(14, 0))
    canvas = tk.Canvas(outer, bg=BG, highlightthickness=0, bd=0)
    gsb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=gsb.set)
    gsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    sf = tk.Frame(canvas, bg=BG)
    win_id = canvas.create_window((0, 0), window=sf, anchor="nw")
    sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
    for ev, dy in (("<MouseWheel>", None), ("<Button-4>", -1), ("<Button-5>", 1)):
        if dy is None:
            canvas.bind(ev, lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))
        else:
            canvas.bind(ev, lambda e, d=dy: canvas.yview_scroll(d, "units"))
    canvas.bind("<Enter>", lambda e: canvas.focus_set())
    return canvas, sf


def _header(win, title, subtitle, accent_color=ACCENT):
    hdr = tk.Frame(win, bg=BG)
    hdr.pack(fill="x", padx=28, pady=(24, 0))
    tk.Label(hdr, text="C H R O M A C O", font=("Segoe UI", 8, "bold"),
             fg=accent_color, bg=BG).pack(anchor="w")
    tk.Label(hdr, text=title, font=("Segoe UI", 20, "bold"),
             fg=TEXT_PRI, bg=BG).pack(anchor="w", pady=(2, 1))
    tk.Label(hdr, text=subtitle, font=("Segoe UI", 9),
             fg=TEXT_SEC, bg=BG).pack(anchor="w")
    tk.Frame(win, bg=accent_color, height=2).pack(fill="x", padx=28, pady=(12, 0))


def _card(parent):
    c = tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
    c.pack(fill="x", pady=(0, 4))
    return c


def _result_labels(parent):
    res = tk.Label(parent, text="", font=("Segoe UI", 13, "bold"), fg=SUCCESS, bg=BG)
    res.pack(pady=(10, 0))
    err = tk.Label(parent, text="", font=("Segoe UI", 9), fg=DANGER, bg=BG)
    err.pack(pady=(2, 16))
    return res, err


def _show_result(lbl_res, lbl_err, text):
    lbl_res.config(text=text, fg=SUCCESS)
    lbl_err.config(text="")


def _show_error(lbl_res, lbl_err, text):
    lbl_err.config(text=text)
    lbl_res.config(text="")


# ══════════════════════════════════════════════════════════════════════
#  SELECTION DIALOG
# ══════════════════════════════════════════════════════════════════════

class KovatsSelector:
    """Small pop-up that lets the user choose which Kovats tool to open."""

    def __init__(self, parent):
        self.parent = parent
        dlg = tk.Toplevel(parent)
        dlg.title("Select Kovats Tool")
        dlg.geometry("420x400")
        dlg.resizable(False, False)
        dlg.config(bg=BG)
        dlg.grab_set()
        _dpi_scale(dlg)
        self.dlg = dlg

        tk.Label(dlg, text="C H R O M A C O", font=("Segoe UI", 8, "bold"),
                 fg=ACCENT, bg=BG).pack(anchor="w", padx=28, pady=(22, 0))
        tk.Label(dlg, text="Kovats Methods", font=("Segoe UI", 18, "bold"),
                 fg=TEXT_PRI, bg=BG).pack(anchor="w", padx=28, pady=(2, 0))
        tk.Label(dlg, text="Which calculation would you like to perform?",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=BG).pack(anchor="w", padx=28)
        tk.Frame(dlg, bg=ACCENT, height=2).pack(fill="x", padx=28, pady=(10, 18))

        btn_row = tk.Frame(dlg, bg=BG)
        btn_row.pack(padx=28, fill="x")

        def open_dead():
            dlg.destroy()
            InterfaceDeadTimeKovats(parent)

        def open_index():
            dlg.destroy()
            InterfaceKovatsIndex(parent)

        for label, sub, cmd, color in [
            ("Dead Time  t\u2098", "Triplet method · N ≥ 3 alkanes", open_dead, ACCENT),
            ("Kovats Index  I", "Van den Dool & Kratz · log interpolation", open_index, PURPLE),
        ]:
            card = tk.Frame(btn_row, bg=SURFACE, highlightbackground=color,
                            highlightthickness=1, cursor="hand2")
            card.pack(fill="x", pady=5)
            inner = tk.Frame(card, bg=SURFACE)
            inner.pack(fill="x", padx=14, pady=10)
            tk.Label(inner, text=label, font=("Segoe UI", 11, "bold"),
                     fg=color, bg=SURFACE, anchor="w").pack(anchor="w", fill="x")
            tk.Label(inner, text=sub, font=("Segoe UI", 8),
                     fg=TEXT_SEC, bg=SURFACE, anchor="w").pack(anchor="w", fill="x")

            def _bind_all(root_widget, c=cmd, col=color, card_ref=card):
                def on_enter(_):
                    card_ref.config(highlightbackground=col)
                    for w in _all_widgets(card_ref):
                        try: w.config(bg=SURFACE2)
                        except Exception: pass
                def on_leave(_):
                    card_ref.config(highlightbackground=col)
                    for w in _all_widgets(card_ref):
                        try: w.config(bg=SURFACE)
                        except Exception: pass
                for w in _all_widgets(root_widget):
                    w.bind("<Button-1>", lambda e, fn=c: fn())
                    w.bind("<Enter>", on_enter)
                    w.bind("<Leave>", on_leave)

            _bind_all(card)

        back = tk.Label(dlg, text="← Back to menu", font=("Segoe UI", 9),
                        fg=TEXT_SEC, bg=BG, cursor="hand2")
        back.pack(anchor="e", padx=28, pady=(12, 0))
        back.bind("<Button-1>", lambda e: dlg.destroy())
        back.bind("<Enter>",    lambda e: back.config(fg=TEXT_PRI))
        back.bind("<Leave>",    lambda e: back.config(fg=TEXT_SEC))


# ══════════════════════════════════════════════════════════════════════
#  WINDOW 1 – Dead Time (Kovats method)
# ══════════════════════════════════════════════════════════════════════

class InterfaceDeadTimeKovats:
    """
    Enter n-alkane data as  carbon_number → retention_time  rows,
    then compute the average dead time t_M.
    """

    def __init__(self, parent):
        win = tk.Toplevel(parent)
        win.title("Dead Time – Kovats Method")
        win.geometry("640x700")
        win.resizable(True, True)
        win.config(bg=BG)
        _dpi_scale(win)
        self.win = win

        _header(win,
                "Dead Time  t\u2098",
                "Kovats triplet method  ·  t\u2098 = (t\u2082\u00b2 \u2212 t\u2081\u00b7t\u2083) / (2t\u2082 \u2212 t\u2081 \u2212 t\u2083)",
                ACCENT)

        _, sf = _make_scrollable_window(win)
        PAD = {"padx": 0, "pady": 8, "fill": "x"}

        # ── Manual entry section ──────────────────────────────────────
        wrap = tk.Frame(sf, bg=BG)
        wrap.pack(**PAD)
        _section_label(wrap, "Alkane Data  (carbon number → retention time)")

        card = _card(wrap)
        tk.Label(card,
                 text="Enter one alkane per row: carbon number  |  retention time (min). "
                      "Use consecutive carbon numbers (e.g. 6, 7, 8 …). At least 3 rows required.",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=SURFACE,
                 justify="left", wraplength=540, anchor="w").pack(anchor="w", padx=14, pady=(10, 6), fill="x")

        # Column headers
        hrow = tk.Frame(card, bg=SURFACE)
        hrow.pack(fill="x", padx=14)
        for h, w in [("Carbon #", 10), ("t_R (min)", 14)]:
            tk.Label(hrow, text=h, font=("Segoe UI", 8, "bold"),
                     fg=ACCENT, bg=SURFACE, width=w, anchor="w").pack(side="left", padx=4)

        # Editable rows
        self._alkane_entries = []
        self._row_frames = []
        self._rows_container = tk.Frame(card, bg=SURFACE)
        self._rows_container.pack(fill="x", padx=14)
        for _ in range(5):
            self._add_alkane_row()

        # Add / Remove row buttons
        btn_add_row = tk.Frame(card, bg=SURFACE)
        btn_add_row.pack(fill="x", padx=14, pady=(6, 2))
        _action_btn(btn_add_row, "+ Add Row",    self._add_alkane_row,    SUCCESS).pack(side="left", padx=(0, 6))
        _action_btn(btn_add_row, "− Remove Row", self._remove_alkane_row, DANGER).pack(side="left")

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=14, pady=(10, 0))

        # Paste area
        tk.Label(card, text="– or paste from Excel (2 columns: carbon #  |  t_R) –",
                 font=("Segoe UI", 8), fg=TEXT_SEC, bg=SURFACE).pack(pady=(8, 2))
        paste_f, self.text_paste = _scrollable_text(card, height=4)
        paste_f.pack(fill="x", padx=14, pady=(0, 6))
        self.text_paste.bind("<Control-v>", lambda e: win.after(80, self._parse_paste))
        self.text_paste.bind("<<Paste>>",   lambda e: win.after(80, self._parse_paste))

        _action_btn(card, "  Parse Paste", self._parse_paste, WARNING).pack(anchor="w", padx=14, pady=(0, 12))

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=14)

        # Calculate button + result
        _action_btn(sf, "  Calculate  t\u2098", self._calculate, ACCENT, large=True).pack(pady=(12, 0))
        self.lbl_res, self.lbl_err = _result_labels(sf)

        # Detail label
        self.lbl_detail = tk.Label(sf, text="", font=("Segoe UI", 9),
                                   fg=TEXT_SEC, bg=BG, justify="left")
        self.lbl_detail.pack(padx=28, anchor="w", pady=(0, 20))

        _back_button_to_selector(win, parent, KovatsSelector)

    # ── row management ────────────────────────────────────────────────

    def _add_alkane_row(self, cn_val="", tr_val=""):
        row = tk.Frame(self._rows_container, bg=SURFACE)
        row.pack(fill="x", pady=2)
        e_cn = _styled_entry(row, width=10)
        e_cn.pack(side="left", padx=(0, 4))
        if cn_val:
            e_cn.insert(0, str(cn_val))
        e_tr = _styled_entry(row, width=14)
        e_tr.pack(side="left", padx=(0, 4))
        if tr_val:
            e_tr.insert(0, str(tr_val))
        self._alkane_entries.append((e_cn, e_tr))
        self._row_frames.append(row)

    def _remove_alkane_row(self):
        if len(self._row_frames) <= 3:
            return
        self._row_frames[-1].destroy()
        self._row_frames.pop()
        self._alkane_entries.pop()

    # ── parse paste ───────────────────────────────────────────────────

    def _parse_paste(self):
        raw = self.text_paste.get("1.0", "end").strip()
        if not raw:
            return
        # Clear existing rows
        for f in self._row_frames:
            f.destroy()
        self._row_frames.clear()
        self._alkane_entries.clear()

        count = 0
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
                cn = int(float(parts[0].replace(",", ".")))
                tr = float(parts[1].replace(",", "."))
                self._add_alkane_row(cn, tr)
                count += 1
            except ValueError:
                continue

        if count == 0:
            self.lbl_err.config(text="No valid rows found in paste.")
        else:
            self.lbl_err.config(text=f"✔  {count} row(s) imported from paste.")
            self.lbl_res.config(text="")

    # ── main calculation ──────────────────────────────────────────────

    def _collect_data(self):
        data = {}
        for e_cn, e_tr in self._alkane_entries:
            raw_cn = e_cn.get().strip()
            raw_tr = e_tr.get().strip()
            if not raw_cn and not raw_tr:
                continue
            cn = int(float(raw_cn.replace(",", ".")))
            tr = float(raw_tr.replace(",", "."))
            data[cn] = tr
        return data

    def _calculate(self):
        try:
            data = self._collect_data()
        except (ValueError, IndexError):
            _show_error(self.lbl_res, self.lbl_err,
                        "Invalid data. Check carbon numbers and retention times.")
            return
        try:
            tm = calculate_dead_time_kovats(data)
            _show_result(self.lbl_res, self.lbl_err,
                         f"t\u2098  =  {tm:.4f} min")

            # Show per-triplet breakdown
            sorted_idx = sorted(data.keys())
            lines = []
            for i in range(len(sorted_idx) - 2):
                a, b, c = sorted_idx[i], sorted_idx[i+1], sorted_idx[i+2]
                if b != a+1 or c != b+1:
                    continue
                t1, t2, t3 = data[a], data[b], data[c]
                denom = 2*t2 - (t1+t3)
                if denom == 0:
                    continue
                val = (t2**2 - t1*t3) / denom
                valid = "✔" if 0 < val < t1 else "✘"
                lines.append(f"  {valid}  C{a}–C{b}–C{c}  →  t\u2098 = {val:.4f} min")
            self.lbl_detail.config(text="Triplet breakdown:\n" + "\n".join(lines))
        except ValueError as e:
            _show_error(self.lbl_res, self.lbl_err, str(e))
            self.lbl_detail.config(text="")


# ══════════════════════════════════════════════════════════════════════
#  WINDOW 2 – Kovats Retention Index
# ══════════════════════════════════════════════════════════════════════

class InterfaceKovatsIndex:
    """
    Compute the Kovats retention index for an unknown compound.
    """

    def __init__(self, parent):
        win = tk.Toplevel(parent)
        win.title("Kovats Retention Index")
        win.geometry("680x820")
        win.resizable(True, True)
        win.config(bg=BG)
        _dpi_scale(win)
        self.win = win

        _header(win,
                "Kovats Index  I",
                "I = 100 · [n + (log t'ₓ − log t'ₙ) / (log t'_N − log t'ₙ)]",
                PURPLE)

        _, sf = _make_scrollable_window(win)
        PAD = {"padx": 0, "pady": 8, "fill": "x"}

        # ── Unknown compound ─────────────────────────────────────────
        wrap_unk = tk.Frame(sf, bg=BG)
        wrap_unk.pack(**PAD)
        _section_label(wrap_unk, "Unknown Compound", color=PURPLE)
        card_unk = _card(wrap_unk)
        self.e_tr_unk = _labelled_entry_row(card_unk, "Gross retention time t_R  (min)")

        # ── Bracketing alkanes ────────────────────────────────────────
        wrap_brk = tk.Frame(sf, bg=BG)
        wrap_brk.pack(**PAD)
        _section_label(wrap_brk, "Bracketing Alkanes", color=PURPLE)
        card_brk = _card(wrap_brk)
        tk.Label(card_brk,
                 text="The two n-alkanes eluting immediately before and after the unknown.",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=SURFACE,
                 justify="left", wraplength=560, anchor="w").pack(anchor="w", padx=14, pady=(10, 4), fill="x")
        self.e_cn_before  = _labelled_entry_row(card_brk, "Carbon # eluting  before  (n)")
        self.e_tr_before  = _labelled_entry_row(card_brk, "t_R of  C(n)  (min)")
        self.e_cn_after   = _labelled_entry_row(card_brk, "Carbon # eluting  after   (N)")
        self.e_tr_after   = _labelled_entry_row(card_brk, "t_R of  C(N)  (min)")

        # ── Additional alkane data for t_M ────────────────────────────
        wrap_alk = tk.Frame(sf, bg=BG)
        wrap_alk.pack(**PAD)
        _section_label(wrap_alk, "All Alkane Data for Dead-Time Calculation", color=PURPLE)
        card_alk = _card(wrap_alk)
        tk.Label(card_alk,
                 text="Provide ≥ 3 consecutive n-alkanes (including the two above) to compute t_M. "
                      "Format: carbon number  |  retention time  (one per row, or paste from Excel).",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=SURFACE,
                 justify="left", wraplength=560, anchor="w").pack(anchor="w", padx=14, pady=(10, 6), fill="x")

        hrow = tk.Frame(card_alk, bg=SURFACE)
        hrow.pack(fill="x", padx=14)
        for h, w in [("Carbon #", 10), ("t_R (min)", 14)]:
            tk.Label(hrow, text=h, font=("Segoe UI", 8, "bold"),
                     fg=PURPLE, bg=SURFACE, width=w, anchor="w").pack(side="left", padx=4)

        self._alk_entries = []
        self._alk_frames  = []
        self._alk_container = tk.Frame(card_alk, bg=SURFACE)
        self._alk_container.pack(fill="x", padx=14)
        for _ in range(5):
            self._add_alk_row()

        btn_alk_row = tk.Frame(card_alk, bg=SURFACE)
        btn_alk_row.pack(fill="x", padx=14, pady=(6, 2))
        _action_btn(btn_alk_row, "+ Add Row",    self._add_alk_row,    SUCCESS).pack(side="left", padx=(0, 6))
        _action_btn(btn_alk_row, "− Remove Row", self._remove_alk_row, DANGER).pack(side="left")

        tk.Frame(card_alk, bg=BORDER, height=1).pack(fill="x", padx=14, pady=(10, 0))
        tk.Label(card_alk, text="– or paste from Excel –",
                 font=("Segoe UI", 8), fg=TEXT_SEC, bg=SURFACE).pack(pady=(8, 2))
        paste_f, self.text_paste_alk = _scrollable_text(card_alk, height=4)
        paste_f.pack(fill="x", padx=14, pady=(0, 6))
        self.text_paste_alk.bind("<Control-v>", lambda e: win.after(80, self._parse_paste_alk))
        self.text_paste_alk.bind("<<Paste>>",   lambda e: win.after(80, self._parse_paste_alk))
        _action_btn(card_alk, "  Parse Paste", self._parse_paste_alk, WARNING).pack(anchor="w", padx=14, pady=(0, 12))

        # ── All gross retention times ─────────────────────────────────
        wrap_all = tk.Frame(sf, bg=BG)
        wrap_all.pack(**PAD)
        _section_label(wrap_all, "All Peak Retention Times  (optional but recommended)", color=TEXT_SEC)
        card_all = _card(wrap_all)
        tk.Label(card_all,
                 text="Paste the gross t_R of every peak in the run (one value per line, or one column). "
                      "The unknown and alkanes will be included automatically.",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=SURFACE,
                 justify="left", wraplength=560, anchor="w").pack(anchor="w", padx=14, pady=(10, 6), fill="x")
        paste_f2, self.text_all_peaks = _scrollable_text(card_all, height=4)
        paste_f2.pack(fill="x", padx=14, pady=(0, 12))

        # ── Calculate ─────────────────────────────────────────────────
        _action_btn(sf, "  Calculate Kovats Index", self._calculate, PURPLE, large=True).pack(pady=(12, 0))
        self.lbl_res, self.lbl_err = _result_labels(sf)

        self.lbl_detail = tk.Label(sf, text="", font=("Segoe UI", 9),
                                   fg=TEXT_SEC, bg=BG, justify="left")
        self.lbl_detail.pack(padx=28, anchor="w", pady=(0, 20))

        _back_button_to_selector(win, parent, KovatsSelector)

    # ── row management ────────────────────────────────────────────────

    def _add_alk_row(self, cn="", tr=""):
        row = tk.Frame(self._alk_container, bg=SURFACE)
        row.pack(fill="x", pady=2)
        e_cn = _styled_entry(row, width=10)
        e_cn.pack(side="left", padx=(0, 4))
        if cn:
            e_cn.insert(0, str(cn))
        e_tr = _styled_entry(row, width=14)
        e_tr.pack(side="left", padx=(0, 4))
        if tr:
            e_tr.insert(0, str(tr))
        self._alk_entries.append((e_cn, e_tr))
        self._alk_frames.append(row)

    def _remove_alk_row(self):
        if len(self._alk_frames) <= 3:
            return
        self._alk_frames[-1].destroy()
        self._alk_frames.pop()
        self._alk_entries.pop()

    def _parse_paste_alk(self):
        raw = self.text_paste_alk.get("1.0", "end").strip()
        if not raw:
            return
        for f in self._alk_frames:
            f.destroy()
        self._alk_frames.clear()
        self._alk_entries.clear()
        count = 0
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
                cn = int(float(parts[0].replace(",", ".")))
                tr = float(parts[1].replace(",", "."))
                self._add_alk_row(cn, tr)
                count += 1
            except ValueError:
                continue
        if count:
            self.lbl_err.config(text=f"✔  {count} alkane row(s) imported.")

    def _collect_alkane_data(self):
        data = {}
        for e_cn, e_tr in self._alk_entries:
            raw_cn = e_cn.get().strip()
            raw_tr = e_tr.get().strip()
            if not raw_cn and not raw_tr:
                continue
            cn = int(float(raw_cn.replace(",", ".")))
            tr = float(raw_tr.replace(",", "."))
            data[cn] = tr
        return data

    def _collect_all_peaks(self, unk_tr, alkane_data):
        raw = self.text_all_peaks.get("1.0", "end").strip()
        peaks = set(alkane_data.values())
        peaks.add(unk_tr)
        if raw:
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.replace(";", "\t").split("\t")
                for p in parts:
                    try:
                        peaks.add(float(p.replace(",", ".")))
                    except ValueError:
                        continue
        return list(peaks)

    def _calculate(self):
        try:
            tr_unk      = float(self.e_tr_unk.get().replace(",", "."))
            cn_before   = int(self.e_cn_before.get().strip())
            tr_before   = float(self.e_tr_before.get().replace(",", "."))
            cn_after    = int(self.e_cn_after.get().strip())
            tr_after    = float(self.e_tr_after.get().replace(",", "."))
            alkane_data = self._collect_alkane_data()
        except (ValueError, TypeError):
            _show_error(self.lbl_res, self.lbl_err,
                        "Invalid input. Check all fields are filled with numbers.")
            return

        # Ensure the bracketing alkanes are in the data
        alkane_data[cn_before] = tr_before
        alkane_data[cn_after]  = tr_after

        all_peaks = self._collect_all_peaks(tr_unk, alkane_data)

        try:
            index = calculate_kovats_index(
                gross_retention_unknown=tr_unk,
                all_gross_times=all_peaks,
                alkane_data=alkane_data,
                n_carbon_before=cn_before,
                n_carbon_after=cn_after,
            )
            # Also expose the computed t_M
            tm = calculate_dead_time_kovats(alkane_data)
            t_net_unk = tr_unk - tm
            t_net_n   = tr_before - tm
            t_net_N   = tr_after - tm

            _show_result(self.lbl_res, self.lbl_err,
                         f"I  =  {index:.2f}")
            self.lbl_detail.config(
                text=(
                    f"  Dead time  t\u2098         =  {tm:.4f} min\n"
                    f"  Net t'R  (unknown)    =  {t_net_unk:.4f} min\n"
                    f"  Net t'R  C{cn_before:>2}          =  {t_net_n:.4f} min\n"
                    f"  Net t'R  C{cn_after:>2}          =  {t_net_N:.4f} min\n"
                    f"  Interpolation factor  =  {(math.log10(t_net_unk)-math.log10(t_net_n))/(math.log10(t_net_N)-math.log10(t_net_n)):.4f}"
                )
            )
        except ValueError as e:
            _show_error(self.lbl_res, self.lbl_err, str(e))
            self.lbl_detail.config(text="")


def _back_button_to_menu(win, label="← Back to menu"):
    """Closes the window — main menu is always open behind it."""
    bar = tk.Frame(win, bg=BG)
    bar.pack(fill="x", padx=28, pady=(10, 0))
    btn = tk.Label(bar, text=label, font=("Segoe UI", 9),
                   fg=TEXT_SEC, bg=BG, cursor="hand2")
    btn.pack(side="right")
    btn.bind("<Button-1>", lambda e: win.destroy())
    btn.bind("<Enter>",    lambda e: btn.config(fg=TEXT_PRI))
    btn.bind("<Leave>",    lambda e: btn.config(fg=TEXT_SEC))


def _back_button_to_selector(win, parent, selector_class, label="← Back"):
    """Closes the window and reopens the given selector."""
    def _go():
        win.destroy()
        selector_class(parent)
    btn = tk.Label(win, text=label, font=("Segoe UI", 9),
                   fg=TEXT_SEC, bg=BG, cursor="hand2")
    btn.place(relx=1.0, x=-28, y=10, anchor="ne")
    btn.bind("<Button-1>", lambda e: _go())
    btn.bind("<Enter>",    lambda e: btn.config(fg=TEXT_PRI))
    btn.bind("<Leave>",    lambda e: btn.config(fg=TEXT_SEC))


# ══════════════════════════════════════════════════════════════════════
#  MAIN WINDOW  (with the trigger button)
# ══════════════════════════════════════════════════════════════════════

class MainApp:
    def __init__(self):
        root = tk.Tk()
        root.title("CHROMACO")
        root.geometry("480x260")
        root.resizable(False, False)
        root.config(bg=BG)
        _dpi_scale(root)

        hdr = tk.Frame(root, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(24, 0))
        tk.Label(hdr, text="C H R O M A C O", font=("Segoe UI", 8, "bold"),
                 fg=ACCENT, bg=BG).pack(anchor="w")
        tk.Label(hdr, text="Chromatography Tools",
                 font=("Segoe UI", 20, "bold"), fg=TEXT_PRI, bg=BG).pack(anchor="w", pady=(2, 1))
        tk.Label(hdr, text="Select a module to get started",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=BG).pack(anchor="w")
        tk.Frame(root, bg=ACCENT, height=2).pack(fill="x", padx=28, pady=(12, 16))

        btn_row = tk.Frame(root, bg=BG)
        btn_row.pack(padx=28, fill="x")

        _action_btn(btn_row, "  Theoretical Plates  N",
                    lambda: messagebox.showinfo("Info", "Open InterfacePlateau here."),
                    ACCENT).pack(side="left", padx=(0, 10))
        _action_btn(btn_row, "  Kovats Methods",
                    lambda: KovatsSelector(root),
                    PURPLE).pack(side="left")

        root.mainloop()


if __name__ == "__main__":
    MainApp()
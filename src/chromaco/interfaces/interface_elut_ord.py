"""
interface_elut_ord.py
---------------------
Modernised Tkinter interface for elution order calculation.
Matches the Chromaco dark design system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox

from chromaco.predictions.logpprd import logp_correction
from chromaco.predictions.dipoleprd import dipole_rdkit
from chromaco.interfaces.fonctions_colonnes import (
    load_logp_db, load_dipole_db, sort_by_logp, sort_by_dipole,
)

# ── Design tokens (shared with main_menu) ──────────────────────────────────────
BG       = "#0f1117"
SURFACE  = "#1a1d27"
SURFACE2 = "#20243a"
BORDER   = "#2a2d3e"
ACCENT   = "#68d391"   # green – matches "Order of Elution" button accent
ACCENT2  = "#4f9cf9"   # blue
TEXT_PRI = "#e8eaf2"
TEXT_SEC = "#7b80a0"
SUCCESS  = "#68d391"
WARNING  = "#f6ad55"
DANGER   = "#f7706a"
BTN_LOGP   = "#4f9cf9"   # blue  – LogP
BTN_DIPOLE = "#68d391"   # green – Dipole


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _dpi_scale(win):
    try:
        scale = win.winfo_fpixels("1i") / 72
        if scale > 1.25:
            win.tk.call("tk", "scaling", scale)
    except Exception:
        pass


def _base_window(parent, title, w, h, resizable=(False, False)):
    win = tk.Toplevel(parent)
    win.title(title)
    win.geometry(f"{w}x{h}")
    win.resizable(*resizable)
    win.config(bg=BG)
    _dpi_scale(win)
    return win


def _header(win, tag, title, subtitle=None):
    hdr = tk.Frame(win, bg=BG)
    hdr.pack(fill="x", padx=28, pady=(22, 0))
    tk.Label(hdr, text="C H R O M A C O", font=("Segoe UI", 8, "bold"),
             fg=ACCENT, bg=BG).pack(anchor="w")
    tk.Label(hdr, text=title, font=("Segoe UI", 18, "bold"),
             fg=TEXT_PRI, bg=BG).pack(anchor="w", pady=(2, 1))
    if subtitle:
        tk.Label(hdr, text=subtitle, font=("Segoe UI", 9),
                 fg=TEXT_SEC, bg=BG).pack(anchor="w")
    tk.Frame(win, bg=ACCENT, height=2).pack(fill="x", padx=28, pady=(10, 0))


def _section_label(parent, text):
    tk.Label(parent, text=text.upper(), font=("Segoe UI", 8, "bold"),
             fg=ACCENT, bg=BG).pack(anchor="w", pady=(0, 4))


def _card(parent):
    f = tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER,
                 highlightthickness=1)
    f.pack(fill="x")
    return f


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


def _styled_entry(parent, width=12, default=""):
    e = tk.Entry(parent, width=width, font=("Segoe UI", 11),
                 bg=SURFACE2, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                 relief="flat", highlightbackground=BORDER,
                 highlightthickness=1, highlightcolor=ACCENT)
    if default:
        e.insert(0, default)
    return e


# ── Main class ─────────────────────────────────────────────────────────────────

class InterfaceElution:

    def __init__(self, parent):
        self.parent      = parent
        self.column_type = None
        self.n_compounds = None
        self.mol_entries = []
        self._open_column_choice()

    # ── Step 1: column type ────────────────────────────────────────────────────

    def _open_column_choice(self):
        win = _base_window(self.parent, "Order of Elution", 500, 400)
        self.win_col = win
        _header(win, "CHROMACO", "Order of Elution", "Select a stationary phase")

        body = tk.Frame(win, bg=BG)
        body.pack(fill="x", padx=28, pady=20)

        _section_label(body, "Column type")

        row = tk.Frame(body, bg=BG)
        row.pack(fill="x", pady=(4, 0))

        def make_col_btn(parent, label, col_type, color):
            stripe_color = color
            outer = tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER,
                             highlightthickness=1, cursor="hand2")
            outer.pack(side="left", fill="both", expand=True, padx=(0, 6))

            stripe = tk.Frame(outer, bg=stripe_color, width=4)
            stripe.pack(side="left", fill="y")

            inner = tk.Frame(outer, bg=SURFACE)
            inner.pack(fill="both", expand=True, padx=12, pady=14)

            lbl = tk.Label(inner, text=label, font=("Segoe UI", 11, "bold"),
                           fg=TEXT_PRI, bg=SURFACE)
            lbl.pack()

            sub = tk.Label(inner,
                           text="C18, C8 …" if col_type == "apolar" else "Silica, HILIC …",
                           font=("Segoe UI", 8), fg=TEXT_SEC, bg=SURFACE)
            sub.pack()

            def on_click(e):
                self._on_column_selected(col_type)

            def on_enter(e):
                for w in (outer, inner, lbl, sub):
                    w.config(bg="#22263a")
                outer.config(highlightbackground=stripe_color)

            def on_leave(e):
                for w in (outer, inner, lbl, sub):
                    w.config(bg=SURFACE)
                outer.config(highlightbackground=BORDER)

            for w in (outer, stripe, inner, lbl, sub):
                w.bind("<Button-1>", on_click)
                w.bind("<Enter>",    on_enter)
                w.bind("<Leave>",    on_leave)

        make_col_btn(row, "Apolar column", "apolar", BTN_LOGP)
        make_col_btn(row, "Polar column",  "polar",  BTN_DIPOLE)

    def _on_column_selected(self, column_type):
        self.column_type = column_type
        self.win_col.destroy()
        self._open_nb_compounds()

    # ── Step 2: number of compounds ───────────────────────────────────────────

    def _open_nb_compounds(self):
        win = _base_window(self.parent, "Number of Compounds", 450, 400)
        self.win_nb = win
        _header(win, "CHROMACO", "Compounds", "How many molecules to separate?")

        body = tk.Frame(win, bg=BG)
        body.pack(fill="x", padx=28, pady=20)

        _section_label(body, "Number of compounds")

        row = tk.Frame(body, bg=BG)
        row.pack(fill="x", pady=(4, 0))

        self.nb_entry = _styled_entry(row, width=8)
        self.nb_entry.pack(side="left")
        self.nb_entry.bind("<Return>", lambda e: self._on_nb_validate())

        _action_btn(row, "Continue →", self._on_nb_validate, ACCENT
                    ).pack(side="left", padx=(12, 0))

    def _on_nb_validate(self):
        raw = self.nb_entry.get().strip()
        if not raw:
            messagebox.showerror("Error", "Please enter a number.",
                                 parent=self.win_nb)
            return
        try:
            n = int(raw)
            if n < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error",
                                 "Please enter a positive integer (e.g. 3).",
                                 parent=self.win_nb)
            return
        self.n_compounds = n
        self.win_nb.destroy()
        self._open_molecule_input()

    # ── Step 3: molecule input ─────────────────────────────────────────────────

    def _open_molecule_input(self):
        h = 350 + self.n_compounds * 48
        win = _base_window(self.parent, "Molecule Input", 600, h,
                           resizable=(False, True))
        self.win_mol = win
        _header(win, "CHROMACO", "Molecule Input",
                "SMILES or CAS → LogP     |     SMILES → Dipole moment")

        body = tk.Frame(win, bg=BG)
        body.pack(fill="x", padx=28, pady=(18, 0))

        _section_label(body, "Molecule identifiers")

        card = _card(body)
        card.pack_configure(fill="x")  # already packed by _card; fix padx
        # rebuild without auto-pack so we can control padding
        card.pack_forget()
        card = tk.Frame(body, bg=SURFACE, highlightbackground=BORDER,
                        highlightthickness=1)
        card.pack(fill="x", pady=(4, 0))

        self.mol_entries = []
        for i in range(self.n_compounds):
            row = tk.Frame(card, bg=SURFACE)
            row.pack(fill="x", padx=14, pady=6)

            # index badge
            badge = tk.Label(row, text=str(i + 1), font=("Segoe UI", 9, "bold"),
                             fg=BG, bg=ACCENT, width=2, pady=2)
            badge.pack(side="left", padx=(0, 10))

            entry = _styled_entry(row, width=44)
            entry.pack(side="left", fill="x", expand=True)
            self.mol_entries.append(entry)

            if i < self.n_compounds - 1:
                tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=14)

        # bottom padding inside card
        tk.Frame(card, bg=SURFACE, height=8).pack()

        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack(pady=18)

        _action_btn(btn_row, "  Calculate with LogP",
                    self._calc_logp, BTN_LOGP, large=True).pack(side="left", padx=6)
        _action_btn(btn_row, "  Calculate with Dipole",
                    self._calc_dipole, BTN_DIPOLE, large=True).pack(side="left", padx=6)

    def _get_molecules(self):
        return [e.get().strip() for e in self.mol_entries]

    # ── Step 4a: LogP ──────────────────────────────────────────────────────────

    def _calc_logp(self):
        molecules = self._get_molecules()
        empty = [i + 1 for i, m in enumerate(molecules) if not m]
        if empty:
            messagebox.showerror("Error",
                f"Empty field(s): {empty}", parent=self.win_mol)
            return
        try:
            db = load_logp_db()
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Database error", str(e), parent=self.win_mol)
            return

        estimated = []
        for mol in molecules:
            if mol.lower() not in db:
                try:
                    db[mol.lower()] = {"smiles": mol,
                                       "logp": logp_correction(mol)}
                    estimated.append(mol)
                except Exception as e:
                    messagebox.showerror("Estimation error",
                        f"Could not estimate logP for '{mol}'.\n"
                        f"Make sure it is a valid SMILES string.\n\nError: {e}",
                        parent=self.win_mol)
                    return
        try:
            ordered = sort_by_logp(molecules, db, self.column_type)
        except ValueError as e:
            messagebox.showerror("Sorting error", str(e), parent=self.win_mol)
            return
        self._show_result(ordered, method="LogP", estimated=estimated)

    # ── Step 4b: Dipole ────────────────────────────────────────────────────────

    def _calc_dipole(self):
        molecules = self._get_molecules()
        empty = [i + 1 for i, m in enumerate(molecules) if not m]
        if empty:
            messagebox.showerror("Error",
                f"Empty field(s): {empty}", parent=self.win_mol)
            return
        try:
            db = load_dipole_db()
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Database error", str(e), parent=self.win_mol)
            return

        estimated = []
        for mol in molecules:
            if mol.lower() not in db:
                try:
                    dip = dipole_rdkit(mol)
                    db[mol.lower()] = {"molecule": mol, "dipole": dip}
                    estimated.append(mol)
                except Exception as e:
                    messagebox.showerror("Estimation error",
                        f"Could not estimate dipole for '{mol}'.\n"
                        f"Make sure it is a valid SMILES string.\n\nError: {e}",
                        parent=self.win_mol)
                    return
        try:
            ordered = sort_by_dipole(molecules, db, self.column_type)
        except ValueError as e:
            messagebox.showerror("Sorting error", str(e), parent=self.win_mol)
            return
        self._show_result(ordered, method="Dipole moment", estimated=estimated)

    # ── Step 5: result display ─────────────────────────────────────────────────

    def _show_result(self, ordered, method, estimated=None):
        has_warning = bool(estimated)
        h = 500 if has_warning else 400
        win = _base_window(self.parent, "Elution Order Result", 640, h,
                           resizable=(True, False))
        _header(win, "CHROMACO", "Elution Order",
                f"{method}  ·  {self.column_type} column")

        body = tk.Frame(win, bg=BG)
        body.pack(fill="x", padx=28, pady=(18, 0))

        _section_label(body, "First → Last")

        # Result flow card
        card = tk.Frame(body, bg=SURFACE, highlightbackground=BORDER,
                        highlightthickness=1)
        card.pack(fill="x", pady=(4, 0))

        flow = tk.Frame(card, bg=SURFACE)
        flow.pack(fill="x", padx=14, pady=14)

        for idx, mol in enumerate(ordered):
            tk.Label(flow, text=mol, font=("Segoe UI", 12, "bold"),
                     fg=TEXT_PRI, bg=SURFACE).pack(side="left")
            if idx < len(ordered) - 1:
                tk.Label(flow, text="  →  ", font=("Segoe UI", 12),
                         fg=ACCENT, bg=SURFACE).pack(side="left")

        # Warning box
        if estimated:
            names_str = ", ".join(estimated)
            prop = "LogP" if method == "LogP" else "dipole moment"
            warn_text = (
                f"⚠  {names_str} were not found in the database.\n"
                f"   {prop.capitalize()} was estimated computationally "
                f"and may carry prediction errors."
            )
            warn_card = tk.Frame(body, bg="#2a1f0a",
                                 highlightbackground=WARNING,
                                 highlightthickness=1)
            warn_card.pack(fill="x", pady=(12, 0))
            tk.Label(warn_card, text=warn_text, font=("Segoe UI", 9),
                     fg=WARNING, bg="#2a1f0a", justify="left",
                     wraplength=560).pack(padx=14, pady=10, anchor="w")

        _action_btn(win, "  Close", win.destroy, DANGER).pack(pady=16)
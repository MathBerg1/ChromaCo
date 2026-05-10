"""
interface_order_elution.py
--------------------------
Tkinter interface for calculating the elution order of molecules.
All business logic (database loading, sorting) is handled by fonctions_colonnes.py.

Window flow:
  1. Column type selection (apolar / polar)
  2. Number of compounds to separate
  3. Molecule identifier input + calculation method selection
  4. Elution order result display
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox

from predictions.logpprd import logp_correction
from predictions.dipoleprd import dipole_rdkit
from interfaces.fonctions_colonnes import (
    load_logp_db,
    load_dipole_db,
    sort_by_logp,
    sort_by_dipole,
)


class InterfaceElution:

    def __init__(self, parent):
        self.parent      = parent
        self.column_type = None
        self.n_compounds = None
        self.mol_entries = []
        self._open_column_choice()

    # ── Step 1: column type selection ─────────────────────────────────────────

    def _open_column_choice(self):
        self.win_col = tk.Toplevel(self.parent)
        self.win_col.title("Column type")
        self.win_col.geometry("320x180")
        self.win_col.resizable(False, False)

        tk.Label(
            self.win_col,
            text="Select column type",
            font=("Arial", 13, "bold")
        ).pack(pady=20)

        frm = tk.Frame(self.win_col)
        frm.pack()

        tk.Button(
            frm, text="Apolar column", width=15, height=2, bg="#e3f2fd",
            command=lambda: self._on_column_selected("apolar")
        ).pack(side="left", padx=10)

        tk.Button(
            frm, text="Polar column", width=15, height=2, bg="#e8f5e9",
            command=lambda: self._on_column_selected("polar")
        ).pack(side="left", padx=10)

    def _on_column_selected(self, column_type):
        self.column_type = column_type
        self.win_col.destroy()
        self._open_nb_compounds()

    # ── Step 2: number of compounds ───────────────────────────────────────────

    def _open_nb_compounds(self):
        self.win_nb = tk.Toplevel(self.parent)
        self.win_nb.title("Number of compounds")
        self.win_nb.geometry("340x180")
        self.win_nb.resizable(False, False)

        tk.Label(
            self.win_nb,
            text="Number of compounds to separate",
            font=("Arial", 12, "bold")
        ).pack(pady=20)

        self.nb_entry = tk.Entry(self.win_nb, width=10, font=("Arial", 12))
        self.nb_entry.pack()

        tk.Button(
            self.win_nb, text="Validate", width=12, bg="#ffe082",
            command=self._on_nb_validate
        ).pack(pady=15)

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
        height = 120 + self.n_compounds * 45 + 90
        self.win_mol = tk.Toplevel(self.parent)
        self.win_mol.title("Molecules")
        self.win_mol.geometry(f"620x{height}")
        self.win_mol.resizable(False, True)

        tk.Label(
            self.win_mol,
            text="Name of molecules",
            font=("Arial", 12, "bold")
        ).pack(pady=(14, 0))

        tk.Label(
            self.win_mol,
            text="SMILES or CAS  →  LogP      |      SMILES  →  Dipole moment",
            font=("Arial", 9),
            fg="#555555"
        ).pack(pady=(2, 10))

        frm = tk.Frame(self.win_mol)
        frm.pack()

        self.mol_entries = []
        for i in range(self.n_compounds):
            row_frm = tk.Frame(frm)
            row_frm.pack(anchor="w", pady=4)
            tk.Label(row_frm, text=f"{i + 1}.", width=3,
                     font=("Arial", 11)).pack(side="left")
            entry = tk.Entry(row_frm, width=46, font=("Arial", 11))
            entry.pack(side="left", padx=4)
            self.mol_entries.append(entry)

        btn_frm = tk.Frame(self.win_mol)
        btn_frm.pack(pady=16)

        tk.Button(
            btn_frm, text="Calculate with LogP", width=22, height=2,
            bg="#bbdefb", command=self._calc_logp
        ).pack(side="left", padx=8)

        tk.Button(
            btn_frm, text="Calculate with Dipole moment", width=26, height=2,
            bg="#c8e6c9", command=self._calc_dipole
        ).pack(side="left", padx=8)

    def _get_molecules(self):
        return [entry.get().strip() for entry in self.mol_entries]

    # ── Step 4a: LogP calculation ──────────────────────────────────────────────

    def _calc_logp(self):
        molecules = self._get_molecules()

        empty = [i + 1 for i, m in enumerate(molecules) if not m]
        if empty:
            messagebox.showerror(
                "Error",
                f"Please fill all fields. Empty field(s): {empty}",
                parent=self.win_mol
            )
            return

        try:
            db = load_logp_db()
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Database error", str(e), parent=self.win_mol)
            return

        missing   = [m for m in molecules if m.lower() not in db]
        estimated = []

        if missing:
            for mol in missing:
                try:
                    estimated_logp = logp_corrige(mol)
                    db[mol.lower()] = {"smiles": mol, "logp": estimated_logp}
                    estimated.append(mol)
                except Exception as e:
                    messagebox.showerror(
                        "Estimation error",
                        f"Could not estimate logP for '{mol}'.\n"
                        f"Make sure it is a valid SMILES string.\n\nError: {e}",
                        parent=self.win_mol
                    )
                    return

        try:
            ordered = sort_by_logp(molecules, db, self.column_type)
        except ValueError as e:
            messagebox.showerror("Sorting error", str(e), parent=self.win_mol)
            return

        self._show_result(ordered, method="LogP", estimated=estimated)

    # ── Step 4b: Dipole calculation ────────────────────────────────────────────

    def _calc_dipole(self):
        molecules = self._get_molecules()

        empty = [i + 1 for i, m in enumerate(molecules) if not m]
        if empty:
            messagebox.showerror(
                "Error",
                f"Please fill all fields. Empty field(s): {empty}",
                parent=self.win_mol
            )
            return

        try:
            db = load_dipole_db()
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Database error", str(e), parent=self.win_mol)
            return

        missing   = [m for m in molecules if m.lower() not in db]
        estimated = []

        if missing:
            for mol in missing:
                try:
                    dip = dipole_rdkit(mol)
                    db[mol.lower()] = {"molecule": mol, "dipole": dip}
                    estimated.append(mol)
                except Exception as e:
                    messagebox.showerror(
                        "Estimation error",
                        f"Could not estimate dipole for '{mol}'.\n"
                        f"Make sure it is a valid SMILES string.\n\nError: {e}",
                        parent=self.win_mol
                    )
                    return

        try:
            ordered = sort_by_dipole(molecules, db, self.column_type)
        except ValueError as e:
            messagebox.showerror("Sorting error", str(e), parent=self.win_mol)
            return

        self._show_result(ordered, method="Dipole moment", estimated=estimated)

    # ── Step 5: result display ─────────────────────────────────────────────────

    def _show_result(self, ordered, method, estimated=None):
        win = tk.Toplevel(self.parent)
        win.title("Order of elution")
        win.geometry("660x260")
        win.resizable(True, False)

        col_label = "apolar" if self.column_type == "apolar" else "polar"

        tk.Label(
            win,
            text=f"Order of elution  —  {method}  |  {col_label} column",
            font=("Arial", 11, "bold")
        ).pack(pady=14)

        tk.Label(win, text="First to last:", font=("Arial", 10),
                 fg="#333333").pack()

        txt = tk.Text(win, height=3, font=("Arial", 12), wrap="word",
                      relief="flat", bg="#f5f5f5")
        txt.insert("1.0", "  →  ".join(ordered))
        txt.config(state="disabled")
        txt.pack(padx=20, pady=6, fill="x")

        if estimated:
            names_str = ", ".join(estimated)
            if method == "LogP":
                warning = (
                    f"⚠ {names_str} were not in the database.\n"
                    f"LogP was estimated via RDKit + linear regression "
                    f"and may produce errors on the predicted value."
                )
            else:
                warning = (
                    f"⚠ {names_str} were not in the database.\n"
                    f"Dipole moment was estimated via an internal function "
                    f"and may produce errors on the predicted value."
                )

            tk.Label(
                win, text=warning, font=("Arial", 9), fg="#b71c1c",
                justify="left", wraplength=620,
            ).pack(padx=20, pady=(0, 6), anchor="w")

        tk.Button(win, text="Close", command=win.destroy,
                  bg="#ffcdd2").pack(pady=8)
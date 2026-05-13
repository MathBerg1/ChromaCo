"""
interface_ajouts_doses.py
-------------------------
Tkinter interface for the standard addition method.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chromaco.interfaces.fonctions_colonnes import plot_standard_addition


class InterfaceAjoutsDoses:
    def __init__(self, parent):

        self.fenetre = tk.Toplevel(parent)
        self.fenetre.title("Standard addition method")
        self.fenetre.geometry("620x700")
        self.fenetre.resizable(False, True)

        # ── Manual input section ───────────────────────────────────────────────
        frame_manual = tk.LabelFrame(self.fenetre, text="Manual input", padx=10, pady=10)
        frame_manual.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_manual,
                 text="Enter each point manually (concentration added + area),\n"
                      "then click 'Add point'. Include the blank (concentration = 0).",
                 font=("Arial", 9), fg="#555555", justify="left").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        tk.Label(frame_manual, text="Concentration added:").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_conc = tk.Entry(frame_manual, width=14)
        self.entry_conc.grid(row=1, column=1, padx=8)

        tk.Label(frame_manual, text="Peak area:").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_area = tk.Entry(frame_manual, width=14)
        self.entry_area.grid(row=2, column=1, padx=8)

        frm_btns = tk.Frame(frame_manual)
        frm_btns.grid(row=3, column=0, columnspan=3, pady=6)
        tk.Button(frm_btns, text="Add point", bg="#ffe082", width=12,
                  command=self._add_manual_point).pack(side="left", padx=4)
        tk.Button(frm_btns, text="Remove last", bg="#ffcdd2", width=12,
                  command=self._remove_last_point).pack(side="left", padx=4)
        tk.Button(frm_btns, text="Clear all", bg="#ffcdd2", width=10,
                  command=self._clear_all).pack(side="left", padx=4)

        # ── Unit input ─────────────────────────────────────────────────────────
        frame_unit = tk.LabelFrame(self.fenetre, text="Units", padx=10, pady=10)
        frame_unit.pack(fill="x", padx=15, pady=(0, 5))

        tk.Label(frame_unit, text="Concentration unit:").grid(row=0, column=0, sticky="w")
        self.entry_unit = tk.Entry(frame_unit, width=10)
        self.entry_unit.grid(row=0, column=1, padx=8)
        self.entry_unit.insert(0, "mg/L")

        # ── Excel paste section ────────────────────────────────────────────────
        frame_excel = tk.LabelFrame(self.fenetre, text="Paste from Excel", padx=10, pady=10)
        frame_excel.pack(fill="x", padx=15, pady=(0, 5))

        tk.Label(frame_excel,
                 text="Paste your Excel data (two columns: concentration added | peak area).\n"
                      "Include the blank row (concentration = 0).",
                 justify="left", fg="#555555", font=("Arial", 9)).pack(anchor="w")

        self.text_paste = tk.Text(frame_excel, height=4, font=("Courier", 10))
        self.text_paste.pack(fill="x", pady=5)
        self.text_paste.bind("<Control-v>", self._on_paste)
        self.text_paste.bind("<<Paste>>", self._on_paste)

        tk.Button(frame_excel, text="Parse data", bg="#ffe082", width=12,
                  command=self._parse_paste).pack(pady=(0, 5))

        # ── Data table ────────────────────────────────────────────────────────
        frame_table = tk.LabelFrame(self.fenetre, text="Data points", padx=10, pady=6)
        frame_table.pack(fill="x", padx=15, pady=(0, 5))

        frm_header = tk.Frame(frame_table, bg="#e3f2fd")
        frm_header.pack(fill="x")
        tk.Label(frm_header, text=f"{'#':>4}  {'Concentration added':>22}  {'Peak area':>16}",
                 font=("Courier", 10, "bold"), bg="#e3f2fd").pack(anchor="w", padx=4)

        frm_list = tk.Frame(frame_table)
        frm_list.pack(fill="x")
        scrollbar = tk.Scrollbar(frm_list, orient="vertical")
        self.listbox = tk.Listbox(frm_list, height=6, font=("Courier", 10),
                                  yscrollcommand=scrollbar.set,
                                  bg="#f9f9f9", selectbackground="#90caf9")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="x", expand=True)

        self._points = []

        # ── Calculate button ───────────────────────────────────────────────────
        tk.Button(self.fenetre,
                  text="Calculate unknown concentration + show plot",
                  bg="#c8e6c9", width=42, height=2,
                  command=self._calculate).pack(pady=8)

        # ── Result display ─────────────────────────────────────────────────────
        self.label_resultat = tk.Label(self.fenetre, text="", font=("Arial", 12, "bold"))
        self.label_resultat.pack(pady=4)

        self.label_details = tk.Label(self.fenetre, text="", font=("Arial", 10), fg="#444444")
        self.label_details.pack()

        self.label_erreur = tk.Label(self.fenetre, text="", fg="red")
        self.label_erreur.pack()

    # ── Point management ──────────────────────────────────────────────────────

    def _add_manual_point(self):
        try:
            c = float(self.entry_conc.get().replace(",", "."))
            a = float(self.entry_area.get().replace(",", "."))
        except ValueError:
            self.label_erreur.config(text="Please enter valid numbers.")
            return
        self._points.append((c, a))
        self._refresh_listbox()
        self.entry_conc.delete(0, "end")
        self.entry_area.delete(0, "end")
        self.label_erreur.config(text="")

    def _remove_last_point(self):
        if self._points:
            self._points.pop()
            self._refresh_listbox()

    def _clear_all(self):
        self._points = []
        self._refresh_listbox()
        self.label_resultat.config(text="")
        self.label_details.config(text="")
        self.label_erreur.config(text="")

    def _refresh_listbox(self):
        self.listbox.delete(0, "end")
        for i, (c, a) in enumerate(self._points):
            self.listbox.insert("end",
                f"  {i+1:>2}.   {c:>20.4f}   {a:>16.4f}")

    # ── Paste handler ──────────────────────────────────────────────────────────

    def _on_paste(self, event=None):
        self.fenetre.after(100, self._parse_paste)

    def _parse_paste(self):
        raw = self.text_paste.get("1.0", "end").strip()
        if not raw:
            self.label_erreur.config(text="Nothing to parse.")
            return

        new_points = []
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
                c = float(parts[0].replace(",", "."))
                a = float(parts[1].replace(",", "."))
                new_points.append((c, a))
            except ValueError:
                continue

        if not new_points:
            self.label_erreur.config(
                text="No valid rows found. Make sure data has two numeric columns.")
            return

        self._points = new_points
        self._refresh_listbox()
        self.label_erreur.config(
            text=f"{len(self._points)} point(s) loaded successfully.")

    # ── Calculation ────────────────────────────────────────────────────────────

    def _calculate(self):
        if len(self._points) < 2:
            messagebox.showwarning(
                "Not enough points",
                "Please enter at least 2 data points.",
                parent=self.fenetre
            )
            return

        concentrations = [p[0] for p in self._points]
        areas = [p[1] for p in self._points]
        unit = self.entry_unit.get().strip()

        try:
            # Compute only (NO PLOT)
            result = plot_standard_addition(concentrations, areas, show_plot=False)
        except ValueError as e:
            self.label_erreur.config(text=str(e))
            self.label_resultat.config(text="")
            self.label_details.config(text="")
            return

        C = abs(result["C_unknown"])
        a = result["a"]
        b = result["b"]
        r2 = result["r2"]

        sign = "+" if b >= 0 else "-"

        # Show result BEFORE plot
        self.label_resultat.config(text=f"Concentration of analyte in solution: {C:.6f} {unit}")
        self.label_details.config(
            text=f"y = {a:.4f}x {sign} {abs(b):.4f}    R² = {r2:.4f}"
        )
        self.label_erreur.config(text="")

        # Show the plot ONCE
        plot_standard_addition(concentrations, areas, show_plot=True)

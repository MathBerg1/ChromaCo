import tkinter as tk
from tkinter import messagebox
from chromaco.interfaces.fonctions_colonnes import resolution_between_two_peaks


class InterfaceResolution:
    def __init__(self, parent):

        self.fenetre = tk.Toplevel(parent)
        self.fenetre.title("Calculator of the resolution between two peaks")
        self.fenetre.geometry("600x640")
        self.fenetre.resizable(False, True)

        # ── Manual input fields ────────────────────────────────────────────────
        frame_manual = tk.LabelFrame(self.fenetre, text="Manual input", padx=10, pady=10)
        frame_manual.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_manual, text="Brut retention time peak 1 [min] :").grid(row=0, column=0, sticky="w", pady=3)
        self.entree1 = tk.Entry(frame_manual, width=15)
        self.entree1.grid(row=0, column=1, padx=10)

        tk.Label(frame_manual, text="Width of the base of peak 1 [min] :").grid(row=1, column=0, sticky="w", pady=3)
        self.entree2 = tk.Entry(frame_manual, width=15)
        self.entree2.grid(row=1, column=1, padx=10)

        tk.Label(frame_manual, text="Brut retention time peak 2 [min] :").grid(row=2, column=0, sticky="w", pady=3)
        self.entree3 = tk.Entry(frame_manual, width=15)
        self.entree3.grid(row=2, column=1, padx=10)

        tk.Label(frame_manual, text="Width of the base of peak 2 [min] :").grid(row=3, column=0, sticky="w", pady=3)
        self.entree4 = tk.Entry(frame_manual, width=15)
        self.entree4.grid(row=3, column=1, padx=10)

        tk.Button(frame_manual, text="Calculate", bg="#bbdefb", width=15,
                  command=self._calculer_manuel).grid(row=4, column=0, columnspan=2, pady=8)

        # ── Excel paste section ────────────────────────────────────────────────
        frame_excel = tk.LabelFrame(self.fenetre, text="Paste from Excel", padx=10, pady=10)
        frame_excel.pack(fill="x", padx=15, pady=(0, 5))

        tk.Label(frame_excel,
                 text="Paste your Excel data below (two columns: retention time | peak width base).\n"
                      "Select exactly two rows (one per peak) then click 'Calculate resolution'.",
                 justify="left", fg="#555555", font=("Arial", 9)).pack(anchor="w")

        # Paste area
        self.text_paste = tk.Text(frame_excel, height=5, font=("Courier", 10))
        self.text_paste.pack(fill="x", pady=5)
        self.text_paste.bind("<Control-v>", self._on_paste)
        self.text_paste.bind("<<Paste>>", self._on_paste)

        tk.Button(frame_excel, text="Parse data", bg="#ffe082", width=12,
                  command=self._parse_paste).pack(pady=(0, 5))

        tk.Label(frame_excel,
                 text="Parsed rows — select exactly 2 rows (Ctrl+click for multi-select):",
                 font=("Arial", 9), fg="#555555").pack(anchor="w")

        frm_list = tk.Frame(frame_excel)
        frm_list.pack(fill="x")

        scrollbar = tk.Scrollbar(frm_list, orient="vertical")
        self.listbox = tk.Listbox(frm_list, height=5, font=("Courier", 10),
                                  yscrollcommand=scrollbar.set,
                                  selectmode="multiple",  # allows multi-select
                                  bg="#f9f9f9", selectbackground="#90caf9")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="x", expand=True)

        self._rows = []

        # ── Calculate button — outside frame_excel ─────────────────────────────
        tk.Button(self.fenetre, text="Calculate resolution between selected rows",
                  bg="#c8e6c9", width=38, height=2,
                  command=self._calculer_resolution).pack(pady=8)

        # ── Result display ─────────────────────────────────────────────────────
        self.label_resultat = tk.Label(self.fenetre, text="", font=("Arial", 12, "bold"))
        self.label_resultat.pack(pady=5)

        self.label_erreur = tk.Label(self.fenetre, text="", fg="red")
        self.label_erreur.pack()

    # ── Manual calculation ─────────────────────────────────────────────────────

    def _calculer_manuel(self):
        try:
            tR1 = float(self.entree1.get())
            wb1 = float(self.entree2.get())
            tR2 = float(self.entree3.get())
            wb2 = float(self.entree4.get())
            res = resolution_between_two_peaks(tR1, tR2, wb1, wb2)
            self.label_resultat.config(text=f"Resolution : {res:.4f}")
            self.label_erreur.config(text="")
        except ValueError:
            self.label_erreur.config(text="Please enter valid numbers.")
            self.label_resultat.config(text="")

    # ── Paste handler ──────────────────────────────────────────────────────────

    def _on_paste(self, event=None):
        self.fenetre.after(100, self._parse_paste)

    def _parse_paste(self):
        raw = self.text_paste.get("1.0", "end").strip()
        if not raw:
            self.label_erreur.config(text="Nothing to parse.")
            return

        self._rows = []
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
                tR = float(parts[0].replace(",", "."))
                wb = float(parts[1].replace(",", "."))
                self._rows.append((tR, wb))
                self.listbox.insert("end",
                    f"  tR = {tR:>10.4f}    wb = {wb:>10.4f}")
            except ValueError:
                continue

        if not self._rows:
            self.label_erreur.config(
                text="No valid rows found. Make sure data has two numeric columns.")
        else:
            self.label_erreur.config(
                text=f"{len(self._rows)} row(s) parsed. Select 2 rows to calculate resolution.")

    # ── Resolution calculation ─────────────────────────────────────────────────

    def _calculer_resolution(self):
        selection = self.listbox.curselection()

        if len(selection) != 2:
            messagebox.showwarning(
                "Select exactly 2 rows",
                f"Please select exactly 2 rows (one per peak).\n"
                f"Currently selected: {len(selection)} row(s).\n\n"
                f"Use Ctrl+click to select multiple rows.",
                parent=self.fenetre
            )
            return

        idx1, idx2 = selection[0], selection[1]
        tR1, wb1   = self._rows[idx1]
        tR2, wb2   = self._rows[idx2]

        try:
            res = resolution_between_two_peaks(tR1, tR2, wb1, wb2)
            self.label_resultat.config(
                text=f"Peak {idx1+1} (tR={tR1}, wb={wb1})  &  "
                     f"Peak {idx2+1} (tR={tR2}, wb={wb2})\n"
                     f"Resolution : {res:.4f}")
            self.label_erreur.config(text="")
        except Exception as e:
            self.label_erreur.config(text=f"Calculation error: {e}")
            self.label_resultat.config(text="")
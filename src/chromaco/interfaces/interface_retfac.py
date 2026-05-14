import tkinter as tk
from tkinter import messagebox
from chromaco.interfaces.fonctions_colonnes import calculate_retention_factor


class InterfaceRetentionFactor:
    def __init__(self, parent):

        self.fenetre = tk.Toplevel(parent)
        self.fenetre.title("Calculator of the retention factor k")
        self.fenetre.geometry("600x640")
        self.fenetre.resizable(False, True)

        # ── Manual input fields ────────────────────────────────────────────────
        frame_manual = tk.LabelFrame(self.fenetre, text="Manual input", padx=10, pady=10)
        frame_manual.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_manual, text="Retention time tR [min] :").grid(row=0, column=0, sticky="w", pady=3)
        self.entree1 = tk.Entry(frame_manual, width=15)
        self.entree1.grid(row=0, column=1, padx=10)

        tk.Label(frame_manual, text="Dead time t0 [min] :").grid(row=1, column=0, sticky="w", pady=3)
        self.entree2 = tk.Entry(frame_manual, width=15)
        self.entree2.grid(row=1, column=1, padx=10)

        tk.Button(frame_manual, text="Calculate", bg="#bbdefb", width=15,
                  command=self._calculer_manuel).grid(row=2, column=0, columnspan=2, pady=8)

        # ── Excel paste section ────────────────────────────────────────────────
        frame_excel = tk.LabelFrame(self.fenetre, text="Paste from Excel", padx=10, pady=10)
        frame_excel.pack(fill="x", padx=15, pady=(0, 5))

        tk.Label(frame_excel,
                 text="Paste your Excel data below (two columns: tR | t0).\n"
                      "Select exactly ONE row then click 'Calculate retention factor'.",
                 justify="left", fg="#555555", font=("Arial", 9)).pack(anchor="w")

        # Paste area
        self.text_paste = tk.Text(frame_excel, height=5, font=("Courier", 10))
        self.text_paste.pack(fill="x", pady=5)
        self.text_paste.bind("<Control-v>", self._on_paste)
        self.text_paste.bind("<<Paste>>", self._on_paste)

        tk.Button(frame_excel, text="Parse data", bg="#ffe082", width=12,
                  command=self._parse_paste).pack(pady=(0, 5))

        tk.Label(frame_excel,
                 text="Parsed rows — select exactly 1 row:",
                 font=("Arial", 9), fg="#555555").pack(anchor="w")

        frm_list = tk.Frame(frame_excel)
        frm_list.pack(fill="x")

        scrollbar = tk.Scrollbar(frm_list, orient="vertical")
        self.listbox = tk.Listbox(frm_list, height=5, font=("Courier", 10),
                                  yscrollcommand=scrollbar.set,
                                  selectmode="single",
                                  bg="#f9f9f9", selectbackground="#90caf9")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="x", expand=True)

        self._rows = []

        # ── Calculate button — outside frame_excel ─────────────────────────────
        tk.Button(self.fenetre, text="Calculate retention factor from selected row",
                  bg="#c8e6c9", width=38, height=2,
                  command=self._calculer_retention).pack(pady=8)

        # ── Result display ─────────────────────────────────────────────────────
        self.label_resultat = tk.Label(self.fenetre, text="", font=("Arial", 12, "bold"))
        self.label_resultat.pack(pady=5)

        self.label_erreur = tk.Label(self.fenetre, text="", fg="red")
        self.label_erreur.pack()

    # ── Manual calculation ─────────────────────────────────────────────────────

    def _calculer_manuel(self):
        try:
            tR = float(self.entree1.get())
            t0 = float(self.entree2.get())
            k = calculate_retention_factor(tR, t0)
            self.label_resultat.config(text=f"Retention factor k : {k:.4f}")
            self.label_erreur.config(text="")
        except ValueError as e:
            self.label_erreur.config(text=f"Error: {e}")
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
                t0 = float(parts[1].replace(",", "."))
                self._rows.append((tR, t0))
                self.listbox.insert("end",
                    f"  tR = {tR:>10.4f}    t0 = {t0:>10.4f}")
            except ValueError:
                continue

        if not self._rows:
            self.label_erreur.config(
                text="No valid rows found. Make sure data has two numeric columns.")
        else:
            self.label_erreur.config(
                text=f"{len(self._rows)} row(s) parsed. Select 1 row to calculate k.")

    # ── Retention factor calculation ───────────────────────────────────────────

    def _calculer_retention(self):
        selection = self.listbox.curselection()

        if len(selection) != 1:
            messagebox.showwarning(
                "Select exactly 1 row",
                f"Please select exactly 1 row.\n"
                f"Currently selected: {len(selection)} row(s).",
                parent=self.fenetre
            )
            return

        idx = selection[0]
        tR, t0 = self._rows[idx]

        try:
            k = calculate_retention_factor(tR, t0)
            self.label_resultat.config(
                text=f"Row {idx+1} (tR={tR}, t0={t0})\n"
                     f"Retention factor k : {k:.4f}")
            self.label_erreur.config(text="")
        except Exception as e:
            self.label_erreur.config(text=f"Calculation error: {e}")
            self.label_resultat.config(text="")

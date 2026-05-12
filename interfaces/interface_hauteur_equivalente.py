import tkinter as tk
from tkinter import messagebox
from fonctions_colonnes import equivalent_high_one


class InterfaceHauteur:
    def __init__(self, parent):

        self.fenetre = tk.Toplevel(parent)
        self.fenetre.title("Calculator of the equivalent height")
        self.fenetre.geometry("600x620")
        self.fenetre.resizable(False, True)

        # ── Manual input fields ────────────────────────────────────────────────
        frame_manual = tk.LabelFrame(self.fenetre, text="Manual input", padx=10, pady=10)
        frame_manual.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_manual, text="Brut retention time [min] :").grid(row=0, column=0, sticky="w", pady=3)
        self.entree1 = tk.Entry(frame_manual, width=15)
        self.entree1.grid(row=0, column=1, padx=10)

        tk.Label(frame_manual, text="Width of the base of the peak [min] :").grid(row=1, column=0, sticky="w", pady=3)
        self.entree2 = tk.Entry(frame_manual, width=15)
        self.entree2.grid(row=1, column=1, padx=10)

        tk.Label(frame_manual, text="Length of the column [m] :").grid(row=2, column=0, sticky="w", pady=3)
        self.entree3 = tk.Entry(frame_manual, width=15)
        self.entree3.grid(row=2, column=1, padx=10)

        tk.Button(frame_manual, text="Calculate", bg="#bbdefb", width=15,
                  command=self._calculer_manuel).grid(row=3, column=0, columnspan=2, pady=8)

        # ── Excel paste section ────────────────────────────────────────────────
        frame_excel = tk.LabelFrame(self.fenetre, text="Paste from Excel", padx=10, pady=10)
        frame_excel.pack(fill="x", padx=15, pady=(0, 5))

        tk.Label(frame_excel,
                 text="Paste your Excel data below (two columns: retention time | peak width).\n"
                      "Select a row then click 'Calculate selected row'.",
                 justify="left", fg="#555555", font=("Arial", 9)).pack(anchor="w")

        # Column length input for Excel mode
        frm_len = tk.Frame(frame_excel)
        frm_len.pack(anchor="w", pady=5)
        tk.Label(frm_len, text="Length of the column [m] :").pack(side="left")
        self.entree_col_len = tk.Entry(frm_len, width=10)
        self.entree_col_len.pack(side="left", padx=8)

        # Paste area (Text widget)
        self.text_paste = tk.Text(frame_excel, height=5, font=("Courier", 10))
        self.text_paste.pack(fill="x", pady=5)
        self.text_paste.bind("<Control-v>", self._on_paste)
        self.text_paste.bind("<<Paste>>", self._on_paste)

        tk.Button(frame_excel, text="Parse data", bg="#ffe082", width=12,
                  command=self._parse_paste).pack(pady=(0, 5))

        # Parsed rows label
        tk.Label(frame_excel, text="Parsed rows — click a row to select it:",
                 font=("Arial", 9), fg="#555555").pack(anchor="w")

        # Listbox with scrollbar
        frm_list = tk.Frame(frame_excel)
        frm_list.pack(fill="x")

        scrollbar = tk.Scrollbar(frm_list, orient="vertical")
        self.listbox = tk.Listbox(frm_list, height=5, font=("Courier", 10),
                                  yscrollcommand=scrollbar.set, selectmode="single",
                                  bg="#f9f9f9", selectbackground="#90caf9")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="x", expand=True)

        # Internal storage of parsed rows
        self._rows = []

        # ── Calculate selected row button — OUTSIDE frame_excel ────────────────
        tk.Button(self.fenetre, text="Calculate selected row", bg="#c8e6c9",
                  width=25, height=2,
                  command=self._calculer_ligne).pack(pady=8)

        # ── Result display ─────────────────────────────────────────────────────
        self.label_resultat = tk.Label(self.fenetre, text="", font=("Arial", 12, "bold"))
        self.label_resultat.pack(pady=5)

        self.label_erreur = tk.Label(self.fenetre, text="", fg="red")
        self.label_erreur.pack()

    # ── Manual calculation ─────────────────────────────────────────────────────

    def _calculer_manuel(self):
        try:
            tR  = float(self.entree1.get())
            wb  = float(self.entree2.get())
            L   = float(self.entree3.get())
            res = equivalent_high_one(L, tR, wb)
            self.label_resultat.config(text=f"Result : {res:.6f} m")
            self.label_erreur.config(text="")
        except ValueError:
            self.label_erreur.config(text="Please enter valid numbers.")
            self.label_resultat.config(text="")

    # ── Paste handler ──────────────────────────────────────────────────────────

    def _on_paste(self, event=None):
        """Trigger parse after paste completes."""
        self.fenetre.after(100, self._parse_paste)

    def _parse_paste(self):
        """Read the Text widget, parse tab-separated rows, fill listbox."""
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

            # Accept tab, semicolon or multiple spaces
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
                continue  # skip headers or non-numeric lines

        if not self._rows:
            self.label_erreur.config(
                text="No valid rows found. Make sure data has two numeric columns.")
        else:
            self.label_erreur.config(text=f"{len(self._rows)} row(s) parsed successfully.")

    # ── Row calculation ────────────────────────────────────────────────────────

    def _calculer_ligne(self):
        """Calculate equivalent height for the selected listbox row."""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No selection",
                                   "Please click on a row in the list first.",
                                   parent=self.fenetre)
            return

        try:
            L = float(self.entree_col_len.get())
        except ValueError:
            self.label_erreur.config(text="Please enter a valid column length.")
            return

        idx = selection[0]
        tR, wb = self._rows[idx]

        try:
            res = equivalent_high_one(L, tR, wb)
            self.label_resultat.config(
                text=f"Row {idx + 1} — tR={tR}, wb={wb}  →  H = {res:.6f} m")
            self.label_erreur.config(text="")
        except Exception as e:
            self.label_erreur.config(text=f"Calculation error: {e}")
            self.label_resultat.config(text="")
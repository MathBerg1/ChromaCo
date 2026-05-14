import tkinter as tk
from tkinter import messagebox
from chromaco.interfaces.fonctions_colonnes import compare_two_columns_advanced


class InterfaceCompareColumns:
    def __init__(self, parent):

        self.fenetre = tk.Toplevel(parent)
        self.fenetre.title("Comparison of two chromatography columns")
        self.fenetre.geometry("720x780")
        self.fenetre.resizable(True, True)

        # ───────────────────────────────────────────────
        # SCROLLABLE CANVAS (global scroll)
        # ───────────────────────────────────────────────
        container = tk.Frame(self.fenetre)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.scroll_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.bind("<Configure>",
                               lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Scroll global
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # ───────────────────────────────────────────────
        # COLUMN LENGTH
        # ───────────────────────────────────────────────
        frame_len = tk.LabelFrame(self.scroll_frame, text="Column configuration", padx=10, pady=10)
        frame_len.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_len, text="Column length [m] :").grid(row=0, column=0, sticky="w")
        self.entry_length = tk.Entry(frame_len, width=10)
        self.entry_length.grid(row=0, column=1, padx=10)
        self.entry_length.insert(0, "0.25")

        # ───────────────────────────────────────────────
        # COLUMN A INPUT
        # ───────────────────────────────────────────────
        frame_A = tk.LabelFrame(self.scroll_frame, text="Column A — paste data", padx=10, pady=10)
        frame_A.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_A, text="Paste two columns: retention time | peak width",
                 fg="#555", font=("Arial", 9)).pack(anchor="w")

        self.boxA = tk.Text(frame_A, height=5, font=("Courier", 10))
        self.boxA.pack(fill="x", pady=5)

        # ───────────────────────────────────────────────
        # COLUMN B INPUT
        # ───────────────────────────────────────────────
        frame_B = tk.LabelFrame(self.scroll_frame, text="Column B — paste data", padx=10, pady=10)
        frame_B.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_B, text="Paste two columns: retention time | peak width",
                 fg="#555", font=("Arial", 9)).pack(anchor="w")

        self.boxB = tk.Text(frame_B, height=5, font=("Courier", 10))
        self.boxB.pack(fill="x", pady=5)

        # ───────────────────────────────────────────────
        # PARSE BUTTON
        # ───────────────────────────────────────────────
        tk.Button(self.scroll_frame, text="Parse data", bg="#ffe082", width=20,
                  command=self._parse_all).pack(pady=5)

        # ───────────────────────────────────────────────
        # PEAK SELECTION (ONE LISTBOX)
        # ───────────────────────────────────────────────
        frame_peaks = tk.LabelFrame(self.scroll_frame, text="Select peaks to compare", padx=10, pady=10)
        frame_peaks.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_peaks, text="If no peak is selected, all peaks will be compared.",
                 fg="#555", font=("Arial", 9)).pack(anchor="w")

        self.listbox_peaks = tk.Listbox(frame_peaks, height=6, font=("Courier", 10),
                                        bg="#f9f9f9", selectbackground="#90caf9",
                                        selectmode="multiple")
        self.listbox_peaks.pack(fill="x")

        # ───────────────────────────────────────────────
        # COMPARE BUTTON
        # ───────────────────────────────────────────────
        tk.Button(self.scroll_frame, text="Compare columns", bg="#c8e6c9",
                  width=25, height=2,
                  command=self._compare).pack(pady=10)

        # ───────────────────────────────────────────────
        # RESULTS (independent scroll)
        # ───────────────────────────────────────────────
        frame_res = tk.LabelFrame(self.scroll_frame, text="Results", padx=10, pady=10)
        frame_res.pack(fill="both", expand=True, padx=15, pady=10)

        self.text = tk.Text(frame_res, height=15, font=("Courier", 10), state="disabled")
        self.text.pack(fill="both", expand=True)

        # Scroll indépendant pour la zone résultats
        self.text.bind("<Enter>", lambda e: self._activate_result_scroll())
        self.text.bind("<Leave>", lambda e: self._deactivate_result_scroll())

        self.label_status = tk.Label(self.scroll_frame, text="", fg="red")
        self.label_status.pack()

        # Internal storage
        self.columnA = {}
        self.columnB = {}

    # ───────────────────────────────────────────────
    # SCROLL FUNCTIONS
    # ───────────────────────────────────────────────
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def _scroll_results(self, event):
        self.text.yview_scroll(int(-event.delta / 120), "units")

    def _activate_result_scroll(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.text.bind_all("<MouseWheel>", self._scroll_results)

    def _deactivate_result_scroll(self):
        self.text.unbind_all("<MouseWheel>")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    # ───────────────────────────────────────────────
    # PARSING
    # ───────────────────────────────────────────────
    def _parse_box(self, box):
        raw = box.get("1.0", "end").strip()
        peaks = {}
        idx = 1

        for line in raw.splitlines():
            line = line.strip()
            line = line.replace(",", ".")  # virgule décimale

            parts = line.replace(";", "\t").split()
            if len(parts) < 2:
                continue

            try:
                tR = float(parts[0])
                w = float(parts[1])
                peaks[idx] = [tR, w]
                idx += 1
            except:
                continue

        return peaks

    def _parse_all(self):
        self.columnA = self._parse_box(self.boxA)
        self.columnB = self._parse_box(self.boxB)

        self.listbox_peaks.delete(0, "end")

        max_peaks = min(len(self.columnA), len(self.columnB))

        for i in range(1, max_peaks + 1):
            self.listbox_peaks.insert("end", f"Peak {i}")

        self.label_status.config(text=f"{max_peaks} peaks detected.")

    # ───────────────────────────────────────────────
    # COMPARISON
    # ───────────────────────────────────────────────
    def _compare(self):

        selection = self.listbox_peaks.curselection()

        if not selection:
            selected_peaks = None
            mode = "global"
        else:
            selected_peaks = [int(self.listbox_peaks.get(i).split()[1]) for i in selection]
            mode = "subset"

        try:
            length = float(self.entry_length.get().replace(",", "."))
        except:
            messagebox.showerror("Error", "Invalid column length.")
            return

        result = compare_two_columns_advanced(
            columnA=self.columnA,
            columnB=self.columnB,
            column_length=length,
            selected_peaks=selected_peaks,
            mode=mode
        )

        self.text.config(state="normal")
        self.text.delete("1.0", "end")

        self.text.insert("end", "=== COMPARISON RESULTS ===\n\n")

        # VERDICT
        for key, winner in result["verdict"].items():
            param = key.replace("Best_", "").replace("_", " ").title()
            self.text.insert("end", f"{param}: Column {winner}\n")

        # COLUMN A
        self.text.insert("end", "\nColumn A:\n")
        for k, v in result["A"].items():
            self.text.insert("end", f"  {k}: {v}\n")

        # WARNINGS A
        if result["warnings"]["A"]:
            self.text.insert("end", "\n  ⚠ Warnings for Column A:\n")
            for msg in result["warnings"]["A"]:
                self.text.insert("end", f"    - {msg}\n")

        # COLUMN B
        self.text.insert("end", "\nColumn B:\n")
        for k, v in result["B"].items():
            self.text.insert("end", f"  {k}: {v}\n")

        # WARNINGS B
        if result["warnings"]["B"]:
            self.text.insert("end", "\n  ⚠ Warnings for Column B:\n")
            for msg in result["warnings"]["B"]:
                self.text.insert("end", f"    - {msg}\n")

        self.text.config(state="disabled")
        self.label_status.config(text="Comparison complete.")

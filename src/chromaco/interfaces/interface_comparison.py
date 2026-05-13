import tkinter as tk
from tkinter import messagebox
from chromaco.interfaces.fonctions_colonnes import compare_two_columns_advanced, theorical_plates_one

EPSILON = 1e-12


def safe_theoretical_plates(tR, w):
    try:
        if tR <= 0 or w <= 0:
            return 0
        N = theorical_plates_one(tR, w)
        if N < EPSILON:
            return 0
        return N
    except:
        return 0


class InterfaceCompareColumns:
    def __init__(self, parent):

        self.win = tk.Toplevel(parent)
        self.win.title("Column Comparison Tool")
        self.win.geometry("750x800")
        self.win.resizable(False, True)

        container = tk.Frame(self.win)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.inner = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._resize_inner)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        title = tk.Label(self.inner, text="Column Comparison Tool", font=("Arial", 16, "bold"))
        title.pack(pady=15)

        frame_len = tk.LabelFrame(self.inner, text="Column length", padx=10, pady=10)
        frame_len.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_len, text="Column length [m]:").grid(row=0, column=0, sticky="w")
        self.entry_length = tk.Entry(frame_len, width=10)
        self.entry_length.grid(row=0, column=1, padx=10)
        self.entry_length.insert(0, "0.25")

        frame_A = tk.LabelFrame(self.inner, text="Paste Excel data for Column A", padx=10, pady=10)
        frame_A.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_A,
                 text="Paste two columns: retention time | peak width",
                 justify="left", fg="#555555", font=("Arial", 9)).pack(anchor="w")

        self.boxA = tk.Text(frame_A, height=6, font=("Courier", 10))
        self.boxA.pack(fill="x", pady=5)
        self.boxA.bind("<Control-v>", lambda e: self.win.after(100, self._parse_all))
        self.boxA.bind("<<Paste>>", lambda e: self.win.after(100, self._parse_all))

        frame_B = tk.LabelFrame(self.inner, text="Paste Excel data for Column B", padx=10, pady=10)
        frame_B.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_B,
                 text="Paste two columns: retention time | peak width",
                 justify="left", fg="#555555", font=("Arial", 9)).pack(anchor="w")

        self.boxB = tk.Text(frame_B, height=6, font=("Courier", 10))
        self.boxB.pack(fill="x", pady=5)
        self.boxB.bind("<Control-v>", lambda e: self.win.after(100, self._parse_all))
        self.boxB.bind("<<Paste>>", lambda e: self.win.after(100, self._parse_all))

        tk.Button(self.inner, text="Parse data", bg="#FFD6A5", width=15,
                  command=self._parse_all).pack(pady=5)

        frame_peaks = tk.LabelFrame(self.inner, text="Select peaks to include", padx=10, pady=10)
        frame_peaks.pack(fill="x", padx=15, pady=10)

        list_frame = tk.Frame(frame_peaks)
        list_frame.pack(fill="x")

        scrollbar2 = tk.Scrollbar(list_frame, orient="vertical")
        self.peak_list = tk.Listbox(list_frame, height=6, font=("Courier", 10),
                                    yscrollcommand=scrollbar2.set, selectmode="multiple",
                                    bg="#f9f9f9", selectbackground="#90caf9")
        scrollbar2.config(command=self.peak_list.yview)
        scrollbar2.pack(side="right", fill="y")
        self.peak_list.pack(side="left", fill="x", expand=True)

        self.columnA = {}
        self.columnB = {}

        frame_params = tk.LabelFrame(self.inner, text="Select parameters to compare", padx=10, pady=10)
        frame_params.pack(fill="x", padx=15, pady=10)

        self.var_rs = tk.BooleanVar(value=True)
        self.var_n = tk.BooleanVar(value=True)
        self.var_h = tk.BooleanVar(value=True)
        self.var_width = tk.BooleanVar(value=True)
        self.var_time = tk.BooleanVar(value=True)

        tk.Checkbutton(frame_params, text="Resolution", variable=self.var_rs).grid(row=0, column=0, sticky="w", padx=20)
        tk.Checkbutton(frame_params, text="Number of plates", variable=self.var_n).grid(row=1, column=0, sticky="w", padx=20)
        tk.Checkbutton(frame_params, text="HETP", variable=self.var_h).grid(row=2, column=0, sticky="w", padx=20)
        tk.Checkbutton(frame_params, text="Peak width", variable=self.var_width).grid(row=3, column=0, sticky="w", padx=20)
        tk.Checkbutton(frame_params, text="Chromatography time", variable=self.var_time).grid(row=4, column=0, sticky="w", padx=20)

        tk.Button(self.inner, text="Compare selected peaks", bg="#C8F7C5",
                  width=25, height=2, command=self._compare).pack(pady=10)

        self.text = tk.Text(self.inner, height=12, width=90, font=("Courier", 10))
        self.text.pack(pady=10)

        self.label_error = tk.Label(self.inner, text="", fg="red")
        self.label_error.pack()

    def _resize_inner(self, event):
        self.canvas.itemconfig(self.canvas.find_all()[0], width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")

    def _parse_box(self, box):
        raw = box.get("1.0", "end").strip()
        peaks = {}
        idx = 1
        for line in raw.splitlines():
            parts = line.replace(",", " ").split()
            if len(parts) < 2:
                continue
            try:
                tR = float(parts[0])
                w = float(parts[1])
                peaks[idx] = [tR, w]
                idx += 1
            except:
                pass
        return peaks

    def _parse_all(self):
        self.columnA = self._parse_box(self.boxA)
        self.columnB = self._parse_box(self.boxB)

        self.peak_list.delete(0, "end")

        if not self.columnA or not self.columnB:
            self.label_error.config(text="Invalid or empty data.")
            return

        for i in sorted(self.columnA.keys()):
            self.peak_list.insert("end", f"Peak {i}")

        self.label_error.config(text=f"{len(self.columnA)} peaks loaded.")

    def _compare(self):
        try:
            column_length = float(self.entry_length.get())
            if column_length <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Enter a valid column length.")
            return

        selected = self.peak_list.curselection()

        if selected:
            peaks = [i + 1 for i in selected]
            mode = "subset"
        else:
            peaks = None
            mode = "global"

        params = {
            "Rs": self.var_rs.get(),
            "N": self.var_n.get(),
            "H": self.var_h.get(),
            "widths": self.var_width.get(),
            "time": self.var_time.get()
        }

        if not any(params.values()):
            messagebox.showerror("Error", "Select at least one parameter.")
            return

        result = compare_two_columns_advanced(
            columnA=self.columnA,
            columnB=self.columnB,
            column_length=column_length,
            selected_peaks=peaks,
            mode=mode
        )

        elimA = result["elimination"]["A"]
        elimB = result["elimination"]["B"]

        if elimA and elimB:
            messagebox.showwarning("Warning", "Both columns are eliminated (resolution < 1.5).")
        elif elimA:
            messagebox.showwarning("Warning", "Column A is eliminated (resolution < 1.5).")
        elif elimB:
            messagebox.showwarning("Warning", "Column B is eliminated (resolution < 1.5).")

        self.text.config(state="normal")
        self.text.delete("1.0", "end")

        self.text.insert("end", "Comparison results:\n\n")

        for key, winner in result["verdict"].items():
            param = key.replace("Best_", "")
            if params.get(param, False):
                self.text.insert("end", f"{key}: Column {winner}\n")

        self.text.insert("end", "\nColumn A scores:\n")
        for k, v in result["A"].items():
            if params.get(k, False):
                self.text.insert("end", f"  {k}: {v}\n")

        self.text.insert("end", "\nColumn B scores:\n")
        for k, v in result["B"].items():
            if params.get(k, False):
                self.text.insert("end", f"  {k}: {v}\n")

        self.text.config(state="disabled")

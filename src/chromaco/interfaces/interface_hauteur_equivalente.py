import tkinter as tk
import sys
from tkinter import messagebox
from chromaco.interfaces.fonctions_colonnes import equivalent_high_one

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

def _dpi_scale(win):
    try:
        scale = win.winfo_fpixels("1i") / 72
        if scale > 1.25:
            win.tk.call("tk", "scaling", scale)
    except Exception:
        pass

def _section_label(parent, text):
    tk.Label(parent, text=text.upper(), font=("Segoe UI", 8, "bold"),
             fg=ACCENT, bg=BG).pack(anchor="w", pady=(0, 4))

def _styled_entry(parent, width=14):
    return tk.Entry(parent, width=width, font=("Segoe UI", 10),
                    bg=SURFACE2, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                    relief="flat", highlightbackground=BORDER,
                    highlightthickness=1, highlightcolor=ACCENT)

def _action_btn(parent, text, cmd, color, large=False):
    def lighten(h):
        r, g, b = int(h[1:3],16), int(h[3:5],16), int(h[5:7],16)
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

def _scrollable_listbox(parent, height=5):
    frame = tk.Frame(parent, bg=SURFACE2, highlightbackground=BORDER,
                     highlightthickness=1)
    sb = tk.Scrollbar(frame, orient="vertical")
    sb.pack(side="right", fill="y")
    lb = tk.Listbox(frame, height=height, font=("Segoe UI Mono", 10),
                    bg=SURFACE2, fg=TEXT_PRI,
                    selectbackground=ACCENT, selectforeground=BG,
                    relief="flat", highlightthickness=0,
                    activestyle="none", selectmode="single",
                    borderwidth=0, yscrollcommand=sb.set)
    lb.pack(side="left", fill="both", expand=True)
    sb.config(command=lb.yview)
    return frame, lb


class InterfaceHauteur:
    def __init__(self, parent):
        self.fenetre = tk.Toplevel(parent)
        self.fenetre.title("Equivalent Plate Height")
        self.fenetre.geometry("650x780")
        self.fenetre.resizable(True, True)
        self.fenetre.config(bg=BG)
        _dpi_scale(self.fenetre)

        hdr = tk.Frame(self.fenetre, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(24, 0))
        tk.Label(hdr, text="C H R O M A C O", font=("Segoe UI", 8, "bold"),
                 fg=ACCENT, bg=BG).pack(anchor="w")
        tk.Label(hdr, text="Equivalent Plate Height",
                 font=("Segoe UI", 20, "bold"), fg=TEXT_PRI, bg=BG).pack(anchor="w", pady=(2,1))
        tk.Label(hdr, text="H = L / N  via retention time and peak width",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=BG).pack(anchor="w")
        tk.Frame(self.fenetre, bg=ACCENT, height=2).pack(fill="x", padx=28, pady=(12, 0))

        scroll_outer = tk.Frame(self.fenetre, bg=BG)
        scroll_outer.pack(fill="both", expand=True, padx=28, pady=(14, 0))

        self._canvas = tk.Canvas(scroll_outer, bg=BG, highlightthickness=0, bd=0)
        gsb = tk.Scrollbar(scroll_outer, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=gsb.set)
        gsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        sf = tk.Frame(self._canvas, bg=BG)
        self._sf_win = self._canvas.create_window((0, 0), window=sf, anchor="nw")
        sf.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._sf_win, width=e.width))

        self._canvas.bind("<MouseWheel>", lambda e: self._canvas.yview_scroll(int(-e.delta/120), "units"))
        self._canvas.bind("<Button-4>",   lambda e: self._canvas.yview_scroll(-1, "units"))
        self._canvas.bind("<Button-5>",   lambda e: self._canvas.yview_scroll(1,  "units"))
        self._canvas.bind("<Enter>", lambda e: self._canvas.focus_set())

        PAD = {"padx": 0, "pady": 8, "fill": "x"}

        wrap = tk.Frame(sf, bg=BG)
        wrap.pack(**PAD)
        _section_label(wrap, "Manual Input")
        card = tk.Frame(wrap, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x")

        self.entree1 = _labelled_entry_row(card, "Brut retention time (min)")
        self.entree2 = _labelled_entry_row(card, "Width of the peak base (min)")
        self.entree3 = _labelled_entry_row(card, "Column length (m)")

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=14)
        btn_row = tk.Frame(card, bg=SURFACE)
        btn_row.pack(fill="x", padx=14, pady=12)
        _action_btn(btn_row, "  Calculate", self._calculer_manuel, ACCENT).pack(side="left")

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=14)
        result_row = tk.Frame(card, bg=SURFACE)
        result_row.pack(fill="x", padx=14, pady=14)
        self.label_manual_result = tk.Label(result_row, text="—", font=("Segoe UI", 13, "bold"),
                                            fg=TEXT_SEC, bg=SURFACE, anchor="w")
        self.label_manual_result.pack(fill="x")
        self.label_manual_error = tk.Label(result_row, text="", font=("Segoe UI", 9),
                                           fg=DANGER, bg=SURFACE, anchor="w")
        self.label_manual_error.pack(fill="x")

        wrap2 = tk.Frame(sf, bg=BG)
        wrap2.pack(**PAD)
        _section_label(wrap2, "Paste from Excel")
        card2 = tk.Frame(wrap2, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        card2.pack(fill="x")

        tk.Label(card2,
                 text="Paste two columns: retention time  |  peak width\n"
                      "Select a row then click 'Calculate selected row'.",
                 font=("Segoe UI", 9), fg=TEXT_SEC, bg=SURFACE,
                 justify="left").pack(anchor="w", padx=14, pady=(10, 4))

        self.entree_col_len = _labelled_entry_row(card2, "Column length (m)")

        tk.Frame(card2, bg=BORDER, height=1).pack(fill="x", padx=14, pady=(4,0))

        tk.Label(card2, text="Paste area", font=("Segoe UI", 8),
                 fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=14, pady=(8, 2))
        paste_frame, self.text_paste = _scrollable_text(card2, height=5)
        paste_frame.pack(fill="x", padx=14, pady=(0, 6))

        self.text_paste.bind("<MouseWheel>", lambda e: self.text_paste.yview_scroll(int(-e.delta/120), "units"))
        self.text_paste.bind("<Button-4>",   lambda e: self.text_paste.yview_scroll(-1, "units"))
        self.text_paste.bind("<Button-5>",   lambda e: self.text_paste.yview_scroll(1,  "units"))

        self.text_paste.bind("<Control-v>", self._on_paste)
        self.text_paste.bind("<<Paste>>",   self._on_paste)

        parse_row = tk.Frame(card2, bg=SURFACE)
        parse_row.pack(fill="x", padx=14, pady=(0, 10))
        _action_btn(parse_row, "  Parse Data", self._parse_paste, WARNING).pack(side="left")

        tk.Frame(card2, bg=BORDER, height=1).pack(fill="x", padx=14)

        tk.Label(card2, text="Parsed rows — click to select",
                 font=("Segoe UI", 8), fg=TEXT_SEC, bg=SURFACE).pack(anchor="w", padx=14, pady=(8, 2))
        list_frame, self.listbox = _scrollable_listbox(card2, height=5)
        list_frame.pack(fill="x", padx=14, pady=(0, 12))

        self.listbox.bind("<MouseWheel>", lambda e: self.listbox.yview_scroll(int(-e.delta/120), "units"))
        self.listbox.bind("<Button-4>",   lambda e: self.listbox.yview_scroll(-1, "units"))
        self.listbox.bind("<Button-5>",   lambda e: self.listbox.yview_scroll(1,  "units"))

        self._rows = []

        _action_btn(sf, "  Calculate Selected Row", self._calculer_ligne, SUCCESS, large=True).pack(pady=(4, 0))

        self.label_resultat = tk.Label(sf, text="", font=("Segoe UI", 11, "bold"),
                                       fg=SUCCESS, bg=BG)
        self.label_resultat.pack(pady=(10, 0))

        self.label_erreur = tk.Label(sf, text="", font=("Segoe UI", 9),
                                     fg=DANGER, bg=BG)
        self.label_erreur.pack(pady=(2, 16))

    def _calculer_manuel(self):
        try:
            tR  = float(self.entree1.get().replace(",", "."))
            wb  = float(self.entree2.get().replace(",", "."))
            L   = float(self.entree3.get().replace(",", "."))
            res = equivalent_high_one(L, tR, wb)
            self.label_manual_result.config(text=f"H  =  {res:.6f} m", fg=SUCCESS)
            self.label_manual_error.config(text="")
        except ValueError:
            self.label_manual_error.config(text="Please enter valid numbers in all three fields.")
            self.label_manual_result.config(text="—", fg=TEXT_SEC)

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
                self.listbox.insert("end", f"  tR = {tR:>10.4f}    wb = {wb:>10.4f}")
            except ValueError:
                continue

        if not self._rows:
            self.label_erreur.config(text="No valid rows found.")
        else:
            self.label_erreur.config(text=f"✔  {len(self._rows)} row(s) parsed.")
            self.label_resultat.config(text="")

    def _calculer_ligne(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No selection", "Please click a row in the list first.", parent=self.fenetre)
            return
        try:
            L = float(self.entree_col_len.get().replace(",", "."))
        except ValueError:
            self.label_erreur.config(text="Please enter a valid column length.")
            return

        idx = selection[0]
        tR, wb = self._rows[idx]
        try:
            res = equivalent_high_one(L, tR, wb)
            self.label_resultat.config(text=f"H = {res:.6f} m")
            self.label_erreur.config(text="")
        except Exception as e:
            self.label_erreur.config(text=f"Calculation error: {e}")
            self.label_resultat.config(text="")

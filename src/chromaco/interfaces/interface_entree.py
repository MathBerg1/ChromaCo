import tkinter as tk
import ctypes, sys

# ── DPI awareness (Windows) – must come before Tk() ───────────────────────────
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor v2
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

from chromaco.interfaces.interface_hauteur_equivalente import InterfaceHauteur
from chromaco.interfaces.interface_nb_de_plateau import InterfacePlateau
from chromaco.interfaces.interface_resolution_two_peaks import InterfaceResolution
from chromaco.interfaces.interface_standard_addition import StandardAdditionInterface
from chromaco.interfaces.interface_elut_ord import InterfaceElution
from chromaco.interfaces.interface_retfac import InterfaceRetentionFactor
from chromaco.interfaces.interface_comparison import InterfaceCompareColumns
from chromaco.interfaces.interface_selectfact import InterfaceSelectivity
from chromaco.interfaces.interface_kovats import *



# ── Colour tokens ──────────────────────────────────────────────────────────────
BG       = "#0f1117"
SURFACE  = "#1a1d27"
BORDER   = "#2a2d3e"
ACCENT   = "#4f9cf9"
TEXT_PRI = "#e8eaf2"
TEXT_SEC = "#7b80a0"
HOVER_BG = "#22263a"
DANGER   = "#f7706a"

BUTTONS = [
    {"label": "Equivalent Plate Height", "sub": "Van Deemter / HETP",     "icon": "⬆", "command": lambda: InterfaceHauteur(root),        "accent": "#4f9cf9"},
    {"label": "Number of Plates",        "sub": "Column efficiency",       "icon": "≡", "command": lambda: InterfacePlateau(root),         "accent": "#7c6af7"},
    {"label": "Resolution (Two Peaks)",  "sub": "Peak separation",         "icon": "∿", "command": lambda: InterfaceResolution(root),      "accent": "#4fd1c5"},
    {"label": "Order of Elution",        "sub": "Retention sequence",      "icon": "→", "command": lambda: InterfaceElution(root),         "accent": "#68d391"},
    {"label": "Standard Addition",       "sub": "Spike / quantification",  "icon": "+", "command": lambda: StandardAdditionInterface (root),     "accent": "#f6ad55"},
    {"label": "Retention Factor",        "sub": "k′ calculation",          "icon": "k", "command": lambda: InterfaceRetentionFactor(root), "accent": "#fc8181"},
    {"label": "Compare Columns",         "sub": "Side-by-side analysis",   "icon": "⇌", "command": lambda: InterfaceCompareColumns(root),  "accent": "#b794f4"},
    {"label": "Selectivity Factor",         "sub": "Peak identification",   "icon": "α", "command": lambda: InterfaceSelectivity(root),  "accent": "#e794f4"},
    {"label": "Kovats Method",         "sub": "Kovats Index and dead time",   "icon": "I", "command": lambda: KovatsSelector(root),  "accent": "#f49494"}
]


# ── Hover helpers ──────────────────────────────────────────────────────────────
def on_enter(event, widgets_bg, frame, accent):
    frame.config(bg=HOVER_BG, highlightbackground=accent)
    for w in widgets_bg:
        w.config(bg=HOVER_BG)

def on_leave(event, widgets_bg, frame, accent):
    frame.config(bg=SURFACE, highlightbackground=BORDER)
    for w in widgets_bg:
        w.config(bg=SURFACE)


def make_button(parent, cfg):
    accent = cfg["accent"]

    outer = tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER,
                     highlightthickness=1, cursor="hand2")
    outer.pack(fill="x", pady=6)

    stripe = tk.Frame(outer, bg=accent, width=5)
    stripe.pack(side="left", fill="y")

    icon_lbl = tk.Label(outer, text=cfg["icon"], font=("Segoe UI", 16, "bold"),
                        fg=accent, bg=SURFACE, width=3)
    icon_lbl.pack(side="left", padx=(14, 8), pady=16)

    text_frame = tk.Frame(outer, bg=SURFACE)
    text_frame.pack(side="left", fill="both", expand=True, pady=12)

    main_lbl = tk.Label(text_frame, text=cfg["label"],
                        font=("Segoe UI", 11, "bold"),
                        fg=TEXT_PRI, bg=SURFACE, anchor="w")
    main_lbl.pack(fill="x")

    sub_lbl = tk.Label(text_frame, text=cfg["sub"],
                       font=("Segoe UI", 9),
                       fg=TEXT_SEC, bg=SURFACE, anchor="w")
    sub_lbl.pack(fill="x")

    arrow = tk.Label(outer, text="›", font=("Segoe UI", 18),
                     fg=TEXT_SEC, bg=SURFACE)
    arrow.pack(side="right", padx=16)

    bg_widgets = [icon_lbl, text_frame, main_lbl, sub_lbl, arrow]
    all_widgets = [outer, stripe] + bg_widgets

    for w in all_widgets:
        w.bind("<Enter>",    lambda e, bw=bg_widgets, f=outer, a=accent: on_enter(e, bw, f, a))
        w.bind("<Leave>",    lambda e, bw=bg_widgets, f=outer, a=accent: on_leave(e, bw, f, a))
        w.bind("<Button-1>", lambda e, cmd=cfg["command"]: cmd())


# ── Root window ────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("Chromaco · Calculator")
root.geometry("600x800")
root.resizable(True, True)
root.config(bg=BG)

# Scale factor for crisp rendering on HiDPI screens
try:
    scale = root.winfo_fpixels("1i") / 72
    if scale > 1.25:
        root.tk.call("tk", "scaling", scale)
except Exception:
    pass

# ── Header ─────────────────────────────────────────────────────────────────────
header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=32, pady=(28, 0))

tk.Label(header, text="C H R O M A C O",
         font=("Segoe UI", 10, "bold"), fg=ACCENT, bg=BG).pack(anchor="w")

tk.Label(header, text="Chromatography\nCalculator",
         font=("Segoe UI", 22, "bold"), fg=TEXT_PRI, bg=BG,
         justify="left").pack(anchor="w", pady=(4, 2))

tk.Label(header, text="Select a calculation module below",
         font=("Segoe UI", 9), fg=TEXT_SEC, bg=BG).pack(anchor="w")

tk.Frame(root, bg=ACCENT, height=2).pack(fill="x", padx=32, pady=(16, 0))

# ── Scrollable area ────────────────────────────────────────────────────────────
scroll_outer = tk.Frame(root, bg=BG)
scroll_outer.pack(fill="both", expand=True, padx=32, pady=(12, 0))

canvas = tk.Canvas(scroll_outer, bg=BG, highlightthickness=0, bd=0)
scrollbar = tk.Scrollbar(scroll_outer, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

inner = tk.Frame(canvas, bg=BG)
inner_window = canvas.create_window((0, 0), window=inner, anchor="nw")

def on_inner_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

def on_canvas_configure(event):
    canvas.itemconfig(inner_window, width=event.width)

inner.bind("<Configure>", on_inner_configure)
canvas.bind("<Configure>", on_canvas_configure)

# ── LOCAL SCROLL ONLY (trackpad + mouse) ───────────────────────────────────────
def on_mousewheel(event):
    if sys.platform == "darwin":
        delta = -event.delta
    else:
        delta = -1 * (event.delta // 120)
    canvas.yview_scroll(delta, "units")

canvas.bind("<MouseWheel>", on_mousewheel)
canvas.bind("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units"))
canvas.bind("<Button-5>",   lambda e: canvas.yview_scroll(1,  "units"))

# give focus to canvas when mouse enters
canvas.bind("<Enter>", lambda e: canvas.focus_set())


# ── Buttons ────────────────────────────────────────────────────────────────────
for cfg in BUTTONS:
    make_button(inner, cfg)

# ── Footer ─────────────────────────────────────────────────────────────────────
footer = tk.Frame(root, bg=BG)
footer.pack(fill="x", padx=32, pady=(10, 24))

tk.Label(footer, text="v2.0", font=("Segoe UI", 8),
         fg=BORDER, bg=BG).pack(side="left")

exit_btn = tk.Label(footer, text="✕  Quit application",
                    font=("Segoe UI", 9), fg=DANGER, bg=BG, cursor="hand2")
exit_btn.pack(side="right")
exit_btn.bind("<Button-1>", lambda e: root.quit())
exit_btn.bind("<Enter>",    lambda e: exit_btn.config(fg="#ff9e9b"))
exit_btn.bind("<Leave>",    lambda e: exit_btn.config(fg=DANGER))

root.mainloop()

def main():
    global root
    root.mainloop()


if __name__ == "__main__":
    main()


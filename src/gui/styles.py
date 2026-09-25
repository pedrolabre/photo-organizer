import tkinter as tk
from tkinter import ttk


def apply_gui_styles(master: tk.Tk) -> None:
    master.configure(bg="#F1F2EB")
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("TFrame", background="#F1F2EB")
    style.configure("Card.TFrame", background="#FFFFFF", relief="flat")
    style.configure(
        "CardLabel.TLabel",
        background="#FFFFFF",
        foreground="#0F172A",
        font=("Segoe UI", 9, "bold"),
    )
    style.configure(
        "TLabel",
        background="#F1F2EB",
        foreground="#0F172A",
        font=("Segoe UI", 9),
    )
    style.configure(
        "Muted.TLabel",
        background="#FFFFFF",
        foreground="#64748B",
        font=("Segoe UI", 8),
    )
    style.configure(
        "Green.Horizontal.TProgressbar",
        troughcolor="#E2E8F0",
        background="#448844",
        lightcolor="#448844",
        darkcolor="#448844",
        bordercolor="#E2E8F0",
    )

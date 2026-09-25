import tkinter as tk
from tkinter import ttk
from typing import Callable


class DirSelectionCard:
    def __init__(
        self,
        parent: ttk.Frame,
        on_browse_input: Callable[[], None],
        on_browse_output: Callable[[], None],
    ) -> None:
        self.frame: ttk.Frame = ttk.Frame(
            parent, style="Card.TFrame", padding=8
        )
        self.frame.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(
            self.frame,
            text="Pastas de Trabalho",
            style="CardLabel.TLabel",
        ).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 4))

        ttk.Label(self.frame, text="Origem:", style="CardLabel.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.input_entry: ttk.Entry = ttk.Entry(self.frame, width=28)
        self.input_entry.grid(row=1, column=1, sticky=tk.EW, padx=4, pady=2)
        self.btn_in: tk.Button = tk.Button(
            self.frame,
            text="Selecionar...",
            command=on_browse_input,
            bg="#FFFFFF",
            fg="#1E293B",
            relief="groove",
            font=("Segoe UI", 8),
            padx=4,
            pady=1,
        )
        self.btn_in.grid(row=1, column=2, padx=2, pady=2)

        ttk.Label(self.frame, text="Destino:", style="CardLabel.TLabel").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.output_entry: ttk.Entry = ttk.Entry(self.frame, width=28)
        self.output_entry.grid(row=2, column=1, sticky=tk.EW, padx=4, pady=2)
        self.btn_out: tk.Button = tk.Button(
            self.frame,
            text="Selecionar...",
            command=on_browse_output,
            bg="#FFFFFF",
            fg="#1E293B",
            relief="groove",
            font=("Segoe UI", 8),
            padx=4,
            pady=1,
        )
        self.btn_out.grid(row=2, column=2, padx=2, pady=2)
        self.frame.columnconfigure(1, weight=1)

    def set_input_path(self, path: str) -> None:
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, path)

    def set_output_path(self, path: str) -> None:
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, path)

    def get_input_path(self) -> str:
        return self.input_entry.get().strip().strip('"').strip("'").strip()

    def get_output_path(self) -> str:
        return self.output_entry.get().strip().strip('"').strip("'").strip()

    def set_busy(self, busy: bool) -> None:
        state = tk.DISABLED if busy else tk.NORMAL
        self.btn_in.configure(state=state)
        self.btn_out.configure(state=state)


class ConfigCard:
    def __init__(self, parent: ttk.Frame) -> None:
        self.frame: ttk.Frame = ttk.Frame(
            parent, style="Card.TFrame", padding=8
        )
        self.frame.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(
            self.frame,
            text="Configurações e Parâmetros",
            style="CardLabel.TLabel",
        ).grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 4))

        ttk.Label(self.frame, text="Operação:", style="CardLabel.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.op_var: tk.StringVar = tk.StringVar(value="copy")
        self.op_combo: ttk.Combobox = ttk.Combobox(
            self.frame,
            textvariable=self.op_var,
            values=["copy", "move"],
            state="readonly",
            width=10,
        )
        self.op_combo.grid(row=1, column=1, sticky=tk.W, padx=4, pady=2)

        ttk.Label(self.frame, text="Estrutura:", style="CardLabel.TLabel").grid(
            row=1, column=2, sticky=tk.W, padx=(8, 2), pady=2
        )
        self.struct_var: tk.StringVar = tk.StringVar(value="year_month_day")
        self.struct_combo: ttk.Combobox = ttk.Combobox(
            self.frame,
            textvariable=self.struct_var,
            values=["year_month_day", "year_month", "year"],
            state="readonly",
            width=14,
        )
        self.struct_combo.grid(row=1, column=3, sticky=tk.W, padx=4, pady=2)

        self.recur_var: tk.BooleanVar = tk.BooleanVar(value=True)
        self.chk_recur: tk.Checkbutton = tk.Checkbutton(
            self.frame,
            text="Incluir subpastas",
            variable=self.recur_var,
            bg="#FFFFFF",
            fg="#1E293B",
            activebackground="#FFFFFF",
            font=("Segoe UI", 8),
        )
        self.chk_recur.grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=(4, 1)
        )

        self.exact_var: tk.BooleanVar = tk.BooleanVar(value=True)
        self.chk_exact: tk.Checkbutton = tk.Checkbutton(
            self.frame,
            text="Duplicatas exatas",
            variable=self.exact_var,
            bg="#FFFFFF",
            fg="#1E293B",
            activebackground="#FFFFFF",
            font=("Segoe UI", 8),
        )
        self.chk_exact.grid(
            row=2, column=2, columnspan=2, sticky=tk.W, pady=(4, 1)
        )

        self.sim_var: tk.BooleanVar = tk.BooleanVar(value=False)
        self.chk_sim: tk.Checkbutton = tk.Checkbutton(
            self.frame,
            text="Duplicatas similares",
            variable=self.sim_var,
            command=self._on_toggle_sim,
            bg="#FFFFFF",
            fg="#1E293B",
            activebackground="#FFFFFF",
            font=("Segoe UI", 8),
        )
        self.chk_sim.grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=(2, 1)
        )

        self.thresh_var: tk.IntVar = tk.IntVar(value=5)
        self.thresh_scale: tk.Scale = tk.Scale(
            self.frame,
            from_=1,
            to=20,
            orient=tk.HORIZONTAL,
            variable=self.thresh_var,
            command=self._on_scale_change,
            bg="#FFFFFF",
            highlightthickness=0,
            length=100,
            state=tk.DISABLED,
        )
        self.thresh_scale.grid(row=3, column=2, sticky=tk.W, padx=2)
        self.thresh_lbl: tk.Label = tk.Label(
            self.frame,
            text="Limiar: 5",
            font=("Segoe UI", 7),
            bg="#FFFFFF",
            fg="#64748B",
        )
        self.thresh_lbl.grid(row=3, column=3, sticky=tk.W, padx=2)

    def _on_toggle_sim(self) -> None:
        if self.sim_var.get():
            self.thresh_scale.configure(state=tk.NORMAL)
        else:
            self.thresh_scale.configure(state=tk.DISABLED)

    def _on_scale_change(self, val: str) -> None:
        int_val = int(val)
        desc = "rigoroso" if int_val <= 6 else "permissivo"
        self.thresh_lbl.configure(text=f"Limiar: {int_val} ({desc})")

    def get_operation(self) -> str:
        return self.op_var.get()

    def get_structure(self) -> str:
        return self.struct_var.get()

    def get_recursive(self) -> bool:
        return self.recur_var.get()

    def get_exact(self) -> bool:
        return self.exact_var.get()

    def get_similar(self) -> bool:
        return self.sim_var.get()

    def get_threshold(self) -> int:
        return self.thresh_var.get()

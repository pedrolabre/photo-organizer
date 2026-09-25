import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.gui.gui_model import GUIConfig, OrganizeProgress, OrganizeResult, ScanResult
from src.gui.styles import apply_gui_styles
from src.gui.view_components import ConfigCard, DirSelectionCard


class DesktopView:
    def __init__(
        self,
        master: tk.Tk,
        on_browse_input: Callable[[], None],
        on_browse_output: Callable[[], None],
        on_scan: Callable[[], None],
        on_organize: Callable[[], None],
    ) -> None:
        self.master: tk.Tk = master
        self._on_scan: Callable[[], None] = on_scan
        self._on_organize: Callable[[], None] = on_organize

        apply_gui_styles(self.master)

        container = ttk.Frame(self.master, padding=8)
        container.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, 4))

        title_lbl = tk.Label(
            header_frame,
            text="Photo Organizer",
            font=("Segoe UI", 12, "bold"),
            bg="#F1F2EB",
            fg="#1E293B",
        )
        title_lbl.pack(side=tk.LEFT)

        body_frame = ttk.Frame(container)
        body_frame.pack(fill=tk.BOTH, expand=True)

        left_pane = ttk.Frame(body_frame, width=430)
        left_pane.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left_pane.pack_propagate(False)

        right_pane = ttk.Frame(body_frame)
        right_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.dir_card: DirSelectionCard = DirSelectionCard(
            parent=left_pane,
            on_browse_input=on_browse_input,
            on_browse_output=on_browse_output,
        )

        self.cfg_card: ConfigCard = ConfigCard(parent=left_pane)

        act_frame = ttk.Frame(left_pane)
        act_frame.pack(fill=tk.X, pady=(0, 6))

        self.btn_scan: tk.Button = tk.Button(
            act_frame,
            text="Escanear e Visualizar",
            command=self._on_scan,
            bg="#334155",
            fg="#FFFFFF",
            activebackground="#1E293B",
            activeforeground="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
        )
        self.btn_scan.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.btn_organize: tk.Button = tk.Button(
            act_frame,
            text="Organizar Fotos",
            command=self._on_organize,
            bg="#448844",
            fg="#FFFFFF",
            activebackground="#376D37",
            activeforeground="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=5,
            cursor="hand2",
        )
        self.btn_organize.pack(side=tk.LEFT, fill=tk.X, expand=True)

        prog_card = ttk.Frame(left_pane, style="Card.TFrame", padding=6)
        prog_card.pack(fill=tk.X)

        self.prog_bar: ttk.Progressbar = ttk.Progressbar(
            prog_card,
            style="Green.Horizontal.TProgressbar",
            mode="determinate",
            maximum=100,
            value=0,
        )
        self.prog_bar.pack(fill=tk.X, pady=(0, 2))

        self.prog_lbl: tk.Label = tk.Label(
            prog_card,
            text="Pronto para iniciar.",
            font=("Segoe UI", 8),
            bg="#FFFFFF",
            fg="#1E293B",
            anchor=tk.W,
        )
        self.prog_lbl.pack(fill=tk.X)

        res_card = ttk.Frame(right_pane, style="Card.TFrame", padding=8)
        res_card.pack(fill=tk.BOTH, expand=True)

        self.stat_lbl: tk.Label = tk.Label(
            res_card,
            text="Pré-visualização da Estrutura",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F172A",
            anchor=tk.W,
        )
        self.stat_lbl.pack(fill=tk.X, pady=(0, 4))

        tree_box = tk.Frame(res_card, bg="#1E293B")
        tree_box.pack(fill=tk.BOTH, expand=True)

        self.tree_txt: tk.Text = tk.Text(
            tree_box,
            wrap=tk.NONE,
            bg="#1E293B",
            fg="#F8FAFC",
            insertbackground="#FFFFFF",
            font=("Consolas", 9),
            relief="flat",
            padx=6,
            pady=6,
        )
        scroll_y = tk.Scrollbar(tree_box, command=self.tree_txt.yview)
        scroll_x = tk.Scrollbar(
            res_card,
            orient=tk.HORIZONTAL,
            command=self.tree_txt.xview,
        )
        self.tree_txt.configure(
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set,
        )

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_x.pack(fill=tk.X)

    def get_config(self) -> GUIConfig:
        return GUIConfig(
            input_path=self.dir_card.get_input_path(),
            output_path=self.dir_card.get_output_path(),
            operation=self.cfg_card.get_operation(),
            structure=self.cfg_card.get_structure(),
            recursive=self.cfg_card.get_recursive(),
            detect_exact=self.cfg_card.get_exact(),
            detect_similar=self.cfg_card.get_similar(),
            similarity_threshold=self.cfg_card.get_threshold(),
        )

    def set_input_path(self, path: str) -> None:
        self.dir_card.set_input_path(path)

    def set_output_path(self, path: str) -> None:
        self.dir_card.set_output_path(path)

    def set_busy(self, busy: bool) -> None:
        state = tk.DISABLED if busy else tk.NORMAL
        self.btn_scan.configure(state=state)
        self.btn_organize.configure(state=state)
        self.dir_card.set_busy(busy)

    def update_progress(self, progress: OrganizeProgress) -> None:
        self.prog_bar["value"] = progress.percentage
        self.prog_lbl.configure(
            text=f"[{progress.percentage}%] {progress.message}"
        )

    def show_scan_result(self, result: ScanResult) -> None:
        self.tree_txt.delete("1.0", tk.END)
        if result.success:
            self.stat_lbl.configure(
                text=f"Varredura concluída: {result.files_found} fotos | {result.summary}"
            )
            self.tree_txt.insert(
                tk.END,
                result.tree if result.tree else "Nenhuma imagem encontrada.",
            )
        else:
            self.stat_lbl.configure(text="Erro na varredura")
            self.tree_txt.insert(tk.END, f"Falha ao escanear: {result.error}")

    def show_organize_result(self, result: OrganizeResult) -> None:
        self.tree_txt.delete("1.0", tk.END)
        if result.success:
            self.prog_bar["value"] = 100
            self.prog_lbl.configure(text="Processamento concluído com sucesso!")
            self.stat_lbl.configure(
                text=f"Fotos Organizadas: {result.files_organized} de {result.files_processed}"
            )
            text_report = (
                "=== RELATÓRIO DE PROCESSAMENTO ===\n\n"
                f"Status: Sucesso\n"
                f"Total de arquivos processados: {result.files_processed}\n"
                f"Arquivos organizados no destino: {result.files_organized}\n"
                f"Duplicatas exatas detectadas (MD5): {result.duplicates_exact}\n"
                f"Duplicatas visuais detectadas (pHash): {result.duplicates_similar}\n"
                f"Erros encontrados: {result.errors}\n"
                f"Início: {result.started_at}\n"
                f"Conclusão: {result.finished_at}\n"
            )
            self.tree_txt.insert(tk.END, text_report)
        else:
            self.stat_lbl.configure(text="Falha no processamento")
            self.prog_lbl.configure(text="Ocorreu um erro.")
            self.tree_txt.insert(
                tk.END,
                f"Erro durante a organização: {result.error_message}",
            )

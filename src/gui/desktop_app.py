from pathlib import Path
import queue
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any, Optional, Tuple

from src.gui.gui_model import GUIConfig, OrganizeProgress, OrganizeResult, ScanResult
from src.gui.views import DesktopView
from src.gui.worker import TaskWorker


class PhotoOrganizerGUI:
    def __init__(self, root: Optional[tk.Tk] = None) -> None:
        self.root: tk.Tk = root if root is not None else tk.Tk()
        self.root.title("Photo Organizer - Desktop")
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = min(1000, max(820, screen_w - 60))
        win_h = min(500, max(420, screen_h - 220))
        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h - 70) // 2)
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.root.minsize(780, 400)

        self.worker: TaskWorker = TaskWorker()
        self.event_queue: queue.Queue[Tuple[str, Any]] = queue.Queue()

        self.view: DesktopView = DesktopView(
            master=self.root,
            on_browse_input=self._on_browse_input,
            on_browse_output=self._on_browse_output,
            on_scan=self._on_scan,
            on_organize=self._on_organize,
        )

        self._check_timer_id: Optional[str] = None
        self._schedule_queue_check()

    def _schedule_queue_check(self) -> None:
        self._check_timer_id = self.root.after(50, self._check_queue)

    def _check_queue(self) -> None:
        try:
            while not self.event_queue.empty():
                event_type, payload = self.event_queue.get_nowait()
                if event_type == "progress":
                    if isinstance(payload, OrganizeProgress):
                        self.view.update_progress(payload)
                elif event_type == "scan_done":
                    self.view.set_busy(False)
                    if isinstance(payload, ScanResult):
                        self.view.show_scan_result(payload)
                elif event_type == "organize_done":
                    self.view.set_busy(False)
                    if isinstance(payload, OrganizeResult):
                        self.view.show_organize_result(payload)
                elif event_type == "error":
                    self.view.set_busy(False)
                    messagebox.showerror("Erro", str(payload))
        finally:
            self._schedule_queue_check()

    def _on_browse_input(self) -> None:
        selected = filedialog.askdirectory(
            parent=self.root,
            title="Selecione a Pasta de Origem",
        )
        if selected:
            self.view.set_input_path(str(Path(selected).resolve()))

    def _on_browse_output(self) -> None:
        selected = filedialog.askdirectory(
            parent=self.root,
            title="Selecione a Pasta de Destino",
        )
        if selected:
            self.view.set_output_path(str(Path(selected).resolve()))

    def _on_scan(self) -> None:
        config = self.view.get_config()
        valid, msg = config.validate()
        if not valid:
            messagebox.showwarning("Validação de Parâmetros", msg)
            return

        self.view.set_busy(True)
        self.view.update_progress(
            OrganizeProgress(
                stage="scan",
                current=0,
                total=100,
                percentage=0,
                message="Escaneando arquivos...",
            )
        )
        self.worker.start_scan(
            config=config,
            callback=lambda res: self.event_queue.put(("scan_done", res)),
        )

    def _on_organize(self) -> None:
        config = self.view.get_config()
        valid, msg = config.validate()
        if not valid:
            messagebox.showwarning("Validação de Parâmetros", msg)
            return

        self.view.set_busy(True)
        self.view.update_progress(
            OrganizeProgress(
                stage="init",
                current=0,
                total=100,
                percentage=0,
                message="Iniciando organização...",
            )
        )
        self.worker.start_organize(
            config=config,
            progress_cb=lambda p: self.event_queue.put(("progress", p)),
            done_cb=lambda r: self.event_queue.put(("organize_done", r)),
        )

    def run(self) -> None:
        self.root.mainloop()

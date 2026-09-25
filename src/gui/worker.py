from datetime import datetime
from pathlib import Path
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.core.file_scanner import FileScanner
from src.core.metadata_reader import MetadataReader
from src.gui.gui_model import GUIConfig, OrganizeProgress, OrganizeResult, ScanResult
from src.organization.folder_organizer import FolderOrganizer
from src.processing import _process_photos
from src.utils.config import get_config


class ObservableProgressDict(dict):
    def __init__(self, callback: Callable[[OrganizeProgress], None]) -> None:
        super().__init__()
        self._callback: Callable[[OrganizeProgress], None] = callback
        self["processing"] = False
        self["progress"] = {}
        self["last_result"] = None

    def __setitem__(self, key: Any, value: Any) -> None:
        super().__setitem__(key, value)
        if key == "progress" and isinstance(value, dict) and "stage" in value:
            self._callback(
                OrganizeProgress(
                    stage=str(value.get("stage", "")),
                    current=int(value.get("current", 0)),
                    total=int(value.get("total", 0)),
                    percentage=int(value.get("percentage", 0)),
                    message=str(value.get("message", "")),
                )
            )


class TaskWorker:
    def __init__(self) -> None:
        self._active_thread: Optional[threading.Thread] = None
        self._lock: threading.Lock = threading.Lock()

    def is_running(self) -> bool:
        with self._lock:
            return self._active_thread is not None and self._active_thread.is_alive()

    def start_scan(
        self,
        config: GUIConfig,
        callback: Callable[[ScanResult], None],
    ) -> threading.Thread:
        thread = threading.Thread(
            target=self._run_scan,
            args=(config, callback),
            daemon=True,
        )
        with self._lock:
            self._active_thread = thread
        thread.start()
        return thread

    def start_organize(
        self,
        config: GUIConfig,
        progress_cb: Callable[[OrganizeProgress], None],
        done_cb: Callable[[OrganizeResult], None],
    ) -> threading.Thread:
        thread = threading.Thread(
            target=self._run_organize,
            args=(config, progress_cb, done_cb),
            daemon=True,
        )
        with self._lock:
            self._active_thread = thread
        thread.start()
        return thread

    def _run_scan(
        self,
        config: GUIConfig,
        callback: Callable[[ScanResult], None],
    ) -> None:
        try:
            app_config = get_config()
            scanner = FileScanner(app_config)
            files = scanner.scan_directory(
                Path(config.input_path),
                recursive=config.recursive,
            )
            if not files:
                callback(
                    ScanResult(
                        success=True,
                        files_found=0,
                        summary="Nenhuma imagem encontrada na pasta especificada.",
                        tree="",
                    )
                )
                return
            reader = MetadataReader()
            photos_with_dates: List[Tuple[Path, Optional[datetime]]] = []
            for file_path in files:
                metadata = reader.read_metadata(file_path)
                photos_with_dates.append((file_path, metadata.get("datetime")))
            organizer = FolderOrganizer(
                app_config,
                base_output_path=Path(config.output_path),
            )
            organizer.structure = config.structure
            preview = organizer.get_organization_preview(photos_with_dates)
            summary = organizer.get_structure_summary(preview)
            summary_str = (
                f"Total de fotos: {summary.get('total_photos', 0)} | "
                f"Pastas de destino: {summary.get('total_folders', 0)}"
            )
            tree = organizer.get_folder_tree_preview(preview)
            callback(
                ScanResult(
                    success=True,
                    files_found=len(files),
                    summary=summary_str,
                    tree=tree,
                )
            )
        except Exception as exc:
            callback(ScanResult(success=False, error=str(exc)))
        finally:
            with self._lock:
                self._active_thread = None

    def _run_organize(
        self,
        config: GUIConfig,
        progress_cb: Callable[[OrganizeProgress], None],
        done_cb: Callable[[OrganizeResult], None],
    ) -> None:
        try:
            state = ObservableProgressDict(progress_cb)
            _process_photos(
                input_path=Path(config.input_path),
                output_path=Path(config.output_path),
                structure=config.structure,
                operation=config.operation,
                detect_exact=config.detect_exact,
                detect_similar=config.detect_similar,
                similarity_threshold=config.similarity_threshold,
                recursive=config.recursive,
                app_state=state,
            )
            last_res = state.get("last_result") or {}
            done_cb(
                OrganizeResult(
                    success=bool(last_res.get("success", False)),
                    files_processed=int(last_res.get("files_processed", 0)),
                    files_organized=int(last_res.get("files_organized", 0)),
                    duplicates_exact=int(last_res.get("duplicates_exact", 0)),
                    duplicates_similar=int(last_res.get("duplicates_similar", 0)),
                    errors=int(last_res.get("errors", 0)),
                    error_message=str(last_res.get("error", "")),
                    started_at=str(last_res.get("started_at", "")),
                    finished_at=str(last_res.get("finished_at", "")),
                )
            )
        except Exception as exc:
            done_cb(OrganizeResult(success=False, error_message=str(exc)))
        finally:
            with self._lock:
                self._active_thread = None

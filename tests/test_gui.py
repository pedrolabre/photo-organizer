import queue
import tkinter as tk
from pathlib import Path
from typing import Any, List
import pytest
from PIL import Image

from src.gui.gui_model import GUIConfig, OrganizeProgress, OrganizeResult, ScanResult
from src.gui.styles import apply_gui_styles
from src.gui.view_components import ConfigCard, DirSelectionCard
from src.gui.views import DesktopView
from src.gui.worker import ObservableProgressDict, TaskWorker
from src.gui.desktop_app import PhotoOrganizerGUI


def test_gui_config_defaults() -> None:
    cfg = GUIConfig()
    assert cfg.input_path == ""
    assert cfg.output_path == ""
    assert cfg.operation == "copy"
    assert cfg.structure == "year_month_day"
    assert cfg.recursive is True
    assert cfg.detect_exact is True
    assert cfg.detect_similar is False
    assert cfg.similarity_threshold == 5


def test_gui_config_validation(tmp_path: Path) -> None:
    cfg = GUIConfig()
    valid, msg = cfg.validate()
    assert not valid
    assert "origem não pode estar vazia" in msg

    cfg.input_path = str(tmp_path)
    valid, msg = cfg.validate()
    assert not valid
    assert "destino não pode estar vazia" in msg

    out_dir = tmp_path / "output"
    cfg.output_path = str(out_dir)
    valid, msg = cfg.validate()
    assert valid

    cfg.operation = "invalid_op"
    valid, msg = cfg.validate()
    assert not valid

    cfg.operation = "move"
    cfg.structure = "invalid_structure"
    valid, msg = cfg.validate()
    assert not valid

    cfg.structure = "year"
    cfg.similarity_threshold = 999
    valid, msg = cfg.validate()
    assert not valid

    cfg.similarity_threshold = 8
    file_as_dir = tmp_path / "not_a_dir.txt"
    file_as_dir.write_text("sample")
    cfg.input_path = str(file_as_dir)
    valid, msg = cfg.validate()
    assert not valid


def test_gui_config_quoted_paths(tmp_path: Path) -> None:
    quoted_in = f'"{tmp_path}"'
    quoted_out = f"'{tmp_path / 'out'}'"
    cfg = GUIConfig(input_path=quoted_in, output_path=quoted_out)
    valid, msg = cfg.validate()
    assert valid
    assert cfg.input_path == str(tmp_path)
    assert cfg.output_path == str(tmp_path / "out")


def test_gui_models_instantiation() -> None:
    scan = ScanResult(success=True, files_found=10, summary="10 fotos", tree="ano/")
    assert scan.success is True
    assert scan.files_found == 10

    prog = OrganizeProgress(stage="scan", current=5, total=10, percentage=50, message="msg")
    assert prog.percentage == 50

    res = OrganizeResult(
        success=True,
        files_processed=10,
        files_organized=8,
        duplicates_exact=2,
        duplicates_similar=0,
        errors=0,
        started_at="2026-09-24",
        finished_at="2026-09-24",
    )
    assert res.files_organized == 8


def test_observable_progress_dict() -> None:
    events: List[OrganizeProgress] = []

    def on_progress(p: OrganizeProgress) -> None:
        events.append(p)

    obs = ObservableProgressDict(on_progress)
    obs["progress"] = {
        "stage": "metadata",
        "current": 2,
        "total": 4,
        "percentage": 50,
        "message": "lendo",
    }
    assert len(events) == 1
    assert events[0].stage == "metadata"
    assert events[0].percentage == 50


def test_task_worker_scan_empty(tmp_path: Path) -> None:
    worker = TaskWorker()
    assert not worker.is_running()
    cfg = GUIConfig(input_path=str(tmp_path), output_path=str(tmp_path / "out"))
    q: queue.Queue[ScanResult] = queue.Queue()
    t = worker.start_scan(cfg, callback=lambda res: q.put(res))
    t.join(timeout=5)
    assert not q.empty()
    res = q.get_nowait()
    assert res.success is True
    assert res.files_found == 0


def test_task_worker_scan_with_images(tmp_path: Path) -> None:
    in_dir = tmp_path / "photos"
    in_dir.mkdir()
    out_dir = tmp_path / "organized"
    img = Image.new("RGB", (64, 64), color="blue")
    img.save(in_dir / "sample.jpg")

    worker = TaskWorker()
    cfg = GUIConfig(input_path=str(in_dir), output_path=str(out_dir))
    q: queue.Queue[ScanResult] = queue.Queue()
    t = worker.start_scan(cfg, callback=lambda res: q.put(res))
    t.join(timeout=5)
    assert not q.empty()
    res = q.get_nowait()
    assert res.success is True
    assert res.files_found == 1


def test_task_worker_organize(tmp_path: Path) -> None:
    in_dir = tmp_path / "input_photos"
    in_dir.mkdir()
    out_dir = tmp_path / "output_photos"
    img = Image.new("RGB", (64, 64), color="red")
    img.save(in_dir / "test.jpg")

    worker = TaskWorker()
    cfg = GUIConfig(
        input_path=str(in_dir),
        output_path=str(out_dir),
        operation="copy",
        structure="year",
        detect_exact=False,
        detect_similar=False,
    )
    progress_list: List[OrganizeProgress] = []
    done_q: queue.Queue[OrganizeResult] = queue.Queue()

    t = worker.start_organize(
        config=cfg,
        progress_cb=lambda p: progress_list.append(p),
        done_cb=lambda r: done_q.put(r),
    )
    t.join(timeout=8)
    assert not done_q.empty()
    res = done_q.get_nowait()
    assert res.success is True
    assert res.files_organized == 1


def test_desktop_subcards(tmp_path: Path) -> None:
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter Tcl display not available in environment")
    root.withdraw()
    try:
        apply_gui_styles(root)
        frame = tk.Frame(root)
        frame.pack()
        dir_card = DirSelectionCard(
            parent=frame,
            on_browse_input=lambda: None,
            on_browse_output=lambda: None,
        )
        dir_card.set_input_path(str(tmp_path))
        dir_card.set_output_path(str(tmp_path / "dest"))
        assert dir_card.get_input_path() == str(tmp_path)
        assert dir_card.get_output_path() == str(tmp_path / "dest")
        dir_card.set_busy(True)
        dir_card.set_busy(False)

        cfg_card = ConfigCard(parent=frame)
        assert cfg_card.get_operation() == "copy"
        assert cfg_card.get_structure() == "year_month_day"
        assert cfg_card.get_recursive() is True
        assert cfg_card.get_exact() is True
        assert cfg_card.get_similar() is False
        assert cfg_card.get_threshold() == 5

        cfg_card.sim_var.set(True)
        cfg_card._on_toggle_sim()
        assert str(cfg_card.thresh_scale.cget("state")) == str(tk.NORMAL)
        cfg_card._on_scale_change("12")
        assert "12" in cfg_card.thresh_lbl.cget("text")
    finally:
        root.destroy()


def test_desktop_view_and_gui_controller(tmp_path: Path) -> None:
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter Tcl display not available in environment")
    root.withdraw()
    try:
        app = PhotoOrganizerGUI(root=root)
        app.view.set_input_path(str(tmp_path))
        app.view.set_output_path(str(tmp_path / "out"))
        cfg = app.view.get_config()
        assert cfg.input_path == str(tmp_path)
        assert cfg.output_path == str(tmp_path / "out")

        app.view.set_busy(True)
        app.view.set_busy(False)

        prog = OrganizeProgress(
            stage="test",
            current=1,
            total=2,
            percentage=50,
            message="testing",
        )
        app.view.update_progress(prog)
        assert app.view.prog_bar["value"] == 50

        scan_res = ScanResult(
            success=True,
            files_found=3,
            summary="3 fotos",
            tree="tree_content",
        )
        app.view.show_scan_result(scan_res)
        assert "tree_content" in app.view.tree_txt.get("1.0", tk.END)

        org_res = OrganizeResult(
            success=True,
            files_processed=5,
            files_organized=5,
            duplicates_exact=0,
            duplicates_similar=0,
            errors=0,
            started_at="agora",
            finished_at="depois",
        )
        app.view.show_organize_result(org_res)
        assert "RELATÓRIO DE PROCESSAMENTO" in app.view.tree_txt.get("1.0", tk.END)

        app.event_queue.put(("progress", prog))
        app._check_queue()

        app.event_queue.put(("scan_done", scan_res))
        app._check_queue()

        app.event_queue.put(("organize_done", org_res))
        app._check_queue()
    finally:
        root.destroy()

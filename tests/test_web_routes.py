from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
import pytest
from PIL import Image

from app import app
import run_web
import run_desktop


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_dashboard_index_route(client: Any) -> None:
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Photo Organizer" in html
    assert "Versão" not in html
    assert "#F1F2EB" in html or "var(--bg-canvas)" in html
    assert "config-form" in html
    assert "btn-scan" in html
    assert "btn-organize" in html


def test_api_config_endpoint(client: Any) -> None:
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "config" in data
    assert "structure" in data["config"]


def test_api_validate_path(client: Any, tmp_path: Path) -> None:
    resp = client.post("/api/validate-path", json={"path": str(tmp_path)})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["valid"] is True
    assert data["writable"] is True

    resp_non_exist = client.post(
        "/api/validate-path",
        json={"path": str(tmp_path / "non_existing_dir")},
    )
    assert resp_non_exist.status_code == 200
    data_non_exist = resp_non_exist.get_json()
    assert data_non_exist["valid"] is False
    assert data_non_exist["can_create"] is True

    resp_quoted = client.post(
        "/api/validate-path",
        json={"path": f'"{tmp_path}"'},
    )
    assert resp_quoted.status_code == 200
    assert resp_quoted.get_json()["valid"] is True


def test_api_browse_endpoint(client: Any, tmp_path: Path) -> None:
    sub = tmp_path / "subfolder"
    sub.mkdir()
    resp = client.post("/api/browse", json={"path": str(tmp_path)})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["subfolders"]) == 1
    assert data["subfolders"][0]["name"] == "subfolder"


def test_api_scan_endpoint(client: Any, tmp_path: Path) -> None:
    in_dir = tmp_path / "web_photos"
    in_dir.mkdir()
    out_dir = tmp_path / "web_out"
    img = Image.new("RGB", (32, 32), color="green")
    img.save(in_dir / "sample.jpg")

    resp = client.post(
        "/api/scan",
        json={
            "input_path": str(in_dir),
            "output_path": str(out_dir),
            "structure": "year_month_day",
            "recursive": True,
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["files_found"] == 1
    assert "summary" in data
    assert isinstance(data["summary"], dict)
    assert "total_folders" in data["summary"]
    assert "tree" in data


def test_api_progress_and_result(client: Any) -> None:
    resp_prog = client.get("/api/progress")
    assert resp_prog.status_code == 200
    data_prog = resp_prog.get_json()
    assert data_prog["success"] is True
    assert "processing" in data_prog

    app.config["APP_STATE"]["last_result"] = {
        "success": True,
        "files_processed": 1,
        "files_organized": 1,
        "duplicates_exact": 0,
        "duplicates_similar": 0,
        "errors": 0,
        "started_at": "test_start",
        "finished_at": "test_end",
    }
    resp_res = client.get("/api/result")
    assert resp_res.status_code == 200
    data_res = resp_res.get_json()
    assert data_res["success"] is True
    assert data_res["result"]["files_organized"] == 1


def test_run_web_open_browser(monkeypatch: Any) -> None:
    mock_open = MagicMock()
    monkeypatch.setattr(run_web.webbrowser, "open", mock_open)
    run_web.open_browser("http://127.0.0.1:5000", delay=0.01)
    mock_open.assert_called_once_with("http://127.0.0.1:5000")


def test_run_desktop_module() -> None:
    assert hasattr(run_desktop, "main")
    assert hasattr(run_desktop, "PhotoOrganizerGUI")

import pytest
from pathlib import Path
from datetime import datetime
from src.organization.folder_organizer import FolderOrganizer

class DummyConfig:
    class Organization:
        structure = "year_month_day"
        folder_format = {"year": "%Y", "month": "%Y-%m", "day": "%Y-%m-%d"}
        create_no_date_folder = True
    organization = Organization()
    output_folder = "test_output"

def test_preview_and_summary(tmp_path):
    config = DummyConfig()
    config.output_folder = tmp_path
    organizer = FolderOrganizer(config)
    photos = [
        (tmp_path / "img1.jpg", datetime(2022, 12, 17)),
        (tmp_path / "img2.jpg", datetime(2022, 12, 18)),
        (tmp_path / "img3.jpg", None),
    ]
    preview = organizer.get_organization_preview(photos)
    # Normaliza separadores para garantir compatibilidade cross-platform
    def norm(p):
        return str(p).replace("\\", "/")
    assert any(norm("2022/2022-12/2022-12-17") in norm(k) for k in preview)
    assert any("sem_data" in norm(k) for k in preview)
    summary = organizer.get_structure_summary(preview)
    assert summary["total_photos"] == 3
    assert summary["total_folders"] >= 2

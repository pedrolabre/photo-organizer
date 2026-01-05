from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict

from src.utils.logger import get_logger
from src.utils.config import Config

class FolderOrganizer:
    """Gerencia a criação de estrutura de pastas para organização."""

    def __init__(self, config: Config, base_output_path: Path = None):
        self.config = config
        self.logger = get_logger()
        self.base_path = base_output_path or config.output_folder
        self.base_path = Path(self.base_path)
        self.structure = config.organization.structure
        self.folder_formats = config.organization.folder_format
        self.create_no_date_folder = config.organization.create_no_date_folder

    def get_target_folder(self, photo_datetime: datetime) -> Path:
        if photo_datetime is None:
            if self.create_no_date_folder:
                return self.base_path / "sem_data"
            else:
                photo_datetime = datetime.now()
        if self.structure == "year":
            folder_path = self._build_year_structure(photo_datetime)
        elif self.structure == "year_month":
            folder_path = self._build_year_month_structure(photo_datetime)
        elif self.structure == "year_month_day":
            folder_path = self._build_year_month_day_structure(photo_datetime)
        else:
            self.logger.warning(f"Estrutura desconhecida: {self.structure}, usando year_month_day")
            folder_path = self._build_year_month_day_structure(photo_datetime)
        return folder_path

    def _build_year_structure(self, dt: datetime) -> Path:
        year = dt.strftime(self.folder_formats["year"])
        return self.base_path / year

    def _build_year_month_structure(self, dt: datetime) -> Path:
        year = dt.strftime(self.folder_formats["year"])
        month = dt.strftime(self.folder_formats["month"])
        return self.base_path / year / month

    def _build_year_month_day_structure(self, dt: datetime) -> Path:
        year = dt.strftime(self.folder_formats["year"])
        month = dt.strftime(self.folder_formats["month"])
        day = dt.strftime(self.folder_formats["day"])
        return self.base_path / year / month / day

    def create_folder(self, folder_path: Path) -> bool:
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Pasta criada/verificada: {folder_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao criar pasta {folder_path}: {e}")
            return False

    def get_organization_preview(self, photos_with_dates: List[Tuple[Path, datetime]]) -> Dict[str, List[Path]]:
        preview = defaultdict(list)
        for photo_path, photo_date in photos_with_dates:
            target_folder = self.get_target_folder(photo_date)
            preview[str(target_folder)].append(photo_path)
        return dict(preview)

    def get_structure_summary(self, preview: Dict[str, List[Path]]) -> Dict[str, any]:
        total_photos = sum(len(photos) for photos in preview.values())
        total_folders = len(preview)
        years = defaultdict(int)
        for folder_str, photos in preview.items():
            folder = Path(folder_str)
            relative = folder.relative_to(self.base_path)
            year = str(relative.parts[0]) if relative.parts else "unknown"
            years[year] += len(photos)
        return {
            "total_photos": total_photos,
            "total_folders": total_folders,
            "base_path": str(self.base_path),
            "structure": self.structure,
            "photos_by_year": dict(years),
            "folders_detail": {folder: len(photos) for folder, photos in preview.items()},
        }

    def validate_base_path(self) -> Tuple[bool, str]:
        try:
            base = Path(self.base_path)
            if not base.exists():
                base.mkdir(parents=True, exist_ok=True)
                return True, f"Pasta criada: {base}"
            if not base.is_dir():
                return False, f"Caminho não é uma pasta: {base}"
            test_file = base / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
                return True, f"Pasta válida e acessível: {base}"
            except Exception as e:
                return False, f"Sem permissão de escrita: {base}"
        except Exception as e:
            return False, f"Erro ao validar pasta: {e}"

    def get_folder_tree_preview(self, preview: Dict[str, List[Path]]) -> str:
        from collections import defaultdict
        tree = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for folder_str, photos in preview.items():
            folder = Path(folder_str)
            relative = folder.relative_to(self.base_path)
            parts = relative.parts
            if len(parts) == 1:
                tree[parts[0]]["_photos"] = len(photos)
            elif len(parts) == 2:
                tree[parts[0]][parts[1]]["_photos"] = len(photos)
            elif len(parts) == 3:
                tree[parts[0]][parts[1]][parts[2]] = len(photos)
        lines = [f"📁 {self.base_path}"]
        for year in sorted(tree.keys()):
            year_data = tree[year]
            year_total = sum(
                month_data.get("_photos", 0)
                if isinstance(month_data, dict)
                else sum(day_photos for day_photos in month_data.values() if isinstance(day_photos, int))
                for month_data in year_data.values()
            )
            lines.append(f"├─ {year}/ ({year_total} fotos)")
            months = [k for k in year_data.keys() if k != "_photos"]
            for i, month in enumerate(sorted(months)):
                month_data = year_data[month]
                is_last_month = i == len(months) - 1
                month_prefix = "└─" if is_last_month else "├─"
                if "_photos" in month_data:
                    lines.append(f"│  {month_prefix} {month}/ ({month_data['_photos']} fotos)")
                else:
                    month_total = sum(
                        photos for day, photos in month_data.items() if isinstance(photos, int)
                    )
                    lines.append(f"│  {month_prefix} {month}/ ({month_total} fotos)")
                    days = sorted(month_data.keys())
                    for j, day in enumerate(days):
                        is_last_day = j == len(days) - 1
                        day_prefix = "└─" if is_last_day else "├─"
                        day_indent = "   " if is_last_month else "│  "
                        lines.append(
                            f"│  {day_indent}{day_prefix} {day}/ ({month_data[day]} fotos)"
                        )
        return "\n".join(lines)

    def change_base_path(self, new_path: Path):
        self.base_path = Path(new_path)
        self.logger.info(f"Caminho base alterado para: {self.base_path}")

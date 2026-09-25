from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


def clean_path_str(val: str) -> str:
    return val.strip().strip('"').strip("'").strip()


@dataclass
class GUIConfig:
    input_path: str = ""
    output_path: str = ""
    operation: str = "copy"
    structure: str = "year_month_day"
    recursive: bool = True
    detect_exact: bool = True
    detect_similar: bool = False
    similarity_threshold: int = 5

    def clean_paths(self) -> None:
        self.input_path = clean_path_str(self.input_path)
        self.output_path = clean_path_str(self.output_path)

    def validate(self) -> Tuple[bool, str]:
        self.clean_paths()
        if not self.input_path:
            return False, "Pasta de origem não pode estar vazia."
        if not self.output_path:
            return False, "Pasta de destino não pode estar vazia."
        in_path = Path(self.input_path)
        if not in_path.exists():
            return False, "Pasta de origem especificada não existe."
        if not in_path.is_dir():
            return False, "Pasta de origem deve ser um diretório válido."
        if self.operation not in ("copy", "move"):
            return False, "Operação deve ser 'copy' ou 'move'."
        if self.structure not in ("year_month_day", "year_month", "year"):
            return False, "Estrutura de organização inválida."
        if not (1 <= self.similarity_threshold <= 64):
            return False, "Limiar de similaridade deve estar entre 1 e 64."
        return True, ""


@dataclass
class ScanResult:
    success: bool
    files_found: int = 0
    summary: str = ""
    tree: str = ""
    error: str = ""


@dataclass
class OrganizeProgress:
    stage: str = ""
    current: int = 0
    total: int = 0
    percentage: int = 0
    message: str = ""


@dataclass
class OrganizeResult:
    success: bool
    files_processed: int = 0
    files_organized: int = 0
    duplicates_exact: int = 0
    duplicates_similar: int = 0
    errors: int = 0
    error_message: str = ""
    started_at: str = ""
    finished_at: str = ""

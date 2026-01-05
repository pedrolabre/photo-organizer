"""
Organization Configuration Module.

Configurações relacionadas à organização de arquivos.
"""

from typing import Dict
from dataclasses import dataclass, field


@dataclass
class OrganizationConfig:
    """Configurações de organização de arquivos."""
    structure: str = "year_month_day"
    folder_format: Dict[str, str] = field(default_factory=lambda: {
        "year": "%Y",
        "month": "%Y-%m",
        "day": "%Y-%m-%d"
    })
    use_file_date_as_fallback: bool = True
    create_no_date_folder: bool = True
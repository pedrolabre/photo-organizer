"""
Reports Configuration Module.

Configurações relacionadas à geração de relatórios.
"""

from dataclasses import dataclass


@dataclass
class ReportsConfig:
    """Configurações de relatórios."""
    generate_json: bool = True
    include_thumbnails: bool = False
    date_format: str = "%Y-%m-%d %H:%M:%S"
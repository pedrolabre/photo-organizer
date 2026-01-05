"""
Duplicates Configuration Module.

Configurações relacionadas à detecção de duplicatas.
"""

from dataclasses import dataclass


@dataclass
class DuplicatesConfig:
    """Configurações de detecção de duplicatas."""
    detect_exact: bool = True
    detect_similar: bool = False
    similarity_threshold: int = 10
    keep_policy: str = "highest_resolution"
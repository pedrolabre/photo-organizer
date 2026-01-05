"""
Operations Package.

Este pacote contém módulos para operações de arquivo e rastreamento de estatísticas.
"""

from .file_operations import FileOperations
from .stats_tracker import StatsTracker

__all__ = [
    "FileOperations",
    "StatsTracker",
]
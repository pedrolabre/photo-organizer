"""
Performance Configuration Module.

Configurações relacionadas ao desempenho e otimização.
"""

from dataclasses import dataclass


@dataclass
class PerformanceConfig:
    """Configurações de performance."""
    max_threads: int = 0
    cache_size_mb: int = 500
    batch_size: int = 100
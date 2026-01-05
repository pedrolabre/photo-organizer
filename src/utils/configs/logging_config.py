"""
Logging Configuration Module.

Configurações relacionadas ao sistema de logging.
"""

from dataclasses import dataclass


@dataclass
class LoggingConfig:
    """Configurações de logging."""
    level: str = "INFO"
    save_to_file: bool = True
    retention_days: int = 30
    use_colors: bool = True
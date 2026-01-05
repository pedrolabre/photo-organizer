"""
Database Configuration Module.

Configurações relacionadas ao banco de dados.
"""

from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Configurações do banco de dados."""
    filename: str = "photo_organizer.db"
    auto_backup: bool = True
    backup_retention_days: int = 7
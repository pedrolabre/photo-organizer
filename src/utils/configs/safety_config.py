"""
Safety Configuration Module.

Configurações relacionadas à segurança e operações de arquivo.
"""

from dataclasses import dataclass


@dataclass
class SafetyConfig:
    """Configurações de segurança."""
    never_delete_originals: bool = True
    file_operation: str = "copy"
    backup_database: bool = True
    verify_after_copy: bool = True
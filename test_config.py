"""Validação e teste do módulo de configuração src/utils/config.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import get_config


def test_config():
    """Valida o carregamento e integridade das configurações."""
    cfg = get_config("config.yaml")
    assert cfg is not None
    assert isinstance(cfg.input_folders, list)
    assert cfg.output_folder is not None
    assert cfg.quarantine_folder is not None
    assert len(cfg.supported_extensions) > 0
    assert cfg.organization is not None
    assert cfg.duplicates is not None
    assert cfg.safety is not None
    assert cfg.performance is not None
    assert cfg.logging is not None


if __name__ == "__main__":
    test_config()
    print("Configuração validada com sucesso.")

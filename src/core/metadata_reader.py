"""
Leitor de metadados de imagens.

Extrai metadados EXIF de arquivos de imagem, incluindo data/hora,
informações da câmera, localização GPS e propriedades técnicas.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from PIL import Image

from src.utils.logger import get_logger
from .parsers import EXIFParser, GPSParser, DateTimeParser


class MetadataReader:
    """Leitor de metadados de imagens."""

    def __init__(self):
        """Inicializa o leitor de metadados."""
        self.logger = get_logger()

    def read_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Lê todos os metadados disponíveis de uma imagem.

        Args:
            file_path: Caminho do arquivo de imagem

        Returns:
            Dicionário com todos os metadados disponíveis
        """
        if not file_path.exists():
            self.logger.error(f"Arquivo não encontrado: {file_path}")
            return {}

        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "file_extension": file_path.suffix.lower(),
        }

        try:
            # Ler metadados da imagem com PIL
            with Image.open(file_path) as img:
                metadata.update(self._read_basic_info(img))
                metadata.update(EXIFParser.read_exif_data(file_path))

            # Determinar data/hora
            metadata["datetime"] = DateTimeParser._get_datetime(metadata, file_path)

        except Exception as e:
            self.logger.warning(f"Erro ao ler metadados de {file_path}: {e}")

        return metadata

    def _read_basic_info(self, img: Image.Image) -> Dict[str, Any]:
        """Lê informações básicas da imagem."""
        return {
            "width": img.width,
            "height": img.height,
            "mode": img.mode,
            "format": img.format,
        }

    def has_exif(self, file_path: Path) -> bool:
        """
        Verifica se o arquivo possui dados EXIF.

        Args:
            file_path: Caminho do arquivo

        Returns:
            True se possui EXIF
        """
        try:
            exif_data = EXIFParser.read_exif_data(file_path)
            return bool(exif_data)
        except Exception:
            return False

    def get_camera_info(self, metadata: dict) -> str:
        """
        Extrai informações da câmera de uma string legível.

        Args:
            metadata: Dicionário de metadados

        Returns:
            String com informações da câmera
        """
        make = metadata.get("camera_make", "").strip()
        model = metadata.get("camera_model", "").strip()

        if make and model:
            return f"{make} {model}"
        elif make:
            return make
        elif model:
            return model
        else:
            return "Câmera desconhecida"

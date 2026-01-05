"""
Calculador de hashes para detecção de duplicatas.

Calcula hash MD5 (duplicatas exatas) e hash perceptual
(duplicatas visuais) de arquivos de imagem.
"""

import hashlib
from pathlib import Path
from typing import Optional
import imagehash
from PIL import Image

from src.utils.logger import get_logger


class HashCalculator:
    """Calculador de hashes para imagens."""

    def __init__(self):
        """Inicializa o calculador de hashes."""
        self.logger = get_logger()

    def calculate_md5(self, file_path: Path) -> str:
        """
        Calcula hash MD5 de um arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Hash MD5 em hexadecimal
        """
        if not file_path.exists():
            self.logger.error(f"Arquivo não encontrado: {file_path}")
            return ""

        try:
            md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    md5.update(chunk)
            return md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Erro ao calcular MD5 de {file_path}: {e}")
            return ""

    def calculate_phash(self, file_path: Path, hash_size: int = 8) -> Optional[str]:
        """
        Calcula hash perceptual (pHash) de uma imagem.

        Args:
            file_path: Caminho da imagem
            hash_size: Tamanho do hash (default: 8)

        Returns:
            Hash perceptual em hexadecimal ou None se erro
        """
        if not file_path.exists():
            self.logger.error(f"Arquivo não encontrado: {file_path}")
            return None

        try:
            with Image.open(file_path) as img:
                # Converter para RGB se necessário
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                # Calcular pHash
                phash = imagehash.phash(img, hash_size=hash_size)
                return str(phash)
        except Exception as e:
            self.logger.warning(f"Erro ao calcular pHash de {file_path.name}: {e}")
            return None

    def calculate_all_hashes(self, file_path: Path) -> dict:
        """
        Calcula todos os hashes de um arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Dicionário com MD5 e pHash
        """
        return {
            "md5": self.calculate_md5(file_path),
            "phash": self.calculate_phash(file_path),
        }

    def compare_phash(self, hash1: str, hash2: str) -> int:
        """
        Compara dois hashes perceptuais.

        Args:
            hash1: Primeiro hash
            hash2: Segundo hash

        Returns:
            Distância Hamming (0 = idênticos, >0 = diferentes)
        """
        try:
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            return h1 - h2
        except Exception as e:
            self.logger.error(f"Erro ao comparar hashes: {e}")
            return 999  # Distância máxima em caso de erro

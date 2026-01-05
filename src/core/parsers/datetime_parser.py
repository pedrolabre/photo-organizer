"""
DateTime Parser Module.

Responsável por extrair e parsear informações de data/hora de metadados.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class DateTimeParser:
    """Parser para informações de data e hora."""

    @staticmethod
    def _parse_exif_datetime(dt_str: str) -> Optional[datetime]:
        """
        Parse data/hora do formato EXIF.

        Args:
            dt_str: String de data/hora no formato EXIF

        Returns:
            Objeto datetime ou None se inválido
        """
        if not dt_str or dt_str.strip() == '':
            return None

        try:
            # Formato EXIF: "YYYY:MM:DD HH:MM:SS"
            return datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            try:
                # Tentar outros formatos comuns
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None

    @staticmethod
    def _get_datetime(metadata: dict, file_path: Path) -> datetime:
        """
        Determina a melhor data/hora disponível para a imagem.

        Args:
            metadata: Dicionário com metadados
            file_path: Caminho do arquivo

        Returns:
            Objeto datetime determinado
        """
        # Prioridade: DateTimeOriginal > DateTimeDigitized > data do arquivo
        datetime_str = metadata.get("datetime_original") or metadata.get("datetime_digitized")

        if datetime_str:
            parsed_dt = DateTimeParser._parse_exif_datetime(datetime_str)
            if parsed_dt:
                return parsed_dt

        # Fallback para data do arquivo
        return DateTimeParser._get_file_datetime(file_path)

    @staticmethod
    def _get_file_datetime(file_path: Path) -> datetime:
        """
        Obtém data/hora da modificação do arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Objeto datetime da modificação do arquivo
        """
        try:
            timestamp = file_path.stat().st_mtime
            return datetime.fromtimestamp(timestamp)
        except (OSError, ValueError):
            return datetime.now()
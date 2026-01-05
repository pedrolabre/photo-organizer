"""
File Info Module.

Responsável por extrair informações detalhadas de arquivos.
"""

from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict

from src.utils.logger import get_logger


class FileInfoExtractor:
    """Extrator de informações de arquivo."""

    def __init__(self):
        """Inicializa o extrator."""
        self.logger = get_logger()

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Extrai informações detalhadas de um arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Dicionário com informações do arquivo
        """
        try:
            stat = file_path.stat()

            return {
                "path": str(file_path),
                "name": file_path.name,
                "stem": file_path.stem,
                "extension": file_path.suffix.lower(),
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified_time": stat.st_mtime,
                "created_time": stat.st_ctime,
                "is_readable": self._is_readable(file_path),
                "parent_directory": str(file_path.parent),
            }

        except Exception as e:
            self.logger.error(f"Erro ao obter info de {file_path}: {e}")
            return {
                "path": str(file_path),
                "name": file_path.name,
                "error": str(e),
            }

    def group_by_extension(self, files: List[Path]) -> Dict[str, List[Path]]:
        """
        Agrupa arquivos por extensão.

        Args:
            files: Lista de caminhos de arquivo

        Returns:
            Dicionário extension -> lista de arquivos
        """
        grouped = defaultdict(list)

        for file_path in files:
            ext = file_path.suffix.lower() or "no_extension"
            grouped[ext].append(file_path)

        # Converter defaultdict para dict regular e ordenar
        result = {}
        for ext in sorted(grouped.keys()):
            result[ext] = sorted(grouped[ext], key=lambda x: x.name.lower())

        return result

    def get_extension_stats(self, files: List[Path]) -> Dict[str, Any]:
        """
        Calcula estatísticas por extensão.

        Args:
            files: Lista de caminhos de arquivo

        Returns:
            Dicionário com estatísticas por extensão
        """
        grouped = self.group_by_extension(files)
        stats = {}

        for ext, file_list in grouped.items():
            total_size = sum(f.stat().st_size for f in file_list if f.exists())

            stats[ext] = {
                "count": len(file_list),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "files": [str(f) for f in file_list],
            }

        return stats

    def _is_readable(self, file_path: Path) -> bool:
        """
        Verifica se arquivo pode ser lido.

        Args:
            file_path: Caminho do arquivo

        Returns:
            True se arquivo é legível
        """
        try:
            with open(file_path, 'rb') as f:
                f.read(1)
            return True
        except Exception:
            return False
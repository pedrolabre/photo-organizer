"""
File Scanner Module - Photo Organizer.

Coordenador de operações de escaneamento de arquivos.
"""

from pathlib import Path
from typing import List, Dict, Any

from src.utils.config import Config
from .scanners import DirectoryScanner, FileInfoExtractor


class FileScanner:
    """Coordenador de escaneamento de arquivos de imagem."""

    def __init__(self, config: Config):
        """
        Inicializa o scanner de arquivos.

        Args:
            config: Configuração do sistema
        """
        self.config = config
        self.directory_scanner = DirectoryScanner(config)
        self.info_extractor = FileInfoExtractor()

    def scan_all_sources(self) -> List[Path]:
        """
        Escaneia todas as pastas de entrada configuradas.

        Returns:
            Lista consolidada de arquivos de todas as fontes
        """
        return self.directory_scanner.scan_all_sources()

    def scan_directory(self, directory: Path, recursive: bool = True) -> List[Path]:
        """
        Escaneia diretório procurando arquivos de imagem suportados.

        Args:
            directory: Diretório a escanear
            recursive: Se deve escanear subdiretórios

        Returns:
            Lista de caminhos de arquivo encontrados
        """
        return self.directory_scanner.scan_directory(directory, recursive)

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Extrai informações detalhadas de um arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Dicionário com informações do arquivo
        """
        return self.info_extractor.get_file_info(file_path)

    def group_by_extension(self, files: List[Path]) -> Dict[str, List[Path]]:
        """
        Agrupa arquivos por extensão.

        Args:
            files: Lista de caminhos de arquivo

        Returns:
            Dicionário extension -> lista de arquivos
        """
        return self.info_extractor.group_by_extension(files)

    def get_extension_stats(self, files: List[Path]) -> Dict[str, Any]:
        """
        Calcula estatísticas por extensão.

        Args:
            files: Lista de caminhos de arquivo

        Returns:
            Dicionário com estatísticas por extensão
        """
        return self.info_extractor.get_extension_stats(files)

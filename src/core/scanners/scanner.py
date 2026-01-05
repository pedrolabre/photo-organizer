"""
Scanner Module.

Responsável por escanear diretórios e encontrar arquivos de imagem.
"""

from pathlib import Path
from typing import List

from src.utils.config import Config
from src.utils.logger import get_logger


class DirectoryScanner:
    """Scanner de diretórios para arquivos de imagem."""

    def __init__(self, config: Config):
        """
        Inicializa o scanner.

        Args:
            config: Configuração do sistema
        """
        self.config = config
        self.logger = get_logger()
        self.supported_extensions = set(config.supported_extensions)

    def scan_directory(self, directory: Path, recursive: bool = True) -> List[Path]:
        """
        Escaneia diretório procurando arquivos de imagem suportados.

        Args:
            directory: Diretório a escanear
            recursive: Se deve escanear subdiretórios

        Returns:
            Lista de caminhos de arquivo encontrados
        """
        if not directory.exists():
            self.logger.error(f"Diretório não existe: {directory}")
            return []

        if not directory.is_dir():
            self.logger.error(f"Caminho não é diretório: {directory}")
            return []

        files_found = []
        pattern = "**/*" if recursive else "*"

        try:
            for file_path in directory.glob(pattern):
                if file_path.is_file() and self._is_supported_image(file_path):
                    files_found.append(file_path)

        except Exception as e:
            self.logger.error(f"Erro ao escanear {directory}: {e}")

        self.logger.info(f"Encontrados {len(files_found)} arquivos em {directory}")
        return files_found

    def scan_all_sources(self) -> List[Path]:
        """
        Escaneia todas as pastas de entrada configuradas.

        Returns:
            Lista consolidada de arquivos de todas as fontes
        """
        all_files = []

        for source_folder in self.config.input_folders:
            if source_folder.exists():
                files = self.scan_directory(source_folder, recursive=True)
                all_files.extend(files)
                self.logger.info(f"Escaneada {source_folder}: {len(files)} arquivos")
            else:
                self.logger.warning(f"Pasta de entrada não existe: {source_folder}")

        # Remover duplicatas (mesmo arquivo em múltiplas pastas)
        unique_files = list(set(all_files))
        if len(unique_files) != len(all_files):
            removed = len(all_files) - len(unique_files)
            self.logger.info(f"Removidas {removed} duplicatas de arquivos")

        return unique_files

    def _is_supported_image(self, file_path: Path) -> bool:
        """
        Verifica se arquivo é uma imagem suportada.

        Args:
            file_path: Caminho do arquivo

        Returns:
            True se é imagem suportada
        """
        return file_path.suffix.lower() in self.supported_extensions
"""
File Mover Module - Photo Organizer.

Coordenador de operações de arquivo com segurança e rastreamento.
"""

from pathlib import Path
from typing import Tuple, Optional, List

from src.utils.logger import get_logger
from src.utils.config import Config
from .operations import FileOperations, StatsTracker


class FileMover:
    """Coordenador de operações seguras de arquivo."""

    def __init__(self, config: Config):
        """
        Inicializa o movedor de arquivos.

        Args:
            config: Configuração do sistema
        """
        self.config = config
        self.logger = get_logger()

        # Componentes
        self.operations = FileOperations(config.safety.verify_after_copy)
        self.stats = StatsTracker()

        self.operation = config.safety.file_operation  # "copy" ou "move"

    def process_file(
        self,
        source: Path,
        destination_folder: Path,
        new_name: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Path]]:
        """
        Processa um arquivo (copia ou move) para pasta de destino.

        Args:
            source: Arquivo de origem
            destination_folder: Pasta de destino
            new_name: Novo nome opcional

        Returns:
            Tupla (sucesso, mensagem, caminho_final)
        """
        try:
            # Determinar nome final
            final_name = new_name or source.name
            destination = destination_folder / final_name

            # Resolver conflitos de nome
            if destination.exists():
                destination = self.operations.resolve_name_conflict(destination)
                self.logger.info(f"Conflito resolvido: {destination}")

            # Executar operação
            if self.operation == "copy":
                success, message, final_path = self.operations.copy_file(source, destination)
                if success:
                    self.stats.increment_stat("copied")
                    self.stats.add_size(source.stat().st_size)
            elif self.operation == "move":
                success, message, final_path = self.operations.move_file(source, destination)
                if success:
                    self.stats.increment_stat("moved")
                    self.stats.add_size(source.stat().st_size)
            else:
                return False, f"Operação desconhecida: {self.operation}", None

            if not success:
                self.stats.increment_stat("errors")
                self.logger.error(message)
            else:
                self.logger.info(message)

            return success, message, final_path

        except Exception as e:
            error_msg = f"Erro inesperado ao processar {source}: {e}"
            self.stats.increment_stat("errors")
            self.logger.exception(error_msg)
            return False, error_msg, None

    def _verify_copy(self, source: Path, destination: Path) -> bool:
        """Verifica a integridade entre o arquivo original e o copiado."""
        return self.operations._verify_file_integrity(source, destination)

    def get_stats(self) -> dict:
        """
        Retorna estatísticas atuais.

        Returns:
            Dicionário com estatísticas
        """
        return self.stats.get_stats()

    def reset_stats(self):
        """Reseta estatísticas."""
        self.stats.reset_stats()

    def set_operation(self, operation: str):
        """
        Define tipo de operação.

        Args:
            operation: "copy" ou "move"
        """
        if operation not in ["copy", "move"]:
            raise ValueError(f"Operação inválida: {operation}")
        self.operation = operation
        self.logger.info(f"Operação alterada para: {operation}")

    def estimate_space_needed(self, files: List[Path]) -> dict:
        """
        Estima espaço necessário para os arquivos.

        Args:
            files: Lista de caminhos de arquivo

        Returns:
            Dicionário com estatísticas de espaço
        """
        return self.operations.estimate_space_needed(files)

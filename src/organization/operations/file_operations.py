"""
File Operations Module.

Responsável por operações seguras de cópia e movimentação de arquivos.
"""

import shutil
import hashlib
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime


class FileOperations:
    """Operações de arquivo seguras com verificação de integridade."""

    def __init__(self, verify_after_copy: bool = True):
        """
        Inicializa as operações de arquivo.

        Args:
            verify_after_copy: Se deve verificar integridade após cópia
        """
        self.verify_after_copy = verify_after_copy

    def copy_file(self, source: Path, destination: Path) -> Tuple[bool, str, Optional[Path]]:
        """
        Copia arquivo com verificação de integridade.

        Args:
            source: Arquivo de origem
            destination: Arquivo de destino

        Returns:
            Tupla (sucesso, mensagem, caminho_final)
        """
        try:
            # Criar diretório se não existir
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Copiar arquivo
            shutil.copy2(source, destination)

            # Verificar integridade se solicitado
            if self.verify_after_copy:
                if not self._verify_file_integrity(source, destination):
                    return False, "Falha na verificação de integridade após cópia", None

            return True, f"Arquivo copiado: {destination}", destination

        except Exception as e:
            return False, f"Erro ao copiar arquivo: {e}", None

    def move_file(self, source: Path, destination: Path) -> Tuple[bool, str, Optional[Path]]:
        """
        Move arquivo com verificação.

        Args:
            source: Arquivo de origem
            destination: Arquivo de destino

        Returns:
            Tupla (sucesso, mensagem, caminho_final)
        """
        try:
            # Criar diretório se não existir
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Mover arquivo
            shutil.move(str(source), str(destination))

            return True, f"Arquivo movido: {destination}", destination

        except Exception as e:
            return False, f"Erro ao mover arquivo: {e}", None

    def _verify_file_integrity(self, source: Path, destination: Path) -> bool:
        """
        Verifica se arquivo copiado tem mesma integridade do original.

        Args:
            source: Arquivo original
            destination: Arquivo copiado

        Returns:
            True se integridade OK
        """
        try:
            source_hash = self._calculate_hash(source)
            dest_hash = self._calculate_hash(destination)
            return source_hash == dest_hash
        except Exception:
            return False

    def _calculate_hash(self, file_path: Path) -> str:
        """
        Calcula hash MD5 do arquivo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Hash MD5 em hexadecimal
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def resolve_name_conflict(self, destination: Path) -> Path:
        """
        Resolve conflitos de nome adicionando sufixo numérico.

        Args:
            destination: Caminho de destino com possível conflito

        Returns:
            Caminho sem conflito
        """
        if not destination.exists():
            return destination

        stem = destination.stem
        suffix = destination.suffix
        parent = destination.parent
        counter = 1

        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    def estimate_space_needed(self, files: list) -> dict:
        """
        Estima espaço necessário para os arquivos.

        Args:
            files: Lista de caminhos de arquivo

        Returns:
            Dicionário com estatísticas de espaço
        """
        total_size = 0
        file_count = 0
        errors = 0

        for file_path in files:
            try:
                if file_path.exists() and file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            except Exception:
                errors += 1

        # Converter para MB
        total_mb = total_size / (1024 * 1024)

        return {
            "total_files": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_mb, 2),
            "errors": errors,
        }
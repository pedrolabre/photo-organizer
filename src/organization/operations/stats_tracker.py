"""
Statistics Tracker Module.

Responsável por rastrear estatísticas de operações de arquivo.
"""

from typing import Dict, Any


class StatsTracker:
    """Rastreador de estatísticas de operações."""

    def __init__(self):
        """Inicializa o rastreador de estatísticas."""
        self.reset_stats()

    def reset_stats(self):
        """Reseta todas as estatísticas para zero."""
        self.stats = {
            "copied": 0,
            "moved": 0,
            "skipped": 0,
            "errors": 0,
            "total_processed": 0,
            "total_size_bytes": 0,
            "start_time": None,
            "end_time": None,
        }

    def increment_stat(self, stat_name: str, amount: int = 1):
        """
        Incrementa uma estatística.

        Args:
            stat_name: Nome da estatística
            amount: Quantidade a incrementar
        """
        if stat_name in self.stats:
            self.stats[stat_name] += amount

    def add_size(self, size_bytes: int):
        """
        Adiciona tamanho processado.

        Args:
            size_bytes: Tamanho em bytes
        """
        self.stats["total_size_bytes"] += size_bytes

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas atuais.

        Returns:
            Dicionário com todas as estatísticas
        """
        # Calcular total processado
        self.stats["total_processed"] = (
            self.stats["copied"] + self.stats["moved"] + self.stats["skipped"]
        )

        return self.stats.copy()

    def get_summary(self) -> str:
        """
        Retorna resumo formatado das estatísticas.

        Returns:
            String com resumo
        """
        stats = self.get_stats()
        total_mb = stats["total_size_bytes"] / (1024 * 1024)

        return (
            f"Processados: {stats['total_processed']} arquivos "
            f"({total_mb:.1f} MB) | "
            f"Copiados: {stats['copied']} | "
            f"Movidos: {stats['moved']} | "
            f"Pulados: {stats['skipped']} | "
            f"Erros: {stats['errors']}"
        )
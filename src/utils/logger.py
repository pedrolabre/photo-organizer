"""
Sistema de logs centralizado para o Photo Organizer.

Este módulo fornece logging colorido no terminal e em arquivo,
com rotação automática e diferentes níveis de severidade.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import colorama

# Inicializar colorama para cores no Windows
colorama.init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Formatter que adiciona cores aos logs no terminal."""

    # Cores para cada nível de log
    COLORS = {
        "DEBUG": colorama.Fore.CYAN,
        "INFO": colorama.Fore.GREEN,
        "WARNING": colorama.Fore.YELLOW,
        "ERROR": colorama.Fore.RED,
        "CRITICAL": colorama.Fore.RED + colorama.Style.BRIGHT,
    }

    def format(self, record):
        """Formata o log com cores."""
        # Obter a cor baseada no nível
        color = self.COLORS.get(record.levelname, "")
        
        # Adicionar cor ao nome do nível (mantém reset automático via colorama)
        record.levelname = f"{color}{record.levelname}{colorama.Style.RESET_ALL}"
        
        return super().format(record)


class PhotoOrganizerLogger:
    """Gerenciador de logs do Photo Organizer."""

    def __init__(
        self,
        name: str = "PhotoOrganizer",
        log_dir: Optional[Path] = None,
        level: str = "INFO",
        use_colors: bool = True,
        save_to_file: bool = True,
    ):
        """
        Inicializa o sistema de logs.

        Args:
            name: Nome do logger
            log_dir: Diretório onde salvar os logs (padrão: data/logs/)
            level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            use_colors: Usar cores no terminal?
            save_to_file: Salvar logs em arquivo?
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Limpar handlers existentes
        self.logger.handlers.clear()
        
        # Configurar diretório de logs
        if log_dir is None:
            log_dir = Path("data/logs")
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Adicionar handler do console
        self._add_console_handler(use_colors)
        
        # Adicionar handler de arquivo se solicitado
        if save_to_file:
            self._add_file_handler()

    def _add_console_handler(self, use_colors: bool):
        """Adiciona handler para saída no console."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Formato do log
        log_format = "%(asctime)s | %(levelname)-8s | %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        
        if use_colors:
            formatter = ColoredFormatter(log_format, datefmt=date_format)
        else:
            formatter = logging.Formatter(log_format, datefmt=date_format)
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _add_file_handler(self):
        """Adiciona handler para salvar logs em arquivo."""
        # Nome do arquivo com data atual
        log_filename = f"photo_organizer_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_filepath = self.log_dir / log_filename
        
        file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        
        # Formato mais detalhado para arquivo
        log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        
        formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def debug(self, message: str):
        """Log nível DEBUG - informações detalhadas para diagnóstico."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log nível INFO - informações gerais sobre execução."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log nível WARNING - avisos que não impedem execução."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log nível ERROR - erros que impedem operação específica."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log nível CRITICAL - erros graves que impedem execução."""
        self.logger.critical(message)

    def exception(self, message: str):
        """Log de exceção com stack trace completo."""
        self.logger.exception(message)


# Instância global (será configurada pelo config.py)
_global_logger: Optional[PhotoOrganizerLogger] = None


def get_logger() -> PhotoOrganizerLogger:
    """
    Retorna a instância global do logger.
    
    Se ainda não foi inicializado, cria um com configurações padrão.
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = PhotoOrganizerLogger()
    
    return _global_logger


def init_logger(
    log_dir: Optional[Path] = None,
    level: str = "INFO",
    use_colors: bool = True,
    save_to_file: bool = True,
) -> PhotoOrganizerLogger:
    """
    Inicializa o logger global com configurações personalizadas.
    
    Args:
        log_dir: Diretório de logs
        level: Nível de log
        use_colors: Usar cores no terminal
        save_to_file: Salvar em arquivo
    
    Returns:
        Instância do logger configurado
    """
    global _global_logger
    
    _global_logger = PhotoOrganizerLogger(
        log_dir=log_dir,
        level=level,
        use_colors=use_colors,
        save_to_file=save_to_file,
    )
    
    return _global_logger

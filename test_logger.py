"""
Teste do módulo logger.py

Execute este arquivo para verificar se o logger está funcionando corretamente.
"""

import sys
from pathlib import Path

# Adicionar projeto root ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import init_logger, get_logger


def test_logger():
    """Testa todas as funcionalidades do logger."""
    
    print("=" * 60)
    print("TESTE DO SISTEMA DE LOGS")
    print("=" * 60)
    print()
    
    # Inicializar logger
    logger = init_logger(level="DEBUG", use_colors=True, save_to_file=True)
    
    print("✅ Logger inicializado com sucesso!")
    print(f"📁 Logs salvos em: data/logs/")
    print()
    
    # Testar diferentes níveis
    print("Testando diferentes níveis de log:")
    print("-" * 60)
    
    logger.debug("Mensagem DEBUG - detalhes técnicos")
    logger.info("Mensagem INFO - operação normal")
    logger.warning("Mensagem WARNING - algo inesperado")
    logger.error("Mensagem ERROR - falha em operação")
    logger.critical("Mensagem CRITICAL - erro grave!")
    
    print()
    print("-" * 60)
    print("✅ Teste concluído!")
    print()
    print("Verifique o arquivo de log em: data/logs/")
    print("Deve conter todas as mensagens acima com detalhes extras.")
    print()


if __name__ == "__main__":
    test_logger()

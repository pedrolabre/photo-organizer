"""
Teste do módulo file_scanner.py

Execute este arquivo para testar a varredura de imagens.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import get_config
from src.utils.logger import init_logger
from src.core.file_scanner import FileScanner


def test_file_scanner():
    """Testa o scanner de arquivos."""
    
    print("=" * 60)
    print("TESTE DO SCANNER DE ARQUIVOS")
    print("=" * 60)
    print()
    
    # Inicializar logger
    logger = init_logger(level="INFO")
    
    # Carregar configuração
    config = get_config()
    
    # Criar scanner
    scanner = FileScanner(config)
    
    print("✅ Scanner inicializado")
    print()
    
    # Varrer todas as fontes
    print("🔍 Varrendo pastas configuradas...")
    print("-" * 60)
    
    files = scanner.scan_all_sources()
    
    print()
    print("=" * 60)
    print("📊 RESULTADOS DA VARREDURA")
    print("=" * 60)
    print()
    
    if not files:
        print("⚠️  Nenhuma imagem encontrada!")
        print()
        print("💡 DICA: Adicione algumas fotos na pasta:")
        print(f"   {config.input_folders[0]}")
        print()
        return
    
    # Estatísticas gerais
    print(f"📸 Total de imagens: {len(files)}")
    print()
    
    # Tamanho total
    size_info = scanner.calculate_total_size(files)
    print(f"💾 Tamanho total:")
    print(f"   {size_info['mb']:.2f} MB ({size_info['gb']:.2f} GB)")
    print()
    
    # Agrupar por extensão
    groups = scanner.group_by_extension(files)
    print(f"📁 Tipos de arquivo encontrados: {len(groups)}")
    for ext, ext_files in sorted(groups.items()):
        print(f"📸 Total de imagens: {len(files)}")

        # Mostrar tamanho total
        totals = scanner.calculate_total_size(files)
        print(f"Total: {totals['count']} arquivos — {totals['mb']} MB ({totals['gb']} GB)")

        # Agrupar por extensão
        groups = scanner.group_by_extension(files)
        print('\nTipos encontrados:')
        for ext, lst in groups.items():
            print(f"  {ext}: {len(lst)}")

        # Mostrar primeiros 5 arquivos com info
        print('\nPrimeiros 5 arquivos:')
        for f in files[:5]:
            info = scanner.get_file_info(f)
            print(f" - {info['name']} | {info['extension']} | {info['size_mb']} MB | {info['path']}")
    print()
    
    # Mostrar primeiros 5 arquivos
    print("📋 Primeiros arquivos encontrados:")
    print("-" * 60)
    for i, file_path in enumerate(files[:5], 1):
        info = scanner.get_file_info(file_path)
        print(f"{i}. {file_path.name}")
        print(f"   Tamanho: {info['size_mb']} MB")
        print(f"   Caminho: {file_path.parent}")
        print()
    
    if len(files) > 5:
        print(f"... e mais {len(files) - 5} arquivo(s)")
        print()
    
    print("-" * 60)
    print("✅ Teste concluído!")
    print()


if __name__ == "__main__":
    test_file_scanner()

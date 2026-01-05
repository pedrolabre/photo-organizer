"""
Teste do módulo metadata_reader.py

Execute este arquivo para testar a leitura de metadados EXIF.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import get_config
from src.utils.logger import init_logger
from src.core.file_scanner import FileScanner
from src.core.metadata_reader import MetadataReader


def format_datetime(dt):
    """Formata datetime para exibição."""
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "N/A"


def test_metadata_reader():
    """Testa o leitor de metadados."""
    
    print("=" * 60)
    print("TESTE DO LEITOR DE METADADOS")
    print("=" * 60)
    print()
    
    # Inicializar
    logger = init_logger(level="INFO")
    config = get_config()
    scanner = FileScanner(config)
    reader = MetadataReader()
    
    print("✅ Componentes inicializados")
    print()
    
    # Encontrar imagens
    print("🔍 Procurando imagens...")
    files = scanner.scan_all_sources()
    
    if not files:
        print("⚠️  Nenhuma imagem encontrada!")
        print()
        print("💡 Adicione algumas fotos em test_photos/")
        return
    
    print(f"✅ Encontradas {len(files)} imagem(ns)")
    print()
    
    # Testar com as primeiras 3 imagens
    test_count = min(3, len(files))
    
    for i, file_path in enumerate(files[:test_count], 1):
        print("=" * 60)
        print(f"📸 IMAGEM {i}/{test_count}: {file_path.name}")
        print("=" * 60)
        print()
        
        # Ler metadados
        metadata = reader.read_metadata(file_path)
        
        # Informações básicas
        print("📋 INFORMAÇÕES BÁSICAS:")
        print("-" * 60)
        print(f"Arquivo: {metadata.get('file_name', 'N/A')}")
        print(f"Tamanho: {metadata.get('file_size', 0) / 1024 / 1024:.2f} MB")
        print(f"Formato: {metadata.get('format', 'N/A')}")
        print(f"Resolução: {metadata.get('resolution', 'N/A')}")
        print(f"Megapixels: {metadata.get('megapixels', 'N/A')} MP")
        print()
        
        # Data/hora
        print("📅 DATA E HORA:")
        print("-" * 60)
        dt = metadata.get('datetime')
        print(f"Data da foto: {format_datetime(dt)}")
        
        if 'datetime_original' in metadata:
            print(f"Data original (EXIF): {format_datetime(metadata['datetime_original'])}")
        
        if 'datetime_digitized' in metadata:
            print(f"Data digitalizada (EXIF): {format_datetime(metadata['datetime_digitized'])}")
        print()
        
        # Câmera
        print("📷 CÂMERA:")
        print("-" * 60)
        camera = reader.get_camera_info(metadata)
        print(f"Câmera: {camera}")
        
        if 'camera_make' in metadata:
            print(f"Marca: {metadata['camera_make']}")
        
        if 'camera_model' in metadata:
            print(f"Modelo: {metadata['camera_model']}")
        
        if 'software' in metadata:
            print(f"Software: {metadata['software']}")
        print()
        
        # Configurações da foto
        if any(k in metadata for k in ['iso', 'f_number', 'shutter_speed', 'focal_length']):
            print("⚙️  CONFIGURAÇÕES:")
            print("-" * 60)
            
            if 'iso' in metadata:
                print(f"ISO: {metadata['iso']}")
            
            if 'f_number' in metadata:
                print(f"Abertura: f/{metadata['f_number']}")
            
            if 'shutter_speed' in metadata:
                print(f"Velocidade: {metadata['shutter_speed']}s")
            
            if 'focal_length' in metadata:
                print(f"Distância focal: {metadata['focal_length']}mm")
            
            if 'flash' in metadata:
                flash_used = "Sim" if metadata['flash'] & 1 else "Não"
                print(f"Flash: {flash_used}")
            print()
        
        # GPS
        print("🌍 LOCALIZAÇÃO:")
        print("-" * 60)
        if metadata.get('has_gps'):
            print(f"Latitude: {metadata.get('latitude', 'N/A'):.6f}")
            print(f"Longitude: {metadata.get('longitude', 'N/A'):.6f}")
            
            if 'altitude' in metadata:
                print(f"Altitude: {metadata['altitude']} metros")
            
            # Link do Google Maps
            lat = metadata.get('latitude')
            lon = metadata.get('longitude')
            if lat and lon:
                print(f"📍 Google Maps: https://www.google.com/maps?q={lat},{lon}")
        else:
            print("Sem dados de GPS")
        print()
        
        # Verificar se tem EXIF
        has_exif = reader.has_exif(file_path)
        print(f"{'✅' if has_exif else '⚠️ '} Tem dados EXIF: {'Sim' if has_exif else 'Não'}")
        print()
    
    # Resumo
    print("=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    print()
    
    files_with_exif = sum(1 for f in files if reader.has_exif(f))
    print(f"Total de imagens: {len(files)}")
    print(f"Com EXIF: {files_with_exif}")
    print(f"Sem EXIF: {len(files) - files_with_exif}")
    print()
    
    print("-" * 60)
    print("✅ Teste concluído!")
    print()


if __name__ == "__main__":
    test_metadata_reader()

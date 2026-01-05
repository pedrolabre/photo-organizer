"""
Processing Module - Photo Organizer Dashboard

Lógica de processamento em background para organização de fotos.
"""

from pathlib import Path
from datetime import datetime

from src.utils.config import get_config
from src.utils.logger import get_logger
from src.core.file_scanner import FileScanner
from src.core.metadata_reader import MetadataReader
from src.core.hash_calculator import HashCalculator
from src.organization.folder_organizer import FolderOrganizer
from src.organization.file_mover import FileMover
from src.database.db_manager import DBManager
from src.detection.exact_duplicates import ExactDuplicateDetector
from src.detection.similar_detector import SimilarDuplicateDetector


def _update_progress(app_state, stage, current, total, message=""):
    """Atualiza o progresso do processamento."""
    percentage = int((current / total * 100)) if total > 0 else 0
    app_state["progress"] = {
        "stage": stage,
        "current": current,
        "total": total,
        "percentage": percentage,
        "message": message,
    }


def _process_photos(input_path, output_path, structure, operation,
                    detect_exact, detect_similar, similarity_threshold, recursive=True, app_state=None):
    """Processa fotos em background."""
    if app_state is None:
        try:
            from flask import current_app
            app_state = current_app.config.get('APP_STATE')
        except Exception:
            app_state = {}
    app_state["processing"] = True
    app_state["last_result"] = None
    logger = get_logger()
    result = {
        "success": False,
        "files_processed": 0,
        "files_organized": 0,
        "duplicates_exact": 0,
        "duplicates_similar": 0,
        "errors": 0,
        "output_path": str(output_path),
        "started_at": datetime.now().isoformat(),
    }
    try:
        _update_progress(app_state, "scan", 0, 100, "Escaneando arquivos...")
        config = get_config()
        scanner = FileScanner(config)
        files = scanner.scan_directory(input_path, recursive=recursive)
        if not files:
            result["success"] = True
            result["message"] = "Nenhuma imagem encontrada"
            app_state["last_result"] = result
            app_state["processing"] = False
            return
        total_files = len(files)
        result["files_processed"] = total_files
        _update_progress(app_state, "metadata", 0, total_files, "Lendo metadados...")
        reader = MetadataReader()
        hash_calc = HashCalculator()
        photos_data = []
        for i, file_path in enumerate(files):
            metadata = reader.read_metadata(file_path)
            md5_hash = hash_calc.calculate_md5(file_path)
            photos_data.append({
                "path": file_path,
                "datetime": metadata.get("datetime"),
                "md5": md5_hash,
                "metadata": metadata,
            })
            _update_progress(app_state, "metadata", i + 1, total_files,
                           f"Processando {file_path.name}")
        duplicates_exact = []
        if detect_exact:
            _update_progress(app_state, "duplicates_exact", 0, 100,
                           "Detectando duplicatas exatas...")
            db_manager = DBManager()
            exact_detector = ExactDuplicateDetector(db_manager.conn)
            for photo in photos_data:
                existing = db_manager.get_by_md5(photo["md5"])
                if existing:
                    duplicates_exact.append(photo["path"])
            result["duplicates_exact"] = len(duplicates_exact)
        _update_progress(app_state, "organize", 0, total_files, "Organizando arquivos...")
        organizer = FolderOrganizer(config, base_output_path=output_path)
        organizer.structure = structure
        mover = FileMover(config)
        mover.set_operation(operation)
        organized_count = 0
        error_count = 0
        for i, photo in enumerate(photos_data):
            if detect_exact and photo["path"] in duplicates_exact:
                continue
            target_folder = organizer.get_target_folder(photo["datetime"])
            success, msg, new_path = mover.process_file(
                photo["path"],
                target_folder
            )
            if success:
                organized_count += 1
            else:
                error_count += 1
                logger.error(f"Erro ao processar {photo['path'].name}: {msg}")
            _update_progress(app_state, "organize", i + 1, total_files,
                           f"Processando {photo['path'].name}")
        if detect_similar:
            _update_progress(app_state, "duplicates_similar", 0, 100,
                           "Detectando duplicatas similares...")
            similar_detector = SimilarDuplicateDetector()
            similar_groups = similar_detector.group_similar(
                [p["path"] for p in photos_data],
                max_distance=similarity_threshold
            )
            result["duplicates_similar"] = sum(len(g) - 1 for g in similar_groups.values())
        result["success"] = True
        result["files_organized"] = organized_count
        result["errors"] = error_count
        result["finished_at"] = datetime.now().isoformat()
        mover_stats = mover.get_stats()
        result["stats"] = mover_stats
        logger.info(f"Processamento concluído: {organized_count} arquivos organizados")
    except Exception as e:
        logger.exception("Erro durante processamento")
        result["success"] = False
        result["error"] = str(e)
    finally:
        app_state["last_result"] = result
        app_state["processing"] = False
        _update_progress(app_state, "done", 100, 100, "Concluído!")
"""
API Routes Module - Photo Organizer Dashboard

Rotas da API REST para operações do organizador de fotos.
"""

from flask import request, jsonify
from pathlib import Path
import threading

from src.utils.config import get_config
from src.utils.logger import get_logger
from src.core.file_scanner import FileScanner
from src.core.metadata_reader import MetadataReader
from src.organization.folder_organizer import FolderOrganizer
from src.processing import _process_photos


def register_api_routes(app):
    """Registra todas as rotas da API no app Flask."""

    @app.route("/api/config", methods=["GET"])
    def get_current_config():
        try:
            config = get_config()
            return jsonify({
                "success": True,
                "config": {
                    "input_folders": [str(f) for f in config.input_folders],
                    "output_folder": str(config.output_folder),
                    "structure": config.organization.structure,
                    "operation": config.safety.file_operation,
                    "detect_exact": config.duplicates.detect_exact,
                    "detect_similar": config.duplicates.detect_similar,
                    "similarity_threshold": config.duplicates.similarity_threshold,
                }
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/browse", methods=["POST"])
    def browse_folder():
        try:
            data = request.json
            folder_path = Path(data.get("path", ""))
            if not folder_path.exists():
                return jsonify({"success": False, "error": "Pasta não existe"}), 404
            if not folder_path.is_dir():
                return jsonify({"success": False, "error": "Caminho não é uma pasta"}), 400
            subfolders = []
            for item in folder_path.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    subfolders.append({"name": item.name, "path": str(item)})
            return jsonify({
                "success": True,
                "current": str(folder_path),
                "parent": str(folder_path.parent) if folder_path.parent != folder_path else None,
                "subfolders": sorted(subfolders, key=lambda x: x["name"].lower()),
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/validate-path", methods=["POST"])
    def validate_path():
        try:
            data = request.json
            path = Path(data.get("path", ""))
            if not path.exists():
                return jsonify({
                    "success": True,
                    "valid": False,
                    "message": "Pasta não existe (será criada se necessário)",
                    "can_create": True,
                })
            if not path.is_dir():
                return jsonify({
                    "success": True,
                    "valid": False,
                    "message": "Caminho não é uma pasta",
                    "can_create": False,
                })
            test_file = path / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
                writable = True
            except:
                writable = False
            return jsonify({
                "success": True,
                "valid": True,
                "writable": writable,
                "message": "Pasta válida e acessível" if writable else "Pasta sem permissão de escrita",
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/scan", methods=["POST"])
    def scan_folder():
        try:
            data = request.json
            input_path = Path(data.get("input_path"))
            output_path = Path(data.get("output_path"))
            structure = data.get("structure", "year_month_day")
            recursive = data.get("recursive", True)
            if not input_path.exists():
                return jsonify({"success": False, "error": "Pasta de entrada não existe"}), 404
            logger = get_logger()
            config = get_config()
            organizer = FolderOrganizer(config, base_output_path=output_path)
            organizer.structure = structure
            scanner = FileScanner(config)
            files = scanner.scan_directory(input_path, recursive=recursive)
            if not files:
                return jsonify({
                    "success": True,
                    "files_found": 0,
                    "message": "Nenhuma imagem encontrada na pasta",
                })
            reader = MetadataReader()
            photos_with_dates = []
            for file_path in files:
                metadata = reader.read_metadata(file_path)
                photo_date = metadata.get("datetime")
                photos_with_dates.append((file_path, photo_date))
            preview = organizer.get_organization_preview(photos_with_dates)
            summary = organizer.get_structure_summary(preview)
            tree = organizer.get_folder_tree_preview(preview)
            return jsonify({
                "success": True,
                "files_found": len(files),
                "summary": summary,
                "tree": tree,
            })
        except Exception as e:
            logger = get_logger()
            logger.exception("Erro ao escanear pasta")
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/organize", methods=["POST"])
    def organize_photos():
        from flask import current_app
        app_state = current_app.config.get('APP_STATE')
        if app_state["processing"]:
            return jsonify({"success": False, "error": "Processamento já em andamento"}), 409
        try:
            data = request.json
            input_path = Path(data.get("input_path"))
            output_path = Path(data.get("output_path"))
            structure = data.get("structure", "year_month_day")
            operation = data.get("operation", "copy")
            recursive = data.get("recursive", True)
            detect_exact = data.get("detect_exact", True)
            detect_similar = data.get("detect_similar", False)
            similarity_threshold = data.get("similarity_threshold", 5)
            thread = threading.Thread(
                target=_process_photos,
                args=(input_path, output_path, structure, operation,
                      detect_exact, detect_similar, similarity_threshold, recursive, app_state)
            )
            thread.daemon = True
            thread.start()
            return jsonify({
                "success": True,
                "message": "Processamento iniciado",
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/progress", methods=["GET"])
    def get_progress():
        from flask import current_app
        app_state = current_app.config.get('APP_STATE')
        return jsonify({
            "success": True,
            "processing": app_state["processing"],
            "progress": app_state["progress"],
        })

    @app.route("/api/result", methods=["GET"])
    def get_result():
        from flask import current_app
        app_state = current_app.config.get('APP_STATE')
        if app_state["last_result"] is None:
            return jsonify({
                "success": False,
                "error": "Nenhum processamento concluído ainda",
            }), 404
        return jsonify({
            "success": True,
            "result": app_state["last_result"],
        })
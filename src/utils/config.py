"""
Gerenciador de configurações do Photo Organizer.

Carrega e valida configurações do arquivo config.yaml,
fornecendo acesso estruturado a todos os parâmetros do sistema.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from .configs import (
    OrganizationConfig,
    DuplicatesConfig,
    SafetyConfig,
    PerformanceConfig,
    LoggingConfig,
    ReportsConfig,
    DatabaseConfig,
)


class Config:
    """Gerenciador central de configurações."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Inicializa o gerenciador de configurações.

        Args:
            config_path: Caminho para o arquivo config.yaml
        """
        self.config_path = Path(config_path)
        self._raw_config: Dict[str, Any] = {}
        
        # Carregar configurações
        self._load_config()
        
        # Inicializar estruturas de configuração
        self.input_folders: List[Path] = []
        self.output_folder: Path = Path()
        self.quarantine_folder: Path = Path()
        self.supported_extensions: List[str] = []
        
        self.organization = OrganizationConfig()
        self.duplicates = DuplicatesConfig()
        self.safety = SafetyConfig()
        self.performance = PerformanceConfig()
        self.logging = LoggingConfig()
        self.reports = ReportsConfig()
        self.database = DatabaseConfig()
        
        # Processar configurações
        self._process_config()
        
        # Criar diretórios necessários
        self._create_directories()

    def _load_config(self):
        """Carrega o arquivo YAML de configuração."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Arquivo de configuração não encontrado: {self.config_path}\n"
                "Certifique-se de que config.yaml está na raiz do projeto."
            )
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._raw_config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Erro ao ler config.yaml: {e}")

    def _process_config(self):
        """Processa e valida as configurações carregadas."""
        
        # Pastas de entrada
        input_folders_raw = self._raw_config.get("input_folders", [])
        self.input_folders = [Path(folder) for folder in input_folders_raw]
        
        # Pastas de saída
        self.output_folder = Path(self._raw_config.get(
            "output_folder", 
            "output/organized"
        ))
        self.quarantine_folder = Path(self._raw_config.get(
            "quarantine_folder", 
            "output/quarantine"
        ))
        
        # Extensões suportadas
        self.supported_extensions = [
            ext.lower() 
            for ext in self._raw_config.get("supported_extensions", [
                ".jpg", ".jpeg", ".png", ".gif", ".bmp"
            ])
        ]
        
        # Organização
        org_config = self._raw_config.get("organization", {})
        self.organization = OrganizationConfig(
            structure=org_config.get("structure", "year_month_day"),
            folder_format=org_config.get("folder_format", {
                "year": "%Y",
                "month": "%Y-%m",
                "day": "%Y-%m-%d"
            }),
            use_file_date_as_fallback=org_config.get("use_file_date_as_fallback", True),
            create_no_date_folder=org_config.get("create_no_date_folder", True)
        )
        
        # Duplicatas
        dup_config = self._raw_config.get("duplicates", {})
        self.duplicates = DuplicatesConfig(
            detect_exact=dup_config.get("detect_exact", True),
            detect_similar=dup_config.get("detect_similar", False),
            similarity_threshold=dup_config.get("similarity_threshold", 10),
            keep_policy=dup_config.get("keep_policy", "highest_resolution")
        )
        
        # Segurança
        safety_config = self._raw_config.get("safety", {})
        self.safety = SafetyConfig(
            never_delete_originals=safety_config.get("never_delete_originals", True),
            file_operation=safety_config.get("file_operation", "copy"),
            backup_database=safety_config.get("backup_database", True),
            verify_after_copy=safety_config.get("verify_after_copy", True)
        )
        
        # Performance
        perf_config = self._raw_config.get("performance", {})
        self.performance = PerformanceConfig(
            max_threads=perf_config.get("max_threads", 0),
            cache_size_mb=perf_config.get("cache_size_mb", 500),
            batch_size=perf_config.get("batch_size", 100)
        )
        
        # Logging
        log_config = self._raw_config.get("logging", {})
        self.logging = LoggingConfig(
            level=log_config.get("level", "INFO"),
            save_to_file=log_config.get("save_to_file", True),
            retention_days=log_config.get("retention_days", 30),
            use_colors=log_config.get("use_colors", True)
        )
        
        # Relatórios
        report_config = self._raw_config.get("reports", {})
        self.reports = ReportsConfig(
            generate_json=report_config.get("generate_json", True),
            include_thumbnails=report_config.get("include_thumbnails", False),
            date_format=report_config.get("date_format", "%Y-%m-%d %H:%M:%S")
        )
        
        # Banco de dados
        db_config = self._raw_config.get("database", {})
        self.database = DatabaseConfig(
            filename=db_config.get("filename", "photo_organizer.db"),
            auto_backup=db_config.get("auto_backup", True),
            backup_retention_days=db_config.get("backup_retention_days", 7)
        )

    def _create_directories(self):
        """Cria diretórios necessários se não existirem."""
        directories = [
            Path("data/database"),
            Path("data/logs"),
            Path("data/cache"),
            self.output_folder,
            self.quarantine_folder,
            self.quarantine_folder / "groups",
            Path("output/reports"),
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_database_path(self) -> Path:
        """Retorna o caminho completo do banco de dados."""
        return Path("data/database") / self.database.filename

    def is_supported_extension(self, file_path: Path) -> bool:
        """
        Verifica se a extensão do arquivo é suportada.

        Args:
            file_path: Caminho do arquivo

        Returns:
            True se a extensão é suportada
        """
        return file_path.suffix.lower() in self.supported_extensions

    def validate(self) -> List[str]:
        """
        Valida as configurações e retorna lista de erros.

        Returns:
            Lista de mensagens de erro (vazia se tudo OK)
        """
        errors = []
        
        # Validar pastas de entrada
        if not self.input_folders:
            errors.append("Nenhuma pasta de entrada configurada em 'input_folders'")
        
        for folder in self.input_folders:
            if not folder.exists():
                errors.append(f"Pasta de entrada não existe: {folder}")
        
        # Validar estrutura de organização
        valid_structures = ["year", "year_month", "year_month_day"]
        if self.organization.structure not in valid_structures:
            errors.append(
                f"Estrutura de organização inválida: '{self.organization.structure}'. "
                f"Opções válidas: {valid_structures}"
            )
        
        # Validar política de duplicatas
        valid_policies = ["highest_resolution", "newest", "oldest", "first_found"]
        if self.duplicates.keep_policy not in valid_policies:
            errors.append(
                f"Política de duplicatas inválida: '{self.duplicates.keep_policy}'. "
                f"Opções válidas: {valid_policies}"
            )
        
        # Validar operação de arquivo
        valid_operations = ["copy", "move"]
        if self.safety.file_operation not in valid_operations:
            errors.append(
                f"Operação de arquivo inválida: '{self.safety.file_operation}'. "
                f"Opções válidas: {valid_operations}"
            )
        
        return errors

    def __repr__(self) -> str:
        """Representação legível da configuração."""
        return (
            f"Config(\n"
            f"  input_folders={len(self.input_folders)} pastas,\n"
            f"  output_folder={self.output_folder},\n"
            f"  extensions={len(self.supported_extensions)} tipos,\n"
            f"  organization={self.organization.structure}\n"
            f")"
        )


# Instância global
_global_config: Optional[Config] = None


def get_config(config_path: str = "config.yaml") -> Config:
    """
    Retorna a instância global de configuração.

    Args:
        config_path: Caminho para config.yaml

    Returns:
        Instância de Config
    """
    global _global_config
    
    if _global_config is None:
        _global_config = Config(config_path)
    
    return _global_config

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from src.utils.logger import get_logger
from src.core.metadata_reader import MetadataReader


logger = get_logger()


def _to_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except Exception:
        try:
            # fallback: if already a string but different format
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None


def choose_keeper(existing: Dict[str, Any], new: Dict[str, Any], policy: str = "highest_resolution") -> str:
    """Decide qual manter entre `existing` (do DB) e `new` (metadados atuais).

    Retorna 'existing' ou 'new'.
    """
    policy = (policy or "highest_resolution").lower()

    if policy == "first_found":
        return "existing"

    # resolution-based
    existing_res = (existing.get("width") or 0) * (existing.get("height") or 0)
    new_res = (new.get("width") or 0) * (new.get("height") or 0)

    if policy == "highest_resolution":
        if new_res > existing_res:
            return "new"
        return "existing"

    # datetime based
    ex_dt = _to_datetime(existing.get("datetime"))
    new_dt = _to_datetime(new.get("datetime"))
    if policy == "newest":
        if new_dt and ex_dt:
            return "new" if new_dt > ex_dt else "existing"
        # fallback to file size/resolution
        return "new" if new_res > existing_res else "existing"

    if policy == "oldest":
        if new_dt and ex_dt:
            return "new" if new_dt < ex_dt else "existing"
        return "new" if new_res > existing_res else "existing"

    # default
    return "existing"


def choose_keeper_among(paths: List[Path], policy: str = "highest_resolution") -> Path:
    """Escolhe o melhor arquivo dentre uma lista de `paths` segundo a `policy`.

    Retorna o Path do arquivo a ser mantido.
    """
    reader = MetadataReader()
    best = None
    best_meta = None

    for p in paths:
        try:
            meta = reader.read_metadata(p)
        except Exception:
            continue
        if best is None:
            best = Path(p)
            best_meta = meta
            continue

        keep = choose_keeper(dict(best_meta), dict(meta), policy)
        if keep == "new":
            best = Path(p)
            best_meta = meta

    return best

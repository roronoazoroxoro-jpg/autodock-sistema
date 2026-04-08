from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

import yaml


def setup_logging(verbose: bool = True) -> None:
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(f"No existe el archivo de configuracion: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} no encontrado: {path}")


def find_executable(candidates: Iterable[Path], env_var: str | None = None) -> Path:
    if env_var:
        env_value = os.getenv(env_var, "").strip()
        if env_value:
            env_path = Path(env_value)
            if env_path.exists():
                return env_path

    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate

    raise FileNotFoundError(
        "No se encontro ejecutable requerido. "
        f"Revisa PATH o variable de entorno {env_var or '(sin env var)'}"
    )


def which_or_none(executable_name: str) -> Path | None:
    found = shutil.which(executable_name)
    return Path(found) if found else None


def run_cmd(cmd: list[str], description: str) -> None:
    logging.info("%s", description)
    logging.debug("Comando: %s", " ".join(cmd))
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Error ejecutando: {' '.join(cmd)}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    if result.stdout.strip():
        logging.info(result.stdout.strip())

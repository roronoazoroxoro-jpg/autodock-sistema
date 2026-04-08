from __future__ import annotations

import os
import sys
from pathlib import Path

from scripts.common import load_config, which_or_none


def _exists(path_str: str) -> bool:
    return bool(path_str) and Path(path_str).expanduser().exists()


def _print_ok(msg: str) -> None:
    print(f"[OK] {msg}")


def _print_warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def _print_fail(msg: str) -> None:
    print(f"[FAIL] {msg}")


def main() -> int:
    cfg_path = Path("config.yaml").resolve()
    if not cfg_path.exists():
        _print_fail(f"No existe config.yaml en {cfg_path}")
        return 2

    cfg = load_config(cfg_path)
    tools_cfg = cfg.get("tools", {})
    docking_cfg = cfg.get("docking", {})
    inputs_cfg = cfg.get("inputs", {})

    failed = False

    for key in ("center_x", "center_y", "center_z", "size_x", "size_y", "size_z"):
        if key not in docking_cfg:
            _print_fail(f"Falta docking.{key} en config.yaml")
            failed = True
    if not failed:
        _print_ok("Parametros de docking presentes")

    project_root = Path(__file__).resolve().parents[1]

    vina_cfg = tools_cfg.get("vina_executable", "")
    vina_env = os.getenv("VINA_EXE", "")
    vina_path = None

    if _exists(vina_cfg):
        vina_path = Path(vina_cfg)
    elif _exists(vina_env):
        vina_path = Path(vina_env)
    else:
        vina_path = which_or_none("vina") or which_or_none("vina.exe")

    if (not vina_path or not Path(vina_path).exists()):
        local_vina_dir = project_root / "tools" / "vina"
        local_candidates = [local_vina_dir / "vina.exe", *sorted(local_vina_dir.glob("vina*.exe"))]
        for candidate in local_candidates:
            if candidate.exists():
                vina_path = candidate
                break

    if vina_path and Path(vina_path).exists():
        _print_ok(f"Vina encontrado: {vina_path}")
    else:
        _print_fail("No se encontro Vina. Ejecuta scripts/install_windows.ps1")
        failed = True

    mgl_root_cfg = tools_cfg.get("mgltools_root", "")
    mgl_root_env = os.getenv("MGLTOOLS_ROOT", "")
    mgl_root = mgl_root_cfg or mgl_root_env
    if mgl_root and _exists(mgl_root):
        _print_ok(f"MGLTools root encontrado: {mgl_root}")
    else:
        _print_warn("MGLTOOLS_ROOT no encontrado en config ni en entorno")

    _mgl_fallbacks = {
        "MGLTOOLS_PYTHONSH": [
            "pythonsh", "pythonsh.exe", "python.exe",
            "bin/pythonsh", "bin/pythonsh.exe",
        ] if mgl_root else [],
        "MGLTOOLS_PREPARE_RECEPTOR": [
            "MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py",
            "Lib/site-packages/AutoDockTools/Utilities24/prepare_receptor4.py",
        ] if mgl_root else [],
        "MGLTOOLS_PREPARE_LIGAND": [
            "MGLToolsPckgs/AutoDockTools/Utilities24/prepare_ligand4.py",
            "Lib/site-packages/AutoDockTools/Utilities24/prepare_ligand4.py",
        ] if mgl_root else [],
    }
    for var in ("MGLTOOLS_PYTHONSH", "MGLTOOLS_PREPARE_RECEPTOR", "MGLTOOLS_PREPARE_LIGAND"):
        value = os.getenv(var, "")
        if _exists(value):
            _print_ok(f"{var} disponible")
        else:
            resolved = None
            if mgl_root:
                mgl_p = Path(mgl_root)
                for rel in _mgl_fallbacks[var]:
                    candidate = mgl_p / rel
                    if candidate.exists():
                        resolved = candidate
                        break
            if resolved:
                _print_ok(f"{var} resuelto: {resolved}")
            else:
                _print_warn(f"{var} no disponible (revisar instalacion MGLTools)")

    receptor = inputs_cfg.get("receptor", "")
    ligand = inputs_cfg.get("ligand", "")
    if receptor and Path(receptor).exists():
        _print_ok(f"Input receptor encontrado: {receptor}")
    else:
        _print_warn("Input receptor no existe aun (config.inputs.receptor)")

    if ligand and Path(ligand).exists():
        _print_ok(f"Input ligando encontrado: {ligand}")
    else:
        _print_warn("Input ligando no existe aun (config.inputs.ligand)")

    try:
        import Bio  # noqa: F401
        import numpy  # noqa: F401
        import pandas  # noqa: F401
        import yaml  # noqa: F401

        _print_ok("Dependencias Python base disponibles")
    except Exception as exc:
        _print_fail(f"Dependencias Python incompletas: {exc}")
        failed = True

    if failed:
        print("\nResultado: verificacion con fallos")
        return 1

    print("\nResultado: verificacion correcta")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

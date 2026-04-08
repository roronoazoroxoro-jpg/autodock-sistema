"""
Preparación de receptor — Conversión PDB → PDBQT
=================================================

Este módulo convierte un archivo de receptor (proteína) desde formato PDB al
formato PDBQT requerido por AutoDock Vina, utilizando los scripts de MGLTools
(prepare_receptor4.py via pythonsh).

El proceso añade automáticamente hidrógenos polares y cargas de Gasteiger.
Si MGLTools no está disponible, use AutoDockTools gráficamente para preparar
el receptor manualmente y guárdelo como .pdbqt.

Reglas:
    - El archivo PDB de entrada debe estar correctamente formateado (ATOM/HETATM)
    - Se recomienda eliminar agua (HOH) y ligandos co-cristalizados antes de preparar
    - MGLTools debe estar instalado en la ruta configurada en config.yaml
"""
from __future__ import annotations

from pathlib import Path

from scripts.common import find_executable, require_file, run_cmd


def prepare_receptor(
    receptor_pdb: Path,
    receptor_pdbqt: Path,
    mgltools_root: Path | None = None,
) -> Path:
    require_file(receptor_pdb, "Receptor PDB")

    candidates_pythonsh = []
    candidates_script = []

    if mgltools_root:
        candidates_pythonsh.extend(
            [
                mgltools_root / "pythonsh",
                mgltools_root / "pythonsh.exe",
                mgltools_root / "bin" / "pythonsh",
                mgltools_root / "bin" / "pythonsh.exe",
                mgltools_root / "python.exe",  # MGLTools 1.5.6 Windows
            ]
        )
        # Standard MGLTools path
        candidates_script.append(
            mgltools_root
            / "MGLToolsPckgs"
            / "AutoDockTools"
            / "Utilities24"
            / "prepare_receptor4.py"
        )
        # MGLTools 1.5.6 Windows (site-packages layout)
        candidates_script.append(
            mgltools_root
            / "Lib"
            / "site-packages"
            / "AutoDockTools"
            / "Utilities24"
            / "prepare_receptor4.py"
        )

    pythonsh = find_executable(candidates_pythonsh, env_var="MGLTOOLS_PYTHONSH")
    prepare_script = find_executable(candidates_script, env_var="MGLTOOLS_PREPARE_RECEPTOR")

    receptor_pdbqt.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(pythonsh),
        str(prepare_script),
        "-r",
        str(receptor_pdb),
        "-o",
        str(receptor_pdbqt),
        "-A",
        "hydrogens",
    ]
    run_cmd(cmd, "Preparando receptor con MGLTools")
    return receptor_pdbqt

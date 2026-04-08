"""
Preparación de ligando — Conversión PDB → PDBQT
================================================

Este módulo convierte un archivo de ligando (molécula pequeña / fármaco candidato)
desde formato PDB al formato PDBQT requerido por AutoDock Vina, utilizando los
scripts de MGLTools (prepare_ligand4.py via pythonsh).

El proceso detecta automáticamente los enlaces rotables (torsiones) del ligando,
calcula cargas de Gasteiger y estructura el árbol de torsiones en el PDBQT.

Reglas:
    - El archivo PDB de entrada debe tener hidrógenos explícitos
    - Ligandos con más de 15 enlaces rotables pueden resultar en docking lento o impreciso
    - MGLTools debe estar instalado en la ruta configurada en config.yaml
    - Usar archivos PDB obtenidos de PubChem (formato 3D) o DrugBank
"""
from __future__ import annotations

from pathlib import Path

from scripts.common import find_executable, require_file, run_cmd


def prepare_ligand(
    ligand_pdb: Path,
    ligand_pdbqt: Path,
    mgltools_root: Path | None = None,
) -> Path:
    require_file(ligand_pdb, "Ligando PDB")

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
            / "prepare_ligand4.py"
        )
        # MGLTools 1.5.6 Windows (site-packages layout)
        candidates_script.append(
            mgltools_root
            / "Lib"
            / "site-packages"
            / "AutoDockTools"
            / "Utilities24"
            / "prepare_ligand4.py"
        )

    pythonsh = find_executable(candidates_pythonsh, env_var="MGLTOOLS_PYTHONSH")
    prepare_script = find_executable(candidates_script, env_var="MGLTOOLS_PREPARE_LIGAND")

    ligand_pdbqt.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(pythonsh),
        str(prepare_script),
        "-l",
        str(ligand_pdb),
        "-o",
        str(ligand_pdbqt),
        "-A",
        "hydrogens",
    ]
    run_cmd(cmd, "Preparando ligando con MGLTools")
    return ligand_pdbqt

"""
Ejecución de AutoDock Vina
==========================

Este módulo ejecuta AutoDock Vina como subproceso, pasándole el receptor y
el ligando preparados (en formato PDBQT) junto con los parámetros del grid
(centro y dimensiones del sitio de búsqueda).

Vina realiza la búsqueda conformacional Monte Carlo iterada y genera hasta
`num_modes` poses de unión ordenadas por energía de afinidad (kcal/mol).

Salidas generadas:
    <output_pdbqt>  — Todas las poses del ligando (MODE 1 = mejor unión)
    <output_log>    — Tabla de afinidades y RMSD de cada pose

Interpretación de la energía de afinidad:
    < −9 kcal/mol   → Unión muy fuerte (excelente candidato)
    −7 a −9 kcal/mol → Unión buena (candidatos típicos de fármacos)
    −5 a −7 kcal/mol → Unión moderada
    > −5 kcal/mol   → Unión débil (generalmente no interesante)

Reglas:
    - El grid (center_x/y/z y size_x/y/z) debe estar centrado en el sitio activo
    - No cerrar el proceso mientras Vina está calculando
    - Un exhaustiveness más alto (>8) mejora la calidad pero aumenta el tiempo de cálculo
"""
from __future__ import annotations

from pathlib import Path

from scripts.common import find_executable, require_file, run_cmd, which_or_none


def run_vina(
    receptor_pdbqt: Path,
    ligand_pdbqt: Path,
    output_pdbqt: Path,
    output_log: Path,
    docking_cfg: dict,
    vina_path: Path | None = None,
) -> None:
    require_file(receptor_pdbqt, "Receptor PDBQT")
    require_file(ligand_pdbqt, "Ligando PDBQT")

    candidates = []
    if vina_path:
        candidates.append(vina_path)

    project_root = Path(__file__).resolve().parents[1]
    local_vina_dir = project_root / "tools" / "vina"
    candidates.append(local_vina_dir / "vina.exe")
    candidates.extend(sorted(local_vina_dir.glob("vina*.exe")))

    path_vina = which_or_none("vina")
    if path_vina:
        candidates.append(path_vina)
    path_vina_exe = which_or_none("vina.exe")
    if path_vina_exe:
        candidates.append(path_vina_exe)

    vina = find_executable(candidates, env_var="VINA_EXE")

    output_pdbqt.parent.mkdir(parents=True, exist_ok=True)
    output_log.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(vina),
        "--receptor",
        str(receptor_pdbqt),
        "--ligand",
        str(ligand_pdbqt),
        "--center_x",
        str(docking_cfg["center_x"]),
        "--center_y",
        str(docking_cfg["center_y"]),
        "--center_z",
        str(docking_cfg["center_z"]),
        "--size_x",
        str(docking_cfg["size_x"]),
        "--size_y",
        str(docking_cfg["size_y"]),
        "--size_z",
        str(docking_cfg["size_z"]),
        "--exhaustiveness",
        str(docking_cfg.get("exhaustiveness", 8)),
        "--num_modes",
        str(docking_cfg.get("num_modes", 9)),
        "--energy_range",
        str(docking_cfg.get("energy_range", 3)),
        "--cpu",
        str(docking_cfg.get("cpu", 0)),
        "--out",
        str(output_pdbqt),
    ]
    run_cmd(cmd, "Ejecutando AutoDock Vina")

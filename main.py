"""
Pipeline principal de docking molecular — AutoDock Vina MVP
===========================================================

Este script es el núcleo del sistema automatizado de docking. Orquesta todo
el proceso: carga la configuración, prepara los archivos moleculares (conversión
PDB → PDBQT usando MGLTools) y ejecuta AutoDock Vina para calcular las poses
de unión y energías de afinidad.

Uso básico (desde la raíz del proyecto):
    .venv\\Scripts\\python.exe main.py

Con archivos específicos:
    .venv\\Scripts\\python.exe main.py --receptor receptors\\mi_receptor.pdb --ligand ligands\\mi_ligando.pdb --verbose

Con archivos ya preparados (.pdbqt):
    .venv\\Scripts\\python.exe main.py --receptor receptors\\receptor.pdbqt --ligand ligands\\ligando.pdbqt --skip-prepare

Salidas generadas:
    outputs/docked_<receptor>_<ligando>.pdbqt  — Poses de unión del docking
    outputs/docking_<receptor>_<ligando>.log   — Energías de afinidad y RMSD

Reglas de uso:
    - Los archivos de receptor deben estar en receptors/ y los de ligando en ligands/
    - Los nombres de archivo no deben contener espacios ni caracteres especiales
    - Ajustar el grid (center_x/y/z, size_x/y/z) en config.yaml antes de ejecutar
    - Usar --skip-prepare si los archivos ya están en formato .pdbqt
    - Usar --verbose para diagnóstico y resolución de problemas
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from scripts.common import ensure_dir, load_config, require_file, setup_logging
from scripts.prepare_ligand import prepare_ligand
from scripts.prepare_receptor import prepare_receptor
from scripts.run_vina import run_vina

PROJECT_ROOT = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline MVP AutoDock Vina en Windows")
    parser.add_argument("--config", default="config.yaml", help="Ruta a config.yaml")
    parser.add_argument("--receptor", required=False, help="Ruta a receptor .pdb o .pdbqt")
    parser.add_argument("--ligand", required=False, help="Ruta a ligando .pdb o .pdbqt")
    parser.add_argument("--skip-prepare", action="store_true", help="Saltar conversion PDB->PDBQT")
    parser.add_argument("--verbose", action="store_true", help="Habilitar logs detallados")
    return parser


def _as_abs(path_str: str, base: Path | None = None) -> Path:
    path = Path(path_str).expanduser()
    if path.is_absolute():
        return path.resolve()
    return ((base or PROJECT_ROOT) / path).resolve()


def main() -> None:
    args = build_parser().parse_args()
    setup_logging(verbose=args.verbose)

    config_path = _as_abs(args.config, base=PROJECT_ROOT)
    cfg = load_config(config_path)
    config_base = config_path.parent

    project_cfg = cfg.get("project", {})
    inputs_cfg = cfg.get("inputs", {})
    tools_cfg = cfg.get("tools", {})
    docking_cfg = cfg.get("docking", {})

    for key in ("center_x", "center_y", "center_z", "size_x", "size_y", "size_z"):
        if key not in docking_cfg:
            raise KeyError(f"Falta parametro de docking en config.yaml: {key}")

    outputs_dir = _as_abs(project_cfg.get("outputs_dir", "outputs"), base=config_base)
    ensure_dir(outputs_dir)
    prepared_dir = outputs_dir / "prepared"
    ensure_dir(prepared_dir)

    receptor_arg = args.receptor or inputs_cfg.get("receptor", "")
    ligand_arg = args.ligand or inputs_cfg.get("ligand", "")
    if not receptor_arg or not ligand_arg:
        raise ValueError(
            "Debes definir receptor y ligando en config.yaml (inputs.receptor, inputs.ligand) "
            "o pasarlos por CLI con --receptor y --ligand"
        )

    receptor_input = _as_abs(receptor_arg, base=config_base)
    ligand_input = _as_abs(ligand_arg, base=config_base)
    require_file(receptor_input, "Archivo receptor")
    require_file(ligand_input, "Archivo ligando")

    mgl_root_raw = tools_cfg.get("mgltools_root", "")
    mgl_root = _as_abs(mgl_root_raw, base=config_base) if mgl_root_raw else None

    if args.skip_prepare:
        receptor_pdbqt = receptor_input
        ligand_pdbqt = ligand_input
        if receptor_pdbqt.suffix.lower() != ".pdbqt":
            raise ValueError("Con --skip-prepare, receptor debe ser .pdbqt")
        if ligand_pdbqt.suffix.lower() != ".pdbqt":
            raise ValueError("Con --skip-prepare, ligando debe ser .pdbqt")
    else:
        receptor_pdbqt = prepared_dir / f"{receptor_input.stem}.pdbqt"
        ligand_pdbqt = prepared_dir / f"{ligand_input.stem}.pdbqt"

        if receptor_input.suffix.lower() == ".pdbqt":
            receptor_pdbqt = receptor_input
            logging.info("Receptor ya esta en formato PDBQT: %s", receptor_input)
        else:
            prepare_receptor(receptor_input, receptor_pdbqt, mgl_root)

        if ligand_input.suffix.lower() == ".pdbqt":
            ligand_pdbqt = ligand_input
            logging.info("Ligando ya esta en formato PDBQT: %s", ligand_input)
        else:
            prepare_ligand(ligand_input, ligand_pdbqt, mgl_root)

    vina_raw = tools_cfg.get("vina_executable", "")
    vina_path = _as_abs(vina_raw, base=config_base) if vina_raw else None

    output_pdbqt = outputs_dir / f"docked_{receptor_input.stem}_{ligand_input.stem}.pdbqt"
    output_log = outputs_dir / f"docking_{receptor_input.stem}_{ligand_input.stem}.log"

    run_vina(
        receptor_pdbqt=receptor_pdbqt,
        ligand_pdbqt=ligand_pdbqt,
        output_pdbqt=output_pdbqt,
        output_log=output_log,
        docking_cfg=docking_cfg,
        vina_path=vina_path,
    )

    logging.info("Docking finalizado")
    logging.info("Resultado: %s", output_pdbqt)
    logging.info("Log: %s", output_log)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logging.error("Fallo en la ejecucion: %s", exc)
        raise

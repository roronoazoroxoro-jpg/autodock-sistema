"""
Interfaz web del sistema de docking molecular — AutoDock Vina MVP
==================================================================

Servidor Flask que proporciona una interfaz gráfica web para ejecutar docking
molecular sin necesidad de usar la línea de comandos. El doctor puede subir
los archivos de receptor y ligando desde el navegador y obtener los resultados
directamente en pantalla.

Cómo iniciar:
    Doble clic en INICIAR_WEB.bat
    — O desde terminal:
    .venv\\Scripts\\python.exe webapp.py

Acceso:
    Abrir el navegador y ir a: http://localhost:5000

Parámetros opcionales:
    --port    Puerto del servidor (por defecto: 5000)
    --host    Dirección de escucha (por defecto: 127.0.0.1 — solo local)
    --debug   Activar modo debug (solo para desarrollo)

Reglas de seguridad:
    - El servidor escucha SOLO en localhost (127.0.0.1) por defecto — no es accesible desde internet
    - No cambiar el host a 0.0.0.0 sin implementar autenticación adicional
    - Formatos aceptados: .pdb y .pdbqt únicamente
    - No subir archivos que contengan datos sensibles de pacientes sin medidas de seguridad adicionales
    - El servidor debe detenerse al terminar la sesión de trabajo (cerrar la ventana de terminal)
"""
from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from main import _as_abs
from scripts.common import ensure_dir, load_config
from scripts.prepare_ligand import prepare_ligand
from scripts.prepare_receptor import prepare_receptor
from scripts.run_vina import run_vina

ALLOWED_EXTENSIONS = {".pdb", ".pdbqt"}

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "autodock-mvp-secret")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


def _allowed(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    cfg = load_config(_as_abs("config.yaml"))
    project_cfg = cfg.get("project", {})
    tools_cfg = cfg.get("tools", {})
    docking_cfg = cfg.get("docking", {})

    ligands_dir = _as_abs(project_cfg.get("ligands_dir", "ligands"))
    receptors_dir = _as_abs(project_cfg.get("receptors_dir", "receptors"))
    outputs_dir = _as_abs(project_cfg.get("outputs_dir", "outputs"))
    ensure_dir(ligands_dir)
    ensure_dir(receptors_dir)
    ensure_dir(outputs_dir)
    ensure_dir(outputs_dir / "prepared")

    if request.method == "POST":
        receptor = request.files.get("receptor")
        ligand = request.files.get("ligand")
        skip_prepare = request.form.get("skip_prepare") == "on"

        if not receptor or not ligand:
            flash("Debes subir receptor y ligando", "error")
            return redirect(url_for("index"))

        rec_name = secure_filename(receptor.filename or "")
        lig_name = secure_filename(ligand.filename or "")
        if not rec_name or not lig_name or not _allowed(rec_name) or not _allowed(lig_name):
            flash("Formatos permitidos: .pdb o .pdbqt", "error")
            return redirect(url_for("index"))

        receptor_input = receptors_dir / rec_name
        ligand_input = ligands_dir / lig_name
        receptor.save(receptor_input)
        ligand.save(ligand_input)

        try:
            mgl_root_raw = tools_cfg.get("mgltools_root", "")
            mgl_root = _as_abs(mgl_root_raw) if mgl_root_raw else None

            if skip_prepare:
                receptor_pdbqt = receptor_input
                ligand_pdbqt = ligand_input
                if receptor_pdbqt.suffix.lower() != ".pdbqt" or ligand_pdbqt.suffix.lower() != ".pdbqt":
                    raise ValueError("Con skip prepare, ambos archivos deben ser .pdbqt")
            else:
                receptor_pdbqt = outputs_dir / "prepared" / f"{receptor_input.stem}.pdbqt"
                ligand_pdbqt = outputs_dir / "prepared" / f"{ligand_input.stem}.pdbqt"
                if receptor_input.suffix.lower() == ".pdb":
                    prepare_receptor(receptor_input, receptor_pdbqt, mgl_root)
                else:
                    receptor_pdbqt = receptor_input
                if ligand_input.suffix.lower() == ".pdb":
                    prepare_ligand(ligand_input, ligand_pdbqt, mgl_root)
                else:
                    ligand_pdbqt = ligand_input

            vina_raw = tools_cfg.get("vina_executable", "")
            vina_path = _as_abs(vina_raw) if vina_raw else None

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

            flash(f"Docking completado: {output_pdbqt.name}", "success")
            return redirect(url_for("index"))
        except Exception as exc:
            flash(f"Error en docking: {exc}", "error")
            return redirect(url_for("index"))

    return render_template("index.html")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mini app web para ejecutar AutoDock Vina")
    parser.add_argument("--host", default="127.0.0.1", help="Host del servidor Flask")
    parser.add_argument("--port", type=int, default=5000, help="Puerto del servidor Flask")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=False)

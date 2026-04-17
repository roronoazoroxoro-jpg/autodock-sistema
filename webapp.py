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
import json
import logging
import os
from datetime import datetime
from io import BytesIO
from pathlib import Path

from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename

from main import _as_abs
from scripts.common import ensure_dir, load_config
from scripts.prepare_ligand import prepare_ligand
from scripts.prepare_receptor import prepare_receptor
from scripts.run_vina import run_vina

ALLOWED_EXTENSIONS = {".pdb", ".pdbqt"}
HISTORY_FILE = _as_abs("data/web_history.json")
MAX_HISTORY = 30
CHECKLIST_KEYS = (
    "check_inputs",
    "check_grid",
    "check_interpretation",
)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "autodock-mvp-secret")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


def _allowed(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _parse_vina_results(output_pdbqt: Path) -> list[dict[str, float | int]]:
    """Extrae la tabla de resultados desde lineas 'REMARK VINA RESULT' del PDBQT."""
    rows: list[dict[str, float | int]] = []
    if not output_pdbqt.exists():
        return rows

    with output_pdbqt.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.startswith("REMARK VINA RESULT:"):
                continue
            parts = line.split()
            if len(parts) < 6:
                continue
            try:
                rows.append(
                    {
                        "mode": len(rows) + 1,
                        "affinity": float(parts[3]),
                        "rmsd_lb": float(parts[4]),
                        "rmsd_ub": float(parts[5]),
                    }
                )
            except ValueError:
                continue

    return rows


def _best_pose_text(output_pdbqt: Path) -> str:
    """Devuelve el bloque MODEL 1 para visualizacion 3D sencilla."""
    if not output_pdbqt.exists():
        return ""

    lines = output_pdbqt.read_text(encoding="utf-8", errors="ignore").splitlines()
    model_lines: list[str] = []
    in_model_1 = False
    for line in lines:
        if line.startswith("MODEL"):
            in_model_1 = line.strip().split()[-1] == "1"
        if in_model_1:
            model_lines.append(line)
        if in_model_1 and line.startswith("ENDMDL"):
            break
    return "\n".join(model_lines)


def _extract_pose_models(output_pdbqt: Path) -> list[str]:
    """Extrae cada bloque MODEL n ... ENDMDL para selector de poses."""
    if not output_pdbqt.exists():
        return []

    lines = output_pdbqt.read_text(encoding="utf-8", errors="ignore").splitlines()
    models: list[str] = []
    collecting = False
    current: list[str] = []

    for line in lines:
        if line.startswith("MODEL"):
            collecting = True
            current = [line]
            continue
        if collecting:
            current.append(line)
            if line.startswith("ENDMDL"):
                models.append("\n".join(current))
                collecting = False
                current = []

    return models


def _load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def _save_history(records: list[dict]) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(records[:MAX_HISTORY], ensure_ascii=True, indent=2), encoding="utf-8")


def _clear_history() -> None:
    _save_history([])


def _append_history(record: dict) -> list[dict]:
    records = _load_history()
    records.insert(0, record)
    _save_history(records)
    return records[:MAX_HISTORY]


def _summary_rows(result_rows: list[dict[str, float | int]]) -> dict[str, float | int] | None:
    if not result_rows:
        return None
    best = min(result_rows, key=lambda row: float(row["affinity"]))
    return {
        "best_mode": best["mode"],
        "best_affinity": float(best["affinity"]),
        "num_modes": len(result_rows),
    }


def _ligand_ranking(records: list[dict]) -> list[dict[str, float | str]]:
    """Agrupa historial por ligando y deja mejor afinidad por ligando."""
    best_by_ligand: dict[str, float] = {}
    for item in records:
        if item.get("mode") != "docking":
            continue
        ligand = str(item.get("ligand", "")).strip()
        affinity = item.get("best_affinity")
        if not ligand or affinity is None:
            continue
        try:
            affinity_value = float(affinity)
        except (TypeError, ValueError):
            continue

        current_best = best_by_ligand.get(ligand)
        if current_best is None or affinity_value < current_best:
            best_by_ligand[ligand] = affinity_value

    ranking = [
        {"ligand": ligand, "best_affinity": affinity}
        for ligand, affinity in best_by_ligand.items()
    ]
    ranking.sort(key=lambda row: float(row["best_affinity"]))
    return ranking


def _clinical_assessment(result_rows: list[dict[str, float | int]]) -> dict[str, str | float | list[str]] | None:
    """Genera interpretacion clinico-tecnica orientativa a partir de afinidades/RMSD."""
    if not result_rows:
        return None

    best = min(result_rows, key=lambda row: float(row["affinity"]))
    best_aff = float(best["affinity"])

    if best_aff <= -8.0:
        level = "alta"
        headline = "Senal favorable de union"
        guidance = "Priorizar validacion experimental temprana y revision estructural detallada."
        level_color = "verde"
    elif best_aff <= -6.0:
        level = "media"
        headline = "Senal intermedia de union"
        guidance = "Repetir docking con ajustes de grid/exhaustiveness y comparar con controles."
        level_color = "amarillo"
    else:
        level = "baja"
        headline = "Senal debil de union"
        guidance = "Considerar otro ligando o redefinir sitio de busqueda antes de decisiones."
        level_color = "rojo"

    mode1 = next((row for row in result_rows if int(row["mode"]) == 1), result_rows[0])
    mode2 = next((row for row in result_rows if int(row["mode"]) == 2), None)
    delta12 = abs(float(mode1["affinity"]) - float(mode2["affinity"])) if mode2 else 0.0
    consistency = (
        "Consistencia aceptable entre las dos primeras poses."
        if delta12 <= 0.5
        else "Diferencia amplia entre pose 1 y 2: revisar estabilidad del resultado."
    )

    quality_score = max(0.0, min(100.0, 100.0 - (best_aff + 10.0) * 9.0 - delta12 * 8.0))

    return {
        "level": level,
        "headline": headline,
        "best_affinity": best_aff,
        "delta12": delta12,
        "consistency": consistency,
        "guidance": guidance,
        "quality_score": quality_score,
        "level_color": level_color,
        "notes": [
            "Interpretacion orientativa; no sustituye validacion experimental.",
            "Confirmar interacciones en visor 3D y, de ser posible, con replicados.",
        ],
    }


def _records_for_case(records: list[dict], case_id: str) -> list[dict]:
    if not case_id:
        return records
    needle = case_id.strip().lower()
    return [item for item in records if str(item.get("case_id", "")).strip().lower() == needle]


def _build_report_text(records: list[dict]) -> str:
    docking_items = [item for item in records if item.get("mode") == "docking"]
    lines = [
        "Reporte Clinico-Tecnico AutoDock Vina",
        f"Fecha de generacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Resumen de corridas (mas recientes primero):",
    ]

    if not docking_items:
        lines.append("- No hay corridas de docking registradas.")
    else:
        for item in docking_items[:20]:
            lines.append(
                "- {timestamp} | caso={case_id} | receptor={receptor} | ligando={ligand} | afinidad={affinity} | salida={output}".format(
                    timestamp=item.get("timestamp", ""),
                    case_id=item.get("case_id", "N/A"),
                    receptor=item.get("receptor", ""),
                    ligand=item.get("ligand", ""),
                    affinity=item.get("best_affinity", "-"),
                    output=item.get("output", "-"),
                )
            )

    lines.append("")
    lines.append("Ranking por ligando (mejor afinidad):")
    ranking = _ligand_ranking(records)
    if not ranking:
        lines.append("- Sin datos de ranking.")
    else:
        for idx, row in enumerate(ranking[:20], start=1):
            lines.append(f"{idx}. {row['ligand']} -> {row['best_affinity']:.4f} kcal/mol")

    lines.append("")
    lines.append("Nota: afinidad mas negativa suele indicar mejor union teorica.")
    return "\n".join(lines)


def _build_report_html(records: list[dict], case_id: str = "") -> str:
        filtered = _records_for_case(records, case_id)
        title_suffix = f" - Caso {case_id}" if case_id else ""
        rows = []
        for item in filtered[:30]:
                rows.append(
                        "<tr>"
                        f"<td>{item.get('timestamp', '')}</td>"
                        f"<td>{item.get('case_id', '-')}</td>"
                        f"<td>{item.get('mode', '')}</td>"
                        f"<td>{item.get('receptor', '')}</td>"
                        f"<td>{item.get('ligand', '')}</td>"
                        f"<td>{item.get('best_affinity', '-')}</td>"
                        f"<td>{item.get('output', '-')}</td>"
                        "</tr>"
                )
        if not rows:
                rows.append('<tr><td colspan="7">Sin corridas registradas para el criterio seleccionado.</td></tr>')

        ranking = _ligand_ranking(filtered)
        ranking_rows = []
        for idx, item in enumerate(ranking[:20], start=1):
                ranking_rows.append(
                        "<tr>"
                        f"<td>{idx}</td>"
                        f"<td>{item['ligand']}</td>"
                        f"<td>{item['best_affinity']:.4f}</td>"
                        "</tr>"
                )
        if not ranking_rows:
                ranking_rows.append('<tr><td colspan="3">Sin ranking disponible.</td></tr>')

        return f"""
<!doctype html>
<html lang=\"es\">
<head>
    <meta charset=\"utf-8\">
    <title>Reporte Clinico-Tecnico{title_suffix}</title>
    <style>
        body {{ font-family: Segoe UI, Arial, sans-serif; margin: 26px; color: #142524; }}
        h1 {{ margin: 0 0 6px; color: #14544f; }}
        h2 {{ margin: 18px 0 8px; color: #1d3a37; }}
        p.meta {{ margin: 0 0 8px; color: #496160; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 8px; font-size: 13px; }}
        th, td {{ border: 1px solid #cfe1db; padding: 6px; text-align: left; }}
        th {{ background: #eff8f5; }}
        .note {{ margin-top: 14px; font-size: 12px; color: #4b5d5b; }}
    </style>
</head>
<body>
    <h1>Reporte Clinico-Tecnico AutoDock Vina{title_suffix}</h1>
    <p class=\"meta\">Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <h2>Corridas registradas</h2>
    <table>
        <thead>
            <tr>
                <th>Fecha</th><th>Caso</th><th>Operacion</th><th>Receptor</th><th>Ligando</th><th>Mejor afinidad</th><th>Salida</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    <h2>Ranking de ligandos (mejor afinidad historica)</h2>
    <table>
        <thead><tr><th>#</th><th>Ligando</th><th>Mejor afinidad</th></tr></thead>
        <tbody>{''.join(ranking_rows)}</tbody>
    </table>
    <p class=\"note\">Nota: este reporte es orientativo y debe validarse con criterio profesional y evidencia experimental.</p>
</body>
</html>
"""


def _build_report_json(records: list[dict], case_id: str = "") -> dict:
        filtered = _records_for_case(records, case_id)
        return {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "case_filter": case_id,
                "total_records": len(filtered),
                "ranking": _ligand_ranking(filtered),
                "records": filtered,
        }


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

    success_message: str | None = None
    error_message: str | None = None
    result_rows: list[dict[str, float | int]] = []
    summary: dict[str, float | int] | None = None
    output_filename: str | None = None
    receptor_text: str = ""
    docked_text: str = ""
    case_id_value: str = ""
    clinical_goal_value: str = ""
    run_mode_value: str = "dock"
    skip_prepare_value = False
    checklist_state = {key: False for key in CHECKLIST_KEYS}
    history_records = _load_history()
    pose_models: list[str] = []
    ligand_ranking = _ligand_ranking(history_records)
    clinical_assessment: dict[str, str | float | list[str]] | None = None

    if request.method == "POST":
        action = request.form.get("action", "run")
        if action == "clear_history":
            _clear_history()
            success_message = "Historial limpiado correctamente"
            history_records = []
            ligand_ranking = []
            return render_template(
                "index.html",
                success_message=success_message,
                error_message=error_message,
                result_rows=result_rows,
                summary=summary,
                output_filename=output_filename,
                receptor_text=receptor_text,
                docked_text=docked_text,
                history_records=history_records,
                pose_models=pose_models,
                ligand_ranking=ligand_ranking,
                clinical_assessment=clinical_assessment,
                case_id_value=case_id_value,
                clinical_goal_value=clinical_goal_value,
                run_mode_value=run_mode_value,
                skip_prepare_value=skip_prepare_value,
                checklist_state=checklist_state,
            )

        receptor = request.files.get("receptor")
        ligand = request.files.get("ligand")
        skip_prepare = request.form.get("skip_prepare") == "on"
        run_mode = request.form.get("run_mode", "dock")
        run_mode_value = run_mode
        skip_prepare_value = skip_prepare
        case_id_value = (request.form.get("case_id") or "").strip()
        clinical_goal_value = (request.form.get("clinical_goal") or "").strip()
        checklist_state = {key: request.form.get(key) == "on" for key in CHECKLIST_KEYS}

        if run_mode == "dock" and not all(checklist_state.values()):
            error_message = "Antes de ejecutar docking completo, confirma todos los checks de seguridad clinica."
            return render_template(
                "index.html",
                success_message=success_message,
                error_message=error_message,
                result_rows=result_rows,
                summary=summary,
                output_filename=output_filename,
                receptor_text=receptor_text,
                docked_text=docked_text,
                history_records=history_records,
                pose_models=pose_models,
                ligand_ranking=ligand_ranking,
                clinical_assessment=clinical_assessment,
                case_id_value=case_id_value,
                clinical_goal_value=clinical_goal_value,
                run_mode_value=run_mode_value,
                skip_prepare_value=skip_prepare_value,
                checklist_state=checklist_state,
            )

        if not receptor or not ligand:
            error_message = "Debes subir receptor y ligando"
            return render_template(
                "index.html",
                success_message=success_message,
                error_message=error_message,
                result_rows=result_rows,
                summary=summary,
                output_filename=output_filename,
                receptor_text=receptor_text,
                docked_text=docked_text,
                history_records=history_records,
                pose_models=pose_models,
                ligand_ranking=ligand_ranking,
                clinical_assessment=clinical_assessment,
                case_id_value=case_id_value,
                clinical_goal_value=clinical_goal_value,
                run_mode_value=run_mode_value,
                skip_prepare_value=skip_prepare_value,
                checklist_state=checklist_state,
            )

        rec_name = secure_filename(receptor.filename or "")
        lig_name = secure_filename(ligand.filename or "")
        if not rec_name or not lig_name or not _allowed(rec_name) or not _allowed(lig_name):
            error_message = "Formatos permitidos: .pdb o .pdbqt"
            return render_template(
                "index.html",
                success_message=success_message,
                error_message=error_message,
                result_rows=result_rows,
                summary=summary,
                output_filename=output_filename,
                receptor_text=receptor_text,
                docked_text=docked_text,
                history_records=history_records,
                pose_models=pose_models,
                ligand_ranking=ligand_ranking,
                clinical_assessment=clinical_assessment,
                case_id_value=case_id_value,
                clinical_goal_value=clinical_goal_value,
                run_mode_value=run_mode_value,
                skip_prepare_value=skip_prepare_value,
                checklist_state=checklist_state,
            )

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

            if run_mode == "prepare":
                success_message = (
                    f"Preparacion completada. Receptor: {receptor_pdbqt.name} | "
                    f"Ligando: {ligand_pdbqt.name}"
                )
                history_records = _append_history(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "mode": "preparacion",
                        "case_id": case_id_value,
                        "clinical_goal": clinical_goal_value,
                        "receptor": receptor_input.name,
                        "ligand": ligand_input.name,
                        "output": "",
                        "best_affinity": None,
                    }
                )
                return render_template(
                    "index.html",
                    success_message=success_message,
                    error_message=error_message,
                    result_rows=result_rows,
                    summary=summary,
                    output_filename=output_filename,
                    receptor_text=receptor_text,
                    docked_text=docked_text,
                    history_records=history_records,
                    pose_models=pose_models,
                    ligand_ranking=ligand_ranking,
                    clinical_assessment=clinical_assessment,
                    case_id_value=case_id_value,
                    clinical_goal_value=clinical_goal_value,
                    run_mode_value=run_mode_value,
                    skip_prepare_value=skip_prepare_value,
                    checklist_state=checklist_state,
                )

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

            success_message = f"Docking completado: {output_pdbqt.name}"
            result_rows = _parse_vina_results(output_pdbqt)
            summary = _summary_rows(result_rows)
            clinical_assessment = _clinical_assessment(result_rows)
            output_filename = output_pdbqt.name
            receptor_text = receptor_pdbqt.read_text(encoding="utf-8", errors="ignore")
            docked_text = _best_pose_text(output_pdbqt)
            pose_models = _extract_pose_models(output_pdbqt)
            history_records = _append_history(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "mode": "docking",
                    "case_id": case_id_value,
                    "clinical_goal": clinical_goal_value,
                    "receptor": receptor_input.name,
                    "ligand": ligand_input.name,
                    "output": output_pdbqt.name,
                    "best_affinity": summary["best_affinity"] if summary else None,
                }
            )
            ligand_ranking = _ligand_ranking(history_records)
            return render_template(
                "index.html",
                success_message=success_message,
                error_message=error_message,
                result_rows=result_rows,
                summary=summary,
                output_filename=output_filename,
                receptor_text=receptor_text,
                docked_text=docked_text,
                history_records=history_records,
                pose_models=pose_models,
                ligand_ranking=ligand_ranking,
                clinical_assessment=clinical_assessment,
                case_id_value=case_id_value,
                clinical_goal_value=clinical_goal_value,
                run_mode_value=run_mode_value,
                skip_prepare_value=skip_prepare_value,
                checklist_state=checklist_state,
            )
        except Exception as exc:
            error_message = f"Error en docking: {exc}"
            return render_template(
                "index.html",
                success_message=success_message,
                error_message=error_message,
                result_rows=result_rows,
                summary=summary,
                output_filename=output_filename,
                receptor_text=receptor_text,
                docked_text=docked_text,
                history_records=history_records,
                pose_models=pose_models,
                ligand_ranking=ligand_ranking,
                clinical_assessment=clinical_assessment,
                case_id_value=case_id_value,
                clinical_goal_value=clinical_goal_value,
                run_mode_value=run_mode_value,
                skip_prepare_value=skip_prepare_value,
                checklist_state=checklist_state,
            )

    return render_template(
        "index.html",
        success_message=success_message,
        error_message=error_message,
        result_rows=result_rows,
        summary=summary,
        output_filename=output_filename,
        receptor_text=receptor_text,
        docked_text=docked_text,
        history_records=history_records,
        pose_models=pose_models,
        ligand_ranking=ligand_ranking,
        clinical_assessment=clinical_assessment,
        case_id_value=case_id_value,
        clinical_goal_value=clinical_goal_value,
        run_mode_value=run_mode_value,
        skip_prepare_value=skip_prepare_value,
        checklist_state=checklist_state,
    )


@app.get("/report/latest")
def download_latest_report():
    records = _load_history()
    case_id = (request.args.get("case") or "").strip()
    report_text = _build_report_text(_records_for_case(records, case_id))
    report_bytes = report_text.encode("utf-8")
    suffix = f"_{case_id}" if case_id else ""
    filename = f"reporte_docking{suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    return send_file(
        BytesIO(report_bytes),
        mimetype="text/plain; charset=utf-8",
        as_attachment=True,
        download_name=filename,
    )


@app.get("/report/latest/html")
def download_latest_report_html():
    records = _load_history()
    case_id = (request.args.get("case") or "").strip()
    report_html = _build_report_html(records, case_id)
    report_bytes = report_html.encode("utf-8")
    suffix = f"_{case_id}" if case_id else ""
    filename = f"reporte_docking{suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    return send_file(
        BytesIO(report_bytes),
        mimetype="text/html; charset=utf-8",
        as_attachment=True,
        download_name=filename,
    )


@app.get("/report/latest/json")
def download_latest_report_json():
    records = _load_history()
    case_id = (request.args.get("case") or "").strip()
    payload = _build_report_json(records, case_id)
    report_bytes = json.dumps(payload, ensure_ascii=True, indent=2).encode("utf-8")
    suffix = f"_{case_id}" if case_id else ""
    filename = f"reporte_docking{suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return send_file(
        BytesIO(report_bytes),
        mimetype="application/json",
        as_attachment=True,
        download_name=filename,
    )


@app.get("/dashboard_data")
def dashboard_data():
    """Retorna estadísticas agregadas del historial para visualización en dashboard."""
    records = _load_history()
    docking_records = [r for r in records if r.get("mode") == "docking"]
    
    # Total de dockings y estadísticas generales
    total_dockings = len(docking_records)
    affinities = [r.get("best_affinity") for r in docking_records if r.get("best_affinity") is not None]
    avg_affinity = sum(affinities) / len(affinities) if affinities else 0.0
    best_affinity = min(affinities) if affinities else 0.0
    worst_affinity = max(affinities) if affinities else 0.0
    
    # Distribución de niveles clínicos
    level_counts = {"alta": 0, "media": 0, "baja": 0}
    for rec in docking_records:
        best_aff = rec.get("best_affinity")
        if best_aff is None:
            continue
        if best_aff <= -8.0:
            level_counts["alta"] += 1
        elif best_aff <= -6.0:
            level_counts["media"] += 1
        else:
            level_counts["baja"] += 1
    
    # Top 5 ligandos por afinidad
    ligand_scores = {}
    for rec in docking_records:
        ligand = rec.get("ligand", "unknown")
        affinity = rec.get("best_affinity")
        if affinity is not None:
            if ligand not in ligand_scores or affinity < ligand_scores[ligand]:
                ligand_scores[ligand] = affinity
    
    top_ligands = sorted(ligand_scores.items(), key=lambda x: x[1])[:5]
    
    # Timeline de últimos 10 dockings (para gráfica de tendencia)
    recent_dockings = sorted(docking_records, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
    recent_dockings_sorted = sorted(recent_dockings, key=lambda x: x.get("timestamp", ""))
    
    timeline_labels = []
    timeline_affinities = []
    for rec in recent_dockings_sorted:
        ts = rec.get("timestamp", "")
        if ts:
            # Extraer solo la hora (HH:MM)
            time_part = ts.split(" ")[1] if " " in ts else ts
            timeline_labels.append(time_part)
        aff = rec.get("best_affinity", 0)
        timeline_affinities.append(aff if aff is not None else 0.0)
    
    # Evolución por fecha (primeras 10 fechas únicas)
    date_affinities = {}
    for rec in docking_records:
        ts = rec.get("timestamp", "")
        aff = rec.get("best_affinity")
        if ts and aff is not None:
            date_part = ts.split(" ")[0]  # YYYY-MM-DD
            if date_part not in date_affinities:
                date_affinities[date_part] = []
            date_affinities[date_part].append(aff)
    
    date_labels = sorted(date_affinities.keys())[-10:]
    date_avg_affinities = [
        sum(date_affinities[d]) / len(date_affinities[d]) 
        for d in date_labels
    ]
    
    return jsonify({
        "total_dockings": total_dockings,
        "avg_affinity": round(avg_affinity, 3),
        "best_affinity": round(best_affinity, 3),
        "worst_affinity": round(worst_affinity, 3),
        "level_distribution": level_counts,
        "top_ligands": [{"name": name, "affinity": round(aff, 3)} for name, aff in top_ligands],
        "timeline": {
            "labels": timeline_labels,
            "affinities": [round(a, 3) for a in timeline_affinities]
        },
        "date_evolution": {
            "dates": date_labels,
            "avg_affinities": [round(a, 3) for a in date_avg_affinities]
        }
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mini app web para ejecutar AutoDock Vina")
    parser.add_argument("--host", default="127.0.0.1", help="Host del servidor Flask")
    parser.add_argument("--port", type=int, default=5000, help="Puerto del servidor Flask")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=False)

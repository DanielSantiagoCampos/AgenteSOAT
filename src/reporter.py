# src/reporter.py
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from .config import REPORTS_DIR


def build_markdown_report(
    instruction: str,
    rag_evidence: List[Dict],
    explanation_text: str,
    calc_result: Dict[str, Any] | None,
    global_stats: Dict[str, Any] | None,
    logs: List[str],
) -> Path:
    """
    Construye un reporte en formato Markdown con:
      - Instrucción del usuario
      - Explicación generada por el LLM
      - Evidencia RAG (fragmentos del manual)
      - Cálculo individual (cuando aplica)
      - Estadísticas generales del dataset
      - Trazabilidad (logs)
    """

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"reporte_soat_{ts}.md"

    # Evidencia RAG
    if rag_evidence:
        refs_lines = []
        for i, ev in enumerate(rag_evidence, 1):
            refs_lines.append(
                f"- [Fuente {i}] {ev['doc_id']} (chunk {ev['chunk_id']}) — {ev['source_path']}"
            )
        refs_block = "\n".join(refs_lines)
    else:
        refs_block = "_No se encontró evidencia documental relevante._"

    # Cálculo individual
    if calc_result is not None:
        calc_block = "\n".join(f"{k}: {v}" for k, v in calc_result.items())
    else:
        calc_block = "No se realizó un cálculo individual de póliza."

    # Estadísticas
    if global_stats is not None:
        stats_por_tipo = global_stats.get("stats_por_tipo")
        porcentaje = global_stats.get("porcentaje_con_siniestros")
        stats_block = f"{stats_por_tipo}\n\nPorcentaje con siniestros: {porcentaje:.2f} %"
    else:
        stats_block = "No se calcularon estadísticas globales."

    # Logs
    if logs:
        log_block = "\n".join(f"- {line}" for line in logs)
    else:
        log_block = "_Sin trazabilidad registrada._"

    # Markdown final
    content = f"""# Reporte del Agente SOAT

**Fecha:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 1. Instrucción del usuario

> {instruction}

---

## 2. Explicación del agente (Razón + Evidencia)

{explanation_text}

---

## 3. Evidencia documental recuperada (RAG)

{refs_block}

---

## 4. Resultado de cálculo individual (DEBUG)

```text
{calc_block}
```

---

## 5. Estadísticas generales del dataset (DEBUG)

```text
{stats_block}
```

---

## 6. Trazabilidad del agente (acciones ejecutadas)

```text
{log_block}
```

---

_Reporte generado automáticamente por el Agente Cognitivo SOAT_
"""

    report_path.write_text(content, encoding="utf-8")
    return report_path

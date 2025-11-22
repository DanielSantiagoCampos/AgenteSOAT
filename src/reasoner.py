# src/reasoner.py
from typing import List, Dict, Any
import ollama

from .config import OLLAMA_MODEL

# aca es donde le pasamos 
def build_evidence_text(rag_evidence: List[Dict]) -> str:
    text = ""
    for i, ev in enumerate(rag_evidence, 1):
        snippet = ev["text"].replace("\n", " ")
        text += f"[Fuente {i} - {ev['doc_id']}]: {snippet[:500]}...\n\n"
    return text

def explain_soat_calculation(
    instruction: str,
    calc_result: Dict[str, Any] | None,
    global_stats: Dict[str, Any] | None,
    rag_evidence: List[Dict],
) -> str:
    evidence_text = build_evidence_text(rag_evidence)

    calc_text = "No se realizó un cálculo específico por placa."
    if calc_result and "error" not in calc_result:
        calc_text = f"""
Placa: {calc_result['placa']}
Tipo de vehículo: {calc_result['tipo_vehiculo']}
Cilindraje: {calc_result['cilindraje']}
Edad conductor: {calc_result['edad_conductor']}
Siniestros 12m: {calc_result['numero_siniestros_12m']}
Zona de riesgo: {calc_result['zona_riesgo']}

Tarifa base: {calc_result['tarifa_base']:,} COP
Factor edad: {calc_result['factor_edad']}
Factor siniestros: {calc_result['factor_siniestros']}
Factor zona: {calc_result['factor_zona']}
Factor historial: {calc_result['factor_historial']}

Valor estimado del SOAT: {calc_result['valor_estimado']:,} COP
Valor actual en dataset: {calc_result['valor_soat_actual']:,} COP
"""

    stats_text = ""
    if global_stats is not None:
        stats_por_tipo = global_stats["stats_por_tipo"]
        porcentaje = global_stats["porcentaje_con_siniestros"]
        stats_text = f"""
Resumen portafolio (por tipo de vehículo):
{stats_por_tipo}

Porcentaje de vehículos con al menos un siniestro en 12 meses: {porcentaje:.2f}%
"""

    user_prompt = f"""
Instrucción original del usuario:
{instruction}

Evidencia del manual de tarifas SOAT:
{evidence_text}

Resultados del cálculo individual (si aplica):
{calc_text}

Estadísticas generales (si se solicitaron):
{stats_text}

Redacta un informe en español, claro y técnico, explicando:
- Cómo se calculó el valor del SOAT para la placa (si aplica),
- Qué factores de riesgo influyeron (edad, siniestros, zona, historial),
- Cómo se relaciona el cálculo con las reglas del manual,
- Un breve análisis del portafolio si hay estadísticas generales.

Usa referencias del tipo [Fuente i - nombre_doc] cuando te apoyes en el manual.
No inventes cifras adicionales que no estén en los datos.
"""

    resp = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": "Eres un analista de seguros que explica cálculos de SOAT basados en reglas documentadas."},
            {"role": "user", "content": user_prompt},
        ],
    )
    return resp["message"]["content"]

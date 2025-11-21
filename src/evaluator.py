from pathlib import Path


def simple_evaluate_report(report_path: Path) -> dict:
    """
    Evalúa de forma muy básica la estructura del reporte:
    - presencia de secciones clave
    - longitud del contenido
    """
    text = report_path.read_text(encoding="utf-8")
    score = 0
    feedback = []

    # Chequeo de secciones esperadas
    if "## 2. Explicación del agente" in text:
        score += 1
    if "## 3. Evidencia documental (RAG)" in text:
        score += 1
    if "## 4. Resultado de cálculo individual (debug)" in text:
        score += 1
    if "## 5. Estadísticas generales (debug)" in text:
        score += 1
    if "## 6. Trazabilidad de acciones" in text:
        score += 1

    # Comentario sobre longitud
    if len(text) < 800:
        feedback.append(
            "El reporte es relativamente corto; podrías ampliar la explicación o el análisis."
        )
    else:
        feedback.append("La longitud del reporte es adecuada para la sustentación.")

    return {"score": score, "feedback": feedback}
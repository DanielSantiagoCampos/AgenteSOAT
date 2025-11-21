# main.py
from src.planner import plan_from_instruction
from src.retriever import KnowledgeBase
from src.executor import (
    ExecutionContext,
    load_dataset,
    calcular_nueva_poliza_para_placa,
    estadisticas_generales,
)
from src.reasoner import explain_soat_calculation
from src.reporter import build_markdown_report
from src.evaluator import simple_evaluate_report


def print_banner() -> None:
    print("=" * 70)
    print("        Agente Cognitivo SOAT - Proyecto Final Aplicación a la IA")
    print("=" * 70)


def main() -> None:
    print_banner()

    # 1) Leer instrucción del usuario
    instruction = input("Escribe la instrucción para el agente:")

    # 2) Planner: generar plan de acciones usando Ollama
    actions = plan_from_instruction(instruction)
    print(f"[1/6] Plan generado ({len(actions)} acciones):")
    for a in actions:
        print(f"  - {a['id']}: {a['type']} | params={a.get('params', {})}")

    # 3) RAG: indexar documentación y recuperar evidencia relevante
    print("[2/6] Indexando documentación SOAT...")
    kb = KnowledgeBase()
    kb.index_documents()

    print("[2/6] Recuperando evidencia relevante del manual de tarifas...")
    rag_evidence = kb.retrieve(instruction, top_k=5)

    # 4) Executor: ejecutar acciones sobre el dataset
    print("[3/6] Ejecutando plan sobre el dataset de vehículos SOAT...")
    ctx = ExecutionContext()
    calc_result = None
    global_stats = None

    for action in actions:
        t = action.get("type")
        params = action.get("params", {}) or {}

        if t == "load_dataset":
            load_dataset(ctx)
        elif t == "calc_for_plate":
            placa = params.get("placa")
            if placa:
                calc_result = calcular_nueva_poliza_para_placa(ctx, placa)
            else:
                ctx.log("[WARN] Acción calc_for_plate sin 'placa' en params.")
        elif t == "global_stats":
            global_stats = estadisticas_generales(ctx)
        else:
            ctx.log(f"[WARN] Acción no soportada: {t}")

    # 5) Reasoner: explicación en lenguaje natural usando Ollama
    print("[4/6] Generando explicación del agente con el modelo de lenguaje...")
    explanation = explain_soat_calculation(
        instruction=instruction,
        calc_result=calc_result,
        global_stats=global_stats,
        rag_evidence=rag_evidence,
    )

    # 6) Reporter: generar reporte en Markdown
    print("[5/6] Construyendo reporte en Markdown...")
    report_path = build_markdown_report(
        instruction=instruction,
        rag_evidence=rag_evidence,
        explanation_text=explanation,
        calc_result=calc_result,
        global_stats=global_stats,
        logs=ctx.logs,
    )
    print(f"[OK] Reporte generado en: {report_path}")

    # 7) Evaluator: evaluación básica de calidad del reporte
    print("[6/6] Evaluando calidad básica del reporte generado...")
    eval_result = simple_evaluate_report(report_path)
    print(f"Puntaje del reporte: {eval_result['score']}/5")
    print("Feedback:")
    for f in eval_result["feedback"]:
        print(f"- {f}")


if __name__ == "__main__":
    main()

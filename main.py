# main.py
from src.config import REPORTS_DIR
# from src.utils import print_banner if False else None  # opcional si quieres utils.py

from src.planner import plan_from_instruction
from src.retriever import KnowledgeBase
from src.executor import ExecutionContext, load_dataset, calcular_nueva_poliza_para_placa, estadisticas_generales
from src.reasoner import explain_soat_calculation
from src.reporter import build_markdown_report
from src.evaluator import simple_evaluate_report

def main():
    print("=" * 60)
    print("      Agente Cognitivo SOAT - Proyecto Final IA")
    print("=" * 60)

    instruction = input("Escribe la instrucción para el agente:\n> ")

    # 1) Planner
    actions = plan_from_instruction(instruction)
    print(f"\n[1/6] Plan generado ({len(actions)} acciones):")
    for a in actions:
        print(f"- {a['id']}: {a['type']}")

    # 2) RAG
    print("\n[2/6] Indexando documentación SOAT...")
    kb = KnowledgeBase()
    kb.index_documents()
    print("[2/6] Recuperando evidencia relevante del manual...")
    rag_evidence = kb.retrieve(instruction, top_k=5)

    # 3) Ejecutar acciones
    print("\n[3/6] Ejecutando plan sobre datos...")
    ctx = ExecutionContext()
    calc_result = None
    global_stats = None

    for action in actions:
        t = action["type"]
        params = action.get("params", {})

        if t == "load_dataset":
            load_dataset(ctx)
        elif t == "calc_for_plate":
            placa = params["placa"]
            calc_result = calcular_nueva_poliza_para_placa(ctx, placa)
        elif t == "global_stats":
            global_stats = estadisticas_generales(ctx)
        else:
            ctx.log(f"[WARN] Acción no soportada: {t}")

    # 4) Reasoner
    print("\n[4/6] Generando explicación con el modelo de lenguaje...")
    explanation = explain_soat_calculation(
        instruction=instruction,
        calc_result=calc_result,
        global_stats=global_stats,
        rag_evidence=rag_evidence,
    )

    # 5) Reporte
    print("\n[5/6] Generando reporte en Markdown...")
    report_path = build_markdown_report(
        instruction=instruction,
        rag_evidence=rag_evidence,
        explanation_text=explanation,
        calc_result=calc_result,
        global_stats=global_stats,
        logs=ctx.logs,
    )
    print(f"Reporte generado en: {report_path}")

    # 6) Evaluación
    print("\n[6/6] Evaluando calidad básica del reporte...")
    result = simple_evaluate_report(report_path)
    print(f"Puntaje: {result['score']}/5")
    print("Feedback:")
    for f in result["feedback"]:
        print(f"- {f}")

if __name__ == "__main__":
    main()

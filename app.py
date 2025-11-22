import random
import streamlit as st
from pathlib import Path

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

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


def md_to_pdf(md_path: Path) -> Path:
    """
    Convierte un archivo .md sencillo a PDF y devuelve la ruta del PDF.
    """
    pdf_path = md_path.with_suffix(".pdf")
    text = md_path.read_text(encoding="utf-8")

    styles = getSampleStyleSheet()
    story = []

    for line in text.split("\n"):
        if line.startswith("# "):
            story.append(Paragraph(f"<b>{line[2:]}</b>", styles["Title"]))
            story.append(Spacer(1, 12))
        elif line.startswith("## "):
            story.append(Paragraph(f"<b>{line[3:]}</b>", styles["Heading2"]))
            story.append(Spacer(1, 10))
        elif line.startswith("### "):
            story.append(Paragraph(f"<b>{line[4:]}</b>", styles["Heading3"]))
            story.append(Spacer(1, 8))
        else:
            safe_line = line.replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe_line, styles["BodyText"]))
            story.append(Spacer(1, 6))

    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    doc.build(story)
    return pdf_path


def run_agent_once(instruction: str):
    """
    Ejecuta TODO el pipeline del agente SOAT para una instrucción dada
    y devuelve un dict con:
      - explanation
      - report_path_md
      - report_path_pdf
      - calc_result
      - global_stats
      - eval_result
    """

    # 1) Planner
    actions = plan_from_instruction(instruction)

    # 2) RAG: documentación SOAT
    kb = KnowledgeBase()
    kb.index_documents()
    # Aca es donde generamos el json para el ollama con la info del pdf
    rag_evidence = kb.retrieve(instruction, top_k=5)

    # 3) Executor: dataset + acciones
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

    # 4) Reasoner: explicación con LLM
    explanation = explain_soat_calculation(
        instruction=instruction,
        calc_result=calc_result,
        global_stats=global_stats,
        rag_evidence=rag_evidence,
    )

    # 5) Reporter: generar reporte en Markdown
    report_path_md = build_markdown_report(
        instruction=instruction,
        rag_evidence=rag_evidence,
        explanation_text=explanation,
        calc_result=calc_result,
        global_stats=global_stats,
        logs=ctx.logs,
    )

    # 6) Convertir a PDF
    report_path_pdf = md_to_pdf(Path(report_path_md))

    # 7) Evaluator
    eval_result = simple_evaluate_report(Path(report_path_md))

    return {
        "explanation": explanation,
        "report_path_md": str(report_path_md),
        "report_path_pdf": str(report_path_pdf),
        "calc_result": calc_result,
        "global_stats": global_stats,
        "eval_result": eval_result,
    }


# -----------------------
# Interfaz Streamlit tipo chat
# -----------------------

SALUDOS_RESPUESTAS = [
    (
        "👋 ¡Hola! Soy el agente SOAT.\n\n"
        "Puedo ayudarte con cosas como:\n"
        "- Calcular el valor del SOAT para una placa y explicarlo según el manual.\n"
        "- Analizar el archivo de vehículos SOAT y darte estadísticas por tipo de vehículo.\n"
    ),
    (
        "🙌 ¡Hey! Aquí el agente SOAT reportándose.\n\n"
        "Prueba algo como:\n"
        "- Calcula el SOAT para la placa DJK890.\n"
        "- Analiza el portafolio completo y dame insights.\n"
    ),
    (
        "🚗 ¡Bienvenido al asistente SOAT!\n\n"
        "Puedes pedirme, por ejemplo:\n"
        "- Explica el cálculo del SOAT de una placa específica.\n"
        "- Muéstrame estadísticas de siniestros por tipo de vehículo.\n"
    ),
    (
        "👋 ¡Qué se dice! Soy tu agente cognitivo SOAT.\n\n"
        "Ejemplos de cosas que sé hacer:\n"
        "- Estimar el nuevo valor del SOAT según edad, siniestros y zona.\n"
        "- Generar un reporte del portafolio con soporte en el manual de tarifas.\n"
    ),
]

st.set_page_config(page_title="Agente SOAT", page_icon="🚗")

st.title("🚗 Agente Cognitivo SOAT")
st.markdown(
    "Asistente para cálculo de pólizas SOAT y análisis de portafolio, "
    "basado en RAG + reglas del Manual de Tarifas."
)

# Inicializar historial de chat en session_state
if "messages" not in st.session_state:
    st.session_state.messages = []  # cada mensaje: {"role": "user"/"assistant", "content": "texto"}

if "last_report_pdf" not in st.session_state:
    st.session_state.last_report_pdf = None

# Mostrar historial
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# Input tipo chat
user_input = st.chat_input("Escribe tu instrucción sobre SOAT...")

if user_input:
    # 1) Añadir mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2) Mostrarlo de inmediato
    with st.chat_message("user"):
        st.markdown(user_input)

    # Normalizamos texto
    texto = user_input.strip().lower()

    # 3) Si solo es un saludo, respondemos rápido sin pipeline pesado
    saludos_simples = {
        "hola",
        "holi",
        "buenas",
        "buenos días",
        "buenas tardes",
        "buenas noches",
        "que se dice",
        "qué se dice",
    }

    if texto in saludos_simples:
        respuesta = random.choice(SALUDOS_RESPUESTAS)

        with st.chat_message("assistant"):
            st.markdown(respuesta)

        st.session_state.messages.append(
            {"role": "assistant", "content": respuesta}
        )

    else:
        # 4) Ejecutar agente completo solo para consultas "serias"
        with st.chat_message("assistant"):
            with st.spinner("Procesando con el agente SOAT..."):
                try:
                    result = run_agent_once(user_input)

                    explanation = result["explanation"]
                    report_path_md = result["report_path_md"]
                    report_path_pdf = result["report_path_pdf"]
                    eval_result = result["eval_result"]

                    # Guardamos la ruta del último PDF para permitir descarga
                    st.session_state.last_report_pdf = report_path_pdf

                    respuesta = explanation
                    respuesta += "\n\n---\n"
                    respuesta += f"_He generado un reporte detallado en:_ `{report_path_md}`\n"
                    respuesta += f"_Versión en PDF:_ `{report_path_pdf}`\n"
                    respuesta += f"_Puntaje interno del reporte:_ **{eval_result['score']}/5**"

                    st.markdown(respuesta)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": respuesta}
                    )

                except Exception as e:
                    error_msg = f"Ocurrió un error al ejecutar el agente: `{e}`"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

# Si hay un último PDF, mostramos botón de descarga global
if st.session_state.last_report_pdf:
    pdf_path = Path(st.session_state.last_report_pdf)
    if pdf_path.exists():
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="📄 Descargar último reporte en PDF",
            data=pdf_bytes,
            file_name=pdf_path.name,
            mime="application/pdf",
        )

# src/planner.py
import json
import re
from typing import List, Dict, Any, Optional

import ollama

from .config import OLLAMA_MODEL


PLANNER_SYSTEM_PROMPT = """Eres el módulo de PLANIFICACIÓN de un agente cognitivo
para análisis de pólizas SOAT en Colombia.

Tu tarea es:
- Leer la instrucción del usuario (en español, lenguaje natural).
- Diseñar un PLAN de acciones estructurado.
- Devolver ÚNICAMENTE un JSON VÁLIDO con el siguiente formato:

{
  "actions": [
    {
      "id": "a1",
      "type": "load_dataset",
      "params": {}
    },
    {
      "id": "a2",
      "type": "calc_for_plate",
      "params": {"placa": "ABC123"}
    },
    {
      "id": "a3",
      "type": "global_stats",
      "params": {}
    }
  ]
}

Acciones disponibles (type):

1) "load_dataset"
   - Debe ser la PRIMERA acción siempre que se vaya a trabajar con datos.
   - params: { }

2) "calc_for_plate"
   - Cálculo de la nueva póliza SOAT para una placa específica.
   - params:
       {
         "placa": "ABC123"
       }
   - Úsala cuando el usuario mencione una placa o pida cálculo para un vehículo concreto.

3) "global_stats"
   - Análisis estadístico general del dataset de vehículos SOAT.
   - params: { }
   - Úsala cuando el usuario pida cosas como:
     "analiza el archivo", "estadísticas", "porcentaje con siniestros",
     "promedio por tipo de vehículo", etc.

REGLAS IMPORTANTES:
- Siempre responde ÚNICAMENTE con el JSON, sin texto adicional.
- Si la instrucción menciona una placa (ej: ABC123), incluye una acción "calc_for_plate" con esa placa.
- Si el usuario pide análisis global, incluye también una acción "global_stats".
- Si no estás seguro, al menos incluye:
  [
    {"id": "a1", "type": "load_dataset", "params": {}}
  ]
- La clave raíz SIEMPRE debe ser "actions" con una lista.
"""


def _extract_plate_regex(text: str) -> Optional[str]:
    """Extrae una placa tipo ABC123 (tres letras + tres dígitos) si existe en el texto."""
    match = re.search(r"\b([A-Z]{3}\d{3})\b", text.upper())
    if match:
        return match.group(1)
    return None


def plan_from_instruction(instruction: str) -> List[Dict[str, Any]]:
    """Genera un plan de acciones usando un modelo local de Ollama.

    Intenta parsear la respuesta como JSON. Si falla,
    usa un plan de respaldo basado en reglas simples.
    """
    # 1) Intento con LLM (Ollama)
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": instruction},
            ],
        )
        content = response["message"]["content"].strip()

        # A veces el modelo puede envolver el JSON con texto, intentamos aislarlo
        # Buscamos el primer y último corchete/llave coherentes
        # Simple intento: si empieza con ```json, limpiamos eso
        if content.startswith("```"):
            # Eliminar fences tipo ```json ... ```
            content = content.strip("`").strip()
            # En algunos casos queda algo como 'json{...}' → eliminamos 'json' si está pegado
            if content.lower().startswith("json"):
                content = content[4:].strip()

        data = json.loads(content)
        actions = data.get("actions", [])
        # Validación básica
        if not isinstance(actions, list):
            raise ValueError("'actions' no es una lista")

        if not actions:
            raise ValueError("Lista de acciones vacía")

        return actions

    except Exception as e:
        print(f"[WARN] Planner LLM falló o devolvió JSON inválido: {e}")
        print("[INFO] Usando planner de respaldo basado en reglas.")

    # 2) Fallback rule-based simple
    actions: List[Dict[str, Any]] = []

    # Siempre cargar dataset
    actions.append({"id": "a1", "type": "load_dataset", "params": {}})

    lower = instruction.lower()
    placa = _extract_plate_regex(instruction)

    # Si menciona placa, cálculo individual
    if placa:
        actions.append({
            "id": "a2",
            "type": "calc_for_plate",
            "params": {"placa": placa}
        })

    # Si pide analizar, estadísticas, etc.
    keywords_stats = ["analiza", "analizar", "estadística", "estadisticas", "promedio", "porcentaje"]
    if any(k in lower for k in keywords_stats):
        actions.append({
            "id": "a3",
            "type": "global_stats",
            "params": {}
        })

    # Si solo dijo algo muy genérico, al menos dejamos load_dataset
    return actions

# 🧠 Agente Cognitivo SOAT – Proyecto Final Inteligencia Artificial

**Universidad Cooperativa de Colombia – 2025-2**  
**Curso: Aplicación a la Inteligencia Artificial**  
**Estudiantes:**

- Daniel Santiago Campos Piñeros
- Juan Camilo Devia
- Diego Insuno

---

## 📌 1. Resumen Ejecutivo

Este proyecto implementa un **Agente Cognitivo Autónomo** capaz de:

- Interpretar instrucciones en lenguaje natural.
- Recuperar información del **Manual de Tarifas SOAT** (RAG).
- Procesar un dataset de vehículos y conductores.
- Calcular el valor estimado de una póliza SOAT.
- Generar reportes técnicos con evidencia citada.
- Justificar acciones según normatividad y reglas explícitas.

---

## 🧩 2. Arquitectura del Agente Cognitivo

El agente sigue el ciclo:

**Percepción → Planificación → Acción → Razonamiento → Reporte → Evaluación**

### Módulos

| Módulo      | Archivo            | Función                                                        |
| ----------- | ------------------ | -------------------------------------------------------------- |
| Planner     | `src/planner.py`   | Interpreta la instrucción y genera un plan JSON usando Ollama. |
| Retriever   | `src/retriever.py` | Indexa manual PDF y recupera evidencia (RAG).                  |
| Executor    | `src/executor.py`  | Carga dataset, ejecuta cálculos y estadísticas.                |
| Reasoner    | `src/reasoner.py`  | Produce explicación textual basada en evidencia.               |
| Reporter    | `src/reporter.py`  | Crea reporte en Markdown.                                      |
| Evaluator   | `src/evaluator.py` | Evalúa calidad estructural del reporte.                        |
| Orquestador | `main.py`          | Flujo general del agente.                                      |

---

## 📂 3. Estructura del Proyecto

```
SOAT/
├─ main.py
├─ src/
│  ├─ config.py
│  ├─ planner.py
│  ├─ retriever.py
│  ├─ executor.py
│  ├─ reasoner.py
│  ├─ reporter.py
│  ├─ evaluator.py
├─ data/
│  ├─ docs/
│  └─ datasets/
└─ outputs/
   ├─ reports/
   └─ logs/
```

---

## ⚙️ 4. Instalación

```bash
conda activate aplicacionia
pip install pandas scikit-learn matplotlib pdfplumber ollama

pip install reportlab
pip install streamlit

streamlit run app.py
```

Check the http://localhost:8501/

Verificar que Ollama está instalado:

```bash
ollama --version
ollama list
```

Configurar en `src/config.py`:

```python
OLLAMA_MODEL = "llama3.1:8b"
```

---

## ▶️ 5. Ejecución del Agente

```bash
python main.py
```

---

## 💬 6. Ejemplos de Uso

### 🔹 Ejemplo 1 – Cálculo SOAT por placa

```
Calcula el valor del SOAT para la placa DJK890 y explícalo según el manual.
```

### 🔹 Ejemplo 2 – Análisis global

```
Analiza el archivo de vehículos SOAT y dame estadísticas por tipo de vehículo.
```

### 🔹 Ejemplo 3 – Combinado

```
Dime el valor estimado del SOAT para la placa CWZ161 y analiza el portafolio completo.
```

---

## 📊 7. Dataset

Dataset ficticio con 50 registros:

- placa
- tipo_vehiculo
- cilindraje
- edad_conductor
- siniestros
- zona_riesgo
- valor_soat_actual
- fecha_vencimiento

---

## 📘 8. Documento de Conocimiento (RAG)

El archivo:

```
data/docs/Manual_Tarifas_SOAT_2025_Completo.pdf
```

se utiliza para recuperar evidencia textual relevante usando TF-IDF.

---

## 🧪 9. Pruebas recomendadas (placas del dataset)

- DJK890
- CWZ161
- ZSP221
- RHL980
- GKW218
- HPL765

Ejemplo:

```
Explícame el cálculo del SOAT para la placa RHL980.
```

---

## 📝 10. Conclusiones

El agente implementa exitosamente:

- Razonamiento asistido por modelos locales.
- Integración de RAG con normativa de seguros.
- Automatización completa de análisis y reporte.
- Arquitectura clara y modular.

---

# ✔️ Fin del README

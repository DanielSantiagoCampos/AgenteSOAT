# src/executor.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd

from .config import DATASETS_DIR
from .business_rules import calcular_soat_estimado

@dataclass
class ExecutionContext:
    dataset: Optional[pd.DataFrame] = None
    dataset_path: Optional[Path] = None
    artifacts: list = field(default_factory=list)
    logs: list = field(default_factory=list)

    def log(self, msg: str):
        print(msg)
        self.logs.append(msg)

def load_dataset(ctx: ExecutionContext, filename: str = "vehiculos_soat.csv"):
    path = DATASETS_DIR / filename
    ctx.dataset = pd.read_csv(path)
    ctx.dataset_path = path
    ctx.log(f"Dataset cargado desde: {path}")

def buscar_por_placa(ctx: ExecutionContext, placa: str) -> Optional[pd.Series]:
    if ctx.dataset is None:
        raise RuntimeError("Dataset no cargado.")
    fila = ctx.dataset[ctx.dataset["placa"] == placa]
    if fila.empty:
        ctx.log(f"No se encontró la placa {placa} en el dataset.")
        return None
    ctx.log(f"Se encontró registro para la placa {placa}.")
    return fila.iloc[0]

def calcular_nueva_poliza_para_placa(ctx: ExecutionContext, placa: str) -> Dict[str, Any]:
    registro = buscar_por_placa(ctx, placa)
    if registro is None:
        return {"error": f"No se encontró la placa {placa}."}

    tipo = registro["tipo_vehiculo"]
    cil = int(registro["cilindraje"])
    edad = int(registro["edad_conductor"])
    n_sin = int(registro["numero_siniestros_12m"])
    zona = registro["zona_riesgo"]
    anios = int(registro["anios_sin_siniestros"])

    resultado = calcular_soat_estimado(
        tipo_vehiculo=tipo,
        cilindraje=cil,
        edad_conductor=edad,
        numero_siniestros_12m=n_sin,
        zona_riesgo=zona,
        anios_sin_siniestros=anios,
    )

    ctx.log(
        f"Cálculo nueva póliza para {placa}: "
        f"base={resultado['tarifa_base']}, "
        f"estimado={resultado['valor_estimado']}"
    )

    resultado["placa"] = placa
    resultado["tipo_vehiculo"] = tipo
    resultado["cilindraje"] = cil
    resultado["edad_conductor"] = edad
    resultado["numero_siniestros_12m"] = n_sin
    resultado["zona_riesgo"] = zona
    resultado["anios_sin_siniestros"] = anios
    resultado["valor_soat_actual"] = int(registro["valor_soat_actual"])

    return resultado

def estadisticas_generales(ctx: ExecutionContext) -> Dict[str, Any]:
    if ctx.dataset is None:
        raise RuntimeError("Dataset no cargado.")
    df = ctx.dataset

    stats_por_tipo = df.groupby("tipo_vehiculo")["valor_soat_actual"].agg(["count", "mean", "min", "max"])
    porcentaje_con_siniestros = (df[df["numero_siniestros_12m"] > 0].shape[0] / len(df)) * 100

    ctx.log("Calculadas estadísticas generales del portafolio SOAT.")
    return {
        "stats_por_tipo": stats_por_tipo,
        "porcentaje_con_siniestros": porcentaje_con_siniestros,
    }

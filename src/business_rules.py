# src/business_rules.py
from math import ceil

def tarifa_base(tipo_vehiculo: str, cilindraje: int) -> int:
    if tipo_vehiculo == "auto_particular":
        return 600_000
    if tipo_vehiculo == "taxi":
        return 750_000
    if tipo_vehiculo == "bus":
        return 900_000
    if tipo_vehiculo == "camion":
        return 1_000_000
    if tipo_vehiculo == "moto":
        if cilindraje < 100:
            return 400_000
        elif 100 <= cilindraje <= 200:
            return 500_000
        else:
            return 600_000
    # fallback
    return 600_000

def factor_edad(edad: int) -> float:
    if edad < 25:
        return 1.20
    if edad <= 60:
        return 1.00
    return 1.10

def factor_siniestros(numero_siniestros_12m: int) -> float:
    if numero_siniestros_12m == 0:
        return 1.00
    if numero_siniestros_12m == 1:
        return 1.10
    if numero_siniestros_12m == 2:
        return 1.25
    return 1.50  # 3 o más

def factor_zona(zona_riesgo: str) -> float:
    mapping = {"baja": 0.95, "media": 1.00, "alta": 1.15}
    return mapping.get(zona_riesgo, 1.00)

def factor_historial(anios_sin_siniestros: int) -> float:
    if anios_sin_siniestros <= 0:
        return 1.00
    if anios_sin_siniestros == 1:
        return 0.98
    if anios_sin_siniestros == 2:
        return 0.96
    return 0.93  # 3 o más

def calcular_soat_estimado(
    tipo_vehiculo: str,
    cilindraje: int,
    edad_conductor: int,
    numero_siniestros_12m: int,
    zona_riesgo: str,
    anios_sin_siniestros: int,
) -> dict:
    """
    Devuelve un dict con:
    - valor_estimado
    - tarifa_base
    - factores individuales
    - valor_bruto (antes de límites)
    - limites aplicados
    """
    base = tarifa_base(tipo_vehiculo, cilindraje)
    f_edad = factor_edad(edad_conductor)
    f_sin = factor_siniestros(numero_siniestros_12m)
    f_zona = factor_zona(zona_riesgo)
    f_hist = factor_historial(anios_sin_siniestros)

    bruto = base * f_edad * f_sin * f_zona * f_hist

    minimo = base * 0.7
    maximo = base * 2.5

    ajustado = max(minimo, min(maximo, bruto))
    estimado = int(ceil(ajustado / 1000.0) * 1000)

    return {
        "valor_estimado": estimado,
        "tarifa_base": base,
        "factor_edad": f_edad,
        "factor_siniestros": f_sin,
        "factor_zona": f_zona,
        "factor_historial": f_hist,
        "valor_bruto": bruto,
        "limite_min": minimo,
        "limite_max": maximo,
        "valor_ajustado": ajustado,
    }

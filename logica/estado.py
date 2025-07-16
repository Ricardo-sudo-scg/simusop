import json
import os

def cargar_parametros_y_estado():
    with open("data/parametros.json", "r", encoding="utf-8") as f:
        params = json.load(f)

    estado_inicial = {
        "inventario": 200,
        "n": 5,
        "kP": 0, "kA": 0, "kE": 0,
        "acum_mkt": 0,
        "acum_ops": 0,
        "historico": [],
        "utilidad": 0.0
    }

    T = 12  # <<--- AÑADE ESTA LÍNEA
    return params, estado_inicial, T
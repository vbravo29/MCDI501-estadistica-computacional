"""Funciones y constantes comunes de la Sumativa 2.

Todos los notebooks de S2 importan este módulo para usar la misma semilla, el mismo
número de remuestras, las mismas rutas y los resultados de referencia de la Sumativa 1.

Uso desde un notebook ubicado en S2/:

    from utils_s2 import *
    df = cargar_datos()
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

# ---------------------------------------------------------------------------
# Parámetros globales (no cambiar sin avisar al equipo)
# ---------------------------------------------------------------------------
SEED = 42          # semilla común para toda la S2
B = 10_000         # remuestras bootstrap, permutaciones e iteraciones Monte Carlo
ALPHA = 0.05       # nivel de significancia (mismo de la S1)

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
S2 = RAIZ / "S2"
FIG = S2 / "figuras"
TAB = S2 / "tablas"
FIG.mkdir(exist_ok=True)
TAB.mkdir(exist_ok=True)

COLORES = {
    "principal": "#4C72B0",
    "riesgo": "#C44E52",
    "mediana": "#55A868",
    "caja": "#8DA0CB",
    "ic": "#55A868",
    "clasico": "#4C72B0",
    "percentil": "#DD8452",
    "bca": "#55A868",
}

NOMBRES = {
    "age": "Edad (años)", "cigsPerDay": "Cigarrillos por día",
    "totChol": "Colesterol total (mg/dL)", "sysBP": "Presión sistólica (mmHg)",
    "diaBP": "Presión diastólica (mmHg)", "BMI": "IMC (kg/m²)",
    "heartRate": "Frecuencia cardíaca (lpm)", "glucose": "Glucosa (mg/dL)",
}
NUM = list(NOMBRES)

# ---------------------------------------------------------------------------
# Resultados de la Sumativa 1 que se validan en la S2 (informe S1, tablas 4 y 5,
# sección 2.2 y sección 4). Citar siempre estos valores al comparar.
# ---------------------------------------------------------------------------
RESULTADOS_S1 = {
    # Tabla 5: estimaciones puntuales e IC 95 %
    "ic": {
        "edad_media":       {"variable": "age",        "estimacion": 49.58,  "ic": (49.32, 49.84),   "n": 4240, "metodo": "t de Student"},
        "sysbp_media":      {"variable": "sysBP",      "estimacion": 132.35, "ic": (131.69, 133.02), "n": 4240, "metodo": "t de Student"},
        "colesterol_media": {"variable": "totChol",    "estimacion": 236.70, "ic": (235.35, 238.05), "n": 4190, "metodo": "t de Student"},
        "prop_chd_%":       {"variable": "TenYearCHD", "estimacion": 15.19,  "ic": (14.14, 16.30),   "n": 4240, "metodo": "Wilson"},
    },
    # Tabla 4: diferencia de medias (con CHD - sin CHD), IC de Welch
    "diferencias": {
        "age":       {"dif": 5.38,  "ic": (4.71, 6.06),   "g": 0.64},
        "cigsPerDay": {"dif": 1.86, "ic": (0.78, 2.94),   "g": 0.16},
        "totChol":   {"dif": 10.24, "ic": (6.23, 14.25),  "g": 0.23},
        "sysBP":     {"dif": 13.28, "ic": (11.11, 15.45), "g": 0.62},
        "diaBP":     {"dif": 4.81,  "ic": (3.67, 5.96),   "g": 0.41},
        "BMI":       {"dif": 0.86,  "ic": (0.48, 1.24),   "g": 0.21},
        "heartRate": {"dif": 0.77,  "ic": (-0.26, 1.79),  "g": 0.06},
        "glucose":   {"dif": 8.33,  "ic": (4.95, 11.71),  "g": 0.35},
    },
    # Sección 4: pruebas de hipótesis
    "pruebas": {
        "sysbp_chd": {"prueba": "t de Welch", "estadistico": 12.01, "gl": 783.8, "p": "< 0,001",
                      "media_con_chd": 143.62, "media_sin_chd": 130.34, "dif": 13.28},
        "fumar_chd": {"prueba": "chi-cuadrado con Yates", "estadistico": 1.50, "gl": 1, "p": 0.221,
                      "tasa_fumadores_%": 15.9, "tasa_no_fumadores_%": 14.5, "v_cramer": 0.019},
    },
    # Sección 2.2: correlaciones de Spearman destacadas
    "correlaciones": {
        ("sysBP", "diaBP"): 0.78,
        ("age", "sysBP"): 0.39,
        ("BMI", "diaBP"): 0.37,
    },
    # Tasas por grupo (Figura 4 de la S1), útiles para Monte Carlo
    "tasas_chd_%": {
        "global": 15.19,
        "hombres": 18.8, "mujeres": 12.4,
        "hipertension": 24.7, "sin_hipertension": 10.9,
        "diabetes": 36.7, "sin_diabetes": 14.6,
    },
    "prevalencias_%": {"hipertension": 31.1, "diabetes": 2.6, "fumadores": 49.4, "hombres": 42.9},
}


# ---------------------------------------------------------------------------
# Datos, figuras y tablas
# ---------------------------------------------------------------------------
def cargar_datos(limpio: bool = True) -> pd.DataFrame:
    """Carga el dataset de la S1 (por defecto la versión limpia, con cigsPerDay imputado)."""
    archivo = "framingham_limpio.csv" if limpio else "framingham.csv"
    return pd.read_csv(DATA / archivo)


def configurar_graficos() -> None:
    """Mismo estilo de gráficos que la S1."""
    sns.set_theme(style="whitegrid", context="notebook")
    pd.set_option("display.float_format", lambda x: f"{x:,.4f}")


def guardar_figura(nombre: str) -> None:
    """Guarda la figura actual en S2/figuras/<nombre>.png y la muestra.

    Convención de nombre: pX_figN_descripcion (X = parte de la pauta).
    """
    plt.tight_layout()
    plt.savefig(FIG / f"{nombre}.png", dpi=200, bbox_inches="tight")
    plt.show()


def guardar_tabla(tabla: pd.DataFrame, nombre: str) -> pd.DataFrame:
    """Guarda una tabla resumen en S2/tablas/<nombre>.csv y la devuelve para mostrarla."""
    tabla.to_csv(TAB / f"{nombre}.csv", index=True)
    return tabla


# ---------------------------------------------------------------------------
# Remuestreo y simulación
# ---------------------------------------------------------------------------
def ic_bootstrap(muestras, estadistico, metodo: str = "BCa", n_resamples: int = B,
                 confianza: float = 0.95, paired: bool = False, vectorized: bool = True,
                 seed: int = SEED):
    """IC bootstrap no paramétrico con scipy.stats.bootstrap.

    muestras: tupla de arreglos, por ejemplo (x,) para un parámetro de una muestra,
        (x_con_chd, x_sin_chd) para una diferencia entre grupos, o (x, y) con
        paired=True para una correlación (se remuestrean filas completas).
    estadistico: función que recibe los arreglos y un argumento `axis` (por ejemplo np.mean).
        Si la función no acepta `axis` (por ejemplo una correlación de Spearman),
        usar vectorized=False.
    metodo: "percentile", "basic" o "BCa".

    Devuelve (inferior, superior, distribucion_bootstrap). Con la misma semilla,
    los métodos percentil y BCa usan exactamente las mismas remuestras.
    """
    muestras = tuple(np.asarray(m, dtype=float) for m in muestras)
    res = stats.bootstrap(muestras, estadistico, n_resamples=n_resamples,
                          confidence_level=confianza, method=metodo, paired=paired,
                          vectorized=vectorized, random_state=np.random.default_rng(seed))
    return res.confidence_interval.low, res.confidence_interval.high, res.bootstrap_distribution


def p_valor_permutacion(observado: float, nula: np.ndarray, alternativa: str = "dos-colas") -> float:
    """Valor p de permutación con la corrección (k + 1) / (B + 1).

    Con B = 10.000 el menor valor p posible es 1/10.001 ≈ 0,0001, por lo que un
    resultado así debe informarse como "p < 0,001" o "p ≤ 1/(B+1)".
    """
    nula = np.asarray(nula)
    if alternativa == "dos-colas":
        k = np.sum(np.abs(nula) >= abs(observado))
    elif alternativa == "mayor":
        k = np.sum(nula >= observado)
    else:
        k = np.sum(nula <= observado)
    return (k + 1) / (len(nula) + 1)


def jackknife(x, estadistico):
    """Jackknife leave-one-out de un estadístico de una muestra.

    Devuelve un dict con la estimación, el sesgo, el error estándar y los valores
    leave-one-out (útiles para calcular la influencia de cada observación).
    """
    x = np.asarray(x, dtype=float)
    n = len(x)
    theta = estadistico(x)
    loo = np.array([estadistico(np.delete(x, i)) for i in range(n)])
    media_loo = loo.mean()
    sesgo = (n - 1) * (media_loo - theta)
    ee = np.sqrt((n - 1) / n * np.sum((loo - media_loo) ** 2))
    return {"estimacion": theta, "sesgo": sesgo, "ee": ee, "loo": loo,
            "influencia": (n - 1) * (media_loo - loo)}


def media_acumulada(valores) -> pd.DataFrame:
    """Media acumulada y su error estándar Monte Carlo, para graficar la convergencia."""
    v = np.asarray(valores, dtype=float)
    k = np.arange(1, len(v) + 1)
    media = np.cumsum(v) / k
    var = (np.cumsum(v ** 2) - k * media ** 2) / np.maximum(k - 1, 1)
    ee = np.sqrt(np.maximum(var, 0) / k)
    return pd.DataFrame({"iteracion": k, "media": media, "ee": ee})

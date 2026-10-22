"""Funciones y datos comunes de la Sumativa 3.

Uso típico en los notebooks:

    df = cargar_datos()
    train, test = particionar(df)
    train_i, test_i = imputar(train, test, "simple")   # o "eliminacion" / "regresion"
    X_train, X_test, y_train, y_test = preparar_modelo(train_i, test_i, variables)

La partición se hace antes de imputar y los imputadores se ajustan solo con entrenamiento, para evitar
fuga de información (comentario del profesor en la S1).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split

SEED = 42
B = 10_000
TEST_SIZE = 0.30
ALPHA = 0.05
OBJETIVO = "TenYearCHD"

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"
S3 = RAIZ / "S3"
FIG = S3 / "figuras"
TAB = S3 / "tablas"
FIG.mkdir(exist_ok=True)
TAB.mkdir(exist_ok=True)

COLORES = {"principal": "#4C72B0", "riesgo": "#C44E52", "neutro": "#8C8C8C", "ic": "#55A868",
           "eliminacion": "#8C8C8C", "simple": "#DD8452", "regresion": "#4C72B0"}

NOMBRES = {
    "age": "Edad (años)", "male": "Sexo masculino", "education": "Nivel educativo",
    "currentSmoker": "Fumador actual", "cigsPerDay": "Cigarrillos por día", "BPMeds": "Antihipertensivos",
    "prevalentStroke": "ACV previo", "prevalentHyp": "Hipertensión", "diabetes": "Diabetes",
    "totChol": "Colesterol total (mg/dL)", "sysBP": "Presión sistólica (mmHg)",
    "diaBP": "Presión diastólica (mmHg)", "BMI": "IMC (kg/m²)", "heartRate": "Frecuencia cardíaca (lpm)",
    "glucose": "Glucosa (mg/dL)",
}
NUMERICAS = ["age", "cigsPerDay", "totChol", "sysBP", "diaBP", "BMI", "heartRate", "glucose"]
BINARIAS = ["male", "currentSmoker", "BPMeds", "prevalentStroke", "prevalentHyp", "diabetes"]
ORDINALES = ["education"]
PREDICTORES = NUMERICAS + BINARIAS + ORDINALES

# numéricas con faltantes en los datos originales (se imputan por regresión en la parte 1)
NUMERICAS_CON_FALTANTES = ["glucose", "totChol", "cigsPerDay", "BMI", "heartRate"]

# resultados de la S1 y la S2 que se usan para justificar las decisiones de la S3
HALLAZGOS = {
    "S1": {
        "n": 4240,
        "tasa_chd_%": 15.19,
        "faltantes": {"glucose": (388, 9.15), "education": (105, 2.48), "BPMeds": (53, 1.25),
                      "totChol": (50, 1.18), "cigsPerDay": (29, 0.68), "BMI": (19, 0.45), "heartRate": (1, 0.02)},
        "filas_con_faltantes": (582, 13.7),
        "cigsPerDay": "29 faltantes, todos en fumadores; la S1 los imputó con la mediana de fumadores (20)",
        "outliers": "atípicos de Tukey en el extremo superior de las variables clínicas (colesterol 696 mg/dL, "
                    "glucosa 394 mg/dL); la S1 los conservó por ser clínicamente posibles",
        "diferencias_g": {"age": 0.64, "sysBP": 0.62, "diaBP": 0.41, "glucose": 0.35, "totChol": 0.23,
                          "BMI": 0.21, "cigsPerDay": 0.16, "heartRate": 0.06},
        "tasas_chd_%": {"hombres": 18.8, "mujeres": 12.4, "hipertension": 24.7, "sin_hipertension": 10.9,
                        "diabetes": 36.7, "sin_diabetes": 14.6, "fumadores": 15.9, "no_fumadores": 14.5},
    },
    "S2": {
        "correlaciones_estables": {("sysBP", "diaBP"): (0.778, 0.763, 0.791), ("age", "sysBP"): (0.391, 0.365, 0.417),
                                   ("BMI", "diaBP"): (0.375, 0.348, 0.401)},
        "correlaciones_inestables": {("totChol", "glucose"): (0.030, -0.002, 0.061)},
        "ic_bca_dif_sysBP": (11.14, 15.60),
        "ic_bca_dif_glucose": (5.32, 12.16),
        "glucosa_sin_atipicos": "la diferencia según CHD baja de 8,33 a 0,83 mg/dL y deja de ser significativa",
        "glucosa_segun_diabetes": "mediana de 145 mg/dL en diabéticos frente a 78 en no diabéticos",
        "imputacion_glucosa": "imputar con la mediana reduce la DE de 23,95 a 22,86 y casi no cambia la diferencia",
        "tabaquismo_ajustado_edad": "diferencia MH de 4,64 pp; p de permutación < 0,001",
        "vif_sysBP_diaBP": (3.11, 2.85),
        "recomendaciones": [
            "métricas para la clase minoritaria (15,2 % de CHD)",
            "imputar dentro de la validación, ajustando solo con datos de entrenamiento",
            "incluir solo una de las presiones: se mantiene la sistólica",
            "estimar tabaquismo e hipertensión ajustados por edad",
            "no sacar conclusiones en subgrupos pequeños (diabetes n = 109, ACV n = 25)",
        ],
    },
}


def cargar_datos() -> pd.DataFrame:
    """Datos originales de Kaggle, con todos sus faltantes (la S3 decide cómo tratarlos)."""
    return pd.read_csv(DATA / "framingham.csv")


def configurar_graficos() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    pd.set_option("display.float_format", lambda x: f"{x:,.4f}")


def guardar_figura(nombre: str) -> None:
    """Guarda la figura actual en S3/figuras/<nombre>.png y la muestra."""
    plt.tight_layout()
    plt.savefig(FIG / f"{nombre}.png", dpi=200, bbox_inches="tight")
    plt.show()


def guardar_tabla(tabla: pd.DataFrame, nombre: str) -> pd.DataFrame:
    """Guarda una tabla en S3/tablas/<nombre>.csv y la devuelve para mostrarla."""
    tabla.to_csv(TAB / f"{nombre}.csv", index=True)
    return tabla


def particionar(df: pd.DataFrame):
    """Partición 70/30 estratificada por TenYearCHD, con semilla fija."""
    return train_test_split(df, test_size=TEST_SIZE, stratify=df[OBJETIVO], random_state=SEED)


def imputar_simple(train: pd.DataFrame, test: pd.DataFrame):
    """Mediana para numéricas y moda para binarias y ordinales, calculadas solo en entrenamiento."""
    train, test = train.copy(), test.copy()
    for v in NUMERICAS:
        valor = train[v].median()
        train[v], test[v] = train[v].fillna(valor), test[v].fillna(valor)
    for v in BINARIAS + ORDINALES:
        valor = train[v].mode().iloc[0]
        train[v], test[v] = train[v].fillna(valor), test[v].fillna(valor)
    return train, test


def imputar_regresion(train: pd.DataFrame, test: pd.DataFrame):
    """Imputación por regresión lineal múltiple (parte 1).

    Para cada variable de NUMERICAS_CON_FALTANTES se ajusta un modelo con 3 a 5 predictores elegidos con
    la matriz de correlaciones de la S1 y las correlaciones estables de la S2, usando solo filas completas
    del conjunto de entrenamiento, y se predicen los faltantes de entrenamiento y prueba. Las binarias y
    ordinales se imputan con la moda de entrenamiento.
    """
    raise NotImplementedError("La implementa la parte 1 en 01_imputacion.ipynb y la copia aquí.")


def imputar(train: pd.DataFrame, test: pd.DataFrame, estrategia: str):
    """Aplica una de las tres estrategias: 'eliminacion', 'simple' o 'regresion'."""
    if estrategia == "eliminacion":
        return train.dropna(), test.dropna()
    if estrategia == "simple":
        return imputar_simple(train, test)
    if estrategia == "regresion":
        return imputar_regresion(train, test)
    raise ValueError(f"Estrategia desconocida: {estrategia}")


def preparar_modelo(train: pd.DataFrame, test: pd.DataFrame, variables, recortar=None):
    """Matrices de diseño para la regresión logística.

    variables: predictores del modelo. Las numéricas se estandarizan con la media y DE de
        entrenamiento; las binarias quedan en 0/1. Si se incluye `education`, se codifica con
        variables indicadoras (categoría de referencia: 1).
    recortar: dict opcional {variable: (percentil_inf, percentil_sup)} para winsorizar outliers con
        límites calculados en entrenamiento (la decisión se justifica en la parte 2).
    """
    variables = list(variables)
    train, test = train.copy(), test.copy()
    for v, (p_inf, p_sup) in (recortar or {}).items():
        inf, sup = np.percentile(train[v].dropna(), [p_inf, p_sup])
        train[v], test[v] = train[v].clip(inf, sup), test[v].clip(inf, sup)
    X_train, X_test = train[variables].astype(float), test[variables].astype(float)
    numericas = [v for v in variables if v in NUMERICAS]
    media, de = X_train[numericas].mean(), X_train[numericas].std(ddof=0)
    X_train[numericas] = (X_train[numericas] - media) / de
    X_test[numericas] = (X_test[numericas] - media) / de
    if "education" in variables:
        X_train = pd.get_dummies(X_train, columns=["education"], prefix="edu", drop_first=True, dtype=float)
        X_test = pd.get_dummies(X_test, columns=["education"], prefix="edu", drop_first=True, dtype=float)
        X_test = X_test.reindex(columns=X_train.columns, fill_value=0.0)
    return X_train, X_test, train[OBJETIVO].astype(int), test[OBJETIVO].astype(int)

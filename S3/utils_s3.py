"""Funciones compartidas por las partes 1 y 4 de la Sumativa 3.

Alcance deliberado: tratamiento de faltantes y comparacion del impacto de las
estrategias. Este modulo no realiza seleccion de variables ni bootstrap del
modelo logistico, que corresponden a otras partes del trabajo grupal.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from scipy.stats import jarque_bera
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor


SEMILLA = 42
SEED = SEMILLA
B = 10_000
TEST_SIZE = 0.30
ALPHA = 0.05
OBJETIVO = "TenYearCHD"
RAIZ = Path(__file__).resolve().parents[1]
RUTA_DATOS = RAIZ / "data" / "framingham.csv"
DATA = RAIZ / "data"
S3 = RAIZ / "S3"
FIG = S3 / "figuras"
TAB = S3 / "tablas"

COLORES = {
    "principal": "#4C72B0", "riesgo": "#C44E52", "neutro": "#8C8C8C",
    "ic": "#55A868", "eliminacion": "#8C8C8C", "simple": "#DD8452",
    "regresion": "#4C72B0",
}
NOMBRES = {
    "age": "Edad (años)", "male": "Sexo masculino", "education": "Nivel educativo",
    "currentSmoker": "Fumador actual", "cigsPerDay": "Cigarrillos por día",
    "BPMeds": "Antihipertensivos", "prevalentStroke": "ACV previo",
    "prevalentHyp": "Hipertensión", "diabetes": "Diabetes",
    "totChol": "Colesterol total (mg/dL)", "sysBP": "Presión sistólica (mmHg)",
    "diaBP": "Presión diastólica (mmHg)", "BMI": "IMC (kg/m²)",
    "heartRate": "Frecuencia cardíaca (lpm)", "glucose": "Glucosa (mg/dL)",
}
NUMERICAS = ["age", "cigsPerDay", "totChol", "sysBP", "diaBP", "BMI", "heartRate", "glucose"]
BINARIAS = ["male", "currentSmoker", "BPMeds", "prevalentStroke", "prevalentHyp", "diabetes"]
ORDINALES = ["education"]
PREDICTORES = NUMERICAS + BINARIAS + ORDINALES

HALLAZGOS = {
    "S1": {
        "n": 4240, "tasa_chd_%": 15.19,
        "faltantes": {
            "glucose": (388, 9.15), "education": (105, 2.48), "BPMeds": (53, 1.25),
            "totChol": (50, 1.18), "cigsPerDay": (29, 0.68), "BMI": (19, 0.45),
            "heartRate": (1, 0.02),
        },
        "filas_con_faltantes": (582, 13.7),
        "cigsPerDay": "29 faltantes, todos en fumadores",
        "outliers": "Valores clínicos extremos conservados en S1",
        "diferencias_g": {
            "age": 0.64, "sysBP": 0.62, "diaBP": 0.41, "glucose": 0.35,
            "totChol": 0.23, "BMI": 0.21, "cigsPerDay": 0.16, "heartRate": 0.06,
        },
        "tasas_chd_%": {
            "hombres": 18.8, "mujeres": 12.4, "hipertension": 24.7,
            "sin_hipertension": 10.9, "diabetes": 36.7, "sin_diabetes": 14.6,
            "fumadores": 15.9, "no_fumadores": 14.5,
        },
    },
    "S2": {
        "correlaciones_estables": {
            ("sysBP", "diaBP"): (0.778, 0.763, 0.791),
            ("age", "sysBP"): (0.391, 0.365, 0.417),
            ("BMI", "diaBP"): (0.375, 0.348, 0.401),
        },
        "correlaciones_inestables": {("totChol", "glucose"): (0.030, -0.002, 0.061)},
        "ic_bca_dif_sysBP": (11.14, 15.60), "ic_bca_dif_glucose": (5.32, 12.16),
        "glucosa_sin_atipicos": "La diferencia pierde significación sin atípicos",
        "glucosa_segun_diabetes": "Mediana 145 mg/dL en diabéticos y 78 en no diabéticos",
        "imputacion_glucosa": "La mediana reduce ligeramente la dispersión",
        "tabaquismo_ajustado_edad": "Diferencia MH 4,64 pp; p < 0,001",
        "vif_sysBP_diaBP": (3.11, 2.85),
        "recomendaciones": [
            "usar métricas para la clase minoritaria",
            "ajustar la imputación solo con entrenamiento",
            "mantener presión sistólica frente a la colinealidad",
            "ajustar tabaquismo e hipertensión por edad",
            "evitar conclusiones firmes en subgrupos pequeños",
        ],
    },
}

NUMERICAS_CON_FALTANTES = ["cigsPerDay", "totChol", "BMI", "heartRate", "glucose"]
CATEGORICAS_CON_FALTANTES = ["education", "BPMeds"]

# Entre 3 y 5 predictores por variable. Se priorizan relaciones que S2 valido
# como estables: PAS-PAD, edad-PAS e IMC-PAD. El desenlace nunca se usa para
# imputar, evitando incorporar informacion futura en las covariables.
PREDICTORES_IMPUTACION = {
    "cigsPerDay": ["currentSmoker", "age", "male", "sysBP", "diaBP"],
    "totChol": ["age", "sysBP", "diaBP", "male", "currentSmoker"],
    "BMI": ["diaBP", "sysBP", "age", "male", "currentSmoker"],
    "heartRate": ["age", "sysBP", "diaBP", "male", "currentSmoker"],
    "glucose": ["age", "diabetes", "sysBP", "diaBP", "cigsPerDay"],
}


def cargar_datos() -> pd.DataFrame:
    """Carga una copia de los datos originales, sin modificar el archivo fuente."""
    return pd.read_csv(RUTA_DATOS)


def resumen_faltantes(df: pd.DataFrame) -> pd.DataFrame:
    """Número y porcentaje de faltantes, restringido a variables afectadas."""
    tabla = pd.DataFrame({"n_faltantes": df.isna().sum()})
    tabla["porcentaje_faltantes"] = 100 * tabla["n_faltantes"] / len(df)
    return tabla.query("n_faltantes > 0").sort_values(
        "porcentaje_faltantes", ascending=False
    )


def imputar_simple(
    datos: pd.DataFrame,
    valores: dict[str, float] | None = None,
    devolver_valores: bool = False,
):
    """Imputa mediana en numéricas y moda en variables categóricas.

    Si ``valores`` se omite, se estiman en ``datos``. Para prueba deben
    entregarse los valores aprendidos en entrenamiento.
    """
    df = datos.copy()
    if valores is None:
        valores = {}
        for col in df.columns:
            if not df[col].isna().any() or col == OBJETIVO:
                continue
            if col in CATEGORICAS_CON_FALTANTES:
                valores[col] = float(df[col].mode(dropna=True).iloc[0])
            else:
                valores[col] = float(df[col].median())
    salida = df.fillna(valores)
    return (salida, valores) if devolver_valores else salida


@dataclass
class EstadoImputacionRegresion:
    """Parámetros aprendidos que permiten aplicar la imputación sin fuga."""

    modelos: dict
    modas: dict[str, float]
    medianas: dict[str, float]
    limites: dict[str, tuple[float, float]]


def _diagnosticos_ols(X: pd.DataFrame, y: pd.Series, modelo_ols) -> dict:
    residuos = modelo_ols.resid
    X_const = sm.add_constant(X.astype(float), has_constant="add")
    vif = [
        variance_inflation_factor(X_const.values, i)
        for i in range(1, X_const.shape[1])
    ]
    influencia = modelo_ols.get_influence()
    return {
        "JB_p_residuos": float(jarque_bera(residuos).pvalue),
        "BP_p_heterocedasticidad": float(het_breuschpagan(residuos, X_const)[1]),
        "VIF_max": float(max(vif)),
        "Cook_max": float(influencia.cooks_distance[0].max()),
    }


def _ajustar_imputadores(datos_ajuste: pd.DataFrame):
    trabajo = datos_ajuste.copy()
    modelos = {}
    modas = {}
    medianas = {}
    limites = {}
    diagnosticos = []

    # Primero se resuelven faltantes categóricos por moda del conjunto de ajuste.
    for col in CATEGORICAS_CON_FALTANTES:
        modas[col] = float(trabajo[col].mode(dropna=True).iloc[0])
        trabajo[col] = trabajo[col].fillna(modas[col])

    # El orden es intencional: cigsPerDay queda disponible como predictor de glucosa.
    for variable in NUMERICAS_CON_FALTANTES:
        predictores = PREDICTORES_IMPUTACION[variable]
        # El ajuste usa exclusivamente valores originalmente observados tanto
        # en la variable a imputar como en todos sus predictores.
        completos = datos_ajuste[[variable] + predictores].dropna()
        X = completos[predictores].astype(float)
        y = completos[variable].astype(float)

        X_ent, X_val, y_ent, y_val = train_test_split(
            X, y, test_size=0.20, random_state=SEMILLA
        )
        evaluacion = sm.OLS(
            y_ent, sm.add_constant(X_ent, has_constant="add")
        ).fit()
        pred_val = evaluacion.predict(sm.add_constant(X_val, has_constant="add"))

        modelo = sm.OLS(y, sm.add_constant(X, has_constant="add")).fit()
        modelos[variable] = (modelo, predictores)
        medianas[variable] = float(y.median())
        limites[variable] = (float(y.min()), float(y.max()))

        fila = {
            "variable": variable,
            "n_ajuste": len(completos),
            "predictores": ", ".join(predictores),
            "R2_validacion": float(1 - np.sum((y_val - pred_val) ** 2) / np.sum((y_val - y_val.mean()) ** 2)),
            "RMSE_validacion": float(np.sqrt(np.mean((y_val - pred_val) ** 2))),
            "MAE_validacion": float(np.mean(np.abs(y_val - pred_val))),
        }
        fila.update(_diagnosticos_ols(X, y, modelo))
        diagnosticos.append(fila)

        # Imputación secuencial en la copia usada para ajustar variables posteriores.
        faltante = trabajo[variable].isna()
        utilizable = faltante & trabajo[predictores].notna().all(axis=1)
        if utilizable.any():
            X_nuevo = sm.add_constant(
                trabajo.loc[utilizable, predictores].astype(float), has_constant="add"
            )
            valores = modelo.predict(X_nuevo).clip(*limites[variable])
            trabajo.loc[utilizable, variable] = valores
        trabajo[variable] = trabajo[variable].fillna(medianas[variable])

    estado = EstadoImputacionRegresion(modelos, modas, medianas, limites)
    return estado, pd.DataFrame(diagnosticos)


def imputar_regresion(
    datos: pd.DataFrame,
    estado: EstadoImputacionRegresion | None = None,
    devolver_detalle: bool = False,
):
    """Imputa todas las variables incompletas mediante regresión múltiple.

    Parámetros
    ----------
    datos:
        Dataset que se desea transformar.
    estado:
        Modelos aprendidos previamente. Si es ``None`` se ajustan en ``datos``.
        Para evaluación predictiva se ajusta en entrenamiento y el mismo estado
        se aplica en prueba, evitando fuga de información.
    devolver_detalle:
        Cuando es ``True`` retorna ``(datos_imputados, estado, diagnosticos,
        conteos)``. Esta es la forma recomendada al transformar entrenamiento.

    Notas
    -----
    Cada regresión se ajusta solo con observaciones completas para la variable
    objetivo y sus predictores. Si una fila no dispone de todos los predictores,
    se usa como respaldo la mediana aprendida en ajuste. Las predicciones se
    restringen al rango observado de la variable para evitar valores imposibles.
    """
    if estado is None:
        estado, diagnosticos = _ajustar_imputadores(datos)
    else:
        diagnosticos = pd.DataFrame()

    salida = datos.copy()
    conteos = []
    for col in CATEGORICAS_CON_FALTANTES:
        n = int(salida[col].isna().sum())
        salida[col] = salida[col].fillna(estado.modas[col])
        conteos.append({"variable": col, "n_imputados": n, "metodo": "moda"})

    for variable in NUMERICAS_CON_FALTANTES:
        n = int(salida[variable].isna().sum())
        modelo, predictores = estado.modelos[variable]
        faltante = salida[variable].isna()
        utilizable = faltante & salida[predictores].notna().all(axis=1)
        n_regresion = int(utilizable.sum())
        if utilizable.any():
            X_nuevo = sm.add_constant(
                salida.loc[utilizable, predictores].astype(float), has_constant="add"
            )
            valores = modelo.predict(X_nuevo).clip(*estado.limites[variable])
            salida.loc[utilizable, variable] = valores
        restantes = int(salida[variable].isna().sum())
        salida[variable] = salida[variable].fillna(estado.medianas[variable])
        conteos.append(
            {
                "variable": variable,
                "n_imputados": n,
                "n_por_regresion": n_regresion,
                "n_respaldo_mediana": restantes,
                "metodo": "regresion lineal multiple",
            }
        )

    if salida.isna().any().any():
        columnas = salida.columns[salida.isna().any()].tolist()
        raise RuntimeError(f"Persisten faltantes después de imputar: {columnas}")

    if devolver_detalle:
        return salida, estado, diagnosticos, pd.DataFrame(conteos)
    return salida


def comparar_distribuciones(original: pd.DataFrame, datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Compara tamaño y estadísticos descriptivos de las tres estrategias."""
    filas = []
    variables = ["cigsPerDay", "totChol", "BMI", "heartRate", "glucose"]
    for estrategia, df in datasets.items():
        for variable in variables:
            filas.append(
                {
                    "estrategia": estrategia,
                    "variable": variable,
                    "n": int(df[variable].notna().sum()),
                    "media": float(df[variable].mean()),
                    "DE": float(df[variable].std()),
                    "mediana": float(df[variable].median()),
                    "IQR": float(df[variable].quantile(0.75) - df[variable].quantile(0.25)),
                    "media_original_disponible": float(original[variable].mean()),
                }
            )
    return pd.DataFrame(filas)


def comparar_correlaciones(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Recalcula exclusivamente las cinco correlaciones priorizadas en S2."""
    pares = [
        ("sysBP", "diaBP"),
        ("age", "sysBP"),
        ("BMI", "diaBP"),
        ("totChol", "glucose"),
        ("cigsPerDay", "glucose"),
    ]
    filas = []
    for estrategia, df in datasets.items():
        for a, b in pares:
            filas.append(
                {
                    "estrategia": estrategia,
                    "par": f"{a} - {b}",
                    "correlacion": float(df[[a, b]].corr().iloc[0, 1]),
                }
            )
    tabla = pd.DataFrame(filas)
    referencia = tabla.query("estrategia == 'regresion'").set_index("par")["correlacion"]
    tabla["diferencia_vs_regresion"] = tabla.apply(
        lambda r: r["correlacion"] - referencia.loc[r["par"]], axis=1
    )
    return tabla


def _estandarizar(
    train: pd.DataFrame,
    test: pd.DataFrame,
    variables: list[str],
):
    X_train = train[variables].astype(float).copy()
    X_test = test[variables].astype(float).copy()
    binarias = {"male", "currentSmoker", "BPMeds", "prevalentStroke", "prevalentHyp", "diabetes"}
    escalas = {}
    for col in variables:
        if col in binarias:
            continue
        media = float(X_train[col].mean())
        de = float(X_train[col].std(ddof=0)) or 1.0
        X_train[col] = (X_train[col] - media) / de
        X_test[col] = (X_test[col] - media) / de
        escalas[col] = {"media": media, "DE": de}
    return X_train, X_test, escalas


def evaluar_modelo_comun(
    train: pd.DataFrame,
    test: pd.DataFrame,
    variables: list[str],
    estrategia: str,
):
    """Ajusta exactamente la misma regresión logística y devuelve impacto."""
    X_train, X_test, _ = _estandarizar(train, test, variables)
    y_train = train[OBJETIVO].astype(int)
    y_test = test[OBJETIVO].astype(int)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        modelo = sm.Logit(
            y_train, sm.add_constant(X_train, has_constant="add")
        ).fit(disp=False, maxiter=250)

    probabilidades = modelo.predict(sm.add_constant(X_test, has_constant="add"))
    predichos = (probabilidades >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, predichos, labels=[0, 1]).ravel()
    metricas = {
        "estrategia": estrategia,
        "n_total": len(train) + len(test),
        "n_train": len(train),
        "n_test": len(test),
        "eventos_test": int(y_test.sum()),
        "TN": int(tn),
        "FP": int(fp),
        "FN": int(fn),
        "TP": int(tp),
        "accuracy": float(accuracy_score(y_test, predichos)),
        "precision": float(precision_score(y_test, predichos, zero_division=0)),
        "recall": float(recall_score(y_test, predichos, zero_division=0)),
        "F1": float(f1_score(y_test, predichos, zero_division=0)),
        "AUC": float(roc_auc_score(y_test, probabilidades)),
    }

    intervalos = modelo.conf_int()
    coeficientes = pd.DataFrame(
        {
            "estrategia": estrategia,
            "variable": modelo.params.index,
            "coeficiente": modelo.params.values,
            "IC95_inf": intervalos[0].values,
            "IC95_sup": intervalos[1].values,
            "odds_ratio": np.exp(modelo.params.values),
            "IC95_OR_inf": np.exp(intervalos[0].values),
            "IC95_OR_sup": np.exp(intervalos[1].values),
            "p_valor": modelo.pvalues.values,
        }
    )
    return modelo, metricas, coeficientes, np.asarray(probabilidades)


def preparar_particiones_por_estrategia(
    original: pd.DataFrame,
    test_size: float = 0.30,
):
    """Crea particiones comparables; imputadores se ajustan solo en train."""
    indices_train, indices_test = train_test_split(
        original.index,
        test_size=test_size,
        random_state=SEMILLA,
        stratify=original[OBJETIVO],
    )
    train_raw = original.loc[indices_train].copy()
    test_raw = original.loc[indices_test].copy()

    # Eliminación: se conservan los mismos grupos de origen y luego se quitan incompletos.
    train_del = train_raw.dropna().copy()
    test_del = test_raw.dropna().copy()

    train_simple, valores = imputar_simple(train_raw, devolver_valores=True)
    test_simple = imputar_simple(test_raw, valores=valores)

    train_reg, estado, diagnosticos, conteos_train = imputar_regresion(
        train_raw, devolver_detalle=True
    )
    test_reg, _, _, conteos_test = imputar_regresion(
        test_raw, estado=estado, devolver_detalle=True
    )

    particiones = {
        "eliminacion": (train_del, test_del),
        "simple": (train_simple, test_simple),
        "regresion": (train_reg, test_reg),
    }
    return particiones, diagnosticos, conteos_train, conteos_test


# Interfaz común consumida por los notebooks 02 y 03 del trabajo grupal.
def configurar_graficos() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    pd.set_option("display.float_format", lambda x: f"{x:,.4f}")


def guardar_figura(nombre: str) -> None:
    FIG.mkdir(exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIG / f"{nombre}.png", dpi=200, bbox_inches="tight")
    plt.show()


def guardar_tabla(tabla: pd.DataFrame, nombre: str) -> pd.DataFrame:
    TAB.mkdir(exist_ok=True)
    tabla.to_csv(TAB / f"{nombre}.csv", index=True)
    return tabla


def particionar(df: pd.DataFrame):
    """Partición grupal 70/30 estratificada, previa a toda imputación."""
    return train_test_split(
        df, test_size=TEST_SIZE, stratify=df[OBJETIVO], random_state=SEED
    )


def imputar(train: pd.DataFrame, test: pd.DataFrame, estrategia: str):
    """Aplica una estrategia ajustada solo con el conjunto de entrenamiento."""
    if estrategia == "eliminacion":
        return train.dropna().copy(), test.dropna().copy()
    if estrategia == "simple":
        train_i, valores = imputar_simple(train, devolver_valores=True)
        return train_i, imputar_simple(test, valores=valores)
    if estrategia == "regresion":
        train_i, estado, _, _ = imputar_regresion(train, devolver_detalle=True)
        return train_i, imputar_regresion(test, estado=estado)
    raise ValueError(f"Estrategia desconocida: {estrategia}")


def preparar_modelo(train: pd.DataFrame, test: pd.DataFrame, variables, recortar=None):
    """Prepara matrices para los modelos grupales sin usar información de prueba."""
    variables = list(variables)
    train, test = train.copy(), test.copy()
    for variable, (p_inf, p_sup) in (recortar or {}).items():
        inf, sup = np.percentile(train[variable].dropna(), [p_inf, p_sup])
        train[variable] = train[variable].clip(inf, sup)
        test[variable] = test[variable].clip(inf, sup)

    X_train = train[variables].astype(float).copy()
    X_test = test[variables].astype(float).copy()
    numericas = [v for v in variables if v in NUMERICAS]
    if numericas:
        media = X_train[numericas].mean()
        de = X_train[numericas].std(ddof=0).replace(0, 1)
        X_train[numericas] = (X_train[numericas] - media) / de
        X_test[numericas] = (X_test[numericas] - media) / de

    if "education" in variables:
        X_train = pd.get_dummies(
            X_train, columns=["education"], prefix="edu", drop_first=True, dtype=float
        )
        X_test = pd.get_dummies(
            X_test, columns=["education"], prefix="edu", drop_first=True, dtype=float
        ).reindex(columns=X_train.columns, fill_value=0.0)

    return (
        X_train,
        X_test,
        train[OBJETIVO].astype(int),
        test[OBJETIVO].astype(int),
    )

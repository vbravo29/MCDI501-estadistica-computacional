# MCDI501 - Estadística Computacional para la Toma de Decisiones

Magíster en Ciencia de Datos e Inteligencia Artificial, Universidad Andrés Bello.

Proyecto del curso sobre el dataset Framingham Heart Study. El objetivo es analizar qué
factores se asocian al riesgo de desarrollar enfermedad coronaria en 10 años (`TenYearCHD`).

## Integrantes

- 
- 
- 

## Estructura

```
data/
  framingham.csv           datos originales (4.240 filas, 16 variables)
  framingham_limpio.csv    datos después de la limpieza
sumativa-1/
  01_datos_descriptiva.ipynb   calidad de datos, limpieza y estadística descriptiva
  02_bivariado_ic.ipynb        análisis bivariado e intervalos de confianza
  03_hipotesis.ipynb           pruebas de hipótesis
  figuras/                     gráficos generados por los notebooks
```

Fuente de los datos: [Kaggle - Framingham Heart Study](https://www.kaggle.com/datasets/dileep070/heart-disease-prediction-using-logistic-regression).

## Ejecución

Requiere Python 3.10 o superior.

```bash
pip install -r requirements.txt
jupyter notebook
```

Ejecutar `01_datos_descriptiva.ipynb` antes que los demás, ya que genera `framingham_limpio.csv`.
Cada notebook debe ejecutarse completo desde el inicio (Restart & Run All).

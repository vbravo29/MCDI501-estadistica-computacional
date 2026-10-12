# MCDI501 - Estadística Computacional para la Toma de Decisiones

Magíster en Ciencia de Datos e Inteligencia Artificial, Universidad Andrés Bello.

Proyecto del curso sobre el dataset Framingham Heart Study. El objetivo es analizar qué
factores se asocian al riesgo de desarrollar enfermedad coronaria en 10 años (`TenYearCHD`).

## Integrantes

- **Pendiente:** completar nombres y apellidos de los 3 a 4 integrantes antes de la entrega.

## Repositorio

https://github.com/vbravo29/MCDI501-estadistica-computacional

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

Requiere Python 3.11 o superior. Las versiones exactas validadas se encuentran en
`requirements.txt`.

```bash
pip install -r requirements.txt
jupyter notebook
```

Ejecutar `01_datos_descriptiva.ipynb` antes que los demás, ya que genera `framingham_limpio.csv`.
Luego ejecutar `02_bivariado_ic.ipynb` y finalmente `03_hipotesis.ipynb`.
Cada notebook debe ejecutarse completo desde el inicio (Restart & Run All).

Los análisis que contienen valores faltantes usan casos disponibles e informan el tamaño
muestral efectivo. Los archivos de datos originales no deben modificarse.

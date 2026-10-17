# MCDI501 - Estadística Computacional para la Toma de Decisiones

Magíster en Ciencia de Datos e Inteligencia Artificial, Universidad Andrés Bello.

Proyecto del curso sobre el dataset Framingham Heart Study. El objetivo es analizar qué
factores se asocian al riesgo de desarrollar enfermedad coronaria en 10 años (`TenYearCHD`).

## Integrantes

- Víctor Bravo Barrera
- Nayadeth Garrido Ibáñez
- Mauricio Cid

Docente: Jean Paul Maidana González

## Repositorio

https://github.com/vbravo29/MCDI501-estadistica-computacional

## Estructura

```
data/
  framingham.csv           datos originales (4.240 filas, 16 variables)
  framingham_limpio.csv    datos después de la limpieza
S1/                        Sumativa 1: análisis exploratorio e inferencial
  01_datos_descriptiva.ipynb   calidad de datos, limpieza y estadística descriptiva
  02_bivariado_ic.ipynb        análisis bivariado e intervalos de confianza
  03_hipotesis.ipynb           pruebas de hipótesis
  notebook.ipynb               notebook completo (une las tres partes en el orden del informe)
  informe-sumativa-1.docx      informe técnico editable
  informe-sumativa-1.pdf       informe técnico entregado (exportado desde el .docx)
  figuras/                     gráficos generados por los notebooks
S2/                        Sumativa 2: simulación y remuestreo (validación de la S1)
  utils_s2.py                  semilla, B = 10.000, rutas, resultados de referencia de la S1 y funciones comunes
  01_bootstrap_ic.ipynb        parte 1: IC bootstrap percentil y BCa frente a los IC de la S1
  02_permutacion.ipynb         parte 2: tests de permutación de las pruebas de la S1
  03_correlaciones.ipynb       parte 3: estabilidad de correlaciones con bootstrap
  04_montecarlo.ipynb          parte 4: simulación Monte Carlo con parámetros de la S1
  05_robustez.ipynb            parte 5: jackknife, outliers y supuestos
  resultados_validados.md      parte 6: resultados validados para la Sumativa 3
  figuras/                     gráficos generados por los notebooks (pX_figN_descripcion.png)
  tablas/                      tablas resumen en CSV (pX_descripcion.csv)
```

Fuente de los datos: [Kaggle - Framingham Heart Study](https://www.kaggle.com/datasets/dileep070/heart-disease-prediction-using-logistic-regression).

## Entregables

- Sumativa 1: informe `S1/informe-sumativa-1.pdf` y notebook `S1/notebook.ipynb`.
- Sumativa 2: informe PDF (máximo 7 páginas), notebook `S2/notebook.ipynb` y `S2/resultados_validados.md`.

## Ejecución

Requiere Python 3.10 o superior. Las versiones mínimas de las librerías se encuentran en
`requirements.txt`.

```bash
pip install -r requirements.txt
jupyter notebook
```

**Sumativa 1.** Ejecutar `S1/01_datos_descriptiva.ipynb` antes que los demás, ya que genera
`framingham_limpio.csv`. Luego `02_bivariado_ic.ipynb` y `03_hipotesis.ipynb`, o directamente
`S1/notebook.ipynb`, que reúne las tres partes.

**Sumativa 2.** Los notebooks de `S2/` se ejecutan desde esa carpeta y son independientes entre sí.
Todos importan `utils_s2.py`, que fija la semilla 42 y B = 10.000, y verifican al inicio que los datos
reproducen las cifras de la S1.

Cada notebook debe ejecutarse completo desde el inicio (Restart & Run All).
Los análisis que contienen valores faltantes usan casos disponibles e informan el tamaño
muestral efectivo. Los archivos de datos originales no deben modificarse.

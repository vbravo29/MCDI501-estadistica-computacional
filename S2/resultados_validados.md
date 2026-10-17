# Resultados validados – Sumativa 2 (insumo para la Sumativa 3)

Proyecto: factores asociados al riesgo de enfermedad coronaria a 10 años (Framingham Heart Study).
Integrantes: Víctor Bravo Barrera, Nayadeth Garrido Ibáñez, Mauricio Cid.

Todos los resultados se obtuvieron con semilla 42 y 10.000 remuestras, permutaciones o iteraciones
(`S2/utils_s2.py`). Las tablas completas están en `S2/tablas/`.

## 1. Parámetros robustamente estimados

Fuente: `01_bootstrap_ic.ipynb` y `05_robustez.ipynb`.

| Parámetro | IC clásico S1 | IC bootstrap BCa | Sensible a outliers | Valor recomendado para S3 |
| --- | --- | --- | --- | --- |
| Edad media | [49,32; 49,84] | TODO | TODO | TODO |
| Presión sistólica media | [131,69; 133,02] | TODO | TODO | TODO |
| Colesterol total medio | [235,35; 238,05] | TODO | TODO | TODO |
| Proporción de CHD | [14,14 %; 16,30 %] | TODO | TODO | TODO |
| Diferencia de presión sistólica (CHD − sin CHD) | [11,11; 15,45] | TODO | TODO | TODO |
| Diferencia de glucosa (CHD − sin CHD) | [4,95; 11,71] | TODO | TODO | TODO |

Tasas de CHD por tramo de edad (fumadores − no fumadores), IC bootstrap 95 %:

| Tramo de edad | Diferencia S1 | IC bootstrap 95 % | ¿Incluye 0? |
| --- | --- | --- | --- |
| ≤ 45 | 4,2 pp (8,4 % vs 4,1 %) | TODO | TODO |
| 46–55 | 5,5 pp (18,6 % vs 13,1 %) | TODO | TODO |
| > 55 | 4,0 pp (28,6 % vs 24,6 %) | TODO | TODO |

## 2. Pruebas de hipótesis validadas

Fuente: `02_permutacion.ipynb`.

| Prueba | p paramétrico S1 | p permutación | ¿Concuerdan? | Conclusión |
| --- | --- | --- | --- | --- |
| Presión sistólica según CHD | < 0,001 | TODO | TODO | TODO |
| Tabaquismo y CHD | 0,221 | TODO | TODO | TODO |
| Tabaquismo y CHD, estratificada por edad | — | TODO | — | TODO |

## 3. Correlaciones estables

Fuente: `03_correlaciones.ipynb`.

| Par | ρ S1 | IC bootstrap 95 % | ¿Incluye 0? | Clasificación |
| --- | --- | --- | --- | --- |
| Presión sistólica – diastólica | 0,78 | TODO | TODO | TODO |
| Edad – presión sistólica | 0,39 | TODO | TODO | TODO |
| IMC – presión diastólica | 0,37 | TODO | TODO | TODO |

## 4. Observaciones influyentes

Fuente: `05_robustez.ipynb`.

| Variable | Valor | Influencia jackknife | Efecto al excluirla | Recomendación |
| --- | --- | --- | --- | --- |
| TODO | | | | |

## 5. Escenarios Monte Carlo

Fuente: `04_montecarlo.ipynb`.

TODO: casos evitados por escenario, cobertura simulada del IC t y entradas más sensibles.

## 6. Recomendaciones metodológicas para la Sumativa 3

Incluye las indicaciones del docente en la retroalimentación de la S1.

- **Desbalance de clases (15,2 % de CHD):** evaluar los modelos con métricas para la clase minoritaria
  (sensibilidad, precisión, F1, AUC-PR) y no solo con exactitud.
- **Imputación de glucosa dentro de la validación:** ajustar la imputación solo con los datos de
  entrenamiento de cada partición (por ejemplo, dentro de un `Pipeline`) para evitar fuga de información.
- **Colinealidad sistólica–diastólica (ρ = 0,78):** incluir solo una de las dos. TODO: indicar cuál y por qué,
  según su estabilidad y robustez en la S2.
- **Tabaquismo:** estimarlo controlando por edad (regresión logística múltiple), según la confusión
  observada en la S1 y los resultados por tramo de la S2.
- TODO: recomendaciones que salgan de la robustez (observaciones influyentes, transformaciones de variables asimétricas).

# Resultados validados – Sumativa 2 (insumo para la Sumativa 3)

Proyecto: factores asociados al riesgo de enfermedad coronaria a 10 años (Framingham Heart Study).
Integrantes: Víctor Bravo Barrera, Nayadeth Garrido Ibáñez, Mauricio Cid.

Todos los resultados se obtuvieron con semilla 42 y 10.000 remuestras, permutaciones o iteraciones
(`S2/utils_s2.py`). Las tablas completas están en `S2/tablas/`.

## 1. Parámetros robustamente estimados

Fuente: `01_bootstrap_ic.ipynb` y `05_robustez.ipynb`.

| Parámetro | IC clásico S1 | IC bootstrap BCa | Sensible a outliers | Valor recomendado para S3 |
| --- | --- | --- | --- | --- |
| Edad media | [49,32; 49,84] | [49,32; 49,85] | No (cambio máximo 0,28 %) | 49,58 años; IC BCa [49,32; 49,85] |
| Presión sistólica media | [131,69; 133,02] | [131,70; 133,02] | Baja (cambio máximo 1,55 %) | 132,35 mmHg; IC BCa [131,70; 133,02] |
| Colesterol total medio | [235,35; 238,05] | [235,36; 238,05] | Baja (cambio máximo 0,77 %) | 236,70 mg/dL; IC BCa [235,36; 238,05] |
| Proporción de CHD | [14,14 %; 16,30 %] | [14,15 %; 16,27 %] | No evaluable mediante extremos continuos | 15,19 %; IC BCa [14,15 %; 16,27 %] |
| Diferencia de presión sistólica (CHD − sin CHD) | [11,11; 15,45] | No calculado en el bloque bootstrap | Moderada: baja 27,2 % sin atípicos, pero mantiene significación | 13,28 mmHg; informar además 9,66 mmHg sin atípicos |
| Diferencia de glucosa (CHD − sin CHD) | [4,95; 11,71] | [5,32; 12,16] | Alta: baja 90,0 % sin atípicos y deja de ser significativa | 8,33 mg/dL como estimación descriptiva; interpretar con cautela |

Tasas de CHD por tramo de edad (fumadores − no fumadores), IC bootstrap 95 %:

| Tramo de edad | Diferencia S1 | IC bootstrap 95 % | ¿Incluye 0? |
| --- | --- | --- | --- |
| ≤ 45 | 4,2 pp (8,4 % vs 4,1 %) | [1,82; 6,54] pp | No |
| 46–55 | 5,5 pp (18,6 % vs 13,1 %) | [1,84; 9,16] pp | No |
| > 55 | 4,0 pp (28,6 % vs 24,6 %) | [−1,24; 9,39] pp | Sí |

## 2. Pruebas de hipótesis validadas

Fuente: `02_permutacion.ipynb`.

| Prueba | p paramétrico S1 | p permutación | ¿Concuerdan? | Conclusión |
| --- | --- | --- | --- | --- |
| Presión sistólica según CHD | < 0,001 | < 0,001 | Sí | Se rechaza H₀; la diferencia de PAS es robusta |
| Tabaquismo y CHD | 0,221 | 0,210 | Sí | Sin ajustar por edad, no se rechaza H₀ |
| Tabaquismo y CHD, estratificada por edad | — | < 0,001 | Sí con CMH (p < 0,001) | Al controlar por edad aparece una asociación; había confusión |

## 3. Correlaciones estables

Fuente: `03_correlaciones.ipynb`.

| Par | ρ S1 | IC bootstrap 95 % | ¿Incluye 0? | Clasificación |
| --- | --- | --- | --- | --- |
| Presión sistólica – diastólica | 0,78 | [0,763; 0,791] | No | Robusta |
| Edad – presión sistólica | 0,39 | [0,365; 0,417] | No | Robusta |
| IMC – presión diastólica | 0,37 | [0,348; 0,401] | No | Robusta, con sensibilidad moderada a atípicos |
| Colesterol total – glucosa | 0,03 | [−0,002; 0,061] | Sí | Inestable; compatible con ausencia de asociación |
| Cigarrillos por día – glucosa | −0,09 | [−0,118; −0,055] | No | Dirección estable, asociación débil |

## 4. Observaciones influyentes

Fuente: `05_robustez.ipynb`.

| Variable | Valor | Influencia jackknife | Efecto al excluirla | Recomendación |
| --- | --- | --- | --- | --- |
| Presión sistólica | 295 mmHg (fila 481) | Mayor cambio individual: −0,038 mmHg en la media | Sin atípicos, la media baja 1,55 % y la diferencia CHD baja 27,2 % | Mantener PAS, pero revisar valores extremos y reportar análisis sin atípicos |
| Colesterol total | 696 mg/dL (fila 3160) | Mayor cambio individual: −0,110 mg/dL | Sin atípicos, la media baja 0,77 % | Conservar; aplicar control de calidad y análisis de sensibilidad |
| Glucosa | 394 mg/dL (filas 2893 y 2909) | Cada observación cambia la media en −0,081 mg/dL | Sin atípicos, la diferencia CHD baja de 8,33 a 0,83 mg/dL y pierde significación | Transformar o usar métodos robustos; validar la imputación dentro de cada partición |
| Edad | 70 años (filas 1624 y 3137) | Cambio individual de −0,005 años | No se detectaron atípicos por Tukey | Conservar sin tratamiento especial |

## 5. Escenarios Monte Carlo

Fuente: `04_montecarlo.ipynb`.

**Escenario A, programa de control de la hipertensión** (cohorte de 1.000 personas; supone que los
hipertensos controlados pasan a la tasa de los no hipertensos, por lo que es un límite superior):

| Hipertensos controlados | Casos evitados (media) | IC 95 % | Reducción de casos |
| --- | --- | --- | --- |
| 20 % | 8,5 | [3; 15] | 5,6 % |
| 40 % | 17,1 | [10; 26] | 11,3 % |
| 60 % | 25,7 | [16; 36] | 16,9 % |

El modelo reproduce la tasa observada (15,17 % simulada frente a 15,19 % en la S1). Se necesitan unos
7 hipertensos controlados por caso evitado. La entrada más influyente es la tasa de CHD de los
hipertensos (14,3 a 20,1 casos evitados dentro de su IC).

**Escenario B, datos sintéticos de presión sistólica** (lognormal desplazada con la media, DE y asimetría
de cada grupo):

| n total | Cobertura IC 95 % de Welch | Potencia |
| --- | --- | --- |
| 4.240 (S1) | 95,1 % | 100 % |
| 329 | 94,6 % | 93,7 % |
| 132 | 94,7 % | 52,4 % |
| 33 | 92,7 % | 9,8 % |

La prueba de Welch de la S1 es confiable pese a la asimetría; con subgrupos pequeños la cobertura y la
potencia caen.

## 6. Recomendaciones metodológicas para la Sumativa 3

Incluye las indicaciones del docente en la retroalimentación de la S1.

- **Desbalance de clases (15,2 % de CHD):** evaluar los modelos con métricas para la clase minoritaria
  (sensibilidad, precisión, F1, AUC-PR) y no solo con exactitud.
- **Imputación de glucosa dentro de la validación:** ajustar la imputación solo con los datos de
  entrenamiento de cada partición (por ejemplo, dentro de un `Pipeline`) para evitar fuga de información.
- **Colinealidad sistólica–diastólica (ρ = 0,78):** conservar la presión sistólica y excluir la
  diastólica del modelo principal. Ambas son estables, pero la sistólica se vincula directamente con
  las hipótesis y la simulación de la S2; comparar esta decisión mediante validación cruzada.
- **Tabaquismo:** estimarlo controlando por edad (regresión logística múltiple), según la confusión
  observada en la S1 y los resultados por tramo de la S2.
- **Efecto de la hipertensión:** estimarlo ajustado por edad y otros factores, porque es la entrada más
  influyente del escenario Monte Carlo y hoy se apoya en una asociación bivariada.
- **Subgrupos pequeños:** evitar conclusiones sobre grupos como diabetes (n = 109) o ACV previo (n = 25);
  la simulación muestra que con n < 150 la potencia cae bajo 55 %.
- **Valores extremos:** verificar los registros clínicamente improbables y comparar el modelo principal
  con una versión robusta o winsorizada, sin eliminar observaciones solo por una regla automática.
- **Variables asimétricas:** evaluar transformaciones logarítmicas para glucosa y cigarrillos por día, o
  estimadores robustos, y documentar si cambian el signo, la magnitud o la significación de los efectos.
- **Diferencia de glucosa:** no usarla como conclusión confirmatoria sin análisis robusto, porque su
  significación desaparece al retirar atípicos y la mediana entre grupos difiere solo 1 mg/dL.

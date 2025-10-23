Archivos generados para Minitab

Descripción rápida
Estos archivos están preparados para importarse en Minitab (CSV). Incluyen columnas limpias y algunas columnas auxiliares (shift, fecha) para facilitar análisis estadísticos.

Archivos
- `minitab_molienda_variabilidad.csv` — registros de la actividad `Molienda` con: lote_id, fecha_inicio, fecha_fin, duracion_min, operadores, shift, humedad_pct, motivo_parada, notas.
  - Análisis sugerido en Minitab: boxplot de `duracion_min` por `shift` o por `dia` (si se agrega), ANOVA por `shift`, control charts (I-MR) para monitorizar variabilidad de tiempos.

- `minitab_limpieza_defectos.csv` — registros de `Limpieza` con: lote_id, fecha_inicio, duracion_min, rendimiento_kg, defectos_kg, defectos_pct, humedad_pct, motivo_parada, operadores, notas.
  - Análisis sugerido: Pareto de `defectos_kg` por motivo (si se codifica), histogramas y boxplots de `defectos_pct`, correlación `humedad_pct` vs `defectos_pct` (scatter + regressión), pruebas de hipótesis entre turnos.

- `minitab_operadores_desbalance.csv` — formato "largo" con: fecha, area, actividad, lote_id, operadores, shift.
  - Análisis sugerido: gráficas de serie temporal de `operadores` por `area`, ANOVA entre `area` o `shift`, particionar por fecha para ver distribución diaria.

- `minitab_operadores_agg.csv` — agregado por `fecha` + `area`: total_operadores, registros_count, operadores_mean.
  - Análisis sugerido: usar `operadores_mean` para comparar cargas por área (ANOVA / boxplot) y detectar desbalance.

Cómo usar
1. Abrir Minitab y seleccionar File > Open > Worksheet > seleccionar el CSV.
2. Verificar que las columnas numéricas estén en formato numérico. Si no, usar Calc > Numeric Conversion.
3. Realizar análisis sugeridos arriba.

Notas
- Los archivos provienen del CSV simulado `data/produccion_harina.csv` y mantienen la semántica del proyecto.
- Si quieres columnas adicionales (por ejemplo `equipo_id`, `turno` con nombre local, o codificación de motivos), puedo añadirlas y regenerar los CSVs.

Dataset de producción de harina

Descripción
Este directorio contiene datos simulados de producción de harina para un proceso con las siguientes actividades (basado en los diagramas BPMN del proyecto):

- Acondicionamiento: limpieza y control de materia prima
- Molienda: preparación, alimentación de molinos, control de calidad
- Envasado: preparación-dosificación, sellado-etiquetado

Archivo principal: `produccion_harina.csv`

Esquema (columnas)
- lote_id: identificador del lote (string)
- fecha_inicio: timestamp ISO del inicio de la actividad
- fecha_fin: timestamp ISO del fin de la actividad
- actividad: nombre de la actividad
- area: Acondicionamiento|Molienda|Envasado
- duracion_min: duración en minutos
- rendimiento_kg: cantidad producida en kg en la actividad (cuando aplica)
- humedad_pct: humedad del material en porcentaje (cuando aplica)
- defectos_kg: kg rechazados por control de calidad
- motivo_parada: motivo de parada si hubo ("", "mantenimiento", "atasco", "falla_electrica", "calibracion")
- operadores: número de operadores asignados
- notas: texto corto con observaciones

Cómo usar
1. Generar datos (opcional): `python3 scripts/generate_data.py --n 500 --out data/produccion_harina.csv`
2. Analizar: `python3 scripts/analyze_data.py --in data/produccion_harina.csv`

Licencia: datos simulados para ejercicios educativos.

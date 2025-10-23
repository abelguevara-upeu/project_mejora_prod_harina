#!/usr/bin/env python3
"""Generador de datos simulados para producción de harina.
Genera un CSV con eventos por actividad por lote, con variabilidad y anomalías.
"""
import csv
import random
from datetime import datetime, timedelta
import argparse

ACTIVITIES = [
    ("Limpieza","Acondicionamiento"),
    ("Control-Materia-Prima","Acondicionamiento"),
    ("Preparacion-Alimentacion-Molinos","Molienda"),
    ("Molienda","Molienda"),
    ("Control-Calidad-Molienda","Molienda"),
    ("Preparacion-Dosificacion","Envasado"),
    ("Sellado-Etiquetado","Envasado"),
]

PARADA_MOTIVOS = ["", "mantenimiento", "atasco", "falla_electrica", "calibracion"]

random.seed(42)


def rand_time(start):
    # Duraciones base por actividad en minutos
    base = {
        "Limpieza": 30,
        "Control-Materia-Prima": 20,
        "Preparacion-Alimentacion-Molinos": 45,
        "Molienda": 120,
        "Control-Calidad-Molienda": 25,
        "Preparacion-Dosificacion": 20,
        "Sellado-Etiquetado": 35,
    }
    name = start
    b = base.get(name, 30)
    # variación +-30%
    duration = int(random.gauss(b, b*0.12))
    duration = max(1, duration)
    return duration


def generate_row(lote_id, activity_name, area, start_ts):
    dur = rand_time(activity_name)
    fecha_inicio = start_ts
    fecha_fin = fecha_inicio + timedelta(minutes=dur)

    # rendimiento y defectos
    # yield base por lote (kg)
    base_yield = {
        "Limpieza": 1000,
        "Control-Materia-Prima": 1000,
        "Preparacion-Alimentacion-Molinos": 950,
        "Molienda": 900,
        "Control-Calidad-Molienda": 900,
        "Preparacion-Dosificacion": 880,
        "Sellado-Etiquetado": 870,
    }
    ry = base_yield.get(activity_name, 800)
    # variación y pérdidas
    rendimiento = max(0, int(random.gauss(ry, ry*0.07)))
    humedad = round(max(8.0, random.gauss(12.0, 2.5)), 2)

    # defectos aleatorios
    defect_prob = 0.02
    defectos = 0
    if random.random() < defect_prob:
        defectos = int(rendimiento * random.uniform(0.03, 0.15))

    # paradas raras
    motivo = ""
    if random.random() < 0.04:
        motivo = random.choice(PARADA_MOTIVOS[1:])
        # si hubo parada, extiende la duracion
        extra = random.randint(10, 120)
        fecha_fin += timedelta(minutes=extra)
        dur += extra

    operadores = random.randint(2, 6) if area != "Envasado" else random.randint(1, 4)

    notas = ""
    if humedad > 15:
        notas = "Humedad alta"
    if defectos > 0:
        notas = (notas + "; " if notas else "") + "Defectos detectados"

    return {
        "lote_id": lote_id,
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat(),
        "actividad": activity_name,
        "area": area,
        "duracion_min": dur,
        "rendimiento_kg": rendimiento,
        "humedad_pct": humedad,
        "defectos_kg": defectos,
        "motivo_parada": motivo,
        "operadores": operadores,
        "notas": notas,
    }, fecha_fin


def generate(n, out_path):
    # generar lotes con secuencia de actividades
    start_date = datetime.now() - timedelta(days=30)
    rows = []
    for i in range(1, n+1):
        lote_id = f"L-{1000+i}"
        ts = start_date + timedelta(minutes=random.randint(0, 60*24*28))
        # simular secuencia
        for act, area in ACTIVITIES:
            row, ts = generate_row(lote_id, act, area, ts)
            rows.append(row)
            # gap entre actividades
            ts += timedelta(minutes=random.randint(5, 60))

    # escribir csv
    fieldnames = ["lote_id","fecha_inicio","fecha_fin","actividad","area","duracion_min","rendimiento_kg","humedad_pct","defectos_kg","motivo_parada","operadores","notas"]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Generados {len(rows)} registros en {out_path}")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--n', type=int, default=200, help='Número de lotes a generar')
    p.add_argument('--out', type=str, default='data/produccion_harina.csv')
    args = p.parse_args()
    generate(args.n, args.out)

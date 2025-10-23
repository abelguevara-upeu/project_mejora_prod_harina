#!/usr/bin/env python3
"""Analizador simple de datos de producción de harina.
Calcula KPIs por actividad y sugiere mejoras sencillas.
"""
import csv
import argparse
from collections import defaultdict
from statistics import mean, stdev


def load_rows(path):
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            # convertir tipos
            r['duracion_min'] = int(r['duracion_min'])
            r['rendimiento_kg'] = int(r['rendimiento_kg'])
            r['humedad_pct'] = float(r['humedad_pct'])
            r['defectos_kg'] = int(r['defectos_kg'])
            r['operadores'] = int(r['operadores'])
            rows.append(r)
    return rows


def analyze(path):
    rows = load_rows(path)
    by_act = defaultdict(list)
    for r in rows:
        by_act[r['actividad']].append(r)

    results = {}
    for act, recs in by_act.items():
        duraciones = [x['duracion_min'] for x in recs]
        rendimientos = [x['rendimiento_kg'] for x in recs]
        defectos = [x['defectos_kg'] for x in recs]
        hums = [x['humedad_pct'] for x in recs]
        ops = [x['operadores'] for x in recs]

        results[act] = {
            'count': len(recs),
            'duracion_mean': mean(duraciones),
            'duracion_std': stdev(duraciones) if len(duraciones)>1 else 0,
            'rendimiento_mean': mean(rendimientos),
            'defectos_total': sum(defectos),
            'defectos_pct': (sum(defectos)/sum(rendimientos))*100 if sum(rendimientos)>0 else 0,
            'humedad_mean': mean(hums),
            'operadores_mean': mean(ops),
        }

    # imprimir resumen
    print("KPIs por actividad:\n")
    for act, v in sorted(results.items()):
        print(f"Actividad: {act}")
        print(f"  Registros: {v['count']}")
        print(f"  Duración media (min): {v['duracion_mean']:.1f} ± {v['duracion_std']:.1f}")
        print(f"  Rendimiento medio (kg): {v['rendimiento_mean']:.1f}")
        print(f"  Defectos totales (kg): {v['defectos_total']} ({v['defectos_pct']:.2f}% del total)")
        print(f"  Humedad media (%): {v['humedad_mean']:.2f}")
        print(f"  Operadores medios: {v['operadores_mean']:.2f}")
        # sugerencias
        sug = []
        if v['duracion_std'] > v['duracion_mean'] * 0.15:
            sug.append('Estandarizar tiempos / capacitar operadores')
        if v['humedad_mean'] > 14:
            sug.append('Revisar secado o almacenamiento de materia prima')
        if v['defectos_pct'] > 1.0:
            sug.append('Auditar control de calidad y calibración de equipos')
        if v['operadores_mean'] > 4.5:
            sug.append('Optimizar asignación de personal o automatizar tareas')
        if sug:
            print('  Sugerencias:')
            for s in sug:
                print(f'   - {s}')
        print('')


def to_markdown(results, out_path):
    with open(out_path, 'w') as f:
        f.write('# Reporte de análisis - Producción de Harina\n\n')
        f.write('Resumen de KPIs por actividad generado automáticamente.\n\n')
        for act, v in sorted(results.items()):
            f.write(f'## Actividad: {act}\n')
            f.write(f'- Registros: {v["count"]}\n')
            f.write(f'- Duración media (min): {v["duracion_mean"]:.1f} ± {v["duracion_std"]:.1f}\n')
            f.write(f'- Rendimiento medio (kg): {v["rendimiento_mean"]:.1f}\n')
            f.write(f'- Defectos totales (kg): {v["defectos_total"]} ({v["defectos_pct"]:.2f}% del total)\n')
            f.write(f'- Humedad media (%): {v["humedad_mean"]:.2f}\n')
            f.write(f'- Operadores medios: {v["operadores_mean"]:.2f}\n')
            # sugerencias
            sug = []
            if v['duracion_std'] > v['duracion_mean'] * 0.15:
                sug.append('Estandarizar tiempos / capacitar operadores')
            if v['humedad_mean'] > 14:
                sug.append('Revisar secado o almacenamiento de materia prima')
            if v['defectos_pct'] > 1.0:
                sug.append('Auditar control de calidad y calibración de equipos')
            if v['operadores_mean'] > 4.5:
                sug.append('Optimizar asignación de personal o automatizar tareas')
            if sug:
                f.write('\n**Sugerencias:**\n')
                for s in sug:
                    f.write(f'- {s}\n')
            f.write('\n---\n\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--in', dest='infile', required=True, help='CSV de entrada')
    p.add_argument('--out', dest='outfile', required=False, help='Ruta de salida Markdown (.md)')
    args = p.parse_args()
    # ejecutar analisis y opcionalmente exportar
    rows = load_rows(args.infile)
    # reutilizar lógica de analyze pero retornando results
    from collections import defaultdict
    from statistics import mean, stdev

    by_act = defaultdict(list)
    for r in rows:
        by_act[r['actividad']].append(r)

    results = {}
    for act, recs in by_act.items():
        duraciones = [x['duracion_min'] for x in recs]
        rendimientos = [x['rendimiento_kg'] for x in recs]
        defectos = [x['defectos_kg'] for x in recs]
        hums = [x['humedad_pct'] for x in recs]
        ops = [x['operadores'] for x in recs]

        results[act] = {
            'count': len(recs),
            'duracion_mean': mean(duraciones),
            'duracion_std': stdev(duraciones) if len(duraciones)>1 else 0,
            'rendimiento_mean': mean(rendimientos),
            'defectos_total': sum(defectos),
            'defectos_pct': (sum(defectos)/sum(rendimientos))*100 if sum(rendimientos)>0 else 0,
            'humedad_mean': mean(hums),
            'operadores_mean': mean(ops),
        }

    # imprimir resumen en consola (braindown)
    print("KPIs por actividad:\n")
    for act, v in sorted(results.items()):
        print(f"Actividad: {act}")
        print(f"  Registros: {v['count']}")
        print(f"  Duración media (min): {v['duracion_mean']:.1f} ± {v['duracion_std']:.1f}")
        print(f"  Rendimiento medio (kg): {v['rendimiento_mean']:.1f}")
        print(f"  Defectos totales (kg): {v['defectos_total']} ({v['defectos_pct']:.2f}% del total)")
        print(f"  Humedad media (%): {v['humedad_mean']:.2f}")
        print(f"  Operadores medios: {v['operadores_mean']:.2f}")
        sug = []
        if v['duracion_std'] > v['duracion_mean'] * 0.15:
            sug.append('Estandarizar tiempos / capacitar operadores')
        if v['humedad_mean'] > 14:
            sug.append('Revisar secado o almacenamiento de materia prima')
        if v['defectos_pct'] > 1.0:
            sug.append('Auditar control de calidad y calibración de equipos')
        if v['operadores_mean'] > 4.5:
            sug.append('Optimizar asignación de personal o automatizar tareas')
        if sug:
            print('  Sugerencias:')
            for s in sug:
                print(f'   - {s}')
        print('')

    if args.outfile:
        to_markdown(results, args.outfile)
        print(f'Reporte Markdown escrito en {args.outfile}')

#!/usr/bin/env python3
"""Exportar subconjuntos formateados para análisis en Minitab.
Genera CSVs en una carpeta de salida con formatos pensados para:
- Variabilidad en tiempos de molienda
- Altos defectos en limpieza
- Desbalance de operadores (registro y agregados)

Uso:
  python3 scripts/export_minitab.py --in data/produccion_harina.csv --out-dir data/minitab_exports
"""
import csv
import os
import argparse
from datetime import datetime
from collections import defaultdict


def infer_shift(ts_iso):
    h = datetime.fromisoformat(ts_iso).hour
    if 6 <= h < 14:
        return 'Morning'
    if 14 <= h < 22:
        return 'Afternoon'
    return 'Night'


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def export(infile, out_dir):
    ensure_dir(out_dir)
    rows = []
    with open(infile) as f:
        reader = csv.DictReader(f)
        for r in reader:
            # typed fields
            r['duracion_min'] = int(r['duracion_min'])
            r['rendimiento_kg'] = int(r['rendimiento_kg'])
            r['humedad_pct'] = float(r['humedad_pct'])
            r['defectos_kg'] = int(r['defectos_kg'])
            r['operadores'] = int(r['operadores'])
            rows.append(r)

    # 1) Variabilidad en tiempos de molienda
    mol_rows = [r for r in rows if r['actividad'].lower() == 'molienda']
    mol_out = os.path.join(out_dir, 'minitab_molienda_variabilidad.csv')
    with open(mol_out, 'w', newline='') as f:
        fieldnames = ['lote_id','fecha_inicio','fecha_fin','duracion_min','operadores','shift','humedad_pct','motivo_parada','notas']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in mol_rows:
            writer.writerow({
                'lote_id': r['lote_id'],
                'fecha_inicio': r['fecha_inicio'],
                'fecha_fin': r['fecha_fin'],
                'duracion_min': r['duracion_min'],
                'operadores': r['operadores'],
                'shift': infer_shift(r['fecha_inicio']),
                'humedad_pct': r['humedad_pct'],
                'motivo_parada': r.get('motivo_parada',''),
                'notas': r.get('notas',''),
            })

    # 2) Altos defectos en limpieza
    limp_rows = [r for r in rows if r['actividad'].lower() == 'limpieza']
    limp_out = os.path.join(out_dir, 'minitab_limpieza_defectos.csv')
    with open(limp_out, 'w', newline='') as f:
        fieldnames = ['lote_id','fecha_inicio','duracion_min','rendimiento_kg','defectos_kg','defectos_pct','humedad_pct','motivo_parada','operadores','notas']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in limp_rows:
            dpct = (r['defectos_kg'] / r['rendimiento_kg'] * 100) if r['rendimiento_kg']>0 else 0
            writer.writerow({
                'lote_id': r['lote_id'],
                'fecha_inicio': r['fecha_inicio'],
                'duracion_min': r['duracion_min'],
                'rendimiento_kg': r['rendimiento_kg'],
                'defectos_kg': r['defectos_kg'],
                'defectos_pct': round(dpct,4),
                'humedad_pct': r['humedad_pct'],
                'motivo_parada': r.get('motivo_parada',''),
                'operadores': r['operadores'],
                'notas': r.get('notas',''),
            })

    # 3) Desbalance de operadores
    op_out = os.path.join(out_dir, 'minitab_operadores_desbalance.csv')
    with open(op_out, 'w', newline='') as f:
        fieldnames = ['fecha','area','actividad','lote_id','operadores','shift']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            # date only for aggregation
            date = datetime.fromisoformat(r['fecha_inicio']).date().isoformat()
            writer.writerow({
                'fecha': date,
                'area': r['area'],
                'actividad': r['actividad'],
                'lote_id': r['lote_id'],
                'operadores': r['operadores'],
                'shift': infer_shift(r['fecha_inicio']),
            })

    # 3b) agregado por fecha+area (útil para Minitab: ANOVA/boxplot por area/fecha)
    agg = defaultdict(lambda: {'total_operadores':0,'count':0})
    for r in rows:
        date = datetime.fromisoformat(r['fecha_inicio']).date().isoformat()
        key = (date, r['area'])
        agg[key]['total_operadores'] += r['operadores']
        agg[key]['count'] += 1
    agg_out = os.path.join(out_dir, 'minitab_operadores_agg.csv')
    with open(agg_out, 'w', newline='') as f:
        fieldnames = ['fecha','area','total_operadores','registros_count','operadores_mean']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for (date, area), v in sorted(agg.items()):
            mean_ops = round(v['total_operadores']/v['count'],4) if v['count']>0 else 0
            writer.writerow({
                'fecha': date,
                'area': area,
                'total_operadores': v['total_operadores'],
                'registros_count': v['count'],
                'operadores_mean': mean_ops,
            })

    print('Archivos generados:')
    print(' -', mol_out)
    print(' -', limp_out)
    print(' -', op_out)
    print(' -', agg_out)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--in', dest='infile', required=True, help='CSV de entrada')
    p.add_argument('--out-dir', dest='outdir', required=False, default='data/minitab_exports', help='Directorio de salida')
    args = p.parse_args()
    export(args.infile, args.outdir)

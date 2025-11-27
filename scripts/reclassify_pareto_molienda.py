#!/usr/bin/env python3
"""Reclasifica entradas de 'Otros motivos' en el CSV de variabilidad y genera Pareto re-clasificado.

Salida:
 - data/figs/pareto_molienda_table_reclassified.csv
 - data/figs/pareto_molienda_reclassified.png
 - data/figs/pareto_molienda_reclassification_candidates.csv (filas con nueva categoría)

Este script no modifica el CSV original.
"""
import csv
import os
import re
from collections import Counter, OrderedDict
import matplotlib.pyplot as plt

INPUT = 'data/minitab_exports/minitab_molienda_variabilidad.csv'
OUT_DIR = 'data/figs'
os.makedirs(OUT_DIR, exist_ok=True)


KEYWORDS = {
    'Mantenimiento correctivo': [r'mantenimiento', r'correctiv'],
    'Falla eléctrica': [r'falla[_\- ]?elect', r'electric', r'electr'],
    'Calibración': [r'calibr', r'calibraci'],
    'Humedad alta': [r'humedad', r'humedadalta'],
    'Defectos detectados': [r'defect', r'defectos'],
    'Atasco / bloqueo': [r'atasc', r'bloque'],
}


def detect_category(row):
    motivo = (row.get('motivo_parada') or '').lower()
    notas = (row.get('notas') or '').lower()
    text = ' '.join([motivo, notas])

    # direct keyword match
    for cat, keys in KEYWORDS.items():
        for k in keys:
            if re.search(k, text):
                return cat

    # humidity threshold
    try:
        hum = float(row.get('humedad_pct') or 0)
        if hum >= 15:
            return 'Humedad alta'
    except:
        pass

    # look for common short words
    if 'mante' in text:
        return 'Mantenimiento correctivo'
    if 'falla' in text or 'elect' in text:
        return 'Falla eléctrica'
    if 'calib' in text:
        return 'Calibración'
    if 'defect' in text:
        return 'Defectos detectados'
    if 'atas' in text or 'bloq' in text:
        return 'Atasco / bloqueo'

    return 'Sin registrar'


def main():
    rows = list(csv.DictReader(open(INPUT)))
    n = len(rows)

    # Apply detection to all rows and collect counts
    counts = Counter()
    reclassified_rows = []
    for r in rows:
        cat = detect_category(r)
        counts[cat] += 1
        newrow = dict(r)
        newrow['categoria_mapeada'] = cat
        reclassified_rows.append(newrow)

    # write candidate file with mapeo (for traceability)
    cand_path = os.path.join(OUT_DIR, 'pareto_molienda_reclassification_candidates.csv')
    with open(cand_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(reclassified_rows[0].keys()))
        w.writeheader()
        for r in reclassified_rows:
            w.writerow(r)

    # create ordered pareto
    ordered = OrderedDict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
    labels = list(ordered.keys())
    freqs = list(ordered.values())
    perc = [f / n * 100 for f in freqs]
    cum = []
    s = 0
    for p in perc:
        s += p
        cum.append(s)

    # write pareto table reclassified
    out_table = os.path.join(OUT_DIR, 'pareto_molienda_table_reclassified.csv')
    with open(out_table, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Causa a Raíz', 'Frecuencia del Evento', 'Participación', 'Participación Acumulada (%)'])
        for c, fcount, p, ac in zip(labels, freqs, perc, cum):
            w.writerow([c, fcount, f'{p:.0f}%', f'{ac:.0f}%'])

    # plot
    fig, ax1 = plt.subplots(figsize=(9,5))
    bars = ax1.bar(labels, freqs, color='tab:blue', alpha=0.9)
    for i, bar in enumerate(bars):
        if i < 3:
            bar.set_color('#0b8043')
    ax1.set_ylabel('Frecuencia', fontweight='bold')
    ax1.set_xlabel('Causa raíz')
    ax1.tick_params(axis='x', rotation=25)
    ax2 = ax1.twinx()
    ax2.plot(labels, cum, color='#ff7f0e', marker='o', linewidth=2)
    ax2.set_ylabel('Porcentaje acumulado (%)', fontweight='bold')
    ax2.set_ylim(0, 105)
    for i, (fcount, pct) in enumerate(zip(freqs, perc)):
        ax1.text(i, fcount + max(freqs)*0.02, f'{pct:.0f}%', ha='center', fontsize=9)
    plt.title('Pareto Reclasificado - Causas de variabilidad (Molienda)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    out_png = os.path.join(OUT_DIR, 'pareto_molienda_reclassified.png')
    plt.savefig(out_png, dpi=200)
    plt.close()

    print('Reclasificación completa.')
    print('Total filas analizadas:', n)
    for c, fcount, p, ac in zip(labels, freqs, perc, cum):
        print(f'  {c}: {fcount} ({p:.1f}%), acumulado {ac:.1f}%')


if __name__ == '__main__':
    main()

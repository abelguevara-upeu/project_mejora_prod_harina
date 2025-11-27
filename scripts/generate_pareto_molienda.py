#!/usr/bin/env python3
"""Genera tabla y gráfico Pareto para causas de variabilidad de molienda.
Analiza solo el archivo `data/minitab_exports/minitab_molienda_variabilidad.csv`.
Guarda outputs en `data/figs/pareto_molienda.png` y `data/figs/pareto_molienda_table.csv`.
"""
import csv
import os
from collections import Counter, OrderedDict
import matplotlib.pyplot as plt

INPUT = 'data/minitab_exports/minitab_molienda_variabilidad.csv'
OUT_DIR = 'data/figs'
os.makedirs(OUT_DIR, exist_ok=True)


def categorize_row(row):
    motivo = (row.get('motivo_parada') or '').strip().lower()
    notas = (row.get('notas') or '').strip().lower()
    combined = ' '.join([motivo, notas])

    # Categorías y palabras clave
    mapping = [
        ('Mantenimiento correctivo', ['mantenimiento', 'mantenimiento correctivo']),
        ('Falla eléctrica', ['falla_electrica', 'falla electrica', 'falla eléctrica', 'falla-electrica']),
        ('Calibración', ['calibracion', 'calibración']),
        ('Humedad alta', ['humedad alta', 'humedad alta', 'humedadalta']),
        ('Defectos detectados', ['defectos detectados', 'defectos']),
        ('Atasco / bloqueo', ['atasco', 'atascado', 'bloqueo']),
        ('Otros motivos', [])
    ]

    for cat, keys in mapping[:-1]:
        for k in keys:
            if k in combined:
                return cat
    # Si no coincide con keywords, revisar humedad_pct alta
    try:
        hum = float(row.get('humedad_pct') or 0)
        if hum >= 15:
            return 'Humedad alta'
    except:
        pass

    if combined:
        # map some free-text common words
        if 'calibr' in combined:
            return 'Calibración'
        if 'mantenimiento' in combined:
            return 'Mantenimiento correctivo'
        if 'falla' in combined or 'electr' in combined:
            return 'Falla eléctrica'
        if 'humedad' in combined:
            return 'Humedad alta'
        if 'defect' in combined:
            return 'Defectos detectados'
        if 'atasc' in combined or 'bloque' in combined:
            return 'Atasco / bloqueo'

    return 'Otros motivos'


def main():
    rows = list(csv.DictReader(open(INPUT)))
    n = len(rows)
    counts = Counter()

    for r in rows:
        cat = categorize_row(r)
        counts[cat] += 1

    # Ensure consistent ordering: descending
    ordered = OrderedDict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    labels = list(ordered.keys())
    freqs = list(ordered.values())
    perc = [f / n * 100 for f in freqs]
    cum = []
    s = 0
    for p in perc:
        s += p
        cum.append(s)

    # Write summary CSV in Pareto format similar to requested table
    out_table = os.path.join(OUT_DIR, 'pareto_molienda_table.csv')
    with open(out_table, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Causa a Raíz', 'Frecuencia del Evento', 'Participación', 'Participación Acumulada (%)'])
        for c, fcount, p, ac in zip(labels, freqs, perc, cum):
            w.writerow([c, fcount, f'{p:.0f}%', f'{ac:.0f}%'])

    # Plot Pareto
    fig, ax1 = plt.subplots(figsize=(9,5))
    bars = ax1.bar(labels, freqs, color='tab:blue', alpha=0.9)

    # Color top 3 differently
    for i, bar in enumerate(bars):
        if i < 3:
            bar.set_color('#0b8043')

    ax1.set_ylabel('Frecuencia', fontweight='bold')
    ax1.set_xlabel('Causa raíz')

    ax2 = ax1.twinx()
    ax2.plot(labels, cum, color='#ff7f0e', marker='o', linewidth=2)
    ax2.set_ylabel('Porcentaje acumulado (%)', fontweight='bold')
    ax2.set_ylim(0, 105)

    # Annotate percentages above bars
    for i, (fcount, pct) in enumerate(zip(freqs, perc)):
        ax1.text(i, fcount + max(freqs)*0.02, f'{pct:.1f}%', ha='center', fontsize=9)

    plt.title('Pareto - Causas de variabilidad (Molienda)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    out_png = os.path.join(OUT_DIR, 'pareto_molienda.png')
    plt.savefig(out_png, dpi=200)
    plt.close()

    # Print summary
    print('Total filas analizadas:', n)
    print('Resumen Pareto:')
    for c, fcount, p, ac in zip(labels, freqs, perc, cum):
        print(f'  {c}: {fcount} ({p:.2f}%), acumulado {ac:.2f}%')

if __name__ == '__main__':
    main()

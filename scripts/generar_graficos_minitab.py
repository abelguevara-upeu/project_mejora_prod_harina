#!/usr/bin/env python3
"""Genera gráficos de control y capacidad para análisis Lean Six Sigma.
Gráficos: I-MR, Capacidad Normal, Normal Probability Plot, Box Plot, Scatter.
"""
import csv
import os
import math
from statistics import mean, stdev
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuración estilo
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10

def load_data(path):
    """Carga datos de molienda."""
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r['actividad'].lower() == 'molienda':
                # Inferir turno
                h = datetime.fromisoformat(r['fecha_inicio']).hour
                if 6 <= h < 14:
                    shift = 'Morning'
                elif 14 <= h < 22:
                    shift = 'Afternoon'
                else:
                    shift = 'Night'

                rows.append({
                    'lote_id': r['lote_id'],
                    'duracion_min': int(r['duracion_min']),
                    'humedad_pct': float(r['humedad_pct']),
                    'shift': shift,
                    'fecha': datetime.fromisoformat(r['fecha_inicio'])
                })
    return sorted(rows, key=lambda x: x['fecha'])


def plot_imr_chart(data, output_dir, lse=140, lie=100):
    """Gráfico I-MR (Individuales y Rangos Móviles)."""
    duraciones = [x['duracion_min'] for x in data]
    n = len(duraciones)

    # Calcular Moving Ranges
    mr = [abs(duraciones[i] - duraciones[i-1]) for i in range(1, n)]
    mr_mean = mean(mr)

    # Límites I-Chart
    d2 = 1.128  # para n=2
    x_bar = mean(duraciones)
    ucl_i = x_bar + 2.66 * mr_mean
    lcl_i = x_bar - 2.66 * mr_mean

    # Límites MR-Chart
    d3 = 0  # para n=2
    D4 = 3.267
    ucl_mr = D4 * mr_mean
    lcl_mr = d3 * mr_mean

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # I-Chart
    ax1.plot(range(1, n+1), duraciones, marker='o', linestyle='-', color='blue', markersize=4)
    ax1.axhline(x_bar, color='green', linestyle='-', linewidth=2, label=f'Media = {x_bar:.2f}')
    ax1.axhline(ucl_i, color='red', linestyle='--', linewidth=1.5, label=f'UCL = {ucl_i:.2f}')
    ax1.axhline(lcl_i, color='red', linestyle='--', linewidth=1.5, label=f'LCL = {lcl_i:.2f}')
    ax1.axhline(lse, color='orange', linestyle=':', linewidth=2, label=f'LSE = {lse}')
    ax1.axhline(lie, color='orange', linestyle=':', linewidth=2, label=f'LIE = {lie}')

    # Marcar puntos fuera de control
    for i, val in enumerate(duraciones):
        if val > ucl_i or val < lcl_i:
            ax1.plot(i+1, val, 'ro', markersize=8, markerfacecolor='red')

    ax1.set_xlabel('Número de Observación (Lote)')
    ax1.set_ylabel('Duración (min)')
    ax1.set_title('Gráfico de Control I (Individuales) - Tiempos de Molienda', fontweight='bold', fontsize=12)
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, alpha=0.3)

    # MR-Chart
    ax2.plot(range(2, n+1), mr, marker='s', linestyle='-', color='purple', markersize=4)
    ax2.axhline(mr_mean, color='green', linestyle='-', linewidth=2, label=f'MR Media = {mr_mean:.2f}')
    ax2.axhline(ucl_mr, color='red', linestyle='--', linewidth=1.5, label=f'UCL = {ucl_mr:.2f}')
    if lcl_mr > 0:
        ax2.axhline(lcl_mr, color='red', linestyle='--', linewidth=1.5, label=f'LCL = {lcl_mr:.2f}')

    ax2.set_xlabel('Número de Observación (Lote)')
    ax2.set_ylabel('Rango Móvil (min)')
    ax2.set_title('Gráfico de Control MR (Rangos Móviles)', fontweight='bold', fontsize=12)
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'grafico_imr.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # Retornar info de puntos fuera de control
    out_of_control = [(i+1, data[i]['lote_id'], duraciones[i]) for i, val in enumerate(duraciones) if val > ucl_i or val < lcl_i]
    return out_of_control, x_bar, ucl_i, lcl_i


def plot_capability(data, output_dir, lse=140, lie=100, target=120):
    """Gráfico de Capacidad del Proceso (Normal)."""
    duraciones = [x['duracion_min'] for x in data]
    mu = mean(duraciones)
    sigma = stdev(duraciones)

    # Calcular Cp, Cpk
    cp = (lse - lie) / (6 * sigma)
    cpk_upper = (lse - mu) / (3 * sigma)
    cpk_lower = (mu - lie) / (3 * sigma)
    cpk = min(cpk_upper, cpk_lower)

    # % fuera de especificación
    out_spec = sum(1 for d in duraciones if d < lie or d > lse)
    pct_out = (out_spec / len(duraciones)) * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Histograma con curva normal
    ax1.hist(duraciones, bins=20, density=True, alpha=0.6, color='skyblue', edgecolor='black')

    # Curva normal
    import numpy as np
    x = np.linspace(min(duraciones)-10, max(duraciones)+10, 200)
    from math import pi, exp
    normal_curve = [1/(sigma*math.sqrt(2*pi)) * exp(-0.5*((xi-mu)/sigma)**2) for xi in x]
    ax1.plot(x, normal_curve, 'b-', linewidth=2, label='Distribución Normal')

    # Límites de especificación
    ax1.axvline(lse, color='red', linestyle='--', linewidth=2, label=f'LSE = {lse}')
    ax1.axvline(lie, color='red', linestyle='--', linewidth=2, label=f'LIE = {lie}')
    ax1.axvline(mu, color='green', linestyle='-', linewidth=2, label=f'Media = {mu:.2f}')
    ax1.axvline(target, color='orange', linestyle=':', linewidth=2, label=f'Target = {target}')

    ax1.set_xlabel('Duración (min)', fontweight='bold')
    ax1.set_ylabel('Densidad', fontweight='bold')
    ax1.set_title('Capacidad del Proceso - Distribución', fontweight='bold', fontsize=12)
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Tabla de indicadores
    ax2.axis('off')
    tabla_data = [
        ['Indicador', 'Valor', 'Interpretación'],
        ['N (muestras)', f'{len(duraciones)}', ''],
        ['Media (μ)', f'{mu:.2f} min', ''],
        ['Desv. Std (σ)', f'{sigma:.2f} min', ''],
        ['CV', f'{(sigma/mu)*100:.2f}%', ''],
        ['', '', ''],
        ['Cp', f'{cp:.3f}', 'No capaz' if cp < 1.33 else 'Capaz'],
        ['Cpk', f'{cpk:.3f}', 'No capaz' if cpk < 1.33 else 'Capaz'],
        ['', '', ''],
        ['LSE', f'{lse} min', ''],
        ['LIE', f'{lie} min', ''],
        ['Target', f'{target} min', ''],
        ['', '', ''],
        ['% Fuera Espec.', f'{pct_out:.2f}%', 'Inaceptable' if pct_out > 0.5 else 'Aceptable'],
        ['PPM', f'{int(pct_out*10000)}', ''],
    ]

    table = ax2.table(cellText=tabla_data, loc='center', cellLoc='left', colWidths=[0.35, 0.25, 0.4])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # Color header
    for i in range(3):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Color indicators
    table[(6, 0)].set_facecolor('#E3F2FD')
    table[(7, 0)].set_facecolor('#E3F2FD')
    table[(13, 0)].set_facecolor('#FFEBEE')

    ax2.set_title('Indicadores de Capacidad', fontweight='bold', fontsize=12, pad=20)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'grafico_capacidad.png'), dpi=300, bbox_inches='tight')
    plt.close()

    return cp, cpk, pct_out


def plot_normal_probability(data, output_dir):
    """Gráfico de Probabilidad Normal (Q-Q plot)."""
    duraciones = sorted([x['duracion_min'] for x in data])
    n = len(duraciones)

    # Cuantiles teóricos normales
    from math import erf, sqrt
    def norm_ppf(p):
        """Aproximación inversa normal."""
        if p <= 0 or p >= 1:
            return 0
        t = sqrt(-2 * math.log(1 - p)) if p > 0.5 else sqrt(-2 * math.log(p))
        c0, c1, c2 = 2.515517, 0.802853, 0.010328
        d1, d2, d3 = 1.432788, 0.189269, 0.001308
        z = t - (c0 + c1*t + c2*t*t) / (1 + d1*t + d2*t*t + d3*t*t*t)
        return z if p > 0.5 else -z

    # Probabilidades empíricas
    probs = [(i - 0.5) / n for i in range(1, n+1)]
    theoretical_quantiles = [norm_ppf(p) for p in probs]

    # Estandarizar datos
    mu = mean(duraciones)
    sigma = stdev(duraciones)
    standardized = [(d - mu) / sigma for d in duraciones]

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(theoretical_quantiles, standardized, alpha=0.6, s=30, color='blue', edgecolor='black')

    # Línea de referencia (y=x)
    min_val = min(min(theoretical_quantiles), min(standardized))
    max_val = max(max(theoretical_quantiles), max(standardized))
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Línea Normal Ideal')

    ax.set_xlabel('Cuantiles Teóricos (Normal Estándar)', fontweight='bold')
    ax.set_ylabel('Cuantiles Empíricos (Estandarizados)', fontweight='bold')
    ax.set_title('Gráfico de Probabilidad Normal (Q-Q Plot)', fontweight='bold', fontsize=12)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)

    # Anotación sobre normalidad
    textstr = 'Si los puntos siguen la línea roja,\nlos datos son normales.\nDesviaciones indican no-normalidad.'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=props)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'grafico_normalidad.png'), dpi=300, bbox_inches='tight')
    plt.close()


def plot_boxplot_by_shift(data, output_dir):
    """Box Plot de duración por turno."""
    shifts = ['Morning', 'Afternoon', 'Night']
    data_by_shift = {s: [x['duracion_min'] for x in data if x['shift'] == s] for s in shifts}

    fig, ax = plt.subplots(figsize=(10, 6))

    # Crear boxplot
    bp = ax.boxplot([data_by_shift[s] for s in shifts], labels=shifts, patch_artist=True,
                     notch=True, widths=0.5)

    # Colores
    colors = ['#FF9999', '#99CCFF', '#99FF99']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)

    # Estadísticas
    for i, shift in enumerate(shifts, 1):
        datos = data_by_shift[shift]
        media = mean(datos)
        ax.text(i, media, f'μ={media:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax.set_xlabel('Turno', fontweight='bold', fontsize=11)
    ax.set_ylabel('Duración (min)', fontweight='bold', fontsize=11)
    ax.set_title('Distribución de Tiempos de Molienda por Turno', fontweight='bold', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')

    # Leyenda de interpretación
    textstr = 'Caja: Q1-Q3 (50% central)\nLínea: Mediana\nBigotes: Min-Max (sin outliers)\n◆ Outliers'
    props = dict(boxstyle='round', facecolor='lightblue', alpha=0.3)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=8,
            verticalalignment='top', bbox=props)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'grafico_boxplot_turnos.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # Retornar estadísticas por turno
    stats = {}
    for shift in shifts:
        datos = data_by_shift[shift]
        stats[shift] = {
            'n': len(datos),
            'mean': mean(datos),
            'std': stdev(datos) if len(datos) > 1 else 0,
        }
    return stats


def plot_scatter_humidity(data, output_dir):
    """Scatter plot: Humedad vs Duración."""
    humedad = [x['humedad_pct'] for x in data]
    duracion = [x['duracion_min'] for x in data]

    # Calcular correlación
    n = len(humedad)
    from statistics import mean as calc_mean
    mean_h = calc_mean(humedad)
    mean_d = calc_mean(duracion)

    cov = sum((humedad[i] - mean_h) * (duracion[i] - mean_d) for i in range(n)) / (n - 1)
    std_h = stdev(humedad)
    std_d = stdev(duracion)
    r = cov / (std_h * std_d)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(humedad, duracion, alpha=0.6, s=40, color='teal', edgecolor='black')

    # Línea de tendencia (regresión lineal simple)
    b = cov / (std_h ** 2)
    a = mean_d - b * mean_h
    x_line = [min(humedad), max(humedad)]
    y_line = [a + b*x for x in x_line]
    ax.plot(x_line, y_line, 'r--', linewidth=2, label=f'Regresión: y={a:.2f}+{b:.2f}x')

    ax.set_xlabel('Humedad Materia Prima (%)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Duración de Molienda (min)', fontweight='bold', fontsize=12)
    ax.set_title('Correlación: Humedad vs Duración de Molienda', fontweight='bold', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=11)

    # Anotación correlación - más grande y legible
    textstr = f'Correlación (r) = {r:.3f}\n'
    if abs(r) < 0.3:
        textstr += 'Correlación débil'
        color_fondo = 'lightcoral'
    elif abs(r) < 0.7:
        textstr += 'Correlación moderada'
        color_fondo = 'lightyellow'
    else:
        textstr += 'Correlación fuerte'
        color_fondo = 'lightgreen'

    textstr += f'\n\nEcuación:\ny = {a:.2f} + {b:.2f}×x'

    props = dict(boxstyle='round', facecolor=color_fondo, alpha=0.7, edgecolor='black', linewidth=2)
    ax.text(0.03, 0.97, textstr, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', bbox=props, fontweight='bold', family='monospace')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'grafico_scatter_humedad.png'), dpi=300, bbox_inches='tight')
    plt.close()

    return r, a, b


if __name__ == '__main__':
    # Configuración
    DATA_PATH = 'data/produccion_harina.csv'
    OUTPUT_DIR = 'data/figs'
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    LSE = 140
    LIE = 100
    TARGET = 120

    # Cargar datos
    print("Cargando datos...")
    data = load_data(DATA_PATH)
    print(f"Datos cargados: {len(data)} lotes de molienda\n")

    # 1. Gráfico I-MR
    print("Generando gráfico I-MR...")
    out_of_control, x_bar, ucl, lcl = plot_imr_chart(data, OUTPUT_DIR, LSE, LIE)
    print(f"  Media: {x_bar:.2f} min")
    print(f"  UCL: {ucl:.2f}, LCL: {lcl:.2f}")
    print(f"  Puntos fuera de control: {len(out_of_control)}")
    if out_of_control:
        print(f"  Lotes: {', '.join([x[1] for x in out_of_control[:5]])}")

    # 2. Capacidad del Proceso
    print("\nGenerando gráfico de capacidad...")
    cp, cpk, pct_out = plot_capability(data, OUTPUT_DIR, LSE, LIE, TARGET)
    print(f"  Cp: {cp:.3f}, Cpk: {cpk:.3f}")
    print(f"  % fuera de especificación: {pct_out:.2f}%")

    # 3. Probabilidad Normal
    print("\nGenerando gráfico de probabilidad normal...")
    plot_normal_probability(data, OUTPUT_DIR)
    print("  Inspeccione visualmente si los puntos siguen la línea.")

    # 4. Box Plot por turno
    print("\nGenerando box plot por turno...")
    stats_turnos = plot_boxplot_by_shift(data, OUTPUT_DIR)
    for shift, s in stats_turnos.items():
        print(f"  {shift}: n={s['n']}, media={s['mean']:.2f}, std={s['std']:.2f}")

    # 5. Scatter Humedad
    print("\nGenerando scatter humedad vs duración...")
    r, a, b = plot_scatter_humidity(data, OUTPUT_DIR)
    print(f"  Correlación: r={r:.3f}")
    print(f"  Ecuación: Duración = {a:.2f} + {b:.2f} × Humedad")

    print(f"\n✅ Todos los gráficos guardados en: {OUTPUT_DIR}/")
    print("Archivos generados:")
    print("  - grafico_imr.png")
    print("  - grafico_capacidad.png")
    print("  - grafico_normalidad.png")
    print("  - grafico_boxplot_turnos.png")
    print("  - grafico_scatter_humedad.png")

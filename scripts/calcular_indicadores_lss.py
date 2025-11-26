#!/usr/bin/env python3
"""Cálculo de indicadores financieros y de capacidad del proceso para el proyecto LSS.
Genera valores de ROI, VAN, TIR, Payback y métricas Six Sigma (Cp, Cpk, nivel sigma).
"""
import csv
import math
import random
from statistics import mean, stdev

def load_molienda_data(path):
    """Carga datos de molienda del CSV."""
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r['actividad'].lower() == 'molienda':
                rows.append({
                    'duracion_min': int(r['duracion_min']),
                    'humedad_pct': float(r['humedad_pct']),
                    'defectos_kg': int(r['defectos_kg']),
                })
    return rows


def calcular_capacidad(data, lse, lie, target):
    """Calcula indicadores de capacidad del proceso (Cp, Cpk, Pp, Ppk, nivel sigma)."""
    duraciones = [x['duracion_min'] for x in data]
    mu = mean(duraciones)
    sigma = stdev(duraciones)

    # Cp y Cpk
    cp = (lse - lie) / (6 * sigma)
    cpk_upper = (lse - mu) / (3 * sigma)
    cpk_lower = (mu - lie) / (3 * sigma)
    cpk = min(cpk_upper, cpk_lower)

    # Pp y Ppk (asumimos mismo sigma para simplicidad)
    pp = cp
    ppk = cpk

    # % defectos
    defects = sum(1 for d in duraciones if d < lie or d > lse)
    pct_defects = (defects / len(duraciones)) * 100

    # Nivel sigma (aproximado)
    # DPMO = defects per million opportunities
    dpmo = (defects / len(duraciones)) * 1_000_000
    if dpmo >= 1_000_000:
        nivel_sigma = 0
    elif dpmo == 0:
        nivel_sigma = 6.0  # Perfecto
    else:
        # Aproximación inversa normal estándar simplificada
        p = 1 - dpmo/1_000_000
        # Aproximación de Beasley-Springer-Moro para ppf
        if p > 0.5:
            t = math.sqrt(-2 * math.log(1 - p))
        else:
            t = math.sqrt(-2 * math.log(p))
        c0, c1, c2 = 2.515517, 0.802853, 0.010328
        d1, d2, d3 = 1.432788, 0.189269, 0.001308
        nivel_sigma = t - (c0 + c1*t + c2*t*t) / (1 + d1*t + d2*t*t + d3*t*t*t)
        if p < 0.5:
            nivel_sigma = -nivel_sigma

    return {
        'n': len(duraciones),
        'mean': mu,
        'std': sigma,
        'cv': (sigma/mu)*100,
        'cp': cp,
        'cpk': cpk,
        'pp': pp,
        'ppk': ppk,
        'pct_defects': pct_defects,
        'nivel_sigma': nivel_sigma,
    }


def calcular_financiero(inversion, ahorro_anual, tasa_descuento=0.12, horizonte=3):
    """Calcula VAN, TIR, ROI, Payback."""
    flujos = [-inversion] + [ahorro_anual] * horizonte

    # VAN
    van = sum(flujos[t] / ((1 + tasa_descuento)**t) for t in range(len(flujos)))

    # TIR (aproximación iterativa)
    tir = None
    rate = 0.0
    while rate < 2.0:
        van_test = sum(flujos[t] / ((1 + rate)**t) for t in range(len(flujos)))
        if van_test <= 0:
            tir = rate
            break
        rate += 0.001

    # ROI
    beneficio_total = ahorro_anual * horizonte
    roi = ((beneficio_total - inversion) / inversion) * 100

    # Payback
    acumulado = 0
    payback_meses = 0
    ahorro_mensual = ahorro_anual / 12
    for mes in range(1, 100):
        acumulado += ahorro_mensual
        if acumulado >= inversion:
            payback_meses = mes
            break

    return {
        'van': van,
        'tir': tir * 100 if tir else None,
        'roi': roi,
        'payback_meses': payback_meses,
    }


if __name__ == '__main__':
    # Cargar datos
    data_actual = load_molienda_data('data/produccion_harina.csv')

    # Parámetros especificación
    LSE = 140  # min
    LIE = 100  # min
    TARGET = 120  # min

    # Calcular capacidad actual
    cap_actual = calcular_capacidad(data_actual, LSE, LIE, TARGET)

    print("=== INDICADORES DE CAPACIDAD DEL PROCESO (ACTUAL) ===\n")
    print(f"N (muestras):        {cap_actual['n']}")
    print(f"Media (μ):           {cap_actual['mean']:.2f} min")
    print(f"Desv. Estándar (σ):  {cap_actual['std']:.2f} min")
    print(f"CV:                  {cap_actual['cv']:.2f}%")
    print(f"Cp:                  {cap_actual['cp']:.3f}")
    print(f"Cpk:                 {cap_actual['cpk']:.3f}")
    print(f"Pp:                  {cap_actual['pp']:.3f}")
    print(f"Ppk:                 {cap_actual['ppk']:.3f}")
    print(f"% Defectos:          {cap_actual['pct_defects']:.2f}%")
    print(f"Nivel Sigma:         {cap_actual['nivel_sigma']:.2f}σ")

    # Simular proceso mejorado
    print("\n=== PROYECCIÓN PROCESO MEJORADO ===\n")
    # Crear datos sintéticos mejorados (sigma reducida a 8, media centrada en 120)
    random.seed(42)
    data_mejorado = [{'duracion_min': max(90, int(random.gauss(120, 8)))} for _ in range(200)]
    cap_mejorado = calcular_capacidad(data_mejorado, LSE, LIE, TARGET)

    print(f"Media proyectada:    {cap_mejorado['mean']:.2f} min")
    print(f"Sigma proyectada:    {cap_mejorado['std']:.2f} min")
    print(f"Cp proyectado:       {cap_mejorado['cp']:.3f}")
    print(f"Cpk proyectado:      {cap_mejorado['cpk']:.3f}")
    print(f"% Defectos:          {cap_mejorado['pct_defects']:.2f}%")
    print(f"Nivel Sigma:         {cap_mejorado['nivel_sigma']:.2f}σ")

    # Indicadores financieros
    print("\n=== INDICADORES FINANCIEROS ===\n")
    INVERSION = 45_300  # S/
    AHORRO_ANUAL = 166_320  # S/

    fin = calcular_financiero(INVERSION, AHORRO_ANUAL)

    print(f"Inversión total:     S/ {INVERSION:,.2f}")
    print(f"Ahorro anual:        S/ {AHORRO_ANUAL:,.2f}")
    print(f"VAN (3 años, 12%):   S/ {fin['van']:,.2f}")
    print(f"TIR:                 {fin['tir']:.2f}%" if fin['tir'] else "TIR: >200%")
    print(f"ROI:                 {fin['roi']:.2f}%")
    print(f"Payback:             {fin['payback_meses']} meses ({fin['payback_meses']/12:.1f} años)")

    print("\n=== RESUMEN MEJORA ===\n")
    print(f"Reducción σ:         {cap_actual['std']:.2f} → {cap_mejorado['std']:.2f} min (-{((cap_actual['std']-cap_mejorado['std'])/cap_actual['std']*100):.1f}%)")
    print(f"Mejora Cpk:          {cap_actual['cpk']:.3f} → {cap_mejorado['cpk']:.3f} (+{((cap_mejorado['cpk']-cap_actual['cpk'])/cap_actual['cpk']*100):.1f}%)")
    print(f"Reducción defectos:  {cap_actual['pct_defects']:.2f}% → {cap_mejorado['pct_defects']:.2f}% (-{cap_actual['pct_defects']-cap_mejorado['pct_defects']:.2f} pp)")

# -*- coding: utf-8 -*-
"""
Análisis Bivariado
Encuesta: Talleres de Tecnología y Motivación STEM
Autor: Erick Malla Sisalima
Practicum 1.2 - UTPL

Segundo nivel del EDA: cruzar variables entre sí.
1. Comparación de medias por grupo (groupby): género y participación previa
2. Correlaciones de Spearman con la vocación STEM
3. Gráfico comparativo por género

Requiere scipy (para Spearman): pip install scipy
"""

import os
import re
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# 0. Configuración y carga (igual que analisis_eda.py)
# ---------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
ARCHIVO = os.path.join(BASE, "..", "Talleres de Tecnología y Motivación STEM.xlsx")
SALIDA = os.path.join(BASE, "resultados")
os.makedirs(SALIDA, exist_ok=True)
pd.set_option("display.width", 160)

df = pd.read_excel(ARCHIVO, sheet_name="Respuestas de formulario 1")
df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]

likert = list(df.columns[6:15])       # escalas 1-5
habilidades = list(df.columns[15:19]) # escalas 0-3
num = df[likert + habilidades].apply(pd.to_numeric, errors="coerce")

# ---------------------------------------------------------------
# 1. COMPARACIÓN POR GÉNERO
#    Fundamento: groupby divide las filas por categoría y calcula
#    la media de cada grupo por separado. Si la diferencia entre
#    grupos es grande, hay una relación entre las dos variables.
# ---------------------------------------------------------------
print("=" * 70)
print("1. MEDIAS POR GÉNERO (Likert 1-5 y habilidades 0-3)")
print("=" * 70)
genero = df["GÉNERO"]
por_genero = num.groupby(genero).mean().round(2).T
if {"Masculino", "Femenino"}.issubset(por_genero.columns):
    por_genero["Dif M-F"] = (por_genero["Masculino"] - por_genero["Femenino"]).round(2)
    por_genero = por_genero.sort_values("Dif M-F", ascending=False)
print(por_genero.to_string())
por_genero.to_csv(os.path.join(SALIDA, "10_bivariado_genero.csv"), encoding="utf-8-sig")

# Gráfico comparativo (solo preguntas Likert)
comp = num[likert].groupby(genero).mean().T
comp = comp[[c for c in ["Femenino", "Masculino"] if c in comp.columns]]
etiquetas = [c[:45] + "…" if len(c) > 45 else c for c in comp.index]
fig, ax = plt.subplots(figsize=(10, 6))
comp.set_axis(etiquetas, axis=0).sort_values(comp.columns[-1]).plot.barh(
    ax=ax, color=["#A23B72", "#2E86AB"])
ax.set_xlabel("Media (escala 1-5)")
ax.set_title("Motivación y actitudes por género")
ax.set_xlim(0, 5)
plt.tight_layout()
plt.savefig(os.path.join(SALIDA, "grafico_genero.png"), dpi=150)
plt.close()

# ---------------------------------------------------------------
# 2. COMPARACIÓN POR PARTICIPACIÓN PREVIA EN TALLERES
# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("2. MEDIAS POR PARTICIPACIÓN PREVIA EN TALLERES")
print("=" * 70)
previa = df["¿HAS PARTICIPADO EN TALLERES DE TECNOLOGÍA?"]
print("Tamaño de cada grupo:", previa.value_counts().to_dict())
por_previa = num.groupby(previa).mean().round(2).T
if {"Si", "No"}.issubset(por_previa.columns):
    por_previa["Dif Si-No"] = (por_previa["Si"] - por_previa["No"]).round(2)
    por_previa = por_previa.sort_values("Dif Si-No", ascending=False)
print(por_previa.to_string())
print("\nNota: el grupo 'Si' es pequeño (n=16); las diferencias son descriptivas,")
print("no prueban causalidad. Sirven como hipótesis para un diseño pre/post.")
por_previa.to_csv(os.path.join(SALIDA, "11_bivariado_participacion.csv"), encoding="utf-8-sig")

# ---------------------------------------------------------------
# 3. CORRELACIONES CON LA VOCACIÓN STEM
#    Fundamento: Spearman mide asociación entre variables ordinales
#    (como las escalas Likert) usando rangos en lugar de valores,
#    por lo que no exige normalidad ni escalas de intervalo.
#    Valores: 1 = asociación perfecta, 0 = ninguna, -1 = inversa.
# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("3. CORRELACIONES (Spearman) CON 'ME VEO ESTUDIANDO STEM'")
print("=" * 70)
stem = num[likert[3]]  # "Me veo estudiando una carrera relacionada con STEM..."
corr = (num.drop(columns=[likert[3]])
        .corrwith(stem, method="spearman")
        .round(2).sort_values(ascending=False))
print(corr.to_string())
corr.rename("Spearman").to_csv(os.path.join(SALIDA, "12_correlaciones_stem.csv"), encoding="utf-8-sig")

print("\n" + "=" * 70)
print(f"Análisis bivariado completado. Resultados en: {SALIDA}")
print("=" * 70)

# -*- coding: utf-8 -*-
"""
Análisis Exploratorio de Datos (EDA)
Encuesta: Talleres de Tecnología y Motivación STEM
Autor: Erick Malla Sisalima
Practicum 1.2 - UTPL

Aplica los fundamentos del EDA con pandas:
1. Carga y comprensión de la estructura de los datos
2. Diagnóstico de calidad (valores faltantes, tipos, duplicados)
3. Limpieza y preparación
4. Estadística descriptiva (media, mediana, desviación estándar)
5. Análisis de frecuencias (univariado)
6. Tratamiento de preguntas multi-respuesta
7. Visualización
"""

import os
import re
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# 0. Configuración
# ---------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
ARCHIVO = os.path.join(BASE, "..", "Talleres de Tecnología y Motivación STEM.xlsx")
SALIDA = os.path.join(BASE, "resultados")
os.makedirs(SALIDA, exist_ok=True)

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 30)

# ---------------------------------------------------------------
# 0.1 FUNCIÓN AUXILIAR - cálculo de la MODA
# ---------------------------------------------------------------
def calcular_moda(datos):
    """Calcula la moda (valor más frecuente) de los datos conectados.

    Acepta un DataFrame o una Series de pandas.
    - Para una Series devuelve la(s) moda(s) y su frecuencia.
    - Para un DataFrame devuelve una tabla con la moda de cada columna.
    Si una columna es multimodal, se listan todos los valores empatados.
    """
    def _moda_serie(serie):
        s = serie.dropna()
        if s.empty:
            return None, 0
        modas = s.mode()               # pandas devuelve todas las modas empatadas
        frecuencia = int((s == modas.iloc[0]).sum())
        valores = ", ".join(str(m) for m in modas)
        return valores, frecuencia

    if isinstance(datos, pd.Series):
        valores, frecuencia = _moda_serie(datos)
        return pd.DataFrame({"Moda": [valores], "Frecuencia": [frecuencia]},
                            index=[datos.name if datos.name else "valor"])

    filas = {}
    for col in datos.columns:
        valores, frecuencia = _moda_serie(datos[col])
        filas[col] = {"Moda": valores, "Frecuencia": frecuencia}
    return pd.DataFrame(filas).T[["Moda", "Frecuencia"]]


# ---------------------------------------------------------------
# 1. CARGA DE DATOS - primer fundamento del EDA: conocer la fuente
# ---------------------------------------------------------------
df = pd.read_excel(ARCHIVO, sheet_name="Respuestas de formulario 1")
print("=" * 70)
print("1. ESTRUCTURA DEL DATASET")
print("=" * 70)
print(f"Filas (encuestados): {df.shape[0]}  |  Columnas (preguntas): {df.shape[1]}")
print()
df.info()

# ---------------------------------------------------------------
# 2. LIMPIEZA - estandarizar nombres de columnas
# ---------------------------------------------------------------
df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]

# ---------------------------------------------------------------
# 3. DIAGNÓSTICO DE CALIDAD
# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("2. DIAGNÓSTICO DE CALIDAD DE LOS DATOS")
print("=" * 70)
faltantes = df.isna().sum()
faltantes = faltantes[faltantes > 0]
print("Valores faltantes por columna (solo columnas afectadas):")
print(faltantes.to_string() if len(faltantes) else "Sin valores faltantes")
print(f"\nFilas duplicadas: {df.duplicated().sum()}")
faltantes.rename("faltantes").to_csv(os.path.join(SALIDA, "01_valores_faltantes.csv"), encoding="utf-8-sig")

# ---------------------------------------------------------------
# 4. DEMOGRAFÍA - análisis de frecuencias
# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("3. DEMOGRAFÍA (frecuencias absolutas y relativas)")
print("=" * 70)
demograficas = ["Curso", "EDAD", "GÉNERO",
                "¿HAS PARTICIPADO EN TALLERES DE TECNOLOGÍA?",
                "¿TIENES ACCESO A INTERNET EN CASA?",
                "DISPOSITIVO QUE USAS MÁS"]
tablas_demo = []
for col in demograficas:
    if col not in df.columns:
        continue
    t = df[col].value_counts(dropna=True)
    p = (df[col].value_counts(normalize=True) * 100).round(1)
    tabla = pd.DataFrame({"Cantidad": t, "Porcentaje %": p})
    tabla.index.name = col
    print(f"\n--- {col} (N={df[col].notna().sum()}) ---")
    print(tabla.to_string())
    tabla["Variable"] = col
    tablas_demo.append(tabla.reset_index().rename(columns={col: "Categoría"}))
pd.concat(tablas_demo).to_csv(os.path.join(SALIDA, "02_demografia.csv"), index=False, encoding="utf-8-sig")

# ---------------------------------------------------------------
# 5. MOTIVACIÓN Y ACTITUDES (escala Likert 1-5)
# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("4. MOTIVACIÓN Y ACTITUDES - escala Likert 1-5")
print("=" * 70)
# Las 9 preguntas Likert ocupan las columnas 6 a 14 del formulario
likert = list(df.columns[6:15])

datos_likert = df[likert].apply(pd.to_numeric, errors="coerce")
resumen = pd.DataFrame({
    "N": datos_likert.notna().sum(),
    "Media": datos_likert.mean().round(2),
    "Mediana": datos_likert.median(),
    "Moda": calcular_moda(datos_likert)["Moda"],
    "Desv. Est.": datos_likert.std().round(2),
}).sort_values("Media", ascending=False)
print(resumen.to_string())
resumen.to_csv(os.path.join(SALIDA, "03_motivacion_descriptivos.csv"), encoding="utf-8-sig")

# Distribución de frecuencias 1-5 por pregunta
dist = datos_likert.apply(lambda s: s.value_counts()).T.fillna(0).astype(int)
dist = dist.reindex(columns=sorted(dist.columns))
print("\nDistribución de respuestas (1=Totalmente en desacuerdo ... 5=Totalmente de acuerdo):")
print(dist.to_string())
dist.to_csv(os.path.join(SALIDA, "04_motivacion_distribucion.csv"), encoding="utf-8-sig")

# Gráfico
fig, ax = plt.subplots(figsize=(10, 5))
resumen["Media"].sort_values().plot.barh(ax=ax, color="#2E86AB")
ax.set_xlabel("Media (escala 1-5)")
ax.set_title("Motivación y actitudes: media por pregunta")
ax.set_xlim(0, 5)
plt.tight_layout()
plt.savefig(os.path.join(SALIDA, "grafico_motivacion.png"), dpi=150)
plt.close()

# ---------------------------------------------------------------
# 6. AUTOEVALUACIÓN DE HABILIDADES (escala 0-3)
# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("5. AUTOEVALUACIÓN DE HABILIDADES - escala 0-3")
print("=" * 70)
# Las 4 habilidades ocupan las columnas 15 a 18 del formulario
habilidades = list(df.columns[15:19])
datos_hab = df[habilidades].apply(pd.to_numeric, errors="coerce")
resumen_hab = pd.DataFrame({
    "N": datos_hab.notna().sum(),
    "Media": datos_hab.mean().round(2),
    "Mediana": datos_hab.median(),
    "Moda": calcular_moda(datos_hab)["Moda"],
    "Desv. Est.": datos_hab.std().round(2),
}).sort_values("Media", ascending=False)
print(resumen_hab.to_string())
resumen_hab.to_csv(os.path.join(SALIDA, "05_habilidades_descriptivos.csv"), encoding="utf-8-sig")

fig, ax = plt.subplots(figsize=(8, 4))
resumen_hab["Media"].sort_values().plot.barh(ax=ax, color="#F18F01")
ax.set_xlabel("Media (escala 0-3)")
ax.set_title("Nivel de manejo percibido por herramienta")
ax.set_xlim(0, 3)
plt.tight_layout()
plt.savefig(os.path.join(SALIDA, "grafico_habilidades.png"), dpi=150)
plt.close()

# ---------------------------------------------------------------
# 7. PREGUNTAS MULTI-RESPUESTA (separar por comas y contar)
# ---------------------------------------------------------------
def contar_multirespuesta(serie, nombre, archivo_csv, grafico=None):
    """Divide celdas con varias opciones separadas por comas y cuenta cada opción."""
    opciones = (serie.dropna().astype(str)
                .str.split(r",\s*(?![^()]*\))")   # no cortar comas dentro de paréntesis
                .explode().str.strip())
    conteo = opciones[opciones != ""].value_counts()
    print(f"\n--- {nombre} (N encuestados={serie.notna().sum()}, menciones={conteo.sum()}) ---")
    print(conteo.to_string())
    conteo.rename("Cantidad").to_csv(os.path.join(SALIDA, archivo_csv), encoding="utf-8-sig")
    if grafico:
        fig, ax = plt.subplots(figsize=(9, max(3, 0.45 * len(conteo))))
        conteo.sort_values().plot.barh(ax=ax, color="#A23B72")
        ax.set_xlabel("Cantidad de menciones")
        ax.set_title(nombre)
        plt.tight_layout()
        plt.savefig(os.path.join(SALIDA, grafico), dpi=150)
        plt.close()
    return conteo

print("\n" + "=" * 70)
print("6. HERRAMIENTAS, EXPECTATIVAS Y BARRERAS (multi-respuesta)")
print("=" * 70)
col_usado = [c for c in df.columns if c.startswith("He usado")]
col_aporte = [c for c in df.columns if "te gustaría que estos talleres" in c or "taller aporte" in c]
col_barreras = [c for c in df.columns if "dificultar" in c]

if col_usado:
    contar_multirespuesta(df[col_usado[0]], "Herramientas que ya han usado",
                          "06_herramientas_usadas.csv", "grafico_herramientas.png")
if col_aporte:
    contar_multirespuesta(df[col_aporte[0]], "Qué esperan que aporte el taller",
                          "07_expectativas.csv")
if col_barreras:
    contar_multirespuesta(df[col_barreras[0]], "Barreras para participar/aprender",
                          "08_barreras.csv", "grafico_barreras.png")

# Preguntas de opción única de contexto
print("\n--- Contexto escolar ---")
for c in df.columns:
    if "proyecto de año" in c or "etapa del proyecto" in c or "Quién te apoya" in c:
        print(f"\n{c}:")
        print(df[c].value_counts().to_string())

# ---------------------------------------------------------------
# 8. PREGUNTAS ABIERTAS - codificación temática simple por palabras clave
# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("7. PREGUNTAS ABIERTAS - codificación temática")
print("=" * 70)
categorias_tema = {
    "Inteligencia Artificial": ["inteligencia artificial", " ia ", "ia.", "ia,", "chatgpt", "gemini", "aritficial"],
    "Programación": ["program", "codigo", "código", "python", "scratch"],
    "Videojuegos": ["videojuego", "juego"],
    "Robótica": ["robot"],
    "Apps/Web": ["app", "aplicacion", "aplicación", "web", "pagina", "página"],
    "Ciberseguridad": ["cibersegur", "hack", "segur"],
}
col_tema = [c for c in df.columns if "tema tecnológico" in c]
if col_tema:
    textos = df[col_tema[0]].dropna().astype(str).str.lower()
    conteo_temas = {}
    for cat, claves in categorias_tema.items():
        conteo_temas[cat] = sum(any(k in f" {t} " for k in claves) for t in textos)
    tabla_temas = pd.Series(conteo_temas).sort_values(ascending=False)
    print(f"\nTema tecnológico de mayor interés (N={len(textos)} respuestas):")
    print(tabla_temas.to_string())
    tabla_temas.rename("Cantidad").to_csv(os.path.join(SALIDA, "09_temas_interes.csv"), encoding="utf-8-sig")

# ---------------------------------------------------------------
# 9. MODA GENERAL - valor más frecuente de cada variable del dataset
# ---------------------------------------------------------------
print("\n" + "=" * 70)
print("8. MODA - valor más frecuente por variable (datos conectados)")
print("=" * 70)
tabla_moda = calcular_moda(df)
print(tabla_moda.to_string())
tabla_moda.to_csv(os.path.join(SALIDA, "13_moda_general.csv"), encoding="utf-8-sig")

print("\n" + "=" * 70)
print(f"EDA completado. Resultados guardados en: {SALIDA}")
print("=" * 70)

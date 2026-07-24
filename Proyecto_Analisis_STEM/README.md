# Proyecto de Análisis EDA — Talleres de Tecnología y Motivación STEM

Análisis exploratorio de datos (EDA) con **pandas** sobre la encuesta aplicada a 91 estudiantes de 3ro de bachillerato (Practicum 1.2 — Erick Malla Sisalima).

## Estructura

```
Proyecto_Analisis_STEM/
├── Proyecto_Analisis_STEM.sln      # Solución de Visual Studio
├── Proyecto_Analisis_STEM.pyproj   # Proyecto Python de Visual Studio
├── analisis_eda.py                 # Script principal de EDA (univariado)
├── analisis_bivariado.py           # Cruces por género/participación y correlaciones
├── requirements.txt                # Dependencias
└── resultados/                     # Tablas CSV, gráficos PNG y reporte
```

El script lee el archivo `Talleres de Tecnología y Motivación STEM.xlsx` ubicado en la carpeta padre.

## Cómo ejecutarlo

**Opción A — Visual Studio:** abrir `Proyecto_Analisis_STEM.sln` (requiere la carga de trabajo "Desarrollo de Python") y presionar F5.

**Opción B — Terminal / VS Code:**

```
pip install -r requirements.txt
python analisis_eda.py
```

## Qué hace el análisis

1. Carga y estructura del dataset (91 filas × 27 columnas)
2. Diagnóstico de calidad: valores faltantes por columna, duplicados
3. Demografía: tablas de frecuencia (curso, edad, género, acceso a internet, dispositivo)
4. Motivación y actitudes (Likert 1-5): media, mediana, desviación estándar y distribución de frecuencias
5. Autoevaluación de habilidades (escala 0-3)
6. Preguntas multi-respuesta: separación por comas y conteo de menciones (herramientas usadas, expectativas, barreras)
7. Preguntas abiertas: codificación temática por palabras clave

**Análisis bivariado** (`python analisis_bivariado.py`):

1. Medias por género con `groupby('GÉNERO').mean()` — detecta la brecha de género
2. Medias por participación previa en talleres
3. Correlaciones de Spearman con "Me veo estudiando STEM" (`corrwith(method='spearman')`)
4. Gráfico comparativo por género

Los resultados se guardan en `resultados/` como CSV (tablas), PNG (gráficos) y `reporte_eda.txt` (salida completa).

# TP Final - Business Intelligence & Analytics

Dashboard académico que analiza la participación, las calificaciones y la matrícula de tres asignaturas: Álgebra, Algoritmos y Estructuras de Datos, y Probabilidad y Estadística.

**Aplicación desplegada:** https://tp-business-analytics.streamlit.app/

## Estructura del proyecto

```
.
├── README.md
├── requirements.txt          dependencias de Python
├── justificaciones.md        justificación de cada indicador (KPI)
├── kpis_pendientes.md        indicadores calculados que la app todavía no muestra
│
├── data/                     datos del proyecto
│   ├── algebra/              reportes exportados de la plataforma y su versión limpia
│   ├── algoritmosestructuras/
│   ├── probabilidadestadistica/
│   ├── matriculados/         listados oficiales de matriculados
│   ├── integrado/            las tres asignaturas unidas (lo que lee la aplicación)
│   └── kpis/                 gráficos y tablas resultantes de los indicadores
│
├── jupyter/                  INVESTIGACIÓN
│   ├── algebra.ipynb
│   ├── algoritmosestructuras.ipynb
│   ├── probabilidadestadistica.ipynb
│   ├── matriculados.ipynb
│   ├── integracion.ipynb
│   ├── utils_limpieza.py
│   ├── kpis/                 un notebook por grupo de indicadores
│   └── version_anterior/     versiones previas de los notebooks de limpieza
│
└── src/                      APLICACIÓN (lo que se despliega)
    ├── app.py                punto de entrada y navegación
    ├── constants.py          constantes del proyecto (nombres, textos, parámetros)
    ├── data/
    │   ├── kpis/             cálculo de los indicadores
    │   └── services/         preparan los datos que muestra cada pantalla
    └── ui/
        ├── pages/            las siete pantallas
        ├── components/       tarjetas, gráficos, tablas y filtros reutilizables
        └── theme.css         estilos
```

## Investigación (`jupyter/`)

Es el trabajo previo con los datos, hecho en notebooks. Sigue este orden:

1. **Limpieza por asignatura** (`algebra`, `algoritmosestructuras`, `probabilidadestadistica`): toman los reportes exportados de la plataforma (calificaciones, participación y trazabilidad), corrigen errores y los guardan en formato Parquet.
2. **Matriculados** (`matriculados`): consolida los listados oficiales de las tres asignaturas.
3. **Integración** (`integracion`): une todo en `data/integrado/`.
4. **Indicadores** (`kpis/`): calculan y justifican los indicadores de calificaciones, participación, matrícula y los cruces entre participación y notas.

## Aplicación (`src/`)

Es la parte que se publica. Lee los datos de `data/integrado/` y los muestra en siete pantallas: General, Participación, Trazabilidad, Rendimiento Académico, Notas vs Participación, Individual, y Matrícula y Alertas.

- `data/kpis/` calcula los indicadores a partir de los datos integrados.
- `data/services/` toma esos resultados y arma las tablas de cada pantalla.
- `ui/` dibuja las pantallas con Streamlit.

## Cómo ejecutarla en la computadora

```bash
pip install -r requirements.txt
streamlit run src/app.py
```

# TP Final - Business Intelligence & Analytics

Guía para levantar el entorno `tpfinal` con conda, paso a paso.

## Requisitos previos

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) o Anaconda instalado.
- (Opcional) Driver ODBC de Microsoft para SQL Server (ODBC Driver 17 o 18), necesario para que `pyodbc` pueda conectarse a la base.

## 1. Abrir una terminal con conda

En Windows, abrir **Anaconda Prompt** (o Miniconda Prompt). Si conda no está en el PATH de PowerShell, se puede inicializar una vez con:

```powershell
conda init powershell
```

y reabrir la terminal.

## 2. Crear el entorno

```bash
conda create -n tpfinal python=3.12 -y -c conda-forge
```

## 3. Instalar los paquetes

```bash
conda install -n tpfinal -c conda-forge pandas numpy scipy matplotlib seaborn scikit-learn statsmodels jupyterlab openpyxl pyarrow sqlalchemy pyodbc streamlit -y
```

| Paquete | Uso |
|---|---|
| pandas, numpy, scipy | manipulación de datos y cálculo científico |
| matplotlib, seaborn | gráficos |
| scikit-learn, statsmodels | modelos de machine learning y estadística |
| jupyterlab | notebooks |
| openpyxl | lectura/escritura de Excel |
| pyarrow | formato Parquet |
| sqlalchemy, pyodbc | conexión a bases de datos (SQL Server) |
| streamlit | dashboards / apps web |

## 4. Activar el entorno

```bash
conda activate tpfinal
```

## 5. Verificar la instalación

```bash
python -c "import pandas, numpy, scipy, matplotlib, seaborn, sklearn, statsmodels, openpyxl, pyarrow, sqlalchemy, pyodbc, streamlit; print('ok')"
jupyter lab --version
streamlit --version
```

Debe imprimir `ok` y las versiones de JupyterLab y Streamlit.

## 6. Usar el entorno

Abrir JupyterLab (desde la carpeta del proyecto):

```bash
jupyter lab
```

Levantar una app de Streamlit:

```bash
streamlit run src/app.py
```

## Alternativa: reproducir desde un archivo

Para exportar el entorno y recrearlo en otra máquina:

```bash
# exportar (desde el entorno original)
conda env export -n tpfinal --from-history > environment.yml

# recrear
conda env create -f environment.yml
```

## Comandos básicos de conda

### Entornos

```bash
conda env list                          # listar todos los entornos (el activo lleva *)
conda info --envs                       # igual que el anterior
conda create -n <nombre> python=3.12    # crear un entorno nuevo
conda activate <nombre>                 # activar un entorno
conda activate tpfinal                  # activar este proyecto
conda deactivate                        # salir del entorno actual (vuelve a base)
conda env remove -n <nombre>            # borrar un entorno
conda create -n <nuevo> --clone <viejo> # clonar un entorno
conda rename -n <viejo> <nuevo>         # renombrar un entorno
```

### Cambiar de entorno

No hace falta desactivar el actual: activar otro reemplaza al anterior.

```bash
conda activate tpfinal
conda activate otro-entorno
```

Para saber en cuál estás: el prompt muestra `(nombre)` al inicio, o corré `conda info | findstr "active environment"` en Windows (`grep` en Linux/Mac).

### Paquetes

```bash
conda list                          # paquetes del entorno activo
conda list -n tpfinal               # paquetes de un entorno sin activarlo
conda search <paquete>              # buscar versiones disponibles
conda install <paquete>             # instalar en el entorno activo
conda install -n tpfinal <paquete>  # instalar en un entorno específico
conda install <paquete>=1.2.3       # instalar una versión puntual
conda update <paquete>              # actualizar un paquete
conda update --all                  # actualizar todo el entorno
conda remove <paquete>              # desinstalar un paquete
pip install <paquete>               # si no está en conda (usar con el entorno activo)
```

### Ejecutar sin activar

```bash
conda run -n tpfinal python script.py
conda run -n tpfinal jupyter lab
```

### Mantenimiento

```bash
conda --version                     # versión de conda
conda update conda                  # actualizar conda
conda clean --all                   # liberar espacio (cachés y paquetes sin usar)
conda config --show channels        # ver canales configurados
```

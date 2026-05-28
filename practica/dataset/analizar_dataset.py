import pandas as pd
import numpy as np

PRIMER_ANALISIS = True
TRANSFORMAR_DATOS = True
GUARDAR_CSV_TRANSFORMADO = True

# Cargar el archivo CSV obtenido de https://opendata.aragon.es/datos/catalogo/dataset/registro-de-certificacion-de-eficiencia-energetica-de-edificios-de-aragon
file_path = "ENERGIA - Cert. Data.csv"
df = pd.read_csv(file_path)

# ------------------------------------------------------------------------------
# PRIMER ANÁLISIS DEL DATASET
# ------------------------------------------------------------------------------

if PRIMER_ANALISIS:

    # Información básica del dataset
    print("=" * 60)
    print("ANÁLISIS EXPLORATORIO DEL DATASET")
    print("=" * 60)

    # Dimensiones
    print(f"\nDimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")

    # Tipos de datos
    print("\nTipos de datos:")
    print(df.dtypes)

    # Valores nulos por columna
    print("\nValores nulos por columna:")
    print(df.isnull().sum())

    # Estadísticas descriptivas
    print("\nEstadísticas descriptivas:")
    print(df.describe())

    # Primeras filas
    print("\nPrimeras 5 filas de todas las columnas:")
    for col in df.columns:
        print(f"\nColumna: {col}")
        print(df[col].head())

    # Información general
    print("\nInformación general del dataframe:")
    df.info()

    # Contar cuantos registros hay de cada provincia
    print("\nCantidad de registros por provincia:")
    print(df['prov'].value_counts())

    # Contar cuantos registros hay de cada tipo de certificado
    print("\nCantidad de registros por tipo de certificado:")
    print(df['clasificacion_emisiones'].value_counts())
    print(df['clasificacion_consumo'].value_counts())

    # Contar cuantos registros hay de cada tipo de estadoedi
    print("\nCantidad de registros por estadoedi:")
    print(df['estadoedi'].value_counts())

    # Contar cuantos registros hay de cada tipo de tipoedi
    print("\nCantidad de registros por tipoedi:")
    print(df['tipoedi'].value_counts())

    # Contar cuantos registros hay de cada tipo de munic y cuántos distintos hay
    print("\nCantidad de registros por municipio:")
    print(df['munic'].value_counts())
    print(f"\nNúmero de municipios distintos: {df['munic'].nunique()}")

# Comprobar que todos los registros de emision_co acaban en " kgCO2/m2 año"
assert df[df['emision_co'].str.endswith(" kgCO2/m2 año")].shape[0] == df.shape[0], "No todos los registros tienen el formato esperado en 'emision_co'"
# Comprobar que todos los registros de consumo_ener acaban en " kWh/m2 año"
assert df[df['consumo_ener'].str.endswith(" kWh/m2 año")].shape[0] == df.shape[0], "No todos los registros tienen el formato esperado en 'consumo_ener'"
print("\nTodos los registros de 'emision_co' y 'consumo_ener' tienen el formato esperado.")

# ------------------------------------------------------------------------------
# TRANSFORMACIÓN DE LOS DATOS
# ------------------------------------------------------------------------------

if TRANSFORMAR_DATOS:

    # Eliminar " kgCO2/m2 año" de la columna 'emision_co' y cambiar coma por punto decimal
    df['emision_co'] = df['emision_co'].str.replace(" kgCO2/m2 año", "").str.replace(",", ".")
    # Eliminar " kWh/m2 año" de la columna 'consumo_ener'
    df['consumo_ener'] = df['consumo_ener'].str.replace(" kWh/m2 año", "").str.replace(",", ".")
    # Convertir las columnas a tipo numérico
    df['emision_co'] = pd.to_numeric(df['emision_co'], errors='raise')
    df['consumo_ener'] = pd.to_numeric(df['consumo_ener'], errors='raise')

    # Convertir las columnas fec_emision y fec_expira a tipo datetime
    df['fec_emision'] = pd.to_datetime(df['fec_emision'], errors='raise')
    df['fec_expira'] = pd.to_datetime(df['fec_expira'], errors='raise')

    # Convertir las columnas 'prov', 'estadoedi', 'tipoedi', 'munic' a tipo categórico
    df['prov'] = df['prov'].astype('category')
    df['estadoedi'] = df['estadoedi'].astype('category')
    df['tipoedi'] = df['tipoedi'].astype('category')
    df['munic'] = df['munic'].astype('category')

    # Mostrar los clasificacion_consumo distintos de ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    print("\nClasificación de consumo energético distinta de ['A', 'B', 'C', 'D', 'E', 'F', 'G']:")
    print(df[~df['clasificacion_consumo'].isin(['A', 'B', 'C', 'D', 'E', 'F', 'G'])]['clasificacion_consumo'].unique())

    # Convertir las columnas de clasificación a tipo categórico ordenado
    clasificacion_emisiones_order = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    clasificacion_consumo_order = clasificacion_emisiones_order
    df['clasificacion_emisiones'] = pd.Categorical(df['clasificacion_emisiones'], categories=clasificacion_emisiones_order, ordered=True)
    df['clasificacion_consumo'] = pd.Categorical(df['clasificacion_consumo'], categories=clasificacion_consumo_order, ordered=True)

    # Convertir anio a entero (robusto ante nulos)
    df['anio'] = pd.to_numeric(df['anio'], errors='coerce').astype('Int64')

    # Separar la columna 'coordenadas' en 'coordenada_x' y 'coordenada_y'
    df[['coordenada_x', 'coordenada_y']] = df['coordenadas'].str.split(" , ", expand=True)
    # Convertir las nuevas columnas a tipo numérico, cambiando coma por punto decimal
    df['coordenada_x'] = df['coordenada_x'].str.replace(",", ".")
    df['coordenada_y'] = df['coordenada_y'].str.replace(",", ".")
    # Si coordenadas.strip() = "," entonces coordenada_x y coordenada_y deben ser NaN
    mask_invalid = df["coordenadas"].str.strip().isin(["", ",", ".", None])
    df.loc[mask_invalid, ['coordenada_x', 'coordenada_y']] = np.nan
    df['coordenada_x'] = pd.to_numeric(df['coordenada_x'], errors='raise')
    df['coordenada_y'] = pd.to_numeric(df['coordenada_y'], errors='raise')
    df.drop(columns=['coordenadas'], inplace=True)

    # Eliminar columnas que no aportan información relevante para el análisis
    # df.drop(columns=['numcert', 'refcatastral', 'direccion'], inplace=True)

    # Verificar los tipos de datos después de la transformación
    print("\nTipos de datos después de la transformación:")
    print(df.dtypes)

    # Valores nulos por columna
    print("\nValores nulos por columna:")
    print(df.isnull().sum())

    # Eliminar filas con valores nulos en cualquer columna
    print("Se eliminan filas con valores nulos...")
    df.dropna(inplace=True)

    # Eliminar filas con provincias no válidas (distintas de las 3 provincias de Aragón)
    provincias_validas = ['HUESCA', 'ZARAGOZA', 'TERUEL']
    df = df[df['prov'].isin(provincias_validas)]

    # Mostrar las dimensiones del dataframe después de la transformación
    print(f"\nDimensiones después de la transformación: {df.shape[0]} filas x {df.shape[1]} columnas")

    if GUARDAR_CSV_TRANSFORMADO:
        # Guardar el dataframe transformado en un nuevo archivo CSV
        output_file_path = "Transformed_Cert_Data.csv"
        df.to_csv(output_file_path, index=False)
        print(f"Dataframe transformado guardado en: {output_file_path}")

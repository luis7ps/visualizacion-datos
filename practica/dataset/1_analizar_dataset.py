'''
PRIMER ANÁLISIS DEL DATASET
'''

import pandas as pd

# Cargar el archivo CSV obtenido de https://opendata.aragon.es/datos/catalogo/dataset/registro-de-certificacion-de-eficiencia-energetica-de-edificios-de-aragon
# file_path = "dataset/ENERGIA - Cert. Data.csv"
# file_path = "dataset/Transformed_Cert_Data.csv"
file_path = "dataset/Agregado_Municipio_Cert_Data.csv"
df = pd.read_csv(file_path)

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

# Contar cuantos registros hay de cada tipo de munic y cuántos distintos hay
print("\nCantidad de registros por municipio:")
print(df['munic'].value_counts())

# Contar cuantos registros hay de cada tipo de certificado
if 'clasificacion_emisiones' in df.columns and 'clasificacion_consumo' in df.columns:
    print("\nCantidad de registros por tipo de certificado:")
    print(df['clasificacion_emisiones'].value_counts())
    print(df['clasificacion_consumo'].value_counts())

# Contar cuantos registros hay de cada tipo de estadoedi
if 'estadoedi' in df.columns:
    print("\nCantidad de registros por estadoedi:")
    print(df['estadoedi'].value_counts())

# Contar cuantos registros hay de cada tipo de tipoedi
if 'tipoedi' in df.columns:
    print("\nCantidad de registros por tipoedi:")
    print(df['tipoedi'].value_counts())

# Si emision_co y consumo_ener son de tipo object:
if 'emision_co' in df.columns and 'consumo_ener' in df.columns and df['emision_co'].dtype == 'object' and df['consumo_ener'].dtype == 'object':
    # Comprobar que todos los registros de emision_co acaban en " kgCO2/m2 año"
    assert df[df['emision_co'].str.endswith(" kgCO2/m2 año")].shape[0] == df.shape[0], "No todos los registros tienen el formato esperado en 'emision_co'"
    # Comprobar que todos los registros de consumo_ener acaban en " kWh/m2 año"
    assert df[df['consumo_ener'].str.endswith(" kWh/m2 año")].shape[0] == df.shape[0], "No todos los registros tienen el formato esperado en 'consumo_ener'"
    print("\nTodos los registros de 'emision_co' y 'consumo_ener' tienen el formato esperado (kgCO2/m2 año y kWh/m2 año, respectivamente).")

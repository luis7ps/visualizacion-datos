import pandas as pd
import numpy as np
from pyproj import Transformer

PRIMER_ANALISIS = False
TRANSFORMAR_DATOS = True
GUARDAR_CSV_TRANSFORMADO = False
CREAR_DATASET_AGREGADO_MUNICIPIO = True

# Cargar el archivo CSV obtenido de https://opendata.aragon.es/datos/catalogo/dataset/registro-de-certificacion-de-eficiencia-energetica-de-edificios-de-aragon
file_path = "dataset/ENERGIA - Cert. Data.csv"
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

    # Valores nulos por columna
    print("\nValores nulos por columna:")
    print(df.isnull().sum())

    # Eliminar filas con valores nulos en cualquer columna
    print("Se eliminan filas con valores nulos...")
    df.dropna(inplace=True)

    # Eliminar filas con provincias no válidas (distintas de las 3 provincias de Aragón)
    provincias_validas = ['HUESCA', 'ZARAGOZA', 'TERUEL']
    df = df[df['prov'].isin(provincias_validas)]

    # Transformador de coordenadas:
    transformer = Transformer.from_crs(
        "EPSG:25830", # EPSG:25830 = ETRS89 / UTM zone 30N
        "EPSG:4326", # EPSG:4326 = WGS84 (lat/lon)
        always_xy=True # Asegura que las coordenadas se pasen en el orden (x, y)
    )

    # Conversión
    df["longitud"], df["latitud"] = transformer.transform(
        df["coordenada_x"].values,
        df["coordenada_y"].values
    )

    # Verificar los tipos de datos después de la transformación
    print("\nTipos de datos después de la transformación:")
    print(df.dtypes)

    # Mostrar las dimensiones del dataframe después de la transformación
    print(f"\nDimensiones después de la transformación: {df.shape[0]} filas x {df.shape[1]} columnas")

    # Aserción para comprobar que no hay valores nulos en las nuevas columnas de latitud y longitud
    assert df['latitud'].isnull().sum() == 0, "Hay valores nulos en la columna 'latitud' después de la transformación"
    assert df['longitud'].isnull().sum() == 0, "Hay valores nulos en la columna 'longitud' después de la transformación"

    # Control de calidad de coordenadas: latitud entre 39 y 43, longitud entre -2º30' y 1º00' (aproximadamente para Aragón)
    assert df[(df['latitud'] < 39) | (df['latitud'] > 43)].shape[0] == 0, "Hay valores de latitud fuera del rango esperado para Aragón"
    # assert df[(df['longitud'] < -2.5) | (df['longitud'] > 1)].shape[0] == 0, "Hay valores de longitud fuera del rango esperado para Aragón"

    # Como hay valores erróneos de longitud, se eliminan filas con longitud fuera del rango esperado para Aragón
    df = df[(df['longitud'] >= -2.5) & (df['longitud'] <= 1)]
    print(f"\nDimensiones después de eliminar filas con longitud fuera del rango esperado: {df.shape[0]} filas x {df.shape[1]} columnas")

    if GUARDAR_CSV_TRANSFORMADO:
        # Guardar el dataframe transformado en un nuevo archivo CSV
        output_file_path = "dataset/Transformed_Cert_Data.csv"
        df.to_csv(output_file_path, index=False)
        print(f"Dataframe transformado guardado en: {output_file_path}")


if CREAR_DATASET_AGREGADO_MUNICIPIO:
    '''
    Crear un nuevo dataframe con un un municipio por fila, con las siguientes columnas:
    - munic: nombre del municipio
    - provincia: provincia a la que pertenece el municipio
    - num_certificados: número total de certificados en ese municipio
    - fec_emision_avg: fecha de emisión promedio de los certificados en ese municipio
    - fec_expira_avg: fecha de expiración promedio de los certificados en ese municipio
    - emision_co_avg: emisión de CO2 promedio de los certificados en ese municipio
    - consumo_ener_avg: consumo energético promedio de los certificados en ese municipio
    - anio_avg: año promedio
    - superficie_avg: superficie promedio
    - latitud_avg: latitud promedio
    - longitud_avg: longitud promedio

    y para cada atributo de entre clasificacion_emisiones y clasificacion_consumo, crear una columna adicional con el porcentaje de certificados en cada categoría (A, B, C, D, E, F, G) para ese municipio. Por ejemplo, para clasificacion_emisiones se crearían las columnas: clasificacion_emisiones_A_pct, clasificacion_emisiones_B_pct, ..., clasificacion_emisiones_G_pct, y lo mismo para clasificacion_consumo.
    Lo mismo con estadoedi y tipoedi y sus posibles valores.
    '''
    # Agrupar por municipio y provincia, calculando las métricas solicitadas
    df_agregado = df.groupby(['munic', 'prov'], observed=True).agg(
        num_certificados=('numcert', 'count'),
        fec_emision_avg=('fec_emision', 'mean'),
        fec_expira_avg=('fec_expira', 'mean'),
        emision_co_avg=('emision_co', 'mean'),
        consumo_ener_avg=('consumo_ener', 'mean'),
        anio_avg=('anio', 'mean'),
        latitud_avg=('latitud', 'mean'),
        longitud_avg=('longitud', 'mean')
    ).reset_index()

    # Función para calcular el porcentaje de cada categoría en una columna dada
    def calcular_porcentaje_categoria(df, grupo_col, categoria_col, categoria_valores):
        porcentaje_df = df.groupby([grupo_col, categoria_col], observed=True).size().unstack(fill_value=0)
        porcentaje_df = porcentaje_df[categoria_valores]  # Asegura que todas las categorías estén presentes
        porcentaje_df = porcentaje_df.div(porcentaje_df.sum(axis=1), axis=0) * 100  # Convertir a porcentaje
        porcentaje_df.columns = [f"{categoria_col}_{col}_pct" for col in porcentaje_df.columns]  # Renombrar columnas
        return porcentaje_df.reset_index()
    
    # Calcular el porcentaje de cada categoría para clasificacion_emisiones
    categorias_emisiones = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    porcentaje_emisiones = calcular_porcentaje_categoria(df, 'munic', 'clasificacion_emisiones', categorias_emisiones)

    # Calcular el porcentaje de cada categoría para clasificacion_consumo
    categorias_consumo = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    porcentaje_consumo = calcular_porcentaje_categoria(df, 'munic', 'clasificacion_consumo', categorias_consumo)

    # Calcular el porcentaje de cada categoría para estadoedi
    categorias_estadoedi = df['estadoedi'].cat.categories.tolist()
    porcentaje_estadoedi = calcular_porcentaje_categoria(df, 'munic', 'estadoedi', categorias_estadoedi)

    # Calcular el porcentaje de cada categoría para tipoedi
    categorias_tipoedi = df['tipoedi'].cat.categories.tolist()
    porcentaje_tipoedi = calcular_porcentaje_categoria(df, 'munic', 'tipoedi', categorias_tipoedi)

    # Combinar todos los dataframes en uno solo
    df_final = df_agregado.merge(porcentaje_emisiones, on='munic', how='left')
    df_final = df_final.merge(porcentaje_consumo, on='munic', how='left')
    df_final = df_final.merge(porcentaje_estadoedi, on='munic', how='left')
    df_final = df_final.merge(porcentaje_tipoedi, on='munic', how='left')

    # Transformar las columnas fec_emision_avg y fec_expira_avg a date en vez de datetime
    df_final['fec_emision_avg'] = df_final['fec_emision_avg'].dt.date
    df_final['fec_expira_avg'] = df_final['fec_expira_avg'].dt.date

    # Transformar anio_avg a entero por abajo
    df_final['anio_avg'] = df_final['anio_avg'].apply(np.floor).astype('Int64')

    # Guardar el dataframe final en un nuevo archivo CSV
    output_file_path_final = "dataset/Agregado_Municipio_Cert_Data.csv"
    df_final.to_csv(output_file_path_final, index=False)
    print(f"Dataframe agregado por municipio guardado en: {output_file_path_final}")
    print(f"\nDimensiones del dataframe final: {df_final.shape[0]} filas x {df_final.shape[1]} columnas")

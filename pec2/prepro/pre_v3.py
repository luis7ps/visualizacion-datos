import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('pec2/datasets/dataset_3_original.csv')

# Agrupar por 'store', eliminando NULLs y sumando las ventas
grouped_df = df.groupby('store_name', dropna=True)['final_amount'].sum().reset_index()

# Cambiar el nombre de la columna 'final_amount' a 'total_sales'
grouped_df.rename(columns={'final_amount': 'total_sales'}, inplace=True)

# Para cada tienda, añadir una columna con un valor aleatorio que represente el objetivo de ventas (resultado de aplicar entre el 90% y el 130% de las ventas totales)

grouped_df['sales_target'] = grouped_df['total_sales'] * np.random.uniform(0.9, 1.2, size=len(grouped_df))
grouped_df['sales_target'] = grouped_df['sales_target'].round(2)

# Poner sales_target como segunda columna, después de store_name
cols = ['store_name', 'sales_target', 'total_sales']
grouped_df = grouped_df[cols]

print(grouped_df)

print(f"Original data rows: {len(df)}")
print(f"Filtered data rows: {len(grouped_df)}")

# Save to a new CSV file
grouped_df.to_csv('pec2/datasets/dataset_3_final.csv', index=False)


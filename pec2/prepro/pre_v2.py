import pandas as pd

# Read the CSV file
df = pd.read_csv('pec2/datasets/dataset_2_original.csv')

# Filter by column value 
filtered_df = df[df['weight'] > 50]

print(f"Original data rows: {len(df)}")
print(f"Filtered data rows: {len(filtered_df)}")

# Save to a new CSV file
filtered_df.to_csv('pec2/datasets/dataset_2_final.csv', index=False)


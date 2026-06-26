import os
import pandas as pd
import sqlite3

# 1. Load the CSV file into a Pandas DataFrame
csv_file_path = 'Haircare-products - Sheet1 (1).csv'
df = pd.read_csv(csv_file_path)

# Drop completely empty row artifacts (like rows with just commas: ,,,,,,)
df = df.dropna(subset=['name']).fillna("")

# 2. Reorder columns you care about—now explicitly INCLUDING 'product_link'
df_final = df[['name', 'category', 'suitable', 'hair_type', 'hair_pattern', 'scalp_condition', 'product_link']]

# 3. Connect to the SQLite database
conn = sqlite3.connect('evora/db.sqlite3')
cursor = conn.cursor()

# 4. Automatically find missing database columns and fill them with default blank values
table_info = cursor.execute("PRAGMA table_info(my_admin_haircareproducts);").fetchall()
db_columns = [col[1] for col in table_info if col[1] != 'id']

for col in db_columns:
    if col not in df_final.columns:
        # Dynamically set numbers to 0.0 and text to empty strings
        df_final = df_final.assign(**{col: 0.0 if col == 'price' else ""})

# 5. Arrange the columns to perfectly match the target table order
df_final = df_final[db_columns]

# 6. Save directly to SQLite using Pandas
df_final.to_sql('my_admin_haircareproducts', conn, if_exists='append', index=False)

conn.close()
print("\nData successfully imported using Pandas with full links and clean column decoupling!")
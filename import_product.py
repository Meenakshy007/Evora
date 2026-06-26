import sqlite3
import pandas as pd

# 1. Load the CSV file into a Pandas DataFrame and handle missing values
csv_file_path = "skincareProducts.csv"
df = pd.read_csv(csv_file_path).fillna("")

# Rename headers from hyphens to underscores to align perfectly with Django model fields
df = df.rename(
    columns={
        "name": "name",
        "suitable": "suitable",
        "skin-type": "skin_type",
        "category": "category",
        "primary-concern": "primary_concern",
        "secondary-concern": "secondary_concern",
        "product-link": "product_link",
      # Included just in case it maps to your model
    }
)

# 2. Select the columns to match your Django model structure
# (We use .copy() to prevent Pandas from raising a SettingWithCopyWarning later)
df_final = df[
    [
        "name",
        "suitable",
        "skin_type",
        "category",
        "primary_concern",
        "secondary_concern",
        "product_link",

    ]
].copy()

# 3. Connect to the SQLite database
conn = sqlite3.connect("db.sqlite3", timeout=20)
cursor = conn.cursor()

# 4. Target your Django table
table_name = "my_admin_skincareproducts"

try:
    # Fetch existing table schema columns from SQLite
    table_info = cursor.execute(f"PRAGMA table_info({table_name});").fetchall()

    # Get a list of all DB columns except 'id' (Django handles 'id' automatically)
    db_columns = [col[1] for col in table_info if col[1] != "id"]

    # Automatically find missing database columns and fill them with default blank values
    for col in db_columns:
        if col not in df_final.columns:
            # Dynamically set numbers to 0.0 and text to empty strings
            df_final.loc[:, col] = 0.0 if col == "price" else ""

    # 5. Filter df_final to safely include ONLY columns that actually exist in the DB table
    final_columns_to_export = [col for col in df_final.columns if col in db_columns]
    df_final = df_final[final_columns_to_export]

    # 6. Save directly to SQLite using Pandas (append mode preserves existing data)
    df_final.to_sql(table_name, conn, if_exists="append", index=False)
    conn.commit()

    print(
        f"\n🎉 Success! {len(df_final)} rows from '{csv_file_path}' successfully imported into '{table_name}'."
    )

except sqlite3.OperationalError as e:
    print(
        f"\n❌ Database Error: Could not find table '{table_name}'."
        f"\nMake sure you have run 'python manage.py makemigrations' and 'python manage.py migrate' first."
        f"\nDetails: {e}"
    )

finally:
    conn.close()

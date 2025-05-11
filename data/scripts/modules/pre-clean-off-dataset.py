import polars as pl

df = pl.read_parquet("../openfoodfacts_products.parquet")

def detect_empty_columns(df: pl.DataFrame, threshold: float = 0.95):
    total_rows = df.height
    results = []

    for col in df.columns:
        # Count nulls
        nulls = df.select(pl.col(col).is_null().sum()).item()
        
        # Count empty strings (only for string columns)
        empties = 0
        if df.schema[col] == pl.Utf8:
            empties = df.select((pl.col(col) == "").sum()).item()
        
        # Compute total missing
        total_missing = nulls + empties
        ratio = total_missing / total_rows

        if ratio >= threshold:
            results.append((col, ratio))

    return sorted(results, key=lambda x: -x[1])

columns_to_drop = detect_empty_columns(df, threshold=0.95)

# Suppression automatique des colonnes vides à plus de 95%
columns_to_drop = [col for col, ratio in detect_empty_columns(df, threshold=0.95)]

# Suppression du DataFrame
df_cleaned = df.drop(columns_to_drop)

df_cleaned.write_ndjson("../openfoodfacts_no_empty_columns.jsonl")
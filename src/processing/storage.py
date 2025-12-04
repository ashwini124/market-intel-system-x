import pandas as pd
import os

def save_parquet(df, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_parquet(filename, index=False)

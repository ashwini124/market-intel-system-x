import pandas as pd
import re

def clean(df):
    df['content'] = df['content'].str.replace(r"http\S+", "", regex=True)
    df['content'] = df['content'].str.replace(r"[^a-zA-Z0-9@#\s]", " ", regex=True)
    df['content'] = df['content'].str.lower()
    df.drop_duplicates(subset=["content", "timestamp"], inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors="coerce")
    return df

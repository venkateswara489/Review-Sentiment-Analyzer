import pandas as pd

try:
    df = pd.read_csv('amazon_review_200thousand.csv', nrows=5, header=None)
    print("First 5 rows with header=None:")
    print(df)
    
    print("\nAttempting to infer header:")
    df_header = pd.read_csv('amazon_review_200thousand.csv', nrows=5)
    print(df_header)
except Exception as e:
    print(f"Error reading CSV: {e}")

import pandas as pd

# Read dataset
df = pd.read_csv('amazon_review_200thousand.csv', header=None, names=['label', 'title', 'review'])

print("Dataset shape:", df.shape)
print("\nFirst 10 rows:")
print(df.head(10))
print("\nLabel distribution:")
print(df['label'].value_counts().sort_index())
print("\nLabel unique values:", df['label'].unique())

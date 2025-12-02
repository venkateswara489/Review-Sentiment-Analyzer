import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from preprocessing import clean_text, assign_three_way_label

# Configuration
DATA_PATH = 'amazon_review_200thousand.csv'
MODEL_DIR = 'models'
MODEL_PATH = os.path.join(MODEL_DIR, 'sentiment_model.pkl')
VECTORIZER_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')

def load_and_prepare_data(filepath):
    print("Loading data...")
    
    # Read the entire dataset to ensure we get all labels (file is ~90MB, so it fits in memory)
    df = pd.read_csv(filepath, header=None, names=['label', 'title', 'review'])
    
    # Drop missing reviews
    df = df.dropna(subset=['review'])
    
    unique_labels = df['label'].unique()
    print(f"Unique labels found: {unique_labels}")
    
    # This dataset appears to be binary: 1=Negative, 2=Positive
    def map_sentiment(label):
        try:
            label = int(label)
            if label == 1:
                return 'Negative'
            elif label == 2:
                return 'Positive'
            else:
                # For any other value, return Neutral as fallback
                return 'Neutral'
        except:
            return 'Neutral'

    df['sentiment'] = df['label'].apply(map_sentiment)
    
    print(f"\nSentiment distribution:")
    print(df['sentiment'].value_counts())

    
    print("Cleaning text...")
    df['clean_review'] = df['review'].apply(clean_text)
    # Assign 3-way labels using heuristics
    print("Assigning 3-way labels using heuristics based on aspect sentiment and sarcasm detection...")
    df['sentiment3'] = df['review'].apply(assign_three_way_label)
    print("Sentiment3 distribution:")
    print(df['sentiment3'].value_counts())
    
    return df

def train_model():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    df = load_and_prepare_data(DATA_PATH)
    
    print("Preparing dataset for training (including optional seed upsampling)...")
    balanced_df = df

    print("Vectorizing...")
    vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
    X = vectorizer.fit_transform(balanced_df['clean_review'])
    y = balanced_df['sentiment3']

    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Training SVM with class weighting for class imbalance...")
    model = LinearSVC(class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    
    print("Evaluating...")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    print("Saving model and vectorizer...")
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
        
    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump(vectorizer, f)
        
    print("Done!")

if __name__ == "__main__":
    train_model()

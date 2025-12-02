from flask import Flask, render_template, request, jsonify
import pickle
import os
from preprocessing import clean_text, get_aspect_sentiment, detect_sarcasm_and_features, assign_three_way_label

app = Flask(__name__)

# Load models
MODEL_DIR = 'models'
MODEL_PATH = os.path.join(MODEL_DIR, 'sentiment_model.pkl')
VECTORIZER_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')

model = None
vectorizer = None

def load_models():
    global model, vectorizer
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        with open(VECTORIZER_PATH, 'rb') as f:
            vectorizer = pickle.load(f)
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Error loading models: {e}")

load_models()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not model or not vectorizer:
        return jsonify({'error': 'Model not loaded'}), 500
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Preprocess
    cleaned_text = clean_text(text)
    
    # Vectorize
    vec_text = vectorizer.transform([cleaned_text])
    
    # Predict Sentiment from model (3-class)
    model_sentiment = model.predict(vec_text)[0]
    # If needed, get the heuristic sentiment to compare
    heuristic_sentiment = assign_three_way_label(text)
    
    # Aspect Based Sentiment Analysis
    aspects = ['battery', 'screen', 'delivery', 'price', 'quality', 'performance', 'camera', 'sound', 'storage']
    aspect_sentiments = get_aspect_sentiment(text, aspects)
    
    # Smart mixed review detection
    # Count positive and negative aspects that were mentioned
    positive_count = sum(1 for sent in aspect_sentiments.values() if sent == 'Positive')
    negative_count = sum(1 for sent in aspect_sentiments.values() if sent == 'Negative')
    total_mentioned = positive_count + negative_count
    
    # If we have both positive and negative aspects mentioned
    # and they're relatively balanced, classify as Neutral (Mixed)
    final_sentiment = model_sentiment
    if total_mentioned >= 2:  # At least 2 aspects mentioned
        if positive_count > 0 and negative_count > 0:
            # Calculate balance ratio
            ratio = min(positive_count, negative_count) / max(positive_count, negative_count)
            # If ratio > 0.4, it's reasonably balanced, so it's mixed
            if ratio >= 0.4:
                final_sentiment = 'Neutral'
            # If one side dominates heavily, use that
            elif positive_count > negative_count * 2:
                final_sentiment = 'Positive'
            elif negative_count > positive_count * 2:
                final_sentiment = 'Negative'
    
    return jsonify({
        'sentiment': final_sentiment,
        'model_sentiment': model_sentiment,
        'heuristic_sentiment': heuristic_sentiment,
        'aspects': aspect_sentiments
    })

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pickle
import os
import json
from preprocessing import clean_text, get_aspect_sentiment, detect_sarcasm_and_features, assign_three_way_label

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a random secret key for production

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Data Management
USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        # Create default admin if file doesn't exist
        default_users = {'admin': {'password': 'password123'}}
        save_users(default_users)
        return default_users
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users_data):
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=4)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    if user_id not in users:
        return None
    return User(user_id)

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
@login_required
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        users = load_users()
        
        if username in users:
            flash('Username already exists')
        elif password != confirm_password:
            flash('Passwords do not match')
        else:
            users[username] = {'password': password}
            save_users(users)
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
            
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

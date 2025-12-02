# Review Sentiment Analyzer

Lightweight sentiment analysis project for product reviews. The repo contains a Flask demo app, a small preprocessing and heuristic aspect-sentiment module, and a training script that shows how to train a TF-IDF + SVM classifier.

## Contents

- `app.py` - Flask web app exposing a `/predict` endpoint and a minimal UI in `templates/` and `static/`.
- `preprocessing.py` - text cleaning, aspect-based sentiment heuristics, sarcasm detection, and a 3-way label assignment helper.
- `model_training.py` - example script to prepare data, vectorize text, train an SVM classifier, and save model artifacts (not included).
- `requirements.txt` - Python dependencies.
- `amazon_review_200thousand.csv` - dataset (large) used for training. This file is included in the repository as requested, but consider using Git LFS for better handling of large files.

## Quick start

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. (Optional) Train the model locally:

```powershell
python model_training.py
```

This script reads `amazon_review_200thousand.csv`, prepares 3-way labels using the heuristics in `preprocessing.py`, trains a `LinearSVC` model with TF-IDF features, and writes model artifacts to the `models/` folder. The `models/` folder is intentionally omitted from the repository; add your pickles there if you want the Flask app to load a trained model.

3. Run the Flask app:

```powershell
python app.py
```

Open `http://127.0.0.1:5000` in your browser to try the demo.

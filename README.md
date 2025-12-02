# GEN AI - Review Sentiment Analyzer

This repository contains a lightweight review sentiment analysis project built with Flask and scikit-learn.

What to include:
- app.py (Flask application)
- preprocessing.py (text cleaning and aspect sentiment heuristics)
- model_training.py (training script for SVM model)
- inspect_data.py, check_labels.py, test_reviews.py (helper scripts)
- templates/ and static/ for the front-end

Excluded from repo (added to .gitignore):
- Trained models and vectorizers (models/)
- Large datasets (amazon_review_200thousand.csv)
- Pickled files and cached files (*.pkl, __pycache__)

Quick start
-----------
1. Create a virtual environment and install dependencies:

```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Train a model (optional):

```powershell
python model_training.py
```

3. Run the app:

```powershell
python app.py
```

Notes
-----
- If you want to include a sample dataset, add a small `seed_reviews.csv` instead of the full dataset.
- Trained model files (pickles) are intentionally excluded from the repo; add instructions to your README for how to re-train or how to add your model to the `models/` directory.

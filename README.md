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

## Notes & recommendations

- The dataset `amazon_review_200thousand.csv` is ~90MB; GitHub shows a warning for files larger than 50MB. For collaboration, consider using Git LFS for the dataset and other large artifacts (`.pkl` models).
- The repo currently does not include trained model files. To share models, either commit them (not recommended) or provide download instructions in the README and keep `models/` in `.gitignore`.

## Contributing

- If you add new files, please avoid committing large binary files directly; use Git LFS or provide external downloads.

## License

Add a license file if you want to make this project open-source. MIT is a common choice.

---
If you'd like, I can:
- add a `.gitignore` back to ignore `models/`, `venv/`, and `*.pkl` (recommended),
- migrate the dataset to Git LFS, or
- add a small GitHub Actions workflow to run a basic test.

Tell me which of these you'd like me to do next.

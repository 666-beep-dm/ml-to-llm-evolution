# ML Pipeline — Wine Quality Classification

A modular, production-style ML pipeline that trains and compares
**Logistic Regression** and **Random Forest** on the Wine dataset.

## Setup
```bash
# 1. Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline
python train.py
```

## Design Decisions

| Concern | Choice |
|---|---|
| Scaling | `StandardScaler` (fit on train only) |
| Split | 80 / 20, stratified, `random_state=42` |
| Models | `LogisticRegression`, `RandomForestClassifier` |
| Metrics | Accuracy, Precision & Recall (`macro`) |
| Logging | `logging` to stdout with timestamps |
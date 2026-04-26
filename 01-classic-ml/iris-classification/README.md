# Iris Classification — Beginner ML Project

A simple Machine Learning project that trains a Logistic Regression
model to classify Iris flowers into 3 species using scikit-learn.

## Step-by-Step Setup

### 1. Create a virtual environment
```bash
python -m venv .venv
```

### 2. Activate it
```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the script
```bash
python main.py
```

## Expected Output
```
Dataset loaded successfully!
  Total samples : 150
  Features      : ['sepal length (cm)', 'sepal width (cm)', ...]
  Classes       : ['setosa', 'versicolor', 'virginica']

Data split complete!
  Training samples : 120
  Testing samples  : 30

Model trained successfully!

Predictions vs Actual (first 10 samples):
  Predicted : [1, 0, 2, 1, 1, 0, 1, 2, 1, 1]
  Actual    : [1, 0, 2, 1, 1, 0, 1, 2, 1, 1]

───────────────────────────────────
  Model Accuracy: 100.00%
───────────────────────────────────
```
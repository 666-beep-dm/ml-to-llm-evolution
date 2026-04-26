# ML Churn Prediction Service

A production-ready ML REST API for Bank Churn classification, built with
FastAPI, scikit-learn, and XGBoost.

---

## Project Structure

```
ml-service/
├── app/
│   ├── __init__.py
│   ├── api.py            ← FastAPI route definitions
│   ├── schemas.py        ← Pydantic request/response models
│   └── exceptions.py     ← Custom exception handlers
├── core/
│   ├── __init__.py
│   ├── pipeline.py       ← sklearn Pipeline construction
│   ├── trainer.py        ← Training logic
│   └── predictor.py      ← Inference logic
├── models/               ← joblib artifacts saved here
├── data/                 ← place your CSV files here
├── main.py
├── requirements.txt
└── Dockerfile
```

---

## Local Setup (venv)

```bash
# 1. Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python main.py
# API live at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

---

## Docker Setup

```bash
# Build image
docker build -t ml-service:latest .

# Run container (mount models/ so artifacts survive restarts)
docker run -d \
  -p 8000:8000 \
  -v "$(pwd)/models:/app/models" \
  -v "$(pwd)/data:/app/data" \
  --name ml-service \
  ml-service:latest

# View logs
docker logs -f ml-service
```

---

## Dataset

Download the Bank Churn dataset from Kaggle:
https://www.kaggle.com/datasets/shubhammeshram579/bank-customer-churn-prediction

Place the CSV as `data/churn.csv`. Required columns:
`CreditScore`, `Geography`, `Gender`, `Age`, `Tenure`, `Balance`,
`NumOfProducts`, `HasCrCard`, `IsActiveMember`, `EstimatedSalary`, `Exited`

---

## API Usage

### Health check

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### Train the model

```bash
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{"csv_path": "data/churn.csv", "target_column": "Exited"}'
```

**Response:**
```json
{
  "message": "Training complete.",
  "model_path": "models/pipeline.joblib",
  "training_rows": 8000,
  "accuracy": 0.8645
}
```

### Run a prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "credit_score": 620,
      "geography": "France",
      "gender": "Male",
      "age": 42,
      "tenure": 3,
      "balance": 75000.0,
      "num_of_products": 2,
      "has_cr_card": 1,
      "is_active_member": 0,
      "estimated_salary": 95000.0
    }
  }'
```

**Response:**
```json
{
  "prediction": 1,
  "label": "Churn",
  "probability": 0.7823
}
```

### Python requests example

```python
import requests

# Train
requests.post("http://localhost:8000/train", json={
    "csv_path": "data/churn.csv",
    "target_column": "Exited"
})

# Predict
response = requests.post("http://localhost:8000/predict", json={
    "features": {
        "credit_score": 750,
        "geography": "Germany",
        "gender": "Female",
        "age": 35,
        "tenure": 7,
        "balance": 120000.0,
        "num_of_products": 1,
        "has_cr_card": 1,
        "is_active_member": 1,
        "estimated_salary": 60000.0
    }
})
print(response.json())
# {'prediction': 0, 'label': 'No Churn', 'probability': 0.9211}
```

---

## Interactive Docs

Swagger UI:  http://localhost:8000/docs  
ReDoc:       http://localhost:8000/redoc

---

## Design Principles

| Principle | Implementation |
|-----------|---------------|
| Single Responsibility | `Trainer`, `Predictor`, `build_pipeline` each do one thing |
| Open/Closed | Add models via `_get_estimator()` without touching API layer |
| Dependency Inversion | Routes depend on abstractions, not concrete classes |
| Fail-Fast | Errors caught, logged with context, returned as structured JSON |
| No Data Leakage | Scaler fitted only on train split, never on test |

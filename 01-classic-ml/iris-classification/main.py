# main.py
# A beginner-friendly Iris classification project using Logistic Regression.

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# ── 1. Load the dataset ───────────────────────────────────────────────────────
iris = load_iris()
X = iris.data    # Features (sepal/petal length and width)
y = iris.target  # Labels (0 = Setosa, 1 = Versicolor, 2 = Virginica)

print("Dataset loaded successfully!")
print(f"  Total samples : {len(X)}")
print(f"  Features      : {iris.feature_names}")
print(f"  Classes       : {list(iris.target_names)}")
print()

# ── 2. Split into training and testing sets (80/20) ───────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,     # 20% for testing
    random_state=42    # Fixed seed for reproducibility
)

print(f"Data split complete!")
print(f"  Training samples : {len(X_train)}")
print(f"  Testing samples  : {len(X_test)}")
print()

# ── 3. Train the model ────────────────────────────────────────────────────────
model = LogisticRegression(max_iter=200)  # max_iter ensures the model converges
model.fit(X_train, y_train)

print("Model trained successfully!")
print()

# ── 4. Make predictions on the test set ──────────────────────────────────────
y_pred = model.predict(X_test)

# Show a quick side-by-side comparison of predictions vs actual labels
print("Predictions vs Actual (first 10 samples):")
print(f"  Predicted : {list(y_pred[:10])}")
print(f"  Actual    : {list(y_test[:10])}")
print()

# ── 5. Calculate and display the accuracy ────────────────────────────────────
accuracy = accuracy_score(y_test, y_pred)

print("─" * 35)
print(f"  Model Accuracy: {accuracy * 100:.2f}%")
print("─" * 35)
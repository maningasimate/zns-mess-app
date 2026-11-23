import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score

print("=== ZNS/DEFENSE LOGISTICS AI MODEL TRAINING ===")

# 1. Synthesize 12 Months of Institutional Operations Data
np.random.seed(42)
n_samples = 1200

headcount = np.random.randint(200, 2500, size=n_samples)
day_of_week = np.random.randint(0, 7, size=n_samples) # 0=Monday, 6=Sunday
is_training_exercise = np.random.choice([0, 1], size=n_samples, p=[0.75, 0.25])
avg_temperature = np.random.uniform(14.0, 36.0, size=n_samples)
season = np.random.randint(1, 5, size=n_samples)

food_demand = (
    0.85 * headcount +
    320.0 * is_training_exercise -
    3.0 * avg_temperature +
    18.0 * day_of_week +
    np.random.normal(0, 25, size=n_samples)
)

df = pd.DataFrame({
    'headcount': headcount,
    'day_of_week': day_of_week,
    'is_training_exercise': is_training_exercise,
    'avg_temperature': avg_temperature,
    'season': season,
    'food_demand': food_demand
})

X = df[['headcount', 'day_of_week', 'is_training_exercise', 'avg_temperature', 'season']]
y = df['food_demand']

# 2. Train / Test Split & Scaling
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

ridge_model = Ridge(alpha=1.5)
ridge_model.fit(X_train_scaled, y_train)

# 3. Evaluation
predictions = ridge_model.predict(X_test_scaled)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
r2 = r2_score(y_test, predictions)

print(f"[+] Model Training Complete.")
print(f"[+] Root Mean Squared Error (RMSE): {rmse:.4f} kg")
print(f"[+] R-Squared Accuracy Score: {r2:.4f}")

# 4. Serialize Artifacts
joblib.dump(ridge_model, 'military_demand_model.joblib')
joblib.dump(scaler, 'military_demand_scaler.joblib')
print("[+] Model & Scaler successfully saved to disk as .joblib files!")
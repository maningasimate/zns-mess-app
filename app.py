"""
===============================================================================
SYSTEM ARCHITECTURE: ZNS / Defense Force AI Mess Hall Logistics System
CONTROLLER: app.py (Active Stock Filter, Fresh Produce Sorting & Headcount Logging)
===============================================================================
"""

import os
import joblib
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash
from db_connect import get_db_connection

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "zambian_defense_tactical_key_2026")

# Load Serialized Machine Learning Model & Scaler on Server Boot
try:
    ml_model = joblib.load('military_demand_model.joblib')
    ml_scaler = joblib.load('military_demand_scaler.joblib')
    print("[+] AI Model & Scaler successfully loaded into Flask Application.")
except Exception as e:
    print(f"[!] WARNING: Failed to load Joblib ML model artifacts: {e}")
    ml_model, ml_scaler = None, None


# 1. COMMAND DASHBOARD (Excludes expired stock & prioritizes Fresh Produce + urgent expiry)
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query Active Unexpired Batches: Prioritizes Fresh Vegetables and closest expiry urgency
    cursor.execute("""
        SELECT 
            ib.id, fi.item_code, fi.item_name, ib.batch_number,
            ib.current_quantity, fi.unit_of_measure, ib.date_purchased, ib.expiry_date,
            (ib.expiry_date - CURRENT_DATE) AS days_to_expiry, s.supplier_name, fi.category
        FROM inventory_batches ib
        JOIN food_items fi ON ib.food_item_id = fi.id
        LEFT JOIN suppliers s ON ib.supplier_id = s.id
        WHERE ib.expiry_date >= CURRENT_DATE
        ORDER BY ib.expiry_date ASC, CASE WHEN fi.category = 'Fresh Produce' THEN 0 ELSE 1 END ASC 
        LIMIT 6;
    """)
    inventory_records = cursor.fetchall()

    # Query Top 5 Recent AI Forecast Runs (Including Headcount)
    cursor.execute("""
        SELECT df.forecast_date, fi.item_name, df.headcount, df.predicted_demand_kg, df.model_used, df.generated_at
        FROM demand_forecasts df
        JOIN food_items fi ON df.food_item_id = fi.id
        ORDER BY df.generated_at DESC LIMIT 5;
    """)
    forecast_records = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html', inventory=inventory_records, forecasts=forecast_records)


# 2. FULL HISTORICAL INVENTORY PAGE (Active unexpired stock prioritized by perishability)
@app.route('/inventory')
def full_inventory():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            ib.id, fi.item_code, fi.item_name, ib.batch_number,
            ib.quantity_received, ib.current_quantity, fi.unit_of_measure, 
            ib.unit_cost, ib.date_purchased, ib.expiry_date,
            (ib.expiry_date - CURRENT_DATE) AS days_to_expiry, s.supplier_name, fi.category
        FROM inventory_batches ib
        JOIN food_items fi ON ib.food_item_id = fi.id
        LEFT JOIN suppliers s ON ib.supplier_id = s.id
        WHERE ib.expiry_date >= CURRENT_DATE
        ORDER BY ib.expiry_date ASC, CASE WHEN fi.category = 'Fresh Produce' THEN 0 ELSE 1 END ASC;
    """)
    all_batches = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('inventory.html', inventory=all_batches)


# 3. FULL HISTORICAL FORECAST LOGS PAGE (Includes Headcount)
@app.route('/forecasts')
def full_forecasts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT df.forecast_date, fi.item_code, fi.item_name, df.headcount, df.predicted_demand_kg, df.model_used, df.generated_at
        FROM demand_forecasts df
        JOIN food_items fi ON df.food_item_id = fi.id
        ORDER BY df.generated_at DESC;
    """)
    all_forecasts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('forecasts.html', forecasts=all_forecasts)


# 4. EXECUTE AI PREDICTION
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            headcount = int(request.form.get('headcount'))
            day_of_week = int(request.form.get('day_of_week'))
            is_training = int(request.form.get('is_training_exercise'))
            temperature = float(request.form.get('avg_temperature'))
            season = int(request.form.get('season'))
            food_item_id = int(request.form.get('food_item_id'))

            if ml_model and ml_scaler:
                features = np.array([[headcount, day_of_week, is_training, temperature, season]])
                scaled_features = ml_scaler.transform(features)
                predicted_qty = float(ml_model.predict(scaled_features)[0])
                predicted_qty = max(10.0, round(predicted_qty, 2))

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO demand_forecasts (forecast_date, food_item_id, headcount, predicted_demand_kg, model_used)
                    VALUES (%s, %s, %s, %s, %s);
                """, (datetime.now().date() + timedelta(days=1), food_item_id, headcount, predicted_qty, 'Ridge Regression'))
                conn.commit()
                cursor.close()
                conn.close()

                flash(f"AI Demand Prediction Executed & Logged: {predicted_qty} kg Required for {headcount} Personnel.", "success")
            else:
                flash("ML Model Artifacts (.joblib) not found. Run train_model.py first.", "danger")

        except Exception as e:
            flash(f"Prediction Error: {str(e)}", "danger")

        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, item_name, unit_of_measure FROM food_items ORDER BY item_name ASC;")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('predict.html', items=items)


# 5. LIVE STOCK INTAKE ROUTE (For supervisor demo presentations)
@app.route('/add_batch', methods=['GET', 'POST'])
def add_batch():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            food_item_id = int(request.form.get('food_item_id'))
            supplier_id = int(request.form.get('supplier_id'))
            batch_number = request.form.get('batch_number')
            quantity_received = float(request.form.get('quantity_received'))
            unit_cost = float(request.form.get('unit_cost'))
            date_purchased = request.form.get('date_purchased')
            expiry_date = request.form.get('expiry_date')

            cursor.execute("""
                INSERT INTO inventory_batches 
                (food_item_id, supplier_id, batch_number, quantity_received, current_quantity, unit_cost, date_purchased, expiry_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (food_item_id, supplier_id, batch_number, quantity_received, quantity_received, unit_cost, date_purchased, expiry_date))
            
            conn.commit()
            flash("New stock batch successfully received and logged into PostgreSQL!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Error logging batch: {str(e)}", "danger")

    cursor.execute("SELECT id, item_name, unit_of_measure FROM food_items ORDER BY item_name ASC;")
    items = cursor.fetchall()
    cursor.execute("SELECT id, supplier_name FROM suppliers ORDER BY supplier_name ASC;")
    suppliers = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('add_batch.html', items=items, suppliers=suppliers)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
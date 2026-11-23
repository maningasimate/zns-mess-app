"""
===============================================================================
REALISTIC DEFENSE SHELF-LIFE & HEADCOUNT HISTORICAL DATA GENERATOR
FILE: seed_history.py
===============================================================================
"""

import random
from datetime import datetime, timedelta
from db_connect import get_db_connection

# Food Item Shelf Life Mapping (in Days) based on realistic storage
SHELF_LIFE_DAYS = {
    1: 4,    # Green Vegetables: 3-4 days
    2: 6,    # Tomatoes: 7 days
    3: 11,   # Onions: 10-11 days
    4: 21,   # Garlic: 21 days
    5: 18,   # Fresh Fish (Refrigerated): 14-21 days
    6: 21,   # Kapenta: 21 days (3 weeks)
    7: 30,   # Beef (Cold Storage): 30 days (1 month)
    8: 30,   # Chicken/Pork (Cold Storage): 30 days
    9: 45,   # Rice: 45 days (1.5 months)
    10: 120, # Cooking Oil: 180 days (6 months)
    11: 30   # Mealie Meal: 90 days
}

def seed_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("[+] Seeding 100+ Realistic Defense Logistics & AI Prediction Records...")

    # Define historical purchase timeline from August 1, 2026 to November 2, 2026
    current_today = datetime(2026, 11, 2)
    start_date = datetime(2026, 8, 1)

    # 1. Generate 65 Realistic Inventory Batches
    for i in range(1, 66):
        food_item_id = random.randint(1, 11)
        
        # Supplier matching
        if food_item_id in [1, 2, 3, 4]:
            supplier_id = 3 # Chongwe Produce
        elif food_item_id in [5, 7, 8]:
            supplier_id = 2 # Meat Co-op
        else:
            supplier_id = 1 # ZNS National Supply

        batch_no = f"ZNS-BATCH-2026-{100 + i}"
        
        # Calculate realistic purchase date
        days_ago = random.randint(0, 90)
        date_purchased = current_today - timedelta(days=days_ago)
        
        # Calculate exact expiry date using realistic shelf life
        max_shelf = SHELF_LIFE_DAYS[food_item_id]
        expiry_date = date_purchased + timedelta(days=max_shelf)
        
        qty_received = round(random.uniform(100.0, 1500.0), 2)
        current_qty = round(qty_received * random.uniform(0.15, 1.0), 2)
        unit_cost = round(random.uniform(25.0, 480.0), 2)

        cursor.execute("""
            INSERT INTO inventory_batches 
            (food_item_id, supplier_id, batch_number, quantity_received, current_quantity, unit_cost, date_purchased, expiry_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """, (food_item_id, supplier_id, batch_no, qty_received, current_qty, unit_cost, date_purchased.date(), expiry_date.date()))

    # 2. Generate 50 Historical AI Demand Forecast Records (Including Headcount)
    models = ['Ridge Regression', 'Ridge Regression (Optimized)']
    for i in range(1, 51):
        food_item_id = random.randint(1, 11)
        days_ago = random.randint(0, 90)
        forecast_date = current_today - timedelta(days=days_ago)
        
        # Headcount between 200 and 2200 personnel
        headcount = random.choice([450, 800, 1200, 1550, 2100])
        predicted_kg = round((0.85 * headcount) + random.uniform(-40, 60), 2)
        timestamp = forecast_date + timedelta(hours=random.randint(7, 17))

        cursor.execute("""
            INSERT INTO demand_forecasts
            (forecast_date, food_item_id, headcount, predicted_demand_kg, model_used, generated_at)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (forecast_date.date(), food_item_id, headcount, predicted_kg, models[0], timestamp))

    conn.commit()
    cursor.close()
    conn.close()
    print("[+] Successfully seeded 115 realistic records into PostgreSQL!")

if __name__ == '__main__':
    seed_database()
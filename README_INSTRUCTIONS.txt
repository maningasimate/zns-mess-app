Hi Maninga,

Here is the complete, fully functional prototype for Project #22: AI-Based Food Demand Forecasting and Inventory Management System.

📁 Zip Contents:
- Flask Web App (app.py) & PostgreSQL connector (db_connect.py)
- Machine Learning Trainer & Joblib Serializer (train_model.py)
- Historical Seed Script (115+ Records with realistic food shelf-lives)
- PostgreSQL Database Schema Script (update_schema.sql)
- Tactical Military UI (static/ & templates/)

🚀 How to Run on Your Laptop:

1. Extract the ZIP file into your VS Code Projects folder.
2. Database Setup (pgAdmin 4):
   - Create a database named `military_food_db`.
   - Open Query Tool on `military_food_db`, paste the contents of `update_schema.sql`, and hit Execute (F5).
3. Seed History & Train AI Model (VS Code Terminal):
   - Run: python seed_history.py
   - Run: python train_model.py
4. Launch System:
   - Run: python app.py
   - Open browser to: http://127.0.0.1:5000/

Key Features Demonstrated:
- Active stock filtering (excludes expired items from active view)
- Perishability risk sorting (prioritizes fresh produce like rape, tomatoes, onions)
- Dynamic AI demand inference (Ridge Regression) with personnel headcount tracking
- Full historical auditing logs via translucent '+' corner buttons
- Live stock intake form (+ Receive New Stock) for live supervisor demos
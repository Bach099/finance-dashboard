#  TRANSACTION SERVICE  will be running on port 5001
#  This is the main part of the app
#  related to money: adding, reading, editing, and deleting
#  transactions, plus managing savings goals.
#  It stores everything in a finance.db which is a local sql file 

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# CORS lets our HTML frontend (which opens from a file or
# different port) talk to this Python server without the
# browser blocking the request for security reasons.
CORS(app)

# Build the path to finance.db relative to THIS file's location.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'finance.db')


# Here is the DATABASE SETUP 
def get_db():
    """Open a connection to the SQLite database and return it."""
    conn = sqlite3.connect(DB_PATH)
    # row_factory lets us access columns by name (row['amount'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create all tables on first run.
    'IF NOT EXISTS' means this is completely safe to call
    on every startup — it won't erase your data.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Stores every income or expense entry the user creates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            type        TEXT NOT NULL,       -- 'income' or 'expense'
            amount      REAL NOT NULL,
            category    TEXT NOT NULL,       -- e.g. 'food', 'salary'
            description TEXT,               -- optional free-text note
            date        TEXT NOT NULL,       -- stored as 'YYYY-MM-DD'
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS savings_goals (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_name      TEXT NOT NULL,
            goal_amount    REAL NOT NULL,    -- target they want to reach
            current_amount REAL DEFAULT 0,  -- how much saved so far
            created_at     TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


#TRANSACTIONS 

@app.route('/transactions', methods=['POST'])
def add_transaction():
    """
    Create a brand-new transaction.
    The frontend sends JSON like: { type, amount, category, date, description }
    We validate the required fields, then insert into the database.
    """
    data = request.get_json()

    # Make sure none of the essential fields are missing
    required = ['type', 'amount', 'category', 'date']
    for field in required:
        if field not in data:
            return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['type'],
        data['amount'],
        data['category'],
        data.get('description', ''),   
        data['date']
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Transaction saved"}), 201


@app.route('/transactions', methods=['GET'])
def get_transactions():
    """
    Return every transaction, newest first.
    The frontend uses this list to build the history page
    and the recent-transactions section on the dashboard.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    # Convert each SQLite Row object into a plain Python dict
    # so Flask can turn it into JSON automatically.
    return jsonify([dict(row) for row in rows])


@app.route('/transactions/<int:id>', methods=['PUT'])
def update_transaction(id):
    """
    Edit an existing transaction by its ID.
    Example URL: PUT /transactions/5  →  updates the row where id = 5.
    We overwrite all editable fields with whatever the user sent.
    """
    data = request.get_json()

    required = ['type', 'amount', 'category', 'date']
    for field in required:
        if field not in data:
            return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE transactions
        SET type=?, amount=?, category=?, description=?, date=?
        WHERE id=?
    ''', (
        data['type'],
        data['amount'],
        data['category'],
        data.get('description', ''),
        data['date'],
        id
    ))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"status": "error", "message": "Transaction not found"}), 404

    conn.close()
    return jsonify({"status": "success", "message": "Transaction updated"})


@app.route('/transactions/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    """
    Permanently remove a transaction by ID.
    Returns 404 if the ID wasn't found so the frontend
    can show a helpful error instead of silently doing nothing.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id=?', (id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"status": "error", "message": "Transaction not found"}), 404

    conn.close()
    return jsonify({"status": "success", "message": "Transaction deleted"})


#  SAVINGS GOALS

@app.route('/savings', methods=['POST'])
def add_savings_goal():
    """
    Create a new savings goal.
    Expects: { goalName, goalAmount, currentAmount }
    currentAmount lets the user pre-fill how much they've
    already set aside before starting to track here.
    """
    data = request.get_json()

    required = ['goalName', 'goalAmount', 'currentAmount']
    for field in required:
        if field not in data:
            return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO savings_goals (goal_name, goal_amount, current_amount)
        VALUES (?, ?, ?)
    ''', (data['goalName'], data['goalAmount'], data['currentAmount']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Savings goal saved"}), 201


@app.route('/savings', methods=['GET'])
def get_savings():
    """
    Return all savings goals so the frontend can display
    the progress bars on the Savings Goals page.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM savings_goals')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route('/savings/<int:id>', methods=['PUT'])
def update_savings_goal(id):
    """
    Edit an existing savings goal by its ID.
    Example URL: PUT /savings/2  →  updates the goal where id = 2.

    You can update:
      - goalName      — rename the goal
      - goalAmount    — change the target
      - currentAmount — update how much has been saved

    All three fields are required in the request body.
    """
    data = request.get_json()

    required = ['goalName', 'goalAmount', 'currentAmount']
    for field in required:
        if field not in data:
            return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE savings_goals
        SET goal_name=?, goal_amount=?, current_amount=?
        WHERE id=?
    ''', (
        data['goalName'],
        data['goalAmount'],
        data['currentAmount'],
        id
    ))
    conn.commit()

    # 0 affected rows means the ID doesn't exist in the database
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"status": "error", "message": "Savings goal not found"}), 404

    conn.close()
    return jsonify({"status": "success", "message": "Savings goal updated"})


@app.route('/savings/<int:id>', methods=['DELETE'])
def delete_savings_goal(id):
    """
    Delete a savings goal by ID.
    Useful when a goal has been completed or is no longer needed.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM savings_goals WHERE id=?', (id,))
    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"status": "error", "message": "Savings goal not found"}), 404

    conn.close()
    return jsonify({"status": "success", "message": "Savings goal deleted"})


#  Main 
if __name__ == '__main__':
    # Set up the database tables (safe to run every time)
    init_db()
    print("✅ Transaction Service running on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
#  ANALYTICS SERVICE will runs on http://localhost:5002
#  This service is read-only it never writes to the database.
#  Service writes to, so both services stay in sync.


from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)

# CORS is needed so the browser doesn't block requests coming
# from the frontend (which may run on a different port).
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, '..', 'transaction_service', 'finance.db')


def get_db():
    """Open a read connection to the shared SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets us use column names instead of indexes
    return conn


@app.route('/analytics/summary', methods=['GET'])
def get_summary():
    """
    Return a full financial summary used by the dashboard:
      - Total income ever recorded
      - Total expenses ever recorded
      - Net savings (income minus expenses)
      - The single expense category with the highest total
      - A breakdown of every expense category with its total
      - The date of the very first transaction (tracking since)

    If the database file doesn't exist yet (i.e. no transactions
    have been added), we return zeros instead of crashing.
    """

    # Guard: if the database file hasn't been created yet,
    # return a clean zero-state so the dashboard still loads.
    if not os.path.exists(DB_PATH):
        return jsonify({
            "totalIncome":   0,
            "totalExpenses": 0,
            "netSavings":    0,
            "topCategory":   None,
            "byCategory":    [],
            "trackingSince": None
        })

    conn = get_db()
    cursor = conn.cursor()

    # never return None when the table is empty.
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE type = 'income'
    """)
    total_income = cursor.fetchone()['total']

    # Same idea for expenses
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE type = 'expense'
    """)
    total_expenses = cursor.fetchone()['total']

    cursor.execute("""
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE type = 'expense'
        GROUP BY category
        ORDER BY total DESC
    """)
    by_category = [dict(row) for row in cursor.fetchall()]

    # Find the oldest transaction date so we can show
    cursor.execute("SELECT MIN(date) AS first_date FROM transactions")
    first_date_row = cursor.fetchone()
    first_date = first_date_row['first_date'] if first_date_row else None

    conn.close()

    # The top spending category is simply the first item in the
    # sorted list or None if there are no expenses yet.
    top_category = by_category[0]['category'] if by_category else None

    return jsonify({
        "totalIncome":   total_income,
        "totalExpenses": total_expenses,
        "netSavings":    total_income - total_expenses,
        "topCategory":   top_category,
        "byCategory":    by_category,
        "trackingSince": first_date
    })


#  Main
if __name__ == '__main__':
    print("✅ Analytics Service running on http://localhost:5002")
    app.run(port=5002, debug=True)
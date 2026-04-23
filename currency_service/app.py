# currency_service/app.py
# Runs on port 5003.
# Fetches live exchange rates from ExchangeRate-API.
# If the API is down or key is wrong, returns fallback rates

# HOW TO ADD YOUR KEY:
# Option 1 (easiest) edit this file: replace YOUR_API_KEY_HERE below
# Option 2: create a .env file with: EXCHANGE_API_KEY=yourkey

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# If that's not set, falls back to the placeholder in this file.
API_KEY = os.environ.get("EXCHANGE_API_KEY", "YOUR_API_KEY_HERE")


@app.route('/currency', methods=['GET'])
def get_currency():
    base = request.args.get('base', 'USD')

    try:
        url      = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base}"
        response = requests.get(url, timeout=5)
        data     = response.json()

        if data.get('result') == 'success':
            rates = data['conversion_rates']
            return jsonify({
                "base":       base,
                "USD_to_LBP": rates.get('LBP', 89000),
                "USD_to_EUR": rates.get('EUR'),
                "USD_to_GBP": rates.get('GBP'),
                "all_rates":  rates
            })

    except Exception as e:
        print(f"Currency API error: {e}")

    # Fallback rates:  when API is not available or key is missing
    return jsonify({
        "base":       base,
        "note":       "Using fallback rates — live API unavailable",
        "USD_to_LBP": 89000,
        "USD_to_EUR": 0.92,
        "USD_to_GBP": 0.79
    })


if __name__ == '__main__':
    print("Currency Service running on http://localhost:5003")
    app.run(port=5003, debug=True)
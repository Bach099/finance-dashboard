#  CURRENCY SERVICE  —  runs on http://localhost:5003
#  This service fetches live exchange rates from an external
#  API (ExchangeRate-API) and returns the ones our app cares
#  about: USD → LBP, EUR, GBP, and more.

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)

# CORS allows the browser to call this service from the
# frontend without getting blocked by same-origin policy.
CORS(app)

# You need to get your personal API key for https://www.exchangerate-api.com
API_KEY = "c854fa222a904108f1e034f9"


@app.route('/currency', methods=['GET'])
def get_currency():
    """
    Return exchange rates for a given base currency (default: USD).
    The frontend calls this as: GET /currency?base=USD

    We hit the ExchangeRate-API, pull out the rates we need,
    and send them back in a clean format the frontend understands.

    If anything goes wrong (network error, bad API response,
    timeout), we catch the exception and return safe fallback
    values so the dashboard still shows something useful.
    """

    # Read the ?base= query param, defaulting to USD if missing
    base = request.args.get('base', 'USD')

    try:
        # Build the request URL using our API key and base currency
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base}"

        # timeout=5 means: if the API takes more than 5 seconds
        response = requests.get(url, timeout=5)
        data = response.json()

        # The API signals success with result == 'success'
        if data.get('result') == 'success':
            rates = data['conversion_rates']

            # Return the full rates object so the currency
            return jsonify({
                "base":        base,
                "USD_to_LBP":  rates.get('LBP', 89000),  # Lebanese Lira
                "USD_to_EUR":  rates.get('EUR'),           # Euro
                "USD_to_GBP":  rates.get('GBP'),           # British Pound
                "all_rates":   rates                        # everything else
            })

    except Exception as e:
        # Print the error in the terminal for debugging,
        # but don't crash — fall through to the fallback below.
        print(f"Currency API error: {e}")

    # If we reach here, the live API failed for some reason.
    return jsonify({
        "base":        base,
        "note":        "Using fallback rates — live API unavailable",
        "USD_to_LBP":  89000,   # approximate as of 2024
        "USD_to_EUR":  0.92,
        "USD_to_GBP":  0.79
    })


# Main
if __name__ == '__main__':
    print("✅ Currency Service running on http://localhost:5003")
    app.run(port=5003, debug=True)
# Bachir's Finance Dashboard

A personal finance tracker built with Python Flask and vanilla JavaScript.
Three backend services handle transactions, analytics, and live currency rates.
All data is stored locally in a SQLite database.

---
## 📸 Screenshots

![Finance Dashboard Screenshot](https://github.com/Bach099/finance-dashboard/blob/main/Screenshots/Finance-dashboardss.png?raw=true)




## Features

- Add, edit, and delete income and expense transactions
- Dashboard with live summary stats and spending by category
- Savings goals with progress bars — add, edit, and delete
- Live currency exchange rates via ExchangeRate-API
- USD converter (LBP, EUR, GBP, SAR, AED)
- Export transactions to JSON or CSV

---

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | HTML, CSS, JavaScript (no framework) |
| Backend | Python, Flask, Flask-CORS |
| Database | SQLite |
| External API | ExchangeRate-API |

---

## Project Structure

```
finance-dashboard/
├── index.html               # The full single-page frontend
├── transaction_service.py   # CRUD for transactions + savings goals (port 5001)
├── analytics_service.py     # Read-only financial summary (port 5002)
├── currency_service.py      # Live exchange rates (port 5003)
├── requirements.txt         # Python dependencies
├── .gitignore               # Keeps finance.db and cache out of Git
└── README.md                # This file
```

> `finance.db` is created automatically the first time you run `transaction_service.py`. You don't need to create it.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your API key

Open `currency_service.py` and find this line:

```python
API_KEY = "YOUR_API_KEY_HERE"
```

Replace `YOUR_API_KEY_HERE` with a free key from [exchangerate-api.com](https://www.exchangerate-api.com).
**Skipping this is fine** — the app uses fallback rates and still works without it.

### 3. Start all three services

Open **3 separate terminal windows** and run one in each:

```bash
python transaction_service.py   # Terminal 1 — port 5001
python analytics_service.py     # Terminal 2 — port 5002
python currency_service.py      # Terminal 3 — port 5003
```

### 4. Open the app

Double-click `index.html` to open it in your browser. No extra server needed.

---

## API Endpoints

### Transaction Service — `localhost:5001`

| Method | Route | What it does |
|--------|-------|-------------|
| GET | `/transactions` | Get all transactions |
| POST | `/transactions` | Add a transaction |
| PUT | `/transactions/<id>` | Edit a transaction |
| DELETE | `/transactions/<id>` | Delete a transaction |
| GET | `/savings` | Get all savings goals |
| POST | `/savings` | Add a savings goal |
| PUT | `/savings/<id>` | Edit a savings goal |
| DELETE | `/savings/<id>` | Delete a savings goal |

### Analytics Service — `localhost:5002`

| Method | Route | What it does |
|--------|-------|-------------|
| GET | `/analytics/summary` | Income, expenses, net savings, top category |

### Currency Service — `localhost:5003`

| Method | Route | What it does |
|--------|-------|-------------|
| GET | `/currency?base=USD` | Live exchange rates |
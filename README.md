# 💰 Personal Expense Tracker (Streamlit App)

A simple and intuitive expense tracking app built with [Streamlit](https://streamlit.io/).
Track your daily expenses across 5 categories with persistent storage using SQLite.

---

## 🚀 Features

* 5 categories: **Fuel, Products, Food, Coffee, Gifting**
* Add expenses with **date, title, and cost**
* View each category in its own table
* See **totals per category** and a **grand total** at the bottom
* Delete entries with a single click
* Data is stored in a **SQLite database** (`expenses.db`) so it persists even when the app restarts

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/saifdoescode/personal-expense-tracker.git
cd personal-expense-tracker
```

Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\\Scripts\\activate    # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

Open your browser at **[http://localhost:8501](http://localhost:8501)**.

---

## 🗂 Project Structure

```
personal-expense-tracker/
│
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── expenses.db         # SQLite database (auto-created when app runs)
└── .gitignore          # Ignores DB + cache files
```

---

## 🛠 Database

* SQLite database: `expenses.db`
* One table per category: `Fuel`, `Products`, `Food`, `Coffee`, `Gifting`
* Schema:

```sql
CREATE TABLE CategoryName (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    title TEXT,
    cost REAL
);
```

---

## 🌍 Deployment

You can deploy this app for free using **[Streamlit Cloud](https://streamlit.io/cloud)**:

1. Push your code to GitHub.
2. Go to [Streamlit Cloud](https://share.streamlit.io/) and connect your repo.
3. Select `app.py` as the entry point.
4. Done! 🎉

---

## 📜 License

MIT License – feel free to use and modify for personal use.

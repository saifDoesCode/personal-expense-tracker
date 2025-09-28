import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# -----------------------------
# Database Setup
# -----------------------------
DB_FILE = "expenses.db"

# Categories
CATEGORIES = ["Fuel", "Products", "Food", "Coffee", "Gifting"]

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    for cat in CATEGORIES:
        c.execute(f"""
            CREATE TABLE IF NOT EXISTS {cat} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                title TEXT,
                cost REAL
            )
        """)
    conn.commit()
    conn.close()

# Add expense
def add_expense(category, date, title, cost):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"INSERT INTO {category} (date, title, cost) VALUES (?, ?, ?)",
              (date, title, cost))
    conn.commit()
    conn.close()

# Get expenses
def get_expenses(category):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(f"SELECT id, date, title, cost FROM {category}", conn)
    conn.close()
    return df

# Delete expense
def delete_expense(category, expense_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"DELETE FROM {category} WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

# -----------------------------
# Streamlit UI
# -----------------------------

st.set_page_config(page_title="Expense Tracker", layout="wide")
st.title("💰 Personal Expense Tracker")

init_db()

total_all = 0

# Display tables for each category
for cat in CATEGORIES:
    st.subheader(f"📌 {cat}")

    col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
    with col1:
        date = st.date_input(f"{cat} - Date", value=datetime.today(), key=f"date_{cat}")
    with col2:
        title = st.text_input(f"{cat} - Title", key=f"title_{cat}")
    with col3:
        cost = st.number_input(f"{cat} - Cost", min_value=0.0, format="%.2f", key=f"cost_{cat}")
    with col4:
        if st.button(f"Add to {cat}", key=f"add_{cat}"):
            if title and cost > 0:
                add_expense(cat, date.strftime("%Y-%m-%d"), title, cost)
                st.success(f"Added to {cat}!")

    # Show table with delete buttons
    df = get_expenses(cat)
    if not df.empty:
        for idx, row in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 1])
            with col1:
                st.write(row["date"])
            with col2:
                st.write(row["title"])
            with col3:
                st.write(f"AED {row['cost']:.2f}")
            with col4:
                st.write(f"ID: {row['id']}")
            with col5:
                if st.button("❌", key=f"del_{cat}_{row['id']}"):
                    delete_expense(cat, row["id"])
                    st.experimental_rerun()

        total = df["cost"].sum()
        st.markdown(f"**Total {cat}:** AED {total:,.2f}")
        total_all += total
    else:
        st.info("No expenses added yet.")

    st.divider()

# Grand total
st.header("🧾 Grand Total")
st.markdown(f"### Total Expenses Across All Categories: AED {total_all:,.2f}")

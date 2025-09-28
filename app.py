import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

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

# Get all expenses combined
def get_all_expenses():
    all_data = []
    conn = sqlite3.connect(DB_FILE)
    
    for cat in CATEGORIES:
        df = pd.read_sql_query(f"SELECT date, title, cost FROM {cat}", conn)
        df['category'] = cat
        all_data.append(df)
    
    conn.close()
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df['date'] = pd.to_datetime(combined_df['date'])
        return combined_df
    else:
        return pd.DataFrame(columns=['date', 'title', 'cost', 'category'])

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

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["💰 Expense Entry", "📊 Insights & Analytics"])

init_db()

if page == "💰 Expense Entry":
    st.title("💰 Personal Expense Tracker")
    
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
                    st.rerun()

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
                        st.rerun()

            total = df["cost"].sum()
            st.markdown(f"**Total {cat}:** AED {total:,.2f}")
            total_all += total
        else:
            st.info("No expenses added yet.")

        st.divider()

    # Grand total
    st.header("🧾 Grand Total")
    st.markdown(f"### Total Expenses Across All Categories: AED {total_all:,.2f}")

elif page == "📊 Insights & Analytics":
    st.title("📊 Expense Insights & Analytics")
    
    # Get all data
    df = get_all_expenses()
    
    if df.empty:
        st.info("No expenses recorded yet. Go to the Expense Entry page to add some expenses!")
    else:
        # Date range filter
        st.sidebar.subheader("Filters")
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
        else:
            filtered_df = df
        
        # Key Metrics
        st.header("📈 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_spent = filtered_df['cost'].sum()
            st.metric("Total Spent", f"AED {total_spent:,.2f}")
        
        with col2:
            avg_daily = filtered_df.groupby(filtered_df['date'].dt.date)['cost'].sum().mean()
            st.metric("Avg Daily Spend", f"AED {avg_daily:.2f}")
        
        with col3:
            total_transactions = len(filtered_df)
            st.metric("Total Transactions", total_transactions)
        
        with col4:
            avg_transaction = filtered_df['cost'].mean()
            st.metric("Avg Transaction", f"AED {avg_transaction:.2f}")
        
        st.divider()
        
        # Monthly Insights
        st.header("📅 Monthly Insights")
        
        # Prepare monthly data
        filtered_df['year_month'] = filtered_df['date'].dt.to_period('M').astype(str)
        monthly_data = filtered_df.groupby(['year_month', 'category'])['cost'].sum().reset_index()
        monthly_total = filtered_df.groupby('year_month')['cost'].sum().reset_index()
        
        # Monthly spending trend
        fig_monthly_trend = px.line(
            monthly_total, 
            x='year_month', 
            y='cost',
            title='Monthly Spending Trend',
            labels={'cost': 'Amount (AED)', 'year_month': 'Month'},
            markers=True
        )
        fig_monthly_trend.update_layout(xaxis_title="Month", yaxis_title="Amount (AED)")
        st.plotly_chart(fig_monthly_trend, use_container_width=True)
        
        # Monthly spending by category
        fig_monthly_category = px.bar(
            monthly_data,
            x='year_month',
            y='cost',
            color='category',
            title='Monthly Spending by Category',
            labels={'cost': 'Amount (AED)', 'year_month': 'Month'}
        )
        fig_monthly_category.update_layout(xaxis_title="Month", yaxis_title="Amount (AED)")
        st.plotly_chart(fig_monthly_category, use_container_width=True)
        
        st.divider()
        
        # Category Analysis
        st.header("🏷️ Category Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Category pie chart
            category_totals = filtered_df.groupby('category')['cost'].sum().reset_index()
            fig_pie = px.pie(
                category_totals,
                values='cost',
                names='category',
                title='Spending Distribution by Category'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Category bar chart
            fig_bar = px.bar(
                category_totals.sort_values('cost', ascending=False),
                x='category',
                y='cost',
                title='Total Spending by Category',
                labels={'cost': 'Amount (AED)', 'category': 'Category'}
            )
            fig_bar.update_layout(xaxis_title="Category", yaxis_title="Amount (AED)")
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.divider()
        
        # Daily Spending Pattern
        st.header("📊 Daily Spending Patterns")
        
        # Daily spending
        daily_spending = filtered_df.groupby(filtered_df['date'].dt.date)['cost'].sum().reset_index()
        daily_spending.columns = ['date', 'cost']
        
        fig_daily = px.line(
            daily_spending,
            x='date',
            y='cost',
            title='Daily Spending Pattern',
            labels={'cost': 'Amount (AED)', 'date': 'Date'},
            markers=True
        )
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Day of week analysis
        filtered_df['day_of_week'] = filtered_df['date'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_spending = filtered_df.groupby('day_of_week')['cost'].sum().reindex(day_order).reset_index()
        
        fig_dow = px.bar(
            dow_spending,
            x='day_of_week',
            y='cost',
            title='Spending by Day of Week',
            labels={'cost': 'Amount (AED)', 'day_of_week': 'Day of Week'}
        )
        st.plotly_chart(fig_dow, use_container_width=True)
        
        st.divider()
        
        # Top Expenses
        st.header("🔝 Top Expenses")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Highest Single Expenses")
            top_expenses = filtered_df.nlargest(10, 'cost')[['date', 'category', 'title', 'cost']]
            top_expenses['date'] = top_expenses['date'].dt.strftime('%Y-%m-%d')
            top_expenses['cost'] = top_expenses['cost'].apply(lambda x: f"AED {x:.2f}")
            st.dataframe(top_expenses, hide_index=True)
        
        with col2:
            st.subheader("Monthly Summary Table")
            monthly_summary = filtered_df.groupby('year_month').agg({
                'cost': ['sum', 'count', 'mean']
            }).round(2)
            monthly_summary.columns = ['Total (AED)', 'Transactions', 'Avg per Transaction (AED)']
            monthly_summary = monthly_summary.reset_index()
            st.dataframe(monthly_summary, hide_index=True)
import streamlit as st
import csv
from datetime import datetime
from collections import defaultdict
import io
import pandas as pd
import plotly.express as px

def calculate_spending(uploaded_file, monthly_income, start_date=None, end_date=None):
    """
    Calculates spending, income, and savings from a CSV file.

    Args:
        uploaded_file (streamlit.uploaded_file_manager.UploadedFile): The uploaded CSV file object.
        monthly_income (float): The user's monthly income.
        start_date (datetime.date, optional): Start date for filtering transactions. Defaults to None.
        end_date (datetime.date, optional): End date for filtering transactions. Defaults to None.


    Returns:
        dict: A dictionary containing the calculated statistics.
    """

    total_expenses = 0
    total_income = 0
    expenses_without_bills = 0
    category_expenses = defaultdict(float)
    daily_spending = defaultdict(float)
    daily_income = defaultdict(float)

    # List of fixed bills categories
    bills_categories = [
        "Rent", "Electricity", "Heating", "Water",
        "Phone + Internet", "Building Fees", "Taxes", "Energy"
    ]

    transactions = []

    with io.TextIOWrapper(uploaded_file, encoding='utf-8') as file:
        reader = csv.reader(file, skipinitialspace=True)
        header = next(reader) # Read the header row
        for row in reader:
            # Skip empty rows
            if not row or not any(row):
              continue

            #remove unnecessary text
            if row[0].startswith("Ημερομηνία"):
              continue

            # Data Extraction and Type Conversions
            category = row[0].strip()
            amount = float(row[2].replace(",", "."))  # Convert to float and handle decimal commas
            transaction_date = datetime.strptime(row[1], "%d/%m/%Y").date() # Convert date string to a datetime object

            #Filter transactions based on date range
            if start_date and end_date and not (start_date <= transaction_date <= end_date):
                continue
            
            transactions.append({"category": category, "amount": amount, "date": transaction_date})

            # Calculations
            if amount < 0:
                total_expenses += abs(amount)
                category_expenses[category] += abs(amount)
                daily_spending[transaction_date] += abs(amount)

                if category not in bills_categories:
                  expenses_without_bills += abs(amount)

            elif amount > 0:
                total_income += amount
                daily_income[transaction_date] += amount

            
    # Calculate Total Savings
    total_savings = total_income - total_expenses
    #Calculate Remaining Budget
    remaining_budget = monthly_income - total_expenses


    # Build report
    report = {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "total_savings": total_savings,
        "remaining_budget": remaining_budget,
        "expenses_without_bills": expenses_without_bills,
        "category_expenses": dict(category_expenses),
        "daily_spending": dict(daily_spending),
         "daily_income": dict(daily_income),
         "transactions": transactions
    }
    return report


def print_overview(report):
    """Prints the spending report to the console."""

    st.header("Spending Overview")

    #Total spending pie chart
    if report["category_expenses"]:
        df_pie = pd.DataFrame(report["category_expenses"].items(), columns=["Category", "Amount"])
        fig_pie = px.pie(df_pie, values='Amount', names='Category', title='Spending by Category')
        st.plotly_chart(fig_pie)

       
    
    # Total spending bar chart
    if report["category_expenses"]:
        df_bar = pd.DataFrame(report["category_expenses"].items(), columns=["Category", "Amount"])
        fig_bar = px.bar(df_bar, x="Category", y="Amount", title='Spending by Category')
        st.plotly_chart(fig_bar)
    else:
        st.write("No spending data available.")
        
def print_daily_spending(report):
  st.header("Daily Spending and Remaining Income")
  if report["daily_spending"] or report["daily_income"]:
        df_daily_spending = pd.DataFrame(report["daily_spending"].items(), columns=["Date", "Spending"])
        df_daily_income = pd.DataFrame(report["daily_income"].items(), columns=["Date", "Income"])
        df_daily = pd.merge(df_daily_spending, df_daily_income, on="Date", how="outer").fillna(0)
        df_daily["Remaining"] =  monthly_income - df_daily["Spending"]
        df_daily = df_daily.sort_values("Date")
        fig_daily = px.bar(df_daily, x="Date", y=["Income", "Spending", "Remaining"], title='Daily Spending and Remaining Income')
        st.plotly_chart(fig_daily)
  else:
      st.write("No daily spending/income data available.")

def print_category_spending(report):
    """Prints the spending per category report."""
    st.header("Spending Per Category")
    if report["category_expenses"]:
      df_category = pd.DataFrame(report["category_expenses"].items(), columns=["Category", "Amount"])
      fig_category = px.bar(df_category, x="Category", y="Amount", title='Spending Per Category')
      st.plotly_chart(fig_category)
    else:
      st.write("No category spending data available.")



st.title("Spending Tracker")

uploaded_file = st.file_uploader("Upload your transactions CSV", type=["csv"])
monthly_income = st.number_input("Enter your monthly income", value=1150)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=None,  format="YYYY-MM-DD")
with col2:
    end_date = st.date_input("End Date", value=None, format="YYYY-MM-DD")
    


if uploaded_file is not None:
    report = calculate_spending(uploaded_file, monthly_income, start_date, end_date)
    if report:
          st.write(f"Total Income: {report['total_income']:.2f}€")
          st.write(f"Total Expenses: {report['total_expenses']:.2f}€")
          st.write(f"Total Savings: {report['total_savings']:.2f}€")
          st.write(f"Remaining Budget: {report['remaining_budget']:.2f}€")
          st.write(f"Total Expenses without bills: {report['expenses_without_bills']:.2f}€")

          tab1, tab2, tab3 = st.tabs(["Overview", "Daily Spending", "Category Breakdown"])
          with tab1:
              print_overview(report)
          with tab2:
              print_daily_spending(report)
          with tab3:
              print_category_spending(report)
    else:
        st.write("There was an error processing your data.")
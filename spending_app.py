import streamlit as st
import csv
from datetime import datetime
from collections import defaultdict
import io

def calculate_spending(uploaded_file, monthly_income):
    """
    Calculates spending, income, and savings from a CSV file.

    Args:
        uploaded_file (streamlit.uploaded_file_manager.UploadedFile): The uploaded CSV file object.
        monthly_income (float): The user's monthly income.

    Returns:
        dict: A dictionary containing the calculated statistics.
    """

    total_expenses = 0
    total_income = 0
    expenses_without_bills = 0
    category_expenses = defaultdict(float)

    # List of fixed bills categories
    bills_categories = [
        "Rent", "Electricity", "Heating", "Water",
        "Phone + Internet", "Building Fees", "Taxes", "Energy"
    ]

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
            transaction_date = datetime.strptime(row[1], "%d/%m/%Y") # Convert date string to a datetime object

            # Calculations
            if amount < 0:
                total_expenses += abs(amount)
                category_expenses[category] += abs(amount)
                if category not in bills_categories:
                  expenses_without_bills += abs(amount)

            elif amount > 0:
                total_income += amount
            
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
        "category_expenses": dict(category_expenses)
    }
    return report

def print_report(report):
    """Prints the spending report to the console."""
    st.write("--- Spending Report ---")
    st.write(f"Total Income: {report['total_income']:.2f}€")
    st.write(f"Total Expenses: {report['total_expenses']:.2f}€")
    st.write(f"Total Savings: {report['total_savings']:.2f}€")
    st.write(f"Remaining Budget: {report['remaining_budget']:.2f}€")
    st.write(f"Total Expenses without bills: {report['expenses_without_bills']:.2f}€")
    st.write("\n--- Expenses per Category ---")
    for category, amount in report['category_expenses'].items():
        st.write(f"  {category}: {amount:.2f}€")
    st.write("------------------------")


st.title("Spending Tracker")

uploaded_file = st.file_uploader("Upload your transactions CSV", type=["csv"])
monthly_income = st.number_input("Enter your monthly income", value=1150)


if uploaded_file is not None:
    report = calculate_spending(uploaded_file.file, monthly_income)
    print_report(report)

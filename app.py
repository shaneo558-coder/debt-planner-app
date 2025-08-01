import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Title ---
st.set_page_config(page_title="Debt Payoff Planner", layout="wide")
st.title("💰 Debt Payoff & Budget Planner")

# --- Monthly Income ---
st.header("💵 Monthly Income")
freq = st.selectbox("How are you paid?", ["Monthly", "Biweekly", "Weekly"])
income = st.number_input("Enter your paycheck amount", min_value=0.0, step=10.0, value=0.0)

if freq == "Weekly":
    monthly_income = income * 52 / 12
elif freq == "Biweekly":
    monthly_income = income * 26 / 12
else:
    monthly_income = income

st.success(f"Estimated Monthly Income: ${monthly_income:.2f}")

# --- Monthly Expenses ---
st.header("💿 Monthly Expenses")
expenses = {}

def add_expense(category):
    expenses[category] = st.number_input(f"{category} ($)", min_value=0.0, step=5.0, value=0.0, key=category)

# Basic essentials
add_expense("Rent/Mortgage")
add_expense("Groceries")
add_expense("Phone")
add_expense("Internet")

# Utilities toggle
if st.checkbox("Do you pay for Utilities?"):
    for item in ["Electricity", "Gas", "Water", "Sewer", "Trash Pickup", "Heating Oil"]:
        add_expense(item)

# Transportation toggle
if st.checkbox("Do you have Transportation costs?"):
    for item in ["Car Payment", "Fuel/Gas", "Public Transit", "Rideshare", "Parking"]:
        add_expense(item)

# Insurance toggle
if st.checkbox("Do you pay for Insurance?"):
    for item in ["Health Insurance", "Auto Insurance", "Home/Renters Insurance", "Life Insurance"]:
        add_expense(item)

# Streaming toggle
if st.checkbox("Do you subscribe to any Streaming Services?"):
    for item in ["Netflix", "Hulu", "Disney+", "Amazon Prime Video", "HBO Max"]:
        add_expense(item)

# Calculate total expenses
total_expenses = sum(expenses.values())
st.success(f"Total Monthly Expenses: ${total_expenses:.2f}")

# --- Debts ---
st.header("💳 Debts")
num_debts = st.number_input("How many separate debts would you like to enter?", min_value=1, max_value=50, step=1)
st.caption("We’ll guide you through each one step by step after you enter the total.")

debts = []
for i in range(int(num_debts)):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input(f"Debt {i+1} Name", key=f"name_{i}")
    with col2:
        monthly_payment = st.number_input(f"Monthly Payment for {name}", key=f"payment_{i}", value=0.0)
    with col3:
        total_owed = st.number_input(f"Total Owed on {name}", key=f"owed_{i}", value=0.0)
    debts.append({"Item": name, "Monthly Payment": monthly_payment, "Total Owed": total_owed})

debt_df = pd.DataFrame(debts)
monthly_debt_total = debt_df["Monthly Payment"].sum() if not debt_df.empty else 0.0

# --- Summary Section ---
st.header("📊 Summary")
total_outflow = total_expenses + monthly_debt_total
discretionary_income = monthly_income - total_outflow
dti = (total_outflow / monthly_income) * 100 if monthly_income > 0 else 0

st.markdown(f"""
- ✅ **Monthly Income:** ${monthly_income:,.2f}  
- ✅ **Total Monthly Outflow (Expenses + Debts):** ${total_outflow:,.2f}  
- ✅ **Debt-to-Income Ratio:** {dti:.2f}%  
- ✅ **Discretionary Income:** ${discretionary_income:,.2f}
""")

# --- Avalanche or Snowball Recommendation ---
st.subheader("📌 Payoff Strategy Recommendation")
if not debt_df.empty and len(debt_df) > 1:
    max_total = debt_df["Total Owed"].max()
    if max_total > 2 * debt_df["Total Owed"].mean():
        strategy = "Snowball"
        reason = "You have one or more large debts. Snowball helps build momentum by clearing small balances first."
    else:
        strategy = "Avalanche"
        reason = "Your debts are relatively balanced. Avalanche saves more on interest by targeting high APRs first."

    st.info(f"**Recommended Strategy:** {strategy}")
    st.write(reason)

    with st.expander("ℹ️ Strategy Breakdown"):
        st.markdown("""
        - **Avalanche Method**: Pay off the debt with the **highest interest rate first**, saving the most money in the long run.  
        - **Snowball Method**: Pay off the **smallest balance first**, creating quick wins and motivation to stay on track.
        """)
else:
    st.warning("Enter at least 2 debts to get a payoff strategy recommendation.")

# --- Expense Table ---
st.subheader("📈 Expense Breakdown Table")
if expenses:
    expense_df = pd.DataFrame({
        "Category": expenses.keys(),
        "Amount ($)": expenses.values()
    }).sort_values(by="Amount ($)", ascending=False)

    expense_df["% of Total"] = (expense_df["Amount ($)"] / total_expenses * 100).round(2).astype(str) + '%'
    st.dataframe(expense_df.reset_index(drop=True))
else:
    st.warning("No expenses entered to display.")

# --- Footer ---
st.markdown("---")
st.caption("Built by Shane")

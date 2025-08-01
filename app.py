import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Debt Payoff Planner", layout="wide")
st.title("💰 Debt Payoff & Budget Planner")

# --- Session State ---
if "debts" not in st.session_state:
    st.session_state.debts = []

# --- Reset Function ---
def reset_form():
    st.session_state.debts = []
    st.experimental_rerun()

# --- Income Input ---
st.header("💵 Monthly Income")
income_freq = st.selectbox("How are you paid?", ["Monthly", "Biweekly", "Weekly"])
income_amount = st.number_input("Enter your paycheck amount", min_value=0.0, step=10.0, format="%.2f")

if income_freq == "Weekly":
    monthly_income = income_amount * 52 / 12
elif income_freq == "Biweekly":
    monthly_income = income_amount * 26 / 12
else:
    monthly_income = income_amount

st.success(f"Estimated Monthly Income: ${monthly_income:.2f}")

# --- Expenses ---
st.header("🧾 Monthly Expenses")
expense_categories = [
    "Rent/Mortgage", "Groceries", "Electricity", "Gas", "Water", "Sewer",
    "Trash Pickup", "Heating Oil", "Car Payment", "Fuel/Gas", "Public Transit",
    "Rideshare", "Parking", "Health Insurance", "Auto Insurance",
    "Home/Renters Insurance", "Life Insurance", "Phone", "Internet",
    "Netflix", "Hulu", "Disney+", "Amazon Prime Video", "HBO Max"
]

expenses = {}
cols = st.columns(3)
for idx, category in enumerate(expense_categories):
    with cols[idx % 3]:
        expenses[category] = st.number_input(f"{category}", min_value=0.0, step=5.0, format="%.2f", key=category)

total_expenses = sum(expenses.values())
st.success(f"Total Monthly Expenses: ${total_expenses:.2f}")

# --- Debts ---
st.header("💳 Debts")

def add_debt():
    st.session_state.debts.append({"name": "", "monthly_payment": 0.0, "total_owed": 0.0, "apr": 0.0})

if st.button("➕ Add Another Debt"):
    add_debt()

updated_debts = []
for i, debt in enumerate(st.session_state.debts):
    cols = st.columns(4)
    with cols[0]:
        name = st.text_input(f"Debt {i+1} Name", value=debt["name"], key=f"name_{i}")
    with cols[1]:
        monthly_payment = st.number_input(f"Monthly Payment", value=debt["monthly_payment"], key=f"payment_{i}", format="%.2f")
    with cols[2]:
        total_owed = st.number_input(f"Total Owed", value=debt["total_owed"], key=f"owed_{i}", format="%.2f")
    with cols[3]:
        apr = st.number_input(f"APR (%)", value=debt["apr"], key=f"apr_{i}", format="%.2f")
    
    updated_debts.append({
        "name": name,
        "monthly_payment": monthly_payment,
        "total_owed": total_owed,
        "apr": apr
    })

st.session_state.debts = updated_debts

# --- Calculations ---
st.header("📊 Summary")

debt_df = pd.DataFrame(st.session_state.debts)
if not debt_df.empty and not debt_df["monthly_payment"].isnull().all():
    debt_df = debt_df[debt_df["monthly_payment"] > 0]
    debt_df["Estimated Payoff Date"] = debt_df.apply(
        lambda row: (datetime.today() + timedelta(days=(row["total_owed"] / row["monthly_payment"]) * 30)).strftime('%Y-%m')
        if row["monthly_payment"] > 0 else "N/A", axis=1
    )

    total_debt_payment = debt_df["monthly_payment"].sum()
else:
    total_debt_payment = 0.0

total_outflow = total_debt_payment + total_expenses
discretionary_income = monthly_income - total_outflow
dti = (total_outflow / monthly_income * 100) if monthly_income > 0 else 0

st.markdown(f"""
- ✅ **Monthly Income:** ${monthly_income:,.2f}  
- ✅ **Total Monthly Outflow (Debts + Expenses):** ${total_outflow:,.2f}  
- ✅ **Debt-to-Income Ratio (DTI):** {dti:.2f}%  
- ✅ **Discretionary Income:** ${discretionary_income:,.2f}
""")

if not debt_df.empty:
    st.subheader("📅 Debt Details with Payoff Forecast")
    debt_df_display = debt_df.rename(columns={
        "name": "Debt Name",
        "monthly_payment": "Monthly Payment ($)",
        "total_owed": "Total Owed ($)",
        "apr": "APR (%)"
    })
    st.dataframe(debt_df_display[["Debt Name", "Monthly Payment ($)", "Total Owed ($)", "APR (%)", "Estimated Payoff Date"]])

# --- Reset ---
st.markdown("---")
if st.button("🔁 Reset Form"):
    reset_form()

st.caption("Built with ❤️ using Streamlit")




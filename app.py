import streamlit as st
import pandas as pd
import math
import io
import os
import requests

# --- Helper function for Excel export ---
def export_excel(expenses_df, debts_df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        expenses_df.to_excel(writer, sheet_name='Expenses', index=False)
        debts_df.to_excel(writer, sheet_name='Debts', index=False)
    data = buffer.getvalue()
    st.download_button(
        label="📥 Download Excel Report",
        data=data,
        file_name="BudgetMap_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- Page config ---
st.set_page_config(page_title="Debt Payoff Planner", layout="wide")

# --- Sign-up Form (Sidebar) ---
with st.sidebar.form("signup_form", clear_on_submit=True):
    st.header("🔔 Stay in the Loop")
    name  = st.text_input("Your Name")
    email = st.text_input("Your Email")
    submitted = st.form_submit_button("Sign Up")
    if submitted:
        if not name or not email:
            st.error("Please enter both name and email.")
        else:
            url     = st.secrets["signup_webhook_url"]
            payload = {"name": name, "email": email}
            resp    = requests.post(url, json=payload)
            if resp.ok and resp.json().get("status") == "success":
                st.success("Thanks for signing up! 🎉")
            else:
                st.error("Signup failed — please try again.")

# --- Monthly Income ---
st.header("💵 Monthly Income")
freq = st.selectbox("How are you paid?", ["Monthly", "Biweekly", "Weekly"])
base_income = st.number_input("Enter your paycheck amount ($)", min_value=0.0, step=10.0, value=0.0)
if freq == "Weekly":
    monthly_income = base_income * 52 / 12
elif freq == "Biweekly":
    monthly_income = base_income * 26 / 12
else:
    monthly_income = base_income

# Other income sources
if st.checkbox("➕ Add other income sources?"):
    n_other = st.number_input("How many other income sources?", min_value=1, max_value=10, step=1, key="n_other")
    for i in range(int(n_other)):
        label = st.text_input(f"Label for income #{i+1}", key=f"other_label_{i}")
        amt   = st.number_input(f"Amount for {label} ($)", min_value=0.0, step=5.0, value=0.0, key=f"other_amt_{i}")
        monthly_income += amt

st.success(f"Estimated Monthly Income: ${monthly_income:.2f}")

# --- Monthly Expenses ---
st.header("💿 Monthly Expenses")
expenses = {}
def add_expense(cat):
    expenses[cat] = st.number_input(f"{cat} ($)", min_value=0.0, step=5.0, value=0.0, key=cat)

# Core essentials
add_expense("Rent/Mortgage")
add_expense("Groceries")
add_expense("Phone")
add_expense("Internet")

# Utilities toggle with nested range option
if st.checkbox("Do you pay for Utilities?"):
    use_range = st.checkbox("    🔄 Use min/max range for Utilities?", key="use_range")
    for u in ["Electricity", "Gas", "Water", "Sewer", "Trash Pickup", "Heating Oil"]:
        if use_range:
            lo = st.number_input(f"{u} Min ($)", min_value=0.0, step=5.0, key=f"{u}_min")
            hi = st.number_input(f"{u} Max ($)", min_value=0.0, step=5.0, key=f"{u}_max")
            expenses[u] = (lo + hi) / 2
        else:
            add_expense(u)

# Transportation
if st.checkbox("🚗 Transportation costs?"):
    for t in ["Car Payment","Fuel/Gas","Public Transit","Rideshare","Parking"]:
        add_expense(t)

# Insurance
if st.checkbox("🛡️ Insurance?"):
    for ins in ["Health Insurance","Auto Insurance","Home/Renters Insurance","Life Insurance"]:
        add_expense(ins)

# Streaming
if st.checkbox("🎬 Streaming subscriptions?"):
    for s in ["Netflix","Hulu","Disney+","Amazon Prime Video","HBO Max"]:
        add_expense(s)

# Other expenses
if st.checkbox("➕ Add other expenses?"):
    n_exp = st.number_input("How many extra expense categories?", min_value=1, max_value=10, step=1, key="n_exp")
    for i in range(int(n_exp)):
        label = st.text_input(f"Label for expense #{i+1}", key=f"exp_label_{i}")
        amt   = st.number_input(f"Amount for {label} ($)", min_value=0.0, step=5.0, value=0.0, key=f"exp_amt_{i}")
        expenses[label] = amt

total_expenses = sum(expenses.values())
st.success(f"Total Monthly Expenses: ${total_expenses:.2f}")

# --- Debts ---
st.header("💳 Debts")
num_debts = st.number_input("How many debts?", min_value=1, max_value=50, step=1, key="num_debts")
st.caption("Enter each debt’s name, payment, and balance:")

debts = []
for i in range(int(num_debts)):
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input(f"Name of Debt #{i+1}", key=f"name_{i}")
    with c2:
        pay  = st.number_input(f"Monthly Payment for {name} ($)", min_value=0.0, step=5.0, value=0.0, key=f"pay_{i}")
    with c3:
        owed = st.number_input(f"Total Owed on {name} ($)", min_value=0.0, step=5.0, value=0.0, key=f"owed_{i}")
    months = math.ceil(owed / pay) if pay > 0 else 0
    debts.append({"Item": name, "Monthly Payment": pay, "Total Owed": owed, "Payoff Months": months})

debt_df = pd.DataFrame(debts)
monthly_debt_total = debt_df["Monthly Payment"].sum()

# --- Summary ---
st.header("📊 Summary")
total_outflow = total_expenses + monthly_debt_total
discretionary = monthly_income - total_outflow
dti           = (total_outflow / monthly_income * 100) if monthly_income else 0

st.markdown(f"""
- ✅ **Monthly Income:** ${monthly_income:,.2f}  
- ✅ **Total Monthly Outflow:** ${total_outflow:,.2f}  
- ✅ **Debt-to-Income Ratio:** {dti:.2f}%  
- ✅ **Discretionary Income:** ${discretionary:.2f}
""")

# --- Strategy & Timeline ---
st.subheader("📌 Payoff Strategy & Timeline")
if len(debts) > 1:
    max_bal = debt_df["Total Owed"].max()
    if max_bal > 2 * debt_df["Total Owed"].mean():
        strat, note = "Snowball", "Clears small balances first for quick wins."
    else:
        strat, note = "Avalanche", "Targets high-interest debts to save money."
    st.info(f"**Strategy:** {strat} — {note}")
    st.table(debt_df[["Item","Payoff Months"]])
else:
    st.warning("Enter at least 2 debts for a strategy recommendation.")

# --- Expense Breakdown Table (filtered) ---
st.subheader("📈 Expense Breakdown Table")
expense_df = pd.DataFrame({
    "Category": list(expenses.keys()),
    "Amount ($)": list(expenses.values())
})

# —— NEW: drop any row with Amount ≤ $0.50 —— 
expense_df = expense_df[expense_df["Amount ($)"] > 0.50]

if not expense_df.empty:
    expense_df["% of Expense"] = (expense_df["Amount ($)"] / total_expenses * 100).round(1).astype(str) + "%"
    expense_df["% of Income"]  = (expense_df["Amount ($)"] / monthly_income * 100).round(1).astype(str) + "%"
    st.dataframe(expense_df.sort_values("Amount ($)", ascending=False).reset_index(drop=True))
else:
    st.warning("No expenses above $0.50 to display.")

# --- Export ---
export_excel(expense_df, debt_df)

# --- Footer ---
st.markdown("---")
st.caption("Built by Shane")

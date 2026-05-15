from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from personal_finance_engine import PersonalFinanceProfile, calculate_personal_finance


def money(value: float) -> str:
    return f"${value:,.0f}"


def percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def score_color(score: float) -> str:
    if score >= 70:
        return "#16a34a"
    if score >= 45:
        return "#d97706"
    return "#dc2626"


def pf_metric(label: str, value: str, color: str = "#0f172a") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color};">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_personal_finance() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">Personal Finance</h1>
            <div class="hero-muted">Understand liquidity, debt pressure, savings behavior, goals, and investment risk capacity before making portfolio decisions.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "This module is educational decision support. It does not provide financial, tax, legal, or investment advice."
    )

    st.subheader("Financial Inputs")
    income_col, expense_col, asset_col = st.columns(3)
    with income_col:
        monthly_income = st.number_input("Monthly Income", min_value=0.0, value=8000.0, step=100.0)
        monthly_savings_goal = st.number_input("Monthly Savings Goal", min_value=0.0, value=1200.0, step=50.0)
        investment_risk_score = st.slider("Current Investment Risk Score", 0, 100, 45)

    with expense_col:
        fixed_expenses = st.number_input("Fixed Expenses", min_value=0.0, value=2500.0, step=100.0)
        variable_expenses = st.number_input("Variable Expenses", min_value=0.0, value=1500.0, step=100.0)
        monthly_debt_payment = st.number_input("Monthly Debt Payment", min_value=0.0, value=1600.0, step=100.0)

    with asset_col:
        cash_savings = st.number_input("Cash / Savings", min_value=0.0, value=30000.0, step=500.0)
        taxable_investments = st.number_input("Taxable Investments", min_value=0.0, value=45000.0, step=500.0)
        retirement_accounts = st.number_input("Retirement Accounts", min_value=0.0, value=90000.0, step=500.0)
        real_estate_value = st.number_input("Real Estate Value", min_value=0.0, value=300000.0, step=1000.0)

    debt_col, goal_col = st.columns(2)
    with debt_col:
        st.subheader("Debt")
        credit_card_debt = st.number_input("Credit Card Debt", min_value=0.0, value=0.0, step=100.0)
        student_loan = st.number_input("Student Loan", min_value=0.0, value=12000.0, step=500.0)
        auto_loan = st.number_input("Auto Loan", min_value=0.0, value=8000.0, step=500.0)
        mortgage = st.number_input("Mortgage", min_value=0.0, value=220000.0, step=1000.0)

    with goal_col:
        st.subheader("Goal")
        target_goal_amount = st.number_input("Target Goal Amount", min_value=1.0, value=60000.0, step=1000.0)
        current_goal_savings = st.number_input("Current Goal Savings", min_value=0.0, value=30000.0, step=500.0)

    profile = PersonalFinanceProfile(
        monthly_income=monthly_income,
        fixed_expenses=fixed_expenses,
        variable_expenses=variable_expenses,
        cash_savings=cash_savings,
        taxable_investments=taxable_investments,
        retirement_accounts=retirement_accounts,
        real_estate_value=real_estate_value,
        credit_card_debt=credit_card_debt,
        student_loan=student_loan,
        auto_loan=auto_loan,
        mortgage=mortgage,
        monthly_debt_payment=monthly_debt_payment,
        monthly_savings_goal=monthly_savings_goal,
        target_goal_amount=target_goal_amount,
        current_goal_savings=current_goal_savings,
        investment_risk_score=investment_risk_score,
    )
    result = calculate_personal_finance(profile)
    st.session_state["last_personal_finance_profile"] = profile.__dict__
    st.session_state["last_personal_finance_result"] = result

    st.subheader("Financial Snapshot")
    c1, c2, c3 = st.columns(3)
    with c1:
        pf_metric("Net Worth", money(float(result["net_worth"])))
    with c2:
        pf_metric(
            "Monthly Surplus",
            money(float(result["monthly_surplus"])),
            "#16a34a" if float(result["monthly_surplus"]) >= 0 else "#dc2626",
        )
    with c3:
        pf_metric(
            "Financial Health Score",
            f"{float(result['financial_health_score']):.1f}/100",
            score_color(float(result["financial_health_score"])),
        )

    c4, c5, c6 = st.columns(3)
    with c4:
        pf_metric("Emergency Fund", f"{float(result['emergency_months']):.1f} months")
    with c5:
        pf_metric("Savings Rate", percent(float(result["savings_rate"])))
    with c6:
        pf_metric("Debt-to-Income", percent(float(result["debt_to_income"])))

    st.subheader("Health Score Breakdown")
    scores = pd.DataFrame(
        [
            {"Dimension": "Liquidity", "Score": result["liquidity_score"]},
            {"Dimension": "Debt", "Score": result["debt_score"]},
            {"Dimension": "Savings", "Score": result["savings_score"]},
            {"Dimension": "Goal Progress", "Score": result["goal_score"]},
            {"Dimension": "Risk Capacity", "Score": result["risk_capacity_score"]},
        ]
    )
    chart = (
        alt.Chart(scores)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("Dimension:N", sort=None),
            y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("Dimension:N", legend=None),
            tooltip=["Dimension", alt.Tooltip("Score:Q", format=".1f")],
        )
        .properties(height=330)
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Decision-Support Insights")
    insights = result["insights"]
    if isinstance(insights, list) and insights:
        for insight in insights:
            st.info(insight)
    else:
        st.info("No major warning signals from the current inputs.")

    st.subheader("Investment Readiness")
    st.write(
        "Personal Finance answers whether the user can afford investment risk. "
        "Stock and REIT analysis answer which assets may fit the user's goals and risk capacity."
    )

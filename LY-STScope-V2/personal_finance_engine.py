from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PersonalFinanceProfile:
    monthly_income: float
    fixed_expenses: float
    variable_expenses: float
    cash_savings: float
    taxable_investments: float
    retirement_accounts: float
    real_estate_value: float
    credit_card_debt: float
    student_loan: float
    auto_loan: float
    mortgage: float
    monthly_debt_payment: float
    monthly_savings_goal: float
    target_goal_amount: float
    current_goal_savings: float
    investment_risk_score: float


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, float(value)))


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def calculate_personal_finance(profile: PersonalFinanceProfile) -> dict[str, float | list[str]]:
    total_expenses = profile.fixed_expenses + profile.variable_expenses + profile.monthly_debt_payment
    monthly_surplus = profile.monthly_income - total_expenses
    total_assets = (
        profile.cash_savings
        + profile.taxable_investments
        + profile.retirement_accounts
        + profile.real_estate_value
    )
    total_debt = (
        profile.credit_card_debt
        + profile.student_loan
        + profile.auto_loan
        + profile.mortgage
    )
    net_worth = total_assets - total_debt
    monthly_living_expenses = profile.fixed_expenses + profile.variable_expenses
    emergency_months = safe_divide(profile.cash_savings, monthly_living_expenses)
    savings_rate = safe_divide(max(monthly_surplus, 0), profile.monthly_income)
    debt_to_income = safe_divide(profile.monthly_debt_payment, profile.monthly_income)
    goal_progress = safe_divide(profile.current_goal_savings, profile.target_goal_amount)

    liquidity_score = clamp(emergency_months / 6 * 100)
    debt_score = clamp(100 - debt_to_income / 0.36 * 100)
    savings_score = clamp(savings_rate / 0.20 * 100)
    goal_score = clamp(goal_progress * 100)
    risk_capacity_score = clamp(
        liquidity_score * 0.35
        + debt_score * 0.25
        + savings_score * 0.25
        + max(0, 100 - profile.investment_risk_score) * 0.15
    )
    financial_health_score = clamp(
        liquidity_score * 0.25
        + debt_score * 0.25
        + savings_score * 0.25
        + goal_score * 0.15
        + risk_capacity_score * 0.10
    )

    insights: list[str] = []
    if emergency_months < 3:
        insights.append("Emergency fund is below 3 months of living expenses.")
    elif emergency_months >= 6:
        insights.append("Emergency fund is strong relative to monthly expenses.")

    if debt_to_income > 0.36:
        insights.append("Debt payments are high relative to monthly income.")
    elif debt_to_income < 0.15:
        insights.append("Debt burden appears manageable relative to income.")

    if savings_rate < 0.10:
        insights.append("Savings rate is below the common 10% starting benchmark.")
    elif savings_rate >= 0.20:
        insights.append("Savings rate is strong and supports long-term planning.")

    if risk_capacity_score < 45:
        insights.append("Investment risk capacity appears limited until liquidity or debt improves.")
    elif risk_capacity_score >= 70:
        insights.append("Risk capacity appears stronger based on liquidity, debt, and savings behavior.")

    return {
        "total_assets": total_assets,
        "total_debt": total_debt,
        "net_worth": net_worth,
        "monthly_surplus": monthly_surplus,
        "emergency_months": emergency_months,
        "savings_rate": savings_rate,
        "debt_to_income": debt_to_income,
        "goal_progress": goal_progress,
        "liquidity_score": liquidity_score,
        "debt_score": debt_score,
        "savings_score": savings_score,
        "goal_score": goal_score,
        "risk_capacity_score": risk_capacity_score,
        "financial_health_score": financial_health_score,
        "insights": insights,
    }

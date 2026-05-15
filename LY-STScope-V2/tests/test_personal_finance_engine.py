from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from personal_finance_engine import PersonalFinanceProfile, calculate_personal_finance


def assert_close(actual: float, expected: float, tolerance: float = 0.01) -> None:
    if abs(actual - expected) > tolerance:
        raise AssertionError(f"Expected {expected}, got {actual}")


def run_tests() -> None:
    stable_profile = PersonalFinanceProfile(
        monthly_income=8000,
        fixed_expenses=2500,
        variable_expenses=1500,
        cash_savings=30000,
        taxable_investments=45000,
        retirement_accounts=90000,
        real_estate_value=300000,
        credit_card_debt=0,
        student_loan=12000,
        auto_loan=8000,
        mortgage=220000,
        monthly_debt_payment=1600,
        monthly_savings_goal=1200,
        target_goal_amount=60000,
        current_goal_savings=30000,
        investment_risk_score=45,
    )
    stable = calculate_personal_finance(stable_profile)
    assert_close(stable["net_worth"], 225000)
    assert_close(stable["monthly_surplus"], 2400)
    assert_close(stable["emergency_months"], 7.5)
    assert stable["financial_health_score"] > 70
    assert "Emergency fund is strong relative to monthly expenses." in stable["insights"]

    stressed_profile = PersonalFinanceProfile(
        monthly_income=4200,
        fixed_expenses=2100,
        variable_expenses=1200,
        cash_savings=2500,
        taxable_investments=3000,
        retirement_accounts=8000,
        real_estate_value=0,
        credit_card_debt=9000,
        student_loan=26000,
        auto_loan=12000,
        mortgage=0,
        monthly_debt_payment=1200,
        monthly_savings_goal=200,
        target_goal_amount=15000,
        current_goal_savings=1000,
        investment_risk_score=80,
    )
    stressed = calculate_personal_finance(stressed_profile)
    assert stressed["monthly_surplus"] < 0
    assert stressed["emergency_months"] < 1
    assert stressed["debt_to_income"] > 0.25
    assert stressed["financial_health_score"] < 45
    assert "Emergency fund is below 3 months of living expenses." in stressed["insights"]
    assert "Investment risk capacity appears limited until liquidity or debt improves." in stressed["insights"]


if __name__ == "__main__":
    run_tests()
    print("Personal finance engine tests passed.")

# Personal Finance Structure Test

## Goal

Add a future Personal Finance module to LY-STScope without changing the existing stock or REIT functions yet.

## Core Outputs

- Net Worth
- Monthly Surplus
- Savings Rate
- Debt-to-Income
- Emergency Fund Months
- Goal Progress
- Risk Capacity Score
- Financial Health Score

## Score Model

Financial Health Score combines:

- Liquidity Score
- Debt Score
- Savings Score
- Goal Progress Score
- Risk Capacity Score

## Decision-Support Logic

The module should not tell users exactly what to buy. Instead, it should explain financial readiness:

- Is emergency cash strong enough?
- Is debt too high?
- Is monthly surplus positive?
- Is the user ready to take investment risk?
- Does the user's portfolio risk fit their personal finance condition?

## Test Approach

Two sample users are tested:

- Stable profile: strong emergency fund, positive surplus, manageable debt.
- Stressed profile: weak emergency fund, negative surplus, high debt pressure.

The first version is a calculation engine only. UI integration should happen after the logic is stable.

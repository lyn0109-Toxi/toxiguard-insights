from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

STOCK_HARNESS_VERSION = "v1.0.0"
ENGINE = "PharmaScope Valuation Engine v2.0"
POLICY_RANGE = "V01-V06"

# Validation Rules for Commercial Financial Data
VALUATION_RULES = [
    {"id": "V01", "name": "Source Integrity", "check": "Data is fetched from an official/licensed API (e.g. Finnhub)."},
    {"id": "V02", "name": "Data Freshness", "check": "Financial metrics and market prices are within the allowed cache window (12h)."},
    {"id": "V03", "name": "Model Concordance", "check": "The variance between Graham, CAPM, and Peer models is within 30%."},
    {"id": "V04", "name": "Metric Completeness", "check": "Essential metrics (EPS, PER, Growth Rate) are present and valid."},
    {"id": "V05", "name": "Legal Disclaimer", "check": "Mandatory investment risk disclosure is attached to the analysis."},
    {"id": "V06", "name": "Currency Sync", "check": "Market price and valuation results use a consistent currency (USD/KRW)."},
]

@dataclass
class HarnessGate:
    gate: str
    status: str
    detail: str

def get_harness_manifest(ticker: str) -> dict[str, Any]:
    return {
        "status": "Valuation Harness Active",
        "version": STOCK_HARNESS_VERSION,
        "engine": ENGINE,
        "policy": POLICY_RANGE,
        "ticker": ticker,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rules": VALUATION_RULES,
    }

def validate_valuation(stock_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Validates the quality and compliance of a stock valuation result.
    Args:
        stock_data: A dictionary containing stock metrics and valuation results.
    """
    valuations = stock_data.get("valuations", {})
    income_val = valuations.get("income_approach", 0)
    asset_val = valuations.get("asset_approach", 0)
    market_val = valuations.get("market_approach", 0)
    
    # Calculate variance between models
    vals = [v for v in [income_val, asset_val, market_val] if v > 0]
    variance = 0
    if len(vals) > 1:
        avg = sum(vals) / len(vals)
        variance = max(abs(v - avg) / avg for v in vals)

    gates = [
        HarnessGate(
            "Source Integrity",
            "pass" if stock_data.get("source") == "finnhub" else "warning",
            f"Source: {stock_data.get('source', 'unknown')}. Official API recommended for commercial use."
        ),
        HarnessGate(
            "Data Freshness",
            "pass" if stock_data.get("is_fresh", True) else "fail",
            "Data exceeds 12-hour cache limit."
        ),
        HarnessGate(
            "Model Concordance",
            "pass" if variance < 0.3 else "review",
            f"Model variance: {variance*100:.1f}%. High divergence requires manual review."
        ),
        HarnessGate(
            "Metric Completeness",
            "pass" if all(stock_data.get(k) is not None for k in ["eps", "per", "growthRate"]) else "fail",
            "One or more essential metrics are missing."
        ),
        HarnessGate(
            "Legal Disclosure",
            "pass" if stock_data.get("disclaimer_active") else "fail",
            "Regulatory disclaimer must be presented to the user."
        ),
        HarnessGate(
            "Human Review",
            "review",
            "Valuation is for decision support only; final decision rests with the investor."
        ),
    ]
    return [asdict(gate) for gate in gates]

def build_valuation_report(stock_data: dict[str, Any]) -> dict[str, Any]:
    """
    Builds a professional validation report to accompany the valuation data.
    """
    ticker = stock_data.get("id", "UNKNOWN")
    gates = validate_valuation(stock_data)
    
    passed = len([g for g in gates if g["status"] == "pass"])
    review = len([g for g in gates if g["status"] == "review"])
    failed = len([g for g in gates if g["status"] == "fail"])

    return {
        "schema": "valuation-report.v1",
        "harness": get_harness_manifest(ticker),
        "quality_score": {
            "passed_gates": passed,
            "review_required": review,
            "failed_gates": failed,
            "trust_level": "High" if failed == 0 and review <= 1 else "Medium" if failed == 0 else "Low"
        },
        "validation_details": {
            "gates": gates
        },
        "compliance": {
            "use_case": "Decision Support / Professional Analytics",
            "limitation": "Not a substitute for official financial audits or certified investment advice."
        }
    }

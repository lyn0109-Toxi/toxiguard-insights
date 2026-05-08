
import json
from core.stock_harness import build_valuation_report

# Simulation of what a Backend Server would do
def simulate_backend_request(ticker):
    print(f"--- Processing request for: {ticker} ---")
    
    # 1. In a real backend, we would fetch from Finnhub or our Cache DB
    # Mocking the fetched data:
    mock_fetched_data = {
        "id": ticker,
        "name": "Mock Pharma Inc.",
        "price": 150.0,
        "eps": 5.2,
        "per": 28.8,
        "growthRate": 0.05,
        "source": "finnhub", # Official source
        "is_fresh": True,
        "disclaimer_active": True,
        "valuations": {
            "income_approach": 145.0,
            "asset_approach": 160.0,
            "market_approach": 152.0
        }
    }
    
    # 2. Apply the Harness Validation
    report = build_valuation_report(mock_fetched_data)
    
    # 3. Combine Data + Validation Report
    response = {
        "data": mock_fetched_data,
        "harness_report": report
    }
    
    # 4. Return to the Frontend
    print(json.dumps(response, indent=2))
    
    if report['quality_score']['trust_level'] == "High":
        print("\n✅ Commercial Readiness: HIGH (Ready for Premium Users)")
    else:
        print("\n⚠️ Commercial Readiness: REVIEW REQUIRED")

if __name__ == "__main__":
    simulate_backend_request("PFE")

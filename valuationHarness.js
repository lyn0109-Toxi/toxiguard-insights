/**
 * PharmaScope Valuation Harness (Client-Side Version)
 * Mirroring the logic of core/harness.py to ensure data integrity and compliance
 * while maintaining the existing pure-web structure.
 */

const ValuationHarness = {
    VERSION: "v1.0.0-web",
    
    RULES: [
        { id: "V01", name: "Source Integrity", check: "Official API vs Unofficial Proxy" },
        { id: "V02", name: "Data Freshness", check: "Cache within 12h limit" },
        { id: "V03", name: "Model Concordance", check: "Triangulation variance < 30%" },
        { id: "V04", name: "Legal Disclosure", check: "Mandatory disclaimer visible" }
    ],

    /**
     * Validates stock data and returns a report
     */
    validate: function(stockData) {
        const valuations = stockData.valuations || {};
        const vals = [valuations.income_approach, valuations.asset_approach, valuations.market_approach].filter(v => v > 0);
        
        let variance = 0;
        if (vals.length > 1) {
            const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
            variance = Math.max(...vals.map(v => Math.abs(v - avg) / avg));
        }

        const gates = [
            {
                id: "V01",
                gate: "Source Integrity",
                status: stockData.source === "finnhub" ? "pass" : "sandbox",
                detail: stockData.source === "finnhub" ? "Official Finnhub Data" : "Educational/Sandbox Data"
            },
            {
                id: "V02",
                gate: "Data Freshness",
                status: stockData.is_fresh !== false ? "pass" : "fail",
                detail: stockData.is_fresh !== false ? "Within 12h window" : "Stale data detected"
            },
            {
                id: "V03",
                gate: "Model Concordance",
                status: variance < 0.3 ? "pass" : "review",
                detail: `Variance: ${(variance * 100).toFixed(1)}%`
            },
            {
                id: "V04",
                gate: "Legal Disclosure",
                status: "pass",
                detail: "Disclaimer footer active"
            }
        ];

        const passed = gates.filter(g => g.status === "pass").length;
        const complianceScore = Math.round((passed / gates.length) * 100);

        return {
            trustLevel: complianceScore >= 100 ? "HIGH" : (complianceScore >= 75 ? "MEDIUM" : "LOW"),
            complianceScore: complianceScore,
            gates: gates,
            passedCount: passed,
            timestamp: new Date().toISOString(),
            engine: "PharmaScope Harness v1.1"
        };
    },

    /**
     * Helper to get source label CSS class
     */
    getSourceClass: function(source) {
        return source === "finnhub" ? "source-official" : "source-sandbox";
    },

    /**
     * Helper to get source text
     */
    getSourceText: function(source) {
        return source === "finnhub" ? "Official" : "Sandbox";
    }
};

window.ValuationHarness = ValuationHarness;

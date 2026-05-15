from __future__ import annotations

from dataclasses import dataclass

import altair as alt
import pandas as pd
import streamlit as st


st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 18% 12%, rgba(20, 184, 166, 0.16), transparent 30%),
            radial-gradient(circle at 88% 8%, rgba(245, 158, 11, 0.12), transparent 26%),
            linear-gradient(135deg, #0b1018 0%, #111827 52%, #070a0f 100%);
        color: #f8fafc;
    }
    .block-container {
        padding-top: 1.25rem;
        max-width: 1240px;
    }
    h1, h2, h3, p, li, label {
        letter-spacing: 0;
    }
    h1, h2, h3 {
        color: #f8fafc;
    }
    p, li, label {
        color: #dbe7f3;
    }
    .reit-hero {
        border: 1px solid rgba(148, 163, 184, 0.26);
        border-radius: 24px;
        padding: 34px 34px 30px;
        margin-bottom: 22px;
        background:
            linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(17, 24, 39, 0.88)),
            radial-gradient(circle at 82% 18%, rgba(245, 158, 11, 0.18), transparent 30%);
        box-shadow: 0 22px 60px rgba(0, 0, 0, 0.28);
    }
    .brand-line {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 16px;
    }
    .brand-icon {
        width: 62px;
        height: 62px;
        display: grid;
        place-items: center;
        border-radius: 18px;
        border: 1px solid rgba(125, 211, 252, 0.36);
        background: linear-gradient(145deg, #0f2f43, #172033);
        color: #f8fafc;
        font-size: 1.85rem;
        font-weight: 900;
    }
    .brand-title {
        font-size: clamp(2.4rem, 5vw, 4.8rem);
        line-height: 0.94;
        font-weight: 900;
        color: #f8fafc;
    }
    .brand-title span {
        color: #facc15;
    }
    .hero-muted {
        color: #cbd5e1;
        font-size: 1.08rem;
        max-width: 780px;
    }
    .pill {
        display: inline-block;
        padding: 8px 13px;
        border-radius: 999px;
        border: 1px solid rgba(250, 204, 21, 0.28);
        background: rgba(250, 204, 21, 0.10);
        color: #fde68a;
        font-weight: 800;
        margin-top: 18px;
    }
    .metric-card {
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 18px;
        padding: 22px;
        min-height: 132px;
        background: #f8fafc;
        color: #0f172a;
        box-shadow: 0 16px 40px rgba(2, 6, 23, 0.22);
    }
    .metric-label {
        color: #64748b;
        font-weight: 800;
        margin-bottom: 14px;
    }
    .metric-value {
        color: #0f172a;
        font-size: 2.1rem;
        font-weight: 900;
    }
    .section-panel {
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 20px;
        padding: 22px;
        background: rgba(15, 23, 42, 0.70);
        margin: 16px 0 22px;
    }
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        background: #f8fafc !important;
        color: #0f172a !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@dataclass(frozen=True)
class ReitRecord:
    symbol: str
    company: str
    sector: str
    price: float
    dividend_yield: float
    price_to_ffo: float
    affo_payout: float
    nav_discount: float
    debt_to_ebitda: float
    occupancy: float
    ffo_growth: float
    rent_growth: float
    tenant_quality: float
    lease_duration: float
    beta: float
    rate_sensitivity: float


SAMPLE_REITS: list[ReitRecord] = [
    ReitRecord("PLD", "Prologis", "Industrial", 111.40, 3.55, 19.8, 72.0, -3.2, 5.1, 97.2, 5.8, 4.6, 8.8, 5.2, 1.02, -0.62),
    ReitRecord("O", "Realty Income", "Retail Net Lease", 56.20, 5.65, 13.4, 76.0, -8.5, 5.5, 98.6, 3.2, 2.7, 8.5, 9.1, 0.82, -0.78),
    ReitRecord("EQIX", "Equinix", "Data Center", 792.50, 2.15, 24.6, 64.0, 5.4, 4.2, 96.1, 7.4, 5.5, 9.1, 4.8, 0.94, -0.48),
    ReitRecord("AVB", "AvalonBay Communities", "Residential", 197.80, 3.40, 17.1, 68.0, -2.1, 4.8, 95.8, 4.1, 3.8, 8.0, 1.3, 0.88, -0.56),
    ReitRecord("WELL", "Welltower", "Healthcare", 126.70, 2.10, 27.2, 61.0, 9.0, 5.8, 87.5, 8.2, 5.0, 7.8, 6.4, 1.04, -0.44),
    ReitRecord("PSA", "Public Storage", "Storage", 288.30, 4.15, 18.7, 71.0, 1.8, 3.9, 92.8, 3.7, 3.0, 8.2, 0.8, 0.72, -0.40),
    ReitRecord("SPG", "Simon Property Group", "Retail Mall", 159.60, 5.00, 12.8, 67.0, -6.0, 5.9, 95.5, 2.8, 2.4, 7.2, 6.8, 1.35, -0.69),
    ReitRecord("BXP", "BXP", "Office", 66.40, 5.90, 9.2, 82.0, -18.0, 7.1, 88.6, -1.4, 0.8, 6.2, 5.7, 1.28, -0.84),
]


def reit_frame() -> pd.DataFrame:
    df = pd.DataFrame([record.__dict__ for record in SAMPLE_REITS])
    df["dividend_safety_score"] = df.apply(dividend_safety_score, axis=1)
    df["valuation_score"] = df.apply(reit_valuation_score, axis=1)
    df["debt_rate_risk_score"] = df.apply(debt_rate_risk_score, axis=1)
    df["property_quality_score"] = df.apply(property_quality_score, axis=1)
    df["growth_score"] = df.apply(growth_score, axis=1)
    df["reit_composite_score"] = (
        df["dividend_safety_score"] * 0.25
        + df["valuation_score"] * 0.25
        + df["property_quality_score"] * 0.20
        + df["growth_score"] * 0.15
        + (10 - df["debt_rate_risk_score"]) * 0.15
    )
    return df


def clamp_score(value: float) -> float:
    return max(0.0, min(10.0, float(value)))


def dividend_safety_score(row: pd.Series) -> float:
    payout_component = 10 - max(0, row["affo_payout"] - 60) / 4
    leverage_component = 10 - max(0, row["debt_to_ebitda"] - 4) * 1.4
    occupancy_component = row["occupancy"] / 10
    lease_component = min(10, row["lease_duration"] * 1.2)
    return clamp_score(
        payout_component * 0.35
        + leverage_component * 0.25
        + occupancy_component * 0.25
        + lease_component * 0.15
    )


def reit_valuation_score(row: pd.Series) -> float:
    nav_component = 5 - row["nav_discount"] / 4
    ffo_component = 10 - max(0, row["price_to_ffo"] - 10) / 2
    yield_component = min(10, row["dividend_yield"] * 1.35)
    payout_penalty = max(0, row["affo_payout"] - 80) / 5
    return clamp_score(nav_component * 0.35 + ffo_component * 0.35 + yield_component * 0.30 - payout_penalty)


def debt_rate_risk_score(row: pd.Series) -> float:
    leverage_risk = max(0, row["debt_to_ebitda"] - 3.5) * 1.4
    rate_risk = abs(row["rate_sensitivity"]) * 5
    beta_risk = max(0, row["beta"] - 0.8) * 2
    return clamp_score(leverage_risk * 0.45 + rate_risk * 0.35 + beta_risk * 0.20)


def property_quality_score(row: pd.Series) -> float:
    occupancy_component = row["occupancy"] / 10
    tenant_component = row["tenant_quality"]
    rent_component = min(10, max(0, row["rent_growth"] * 1.6))
    return clamp_score(occupancy_component * 0.40 + tenant_component * 0.35 + rent_component * 0.25)


def growth_score(row: pd.Series) -> float:
    ffo_component = min(10, max(0, row["ffo_growth"] * 1.25))
    rent_component = min(10, max(0, row["rent_growth"] * 1.5))
    quality_component = row["property_quality_score"] if "property_quality_score" in row else property_quality_score(row)
    return clamp_score(ffo_component * 0.45 + rent_component * 0.35 + quality_component * 0.20)


def metric_card(label: str, value: str, color: str = "#0f172a") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color};">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def valuation_label(row: pd.Series) -> str:
    if row["reit_composite_score"] >= 7.2:
        return "High Quality / Attractive"
    if row["reit_composite_score"] >= 5.8:
        return "Balanced"
    if row["debt_rate_risk_score"] >= 6.5:
        return "Needs Caution"
    return "Watchlist"


def score_color(score: float, inverted: bool = False) -> str:
    value = 10 - score if inverted else score
    if value >= 7:
        return "#16a34a"
    if value >= 5:
        return "#d97706"
    return "#dc2626"


def build_sidebar() -> None:
    with st.sidebar:
        st.header("LY-STScope Ver.2")
        st.write("REIT-focused educational analysis")
        st.divider()
        st.caption("Developer")
        st.write("Youngnam Lee")
        st.write("lyn0109@gmail.com")
        st.divider()
        st.text_area("Comments or research notes", placeholder="Write questions, ideas, or professor feedback here.")
        st.caption("This prototype is for education and research discussion only.")


def hero() -> None:
    st.markdown(
        """
        <div class="reit-hero">
            <div class="brand-line">
                <div class="brand-icon">RE</div>
                <div class="brand-title">LY-STScope <span>Ver.2</span></div>
            </div>
            <div class="hero-muted">
                REIT-focused finance education platform for valuation, income analysis,
                interest-rate sensitivity, portfolio risk, and sector specialization.
            </div>
            <div class="pill">Educational REIT Analytics - Not Investment Advice</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def overview_tab(df: pd.DataFrame) -> None:
    st.header("REIT Market Lens")
    st.caption("Start with property type, income quality, leverage, and valuation multiples.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Coverage Universe", f"{len(df)} REITs")
    with c2:
        metric_card("Avg Dividend Yield", f"{df['dividend_yield'].mean():.2f}%", "#16a34a")
    with c3:
        metric_card("Avg Price / FFO", f"{df['price_to_ffo'].mean():.1f}x", "#2563eb")
    with c4:
        metric_card("Avg NAV Discount", f"{df['nav_discount'].mean():+.1f}%", "#d97706")

    st.markdown('<div class="section-panel">', unsafe_allow_html=True)
    st.subheader("Sample REIT Universe")
    table = df.copy()
    table["valuation_view"] = table.apply(valuation_label, axis=1)
    table = table.rename(
        columns={
            "symbol": "Symbol",
            "company": "Company",
            "sector": "REIT Sector",
            "price": "Price",
            "dividend_yield": "Dividend Yield %",
            "price_to_ffo": "Price / FFO",
            "affo_payout": "AFFO Payout %",
            "nav_discount": "NAV Discount %",
            "debt_to_ebitda": "Debt / EBITDA",
            "occupancy": "Occupancy %",
            "ffo_growth": "FFO Growth %",
            "rent_growth": "Rent Growth %",
            "tenant_quality": "Tenant Quality",
            "lease_duration": "Avg Lease Years",
            "beta": "Beta",
            "rate_sensitivity": "Rate Sensitivity",
            "dividend_safety_score": "Dividend Safety",
            "valuation_score": "REIT Valuation",
            "debt_rate_risk_score": "Debt/Rate Risk",
            "property_quality_score": "Property Quality",
            "growth_score": "Growth",
            "reit_composite_score": "Composite Score",
            "valuation_view": "Educational View",
        }
    )
    st.dataframe(table, hide_index=True, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Peer Group Map")
    st.caption("REITs should be compared within similar property sectors whenever possible.")
    peer_chart = (
        alt.Chart(df)
        .mark_circle(size=180, opacity=0.84)
        .encode(
            x=alt.X("price_to_ffo:Q", title="Price / FFO"),
            y=alt.Y("dividend_yield:Q", title="Dividend Yield %"),
            color=alt.Color("sector:N", title="Property Sector"),
            size=alt.Size("reit_composite_score:Q", title="Composite Score"),
            tooltip=[
                "symbol",
                "company",
                "sector",
                alt.Tooltip("dividend_yield:Q", format=".2f"),
                alt.Tooltip("price_to_ffo:Q", format=".1f"),
                alt.Tooltip("reit_composite_score:Q", format=".1f"),
            ],
        )
        .properties(height=390)
    )
    st.altair_chart(peer_chart, use_container_width=True)


def valuation_tab(df: pd.DataFrame) -> None:
    st.header("REIT Valuation Triangulation")
    st.caption("REITs are usually better studied with FFO, AFFO, NAV, dividend quality, and leverage.")

    selected_symbol = st.selectbox(
        "Select REIT",
        options=df["symbol"].tolist(),
        format_func=lambda symbol: f"{symbol} - {df.loc[df['symbol'] == symbol, 'company'].iloc[0]}",
    )
    row = df[df["symbol"] == selected_symbol].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Dividend Yield", f"{row['dividend_yield']:.2f}%", "#16a34a")
    with c2:
        metric_card("Price / FFO", f"{row['price_to_ffo']:.1f}x", "#2563eb")
    with c3:
        metric_card("NAV Discount", f"{row['nav_discount']:+.1f}%", "#d97706")
    with c4:
        metric_card("AFFO Payout", f"{row['affo_payout']:.1f}%", "#7c3aed")

    s1, s2, s3, s4, s5 = st.columns(5)
    with s1:
        metric_card("Dividend Safety", f"{row['dividend_safety_score']:.1f}/10", score_color(row["dividend_safety_score"]))
    with s2:
        metric_card("Valuation Score", f"{row['valuation_score']:.1f}/10", score_color(row["valuation_score"]))
    with s3:
        metric_card("Debt/Rate Risk", f"{row['debt_rate_risk_score']:.1f}/10", score_color(row["debt_rate_risk_score"], inverted=True))
    with s4:
        metric_card("Property Quality", f"{row['property_quality_score']:.1f}/10", score_color(row["property_quality_score"]))
    with s5:
        metric_card("Growth", f"{row['growth_score']:.1f}/10", score_color(row["growth_score"]))

    triangulation = pd.DataFrame(
        [
            {"Approach": "Income", "Model": "Dividend / AFFO sustainability", "Signal": f"{row['dividend_yield']:.2f}% yield, {row['affo_payout']:.1f}% payout"},
            {"Approach": "Asset", "Model": "NAV premium or discount", "Signal": f"{row['nav_discount']:+.1f}% vs estimated NAV"},
            {"Approach": "Market", "Model": "Price / FFO peer multiple", "Signal": f"{row['price_to_ffo']:.1f}x Price / FFO"},
        ]
    )
    st.dataframe(triangulation, hide_index=True, use_container_width=True)

    diagnostics = pd.DataFrame(
        [
            {"Lens": "Income Safety", "What it checks": "Dividend yield, AFFO payout, leverage, occupancy, lease duration", "Reading": f"{row['dividend_safety_score']:.1f}/10"},
            {"Lens": "FFO/AFFO Valuation", "What it checks": "Price/FFO, NAV discount, yield, payout burden", "Reading": f"{row['valuation_score']:.1f}/10"},
            {"Lens": "Debt & Rate Risk", "What it checks": "Debt/EBITDA, beta, interest-rate sensitivity", "Reading": f"{row['debt_rate_risk_score']:.1f}/10 risk"},
            {"Lens": "Property Quality", "What it checks": "Occupancy, tenant quality, rent growth", "Reading": f"{row['property_quality_score']:.1f}/10"},
            {"Lens": "Growth", "What it checks": "FFO growth, rent growth, operating quality", "Reading": f"{row['growth_score']:.1f}/10"},
        ]
    )
    st.subheader("REIT Diagnostic Scorecard")
    st.dataframe(diagnostics, hide_index=True, use_container_width=True)

    radar = pd.DataFrame(
        [
            {"Dimension": "Dividend Safety", "Score": row["dividend_safety_score"]},
            {"Dimension": "Valuation", "Score": row["valuation_score"]},
            {"Dimension": "Balance Sheet", "Score": 10 - row["debt_rate_risk_score"]},
            {"Dimension": "Property Quality", "Score": row["property_quality_score"]},
            {"Dimension": "Growth", "Score": row["growth_score"]},
        ]
    )
    chart = (
        alt.Chart(radar)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("Dimension:N", sort=None),
            y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 10])),
            color=alt.Color("Dimension:N", legend=None),
            tooltip=["Dimension", alt.Tooltip("Score:Q", format=".1f")],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)


def macro_tab(df: pd.DataFrame) -> None:
    st.header("Interest-Rate Sensitivity")
    st.caption("REITs are often sensitive to financing conditions, Treasury yields, and income alternatives.")

    chart = (
        alt.Chart(df)
        .mark_circle(size=180, opacity=0.82)
        .encode(
            x=alt.X("dividend_yield:Q", title="Dividend Yield %"),
            y=alt.Y("rate_sensitivity:Q", title="Rate Sensitivity"),
            color=alt.Color("sector:N", title="Sector"),
            tooltip=["symbol", "company", "sector", "dividend_yield", "rate_sensitivity", "debt_to_ebitda"],
        )
        .properties(height=420)
    )
    st.altair_chart(chart, use_container_width=True)
    st.info(
        "A more negative rate sensitivity means the REIT may be more exposed to rising interest rates. "
        "This is an educational signal, not a forecast."
    )

    st.subheader("Debt and Rate Risk Ranking")
    risk_table = df[
        [
            "symbol",
            "company",
            "sector",
            "debt_to_ebitda",
            "rate_sensitivity",
            "beta",
            "debt_rate_risk_score",
        ]
    ].sort_values("debt_rate_risk_score", ascending=False)
    st.dataframe(risk_table, hide_index=True, use_container_width=True)


def quality_tab(df: pd.DataFrame) -> None:
    st.header("Income Safety & Property Quality")
    st.caption("This view focuses on the information real estate investors usually care about first: income durability, tenant quality, occupancy, and growth.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Avg Safety Score", f"{df['dividend_safety_score'].mean():.1f}/10", score_color(df["dividend_safety_score"].mean()))
    with c2:
        metric_card("Avg Occupancy", f"{df['occupancy'].mean():.1f}%", "#2563eb")
    with c3:
        metric_card("Avg Tenant Quality", f"{df['tenant_quality'].mean():.1f}/10", score_color(df["tenant_quality"].mean()))
    with c4:
        metric_card("Avg FFO Growth", f"{df['ffo_growth'].mean():+.1f}%", "#d97706")

    quality_chart = (
        alt.Chart(df)
        .mark_circle(size=190, opacity=0.82)
        .encode(
            x=alt.X("occupancy:Q", title="Occupancy %", scale=alt.Scale(domain=[84, 100])),
            y=alt.Y("affo_payout:Q", title="AFFO Payout %"),
            color=alt.Color("sector:N", title="Property Sector"),
            size=alt.Size("dividend_safety_score:Q", title="Dividend Safety"),
            tooltip=[
                "symbol",
                "company",
                "sector",
                alt.Tooltip("occupancy:Q", format=".1f"),
                alt.Tooltip("affo_payout:Q", format=".1f"),
                alt.Tooltip("tenant_quality:Q", format=".1f"),
                alt.Tooltip("dividend_safety_score:Q", format=".1f"),
            ],
        )
        .properties(height=390)
    )
    st.altair_chart(quality_chart, use_container_width=True)

    st.subheader("Quality and Growth Table")
    table = df[
        [
            "symbol",
            "company",
            "sector",
            "occupancy",
            "tenant_quality",
            "lease_duration",
            "rent_growth",
            "ffo_growth",
            "dividend_safety_score",
            "property_quality_score",
            "growth_score",
        ]
    ].sort_values("property_quality_score", ascending=False)
    st.dataframe(table, hide_index=True, use_container_width=True)


def portfolio_tab(df: pd.DataFrame) -> None:
    st.header("REIT Portfolio Studio")
    st.caption("Study sector concentration, income exposure, beta, and diversification.")

    selected = st.multiselect(
        "Select REIT holdings",
        options=df["symbol"].tolist(),
        default=["PLD", "O", "EQIX", "AVB"],
        format_func=lambda symbol: f"{symbol} - {df.loc[df['symbol'] == symbol, 'company'].iloc[0]}",
    )
    if not selected:
        st.info("Select at least one REIT to build a portfolio view.")
        return

    mode = st.radio("Weighting Mode", ["Equal-weighted", "Dollar allocation"], horizontal=True)
    selected_df = df[df["symbol"].isin(selected)].copy()

    if mode == "Equal-weighted":
        selected_df["Weight"] = 1 / len(selected_df)
    else:
        allocations: dict[str, float] = {}
        cols = st.columns(min(3, len(selected)))
        for idx, symbol in enumerate(selected):
            allocations[symbol] = cols[idx % len(cols)].number_input(
                f"{symbol} allocation $",
                min_value=0.0,
                value=1000.0,
                step=100.0,
            )
        total_allocation = sum(allocations.values())
        selected_df["Weight"] = selected_df["symbol"].map(
            lambda symbol: allocations[symbol] / total_allocation if total_allocation else 0
        )

    weighted_yield = float((selected_df["dividend_yield"] * selected_df["Weight"]).sum())
    weighted_beta = float((selected_df["beta"] * selected_df["Weight"]).sum())
    weighted_rate_sensitivity = float((selected_df["rate_sensitivity"] * selected_df["Weight"]).sum())
    weighted_safety = float((selected_df["dividend_safety_score"] * selected_df["Weight"]).sum())
    weighted_quality = float((selected_df["property_quality_score"] * selected_df["Weight"]).sum())
    weighted_growth = float((selected_df["growth_score"] * selected_df["Weight"]).sum())

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Weighted Dividend Yield", f"{weighted_yield:.2f}%", "#16a34a")
    with c2:
        metric_card("Weighted Beta", f"{weighted_beta:.2f}", "#2563eb")
    with c3:
        metric_card("Rate Sensitivity", f"{weighted_rate_sensitivity:.2f}", "#d97706")

    q1, q2, q3 = st.columns(3)
    with q1:
        metric_card("Income Safety", f"{weighted_safety:.1f}/10", score_color(weighted_safety))
    with q2:
        metric_card("Property Quality", f"{weighted_quality:.1f}/10", score_color(weighted_quality))
    with q3:
        metric_card("Growth Profile", f"{weighted_growth:.1f}/10", score_color(weighted_growth))

    sector_weights = selected_df.groupby("sector", as_index=False)["Weight"].sum()
    pie = (
        alt.Chart(sector_weights)
        .mark_arc(innerRadius=70, outerRadius=130)
        .encode(
            theta=alt.Theta("Weight:Q"),
            color=alt.Color("sector:N", title="REIT Sector"),
            tooltip=["sector", alt.Tooltip("Weight:Q", format=".1%")],
        )
        .properties(height=360)
    )
    st.altair_chart(pie, use_container_width=True)

    display = selected_df[
        [
            "symbol",
            "company",
            "sector",
            "Weight",
            "dividend_yield",
            "price_to_ffo",
            "nav_discount",
            "dividend_safety_score",
            "property_quality_score",
            "debt_rate_risk_score",
            "beta",
        ]
    ].copy()
    display["Weight"] = display["Weight"].map(lambda value: f"{value * 100:.1f}%")
    st.dataframe(display, hide_index=True, use_container_width=True)


def guide_tab() -> None:
    st.header("Ver.2 Learning Guide")
    st.markdown(
        """
        ### Why REITs need a separate model

        REITs are real estate companies that usually distribute a large portion of taxable income as dividends.
        Because depreciation can make accounting earnings less useful, REIT analysis often focuses on FFO,
        AFFO, dividend sustainability, NAV, leverage, occupancy, and interest-rate sensitivity.

        ### Finance theories connected to this app

        - Income approach: dividend and AFFO-based sustainability
        - Asset approach: NAV premium or discount
        - Market approach: Price / FFO peer comparison
        - CAPM: beta and expected return discussion
        - Portfolio risk: weights, covariance, correlation, and diversification
        - Capital structure: debt burden, financing cost, and interest-rate exposure

        ### Future build path

        1. Add live data integration.
        2. Build REIT peer groups by property type.
        3. Add historical price and yield charts.
        4. Add simple equal-weight REIT backtesting.
        5. Add REIT-specific ontology for property type, tenant base, and macro sensitivity.

        ### Customer-focused analysis lenses

        - Income Safety: dividend yield, AFFO payout, occupancy, lease duration, and leverage.
        - FFO/AFFO Valuation: Price/FFO, NAV discount or premium, yield, and payout pressure.
        - Debt & Rate Risk: Debt/EBITDA, beta, and interest-rate sensitivity.
        - Property Quality: occupancy, tenant quality, and rent growth.
        - Growth Profile: FFO growth, rent growth, and operating quality.

        These scores are currently educational sample signals. A professional version should connect
        them to current filings, REIT supplemental reports, Nareit-style sector data, and reliable market feeds.
        """
    )


def main(include_sidebar: bool = True) -> None:
    if include_sidebar:
        build_sidebar()
    hero()
    df = reit_frame()
    tabs = st.tabs(["Overview", "Valuation", "Quality", "Macro Sensitivity", "Portfolio", "Guide"])
    with tabs[0]:
        overview_tab(df)
    with tabs[1]:
        valuation_tab(df)
    with tabs[2]:
        quality_tab(df)
    with tabs[3]:
        macro_tab(df)
    with tabs[4]:
        portfolio_tab(df)
    with tabs[5]:
        guide_tab()

    st.divider()
    st.caption(
        "LY-STScope Ver.2 is an educational prototype. It does not provide investment, legal, tax, or financial advice."
    )


if __name__ == "__main__":
    main()

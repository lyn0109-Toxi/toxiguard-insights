import math
import os
import json
from html import escape
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote

import altair as alt
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf


st.set_page_config(page_title="LY-STScope", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background:
            linear-gradient(90deg, rgba(34,211,238,0.035) 1px, transparent 1px),
            linear-gradient(0deg, rgba(20,184,166,0.030) 1px, transparent 1px),
            radial-gradient(circle at 18% 14%, rgba(14,165,233,0.18), transparent 30%),
            radial-gradient(circle at 86% 8%, rgba(20,184,166,0.13), transparent 24%),
            radial-gradient(circle at 52% 0%, rgba(59,130,246,0.10), transparent 34%),
            linear-gradient(135deg, #111827 0%, #172335 48%, #080c12 100%);
        background-size: 42px 42px, 42px 42px, auto, auto, auto;
        color: #f8fafc;
    }
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        opacity: 0.45;
        background:
            linear-gradient(115deg, transparent 0%, transparent 40%, rgba(37,99,235,0.16) 41%, rgba(37,99,235,0.04) 46%, transparent 52%),
            linear-gradient(65deg, transparent 0%, transparent 58%, rgba(20,184,166,0.15) 59%, rgba(20,184,166,0.03) 64%, transparent 70%);
        animation: dataSweep 14s linear infinite;
    }
    .stApp::after {
        content: "";
        position: fixed;
        right: 28px;
        top: 92px;
        width: 320px;
        height: 180px;
        pointer-events: none;
        z-index: 0;
        opacity: 0.22;
        background:
            linear-gradient(135deg, transparent 0 10%, rgba(37,99,235,0.32) 10% 11%, transparent 11% 25%, rgba(16,185,129,0.30) 25% 26%, transparent 26% 42%, rgba(245,158,11,0.34) 42% 43%, transparent 43% 100%);
        clip-path: polygon(0 80%, 10% 67%, 20% 72%, 30% 48%, 40% 57%, 52% 32%, 65% 40%, 78% 18%, 100% 28%, 100% 100%, 0 100%);
        animation: graphFloat 8s ease-in-out infinite;
    }
    @keyframes dataSweep {
        0% { transform: translateX(-18%) translateY(0); }
        100% { transform: translateX(18%) translateY(0); }
    }
    @keyframes graphFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(12px); }
    }
    h1, h2, h3 {
        color: #f8fafc;
        letter-spacing: 0;
    }
    p, li, label {
        color: #dbe7f3;
    }
    .block-container {
        padding-top: 1.25rem;
        max-width: 1280px;
        position: relative;
        z-index: 1;
    }
    div[data-testid="stHeadingWithActionElements"] h1 {
        font-size: 2.35rem;
        font-weight: 900;
        color: #f8fafc;
        margin-bottom: 0.25rem;
    }
    .brand-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 18px;
        padding: 42px 30px 34px;
        margin: 0 0 20px;
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 28px;
        background:
            radial-gradient(circle at 54% 28%, rgba(20, 184, 166, 0.30), transparent 28%),
            radial-gradient(circle at 48% 20%, rgba(14, 165, 233, 0.22), transparent 34%),
            linear-gradient(135deg, #111827 0%, #172335 48%, #080c12 100%);
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.28);
        backdrop-filter: blur(8px);
        position: relative;
        overflow: hidden;
    }
    .brand-header::after {
        content: "";
        position: absolute;
        left: 7%;
        right: 7%;
        bottom: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #22d3ee, transparent);
        opacity: 0.95;
    }
    .brand-mark {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
        position: relative;
        z-index: 1;
    }
    .brand-icon {
        width: 76px;
        height: 76px;
        border-radius: 20px;
        display: grid;
        place-items: center;
        background:
            linear-gradient(135deg, rgba(255,255,255,0.18), transparent 32%),
            linear-gradient(135deg, rgba(34, 211, 238, 0.22), rgba(20, 184, 166, 0.18)),
            rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(34, 211, 238, 0.42);
        box-shadow: 0 0 30px rgba(34, 211, 238, 0.28), inset 0 0 24px rgba(34, 211, 238, 0.10);
        position: relative;
    }
    .brand-icon::after {
        content: "";
        width: 46px;
        height: 42px;
        background:
            linear-gradient(to top, #22d3ee 0 76%, transparent 76%),
            linear-gradient(to top, #10b981 0 52%, transparent 52%),
            linear-gradient(to top, #60a5fa 0 92%, transparent 92%),
            linear-gradient(to top, #f59e0b 0 63%, transparent 63%);
        background-size: 8px 100%;
        background-position: 2px 0, 14px 0, 26px 0, 38px 0;
        background-repeat: no-repeat;
        border-bottom: 2px solid rgba(226, 232, 240, 0.8);
    }
    .brand-icon::before {
        content: "";
        position: absolute;
        inset: 13px;
        border-radius: 12px;
        border: 1px solid rgba(226, 232, 240, 0.22);
    }
    .brand-name {
        color: #f8fafc;
        font-size: clamp(3.4rem, 7vw, 6.2rem);
        font-weight: 950;
        line-height: 0.92;
        letter-spacing: 0;
        text-shadow: 0 16px 42px rgba(34, 211, 238, 0.26);
    }
    .brand-name .scope-accent {
        color: #19dce8;
        text-shadow: 0 0 34px rgba(34, 211, 238, 0.58);
    }
    .brand-subtitle {
        color: #a9b7c9;
        font-size: 1.05rem;
        font-weight: 850;
        margin-top: 20px;
        letter-spacing: 0.46em;
        text-align: center;
    }
    .brand-badge {
        color: #ccfbf1;
        background: rgba(15, 118, 110, 0.28);
        border: 1px solid rgba(45, 212, 191, 0.38);
        border-radius: 999px;
        padding: 8px 13px;
        font-size: 0.88rem;
        font-weight: 850;
        white-space: nowrap;
        position: relative;
        z-index: 1;
    }
    .terminal-showcase {
        position: relative;
        overflow: hidden;
        padding: 34px;
        margin: 0 0 24px;
        border-radius: 30px;
        border: 1px solid rgba(125, 211, 252, 0.24);
        background:
            radial-gradient(circle at 12% 72%, rgba(34, 211, 238, 0.34), transparent 18%),
            radial-gradient(circle at 86% 62%, rgba(59, 130, 246, 0.32), transparent 20%),
            radial-gradient(circle at 50% 10%, rgba(20, 184, 166, 0.16), transparent 34%),
            linear-gradient(145deg, #101722 0%, #0b1320 48%, #101827 100%);
        box-shadow: 0 28px 70px rgba(15, 23, 42, 0.28);
    }
    .terminal-showcase::before {
        content: "";
        position: absolute;
        inset: auto -8% 4% -8%;
        height: 170px;
        opacity: 0.55;
        background:
            radial-gradient(ellipse at center, rgba(34, 211, 238, 0.48), transparent 58%),
            repeating-radial-gradient(circle at 50% 80%, rgba(125, 211, 252, 0.22) 0 1px, transparent 1px 9px);
        clip-path: polygon(0 64%, 12% 56%, 24% 68%, 38% 42%, 52% 50%, 68% 26%, 84% 44%, 100% 20%, 100% 100%, 0 100%);
        animation: graphFloat 8s ease-in-out infinite;
    }
    .terminal-shell {
        position: relative;
        z-index: 1;
        max-width: 1080px;
        margin: 0 auto;
        border-radius: 26px;
        border: 1px solid rgba(148, 163, 184, 0.36);
        background: rgba(8, 15, 27, 0.88);
        box-shadow:
            0 0 0 5px rgba(148, 163, 184, 0.10),
            0 26px 60px rgba(2, 6, 23, 0.54),
            inset 0 0 44px rgba(14, 165, 233, 0.12);
        overflow: hidden;
    }
    .terminal-topbar {
        display: grid;
        grid-template-columns: 58px minmax(150px, 220px) 1fr auto;
        gap: 16px;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.18);
        background: rgba(15, 23, 42, 0.72);
    }
    .terminal-mini-logo {
        width: 38px;
        height: 38px;
        border-radius: 12px;
        display: grid;
        place-items: center;
        color: #e0f2fe;
        font-weight: 950;
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.18), rgba(16, 185, 129, 0.12));
        border: 1px solid rgba(34, 211, 238, 0.30);
        box-shadow: 0 0 18px rgba(34, 211, 238, 0.20);
    }
    .terminal-search {
        height: 42px;
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        background: rgba(30, 41, 59, 0.78);
        color: #dbeafe;
        display: flex;
        align-items: center;
        gap: 9px;
        padding: 0 13px;
        font-weight: 800;
    }
    .terminal-search span:first-child {
        color: #93c5fd;
        font-size: 1.15rem;
    }
    .terminal-nav {
        display: flex;
        gap: 24px;
        color: #94a3b8;
        font-size: 0.94rem;
        font-weight: 800;
        white-space: nowrap;
    }
    .terminal-nav .active {
        color: #f8fafc;
        position: relative;
    }
    .terminal-nav .active::after {
        content: "";
        position: absolute;
        left: -4px;
        right: -4px;
        bottom: -18px;
        height: 3px;
        border-radius: 999px;
        background: #22d3ee;
        box-shadow: 0 0 18px rgba(34, 211, 238, 0.72);
    }
    .terminal-user {
        color: #cbd5e1;
        font-size: 0.84rem;
        font-weight: 800;
        text-align: right;
        white-space: nowrap;
    }
    .terminal-user b {
        color: #34d399;
    }
    .terminal-body {
        display: grid;
        grid-template-columns: minmax(0, 1.7fr) minmax(280px, 0.9fr);
        gap: 16px;
        padding: 18px 20px 20px;
    }
    .terminal-chart-card,
    .terminal-side-card {
        border-radius: 18px;
        border: 1px solid rgba(125, 211, 252, 0.22);
        background:
            radial-gradient(circle at 50% 30%, rgba(34, 211, 238, 0.12), transparent 34%),
            rgba(15, 23, 42, 0.74);
        box-shadow: inset 0 0 34px rgba(14, 165, 233, 0.08);
    }
    .terminal-chart-card {
        min-height: 470px;
        padding: 18px;
    }
    .terminal-stock-head {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 16px;
        margin-bottom: 14px;
    }
    .terminal-symbol {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 950;
        line-height: 1;
    }
    .terminal-company {
        color: #94a3b8;
        font-weight: 750;
        margin-top: 4px;
    }
    .terminal-price {
        color: #f8fafc;
        font-size: 1.7rem;
        font-weight: 950;
        text-align: right;
    }
    .terminal-price span {
        color: #6ee7b7;
        font-size: 1.35rem;
    }
    .terminal-chart-grid {
        position: relative;
        height: 300px;
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 12px;
        background:
            repeating-linear-gradient(to bottom, transparent 0 58px, rgba(148, 163, 184, 0.15) 59px 60px),
            linear-gradient(180deg, rgba(8, 47, 73, 0.40), rgba(8, 13, 26, 0.22));
        overflow: hidden;
    }
    .ma-line {
        position: absolute;
        left: 5%;
        right: 5%;
        height: 3px;
        border-radius: 999px;
        transform: rotate(-11deg);
        opacity: 0.95;
    }
    .ma-green {
        top: 62%;
        background: linear-gradient(90deg, #86efac, #22c55e);
    }
    .ma-blue {
        top: 78%;
        background: linear-gradient(90deg, #38bdf8, #2563eb);
    }
    .candle-row {
        position: absolute;
        left: 5%;
        right: 5%;
        bottom: 32px;
        height: 230px;
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 7px;
    }
    .candle {
        width: 13px;
        border-radius: 3px 3px 1px 1px;
        position: relative;
        box-shadow: 0 0 10px currentColor;
    }
    .candle::before {
        content: "";
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        bottom: -18px;
        width: 2px;
        height: calc(100% + 36px);
        background: currentColor;
        opacity: 0.48;
    }
    .up { color: #7cff5f; background: #7cff5f; }
    .down { color: #ff674d; background: #ff674d; }
    .volume-row {
        height: 86px;
        margin-top: 14px;
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 12px;
        display: flex;
        align-items: flex-end;
        gap: 8px;
        padding: 10px;
        background: rgba(8, 13, 26, 0.35);
    }
    .vol {
        flex: 1;
        min-width: 5px;
        border-radius: 2px 2px 0 0;
        opacity: 0.62;
    }
    .terminal-side {
        display: grid;
        gap: 16px;
    }
    .terminal-side-card {
        padding: 18px;
    }
    .side-title {
        color: #e2e8f0;
        font-size: 0.98rem;
        font-weight: 950;
        margin-bottom: 18px;
    }
    .metric-grid-dark {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }
    .dark-label {
        color: #cbd5e1;
        font-size: 0.92rem;
        font-weight: 800;
    }
    .dark-value {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 950;
        line-height: 1.05;
        margin-top: 7px;
    }
    .dark-value.green { color: #72ef69; }
    .dark-value.red,
    .terminal-price span.red {
        color: #fb7185;
    }
    .terminal-price span.green {
        color: #6ee7b7;
    }
    .dark-value.orange { color: #fbbf24; font-size: 1.55rem; }
    .radar-wrap {
        width: 210px;
        height: 210px;
        margin: 4px auto 14px;
        border-radius: 50%;
        position: relative;
        background:
            radial-gradient(circle, rgba(125, 211, 252, 0.10) 0 18%, transparent 18% 32%, rgba(125, 211, 252, 0.08) 32% 34%, transparent 34% 49%, rgba(125, 211, 252, 0.08) 49% 51%, transparent 51%),
            conic-gradient(from 25deg, rgba(34, 211, 238, 0.20), rgba(163, 230, 53, 0.24), rgba(251, 191, 36, 0.24), rgba(34, 211, 238, 0.20));
        border: 1px solid rgba(125, 211, 252, 0.22);
    }
    .radar-triangle {
        position: absolute;
        inset: 34px 42px 34px;
        background: linear-gradient(135deg, rgba(163, 230, 53, 0.42), rgba(251, 191, 36, 0.28));
        clip-path: polygon(50% 0, 98% 82%, 0 88%);
        border: 1px solid rgba(255, 255, 255, 0.34);
        filter: drop-shadow(0 0 18px rgba(163, 230, 53, 0.40));
    }
    .radar-scores {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        color: #cbd5e1;
        font-size: 0.82rem;
        font-weight: 800;
    }
    .radar-scores b {
        display: block;
        color: #86efac;
        font-size: 1.35rem;
    }
    .result-terminal {
        margin: 18px 0 26px;
    }
    .terminal-status-strip {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
        padding: 14px 20px 18px;
        border-top: 1px solid rgba(148, 163, 184, 0.18);
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 800;
        background: rgba(15, 23, 42, 0.52);
    }
    .terminal-status-strip b {
        color: #f8fafc;
    }
    .valuation-radar-card {
        display: grid;
        grid-template-columns: minmax(260px, 0.9fr) minmax(280px, 1.1fr);
        gap: 24px;
        align-items: center;
        border: 1px solid #b8c7da;
        border-radius: 18px;
        background:
            radial-gradient(circle at 26% 24%, rgba(34, 211, 238, 0.13), transparent 28%),
            linear-gradient(135deg, #ffffff 0%, #f6fbff 100%);
        box-shadow: 0 16px 34px rgba(30, 64, 105, 0.12);
        padding: 22px;
        margin: 14px 0 22px;
    }
    .valuation-radar-title {
        color: #0f172a;
        font-size: 1.25rem;
        font-weight: 950;
        margin-bottom: 7px;
    }
    .valuation-radar-copy {
        color: #334155;
        font-size: 0.96rem;
        font-weight: 700;
        line-height: 1.55;
        margin-bottom: 14px;
    }
    .valuation-radar-legend {
        display: grid;
        gap: 10px;
    }
    .valuation-radar-legend div {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        border-top: 1px solid #d8e2ef;
        padding-top: 10px;
        color: #334155;
        font-weight: 800;
    }
    .valuation-radar-legend b {
        color: #0f172a;
        font-size: 1.05rem;
    }
    .valuation-radar-svg {
        width: 100%;
        max-width: 380px;
        margin: 0 auto;
        display: block;
        filter: drop-shadow(0 16px 22px rgba(14, 116, 144, 0.14));
    }
    @media (max-width: 900px) {
        .terminal-showcase {
            padding: 18px;
        }
        .terminal-topbar {
            grid-template-columns: 44px 1fr;
        }
        .terminal-nav,
        .terminal-user {
            display: none;
        }
        .terminal-body {
            grid-template-columns: 1fr;
        }
        .brand-mark {
            flex-direction: column;
            text-align: center;
        }
        .brand-subtitle {
            letter-spacing: 0.18em;
            line-height: 1.5;
        }
        .valuation-radar-card {
            grid-template-columns: 1fr;
        }
    }
    div[data-testid="stTabs"] div[role="tablist"] {
        gap: 8px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.28);
        padding: 4px 0 12px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.32);
        border-radius: 12px;
        color: #dbe7f3;
        font-size: 16px;
        font-weight: 800;
        padding: 10px 17px;
        min-height: 46px;
    }
    div[data-testid="stTabs"] button[role="tab"]:hover {
        border-color: #22d3ee;
        color: #f8fafc;
        background: rgba(14, 116, 144, 0.34);
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #0ea5e9, #0f766e);
        border-color: #22d3ee;
        color: #ffffff;
        box-shadow: 0 8px 22px rgba(34,211,238,0.24);
    }
    div[data-testid="stTabs"] button[role="tab"] p {
        font-size: 16px;
        font-weight: 800;
        color: inherit;
        line-height: 1.2;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 23, 42, 0.48);
        border: 1px solid rgba(148, 163, 184, 0.30);
        border-radius: 18px;
        padding: 8px;
        box-shadow: 0 16px 34px rgba(2, 6, 23, 0.24);
    }
    div[data-testid="stForm"] {
        max-width: 620px;
        border: 1px solid rgba(34, 211, 238, 0.34);
        border-radius: 16px;
        padding: 16px 18px 18px;
        background:
            linear-gradient(135deg, rgba(15, 23, 42, 0.88), rgba(17, 34, 52, 0.82));
        box-shadow: 0 14px 34px rgba(2, 6, 23, 0.24);
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button {
        border-color: #3b82f6;
        background: #f8fbff;
        color: #1e3a5f;
        min-height: 42px;
        font-weight: 700;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button:hover {
        border-color: #2563eb;
        color: #0f1f33;
        background: #edf5ff;
    }
    div[data-testid="stTextInput"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stRadio"] label {
        color: #e2e8f0;
        font-size: 15px;
        font-weight: 850;
    }
    div[data-testid="stTextInput"] {
        max-width: 540px;
    }
    div[data-baseweb="input"] {
        background: #ffffff !important;
        border: 2px solid #22d3ee;
        border-radius: 12px;
        box-shadow: 0 0 0 3px rgba(34,211,238,0.10), 0 10px 22px rgba(2,6,23,0.18);
        min-height: 42px;
    }
    div[data-baseweb="input"] > div {
        background: #ffffff !important;
        color: #0f172a !important;
    }
    div[data-baseweb="input"] input {
        background: #ffffff !important;
        color: #0f172a !important;
        caret-color: #0f766e !important;
        font-size: 15px;
        font-weight: 750;
    }
    div[data-baseweb="input"] input::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #34d399;
        box-shadow: 0 0 0 4px rgba(52,211,153,0.22), 0 10px 24px rgba(15,118,110,0.18);
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #f8fafc;
        border: 2px solid #60a5fa;
        border-radius: 10px;
        color: #0f172a;
        min-height: 44px;
    }
    div[data-testid="stButton"] button,
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stFormSubmitButton"] button {
        border-radius: 10px;
        min-height: 40px;
        font-size: 14px;
        font-weight: 800;
    }
    .hero-panel {
        border: 1px solid rgba(125, 211, 252, 0.28);
        border-radius: 20px;
        background:
            radial-gradient(circle at 20% 18%, rgba(34, 211, 238, 0.18), transparent 30%),
            linear-gradient(135deg, rgba(15, 23, 42, 0.86), rgba(17, 34, 52, 0.78));
        padding: 22px 24px;
        margin: 12px 0 22px;
        box-shadow: 0 18px 38px rgba(2, 6, 23, 0.22);
    }
    .hero-panel h1,
    .hero-panel h2,
    .hero-panel h3 {
        color: #f8fafc;
    }
    .hero-panel h1 {
        font-size: 2.1rem;
        line-height: 1.15;
    }
    .detail-hero-title {
        margin: 0 0 6px;
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 950;
        line-height: 1.12;
    }
    .detail-hero-meta {
        color: #cbd5e1;
        font-size: 1rem;
        font-weight: 800;
    }
    .hero-muted {
        color: #cbd5e1;
        font-size: 17px;
        font-weight: 700;
    }
    .metric-card {
        border: 1px solid #cbd7e6;
        border-radius: 14px;
        background: #ffffff;
        padding: 18px 20px;
        min-height: 112px;
        box-shadow: 0 8px 22px rgba(39, 62, 92, 0.07);
    }
    .metric-card .label {
        color: #52657f;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .metric-card .value {
        color: #102033;
        font-size: 27px;
        font-weight: 800;
    }
    .guide-shot {
        border: 1px solid #334155;
        border-radius: 14px;
        overflow: hidden;
        margin: 12px 0 20px;
    }
    .stock-card-link {
        display: block;
        text-decoration: none !important;
        color: inherit !important;
    }
    .stock-card-panel {
        border: 1px solid #d8e2ef;
        border-radius: 16px;
        background:
            radial-gradient(circle at 18% 12%, rgba(34, 211, 238, 0.08), transparent 28%),
            linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        padding: 16px;
        min-height: 292px;
        box-shadow: 0 16px 30px rgba(2, 6, 23, 0.18);
        transition: transform 140ms ease, box-shadow 140ms ease, border-color 140ms ease;
    }
    .stock-card-panel:hover {
        transform: translateY(-2px);
        border-color: #0891b2;
        box-shadow: 0 18px 38px rgba(8, 145, 178, 0.18);
    }
    .stock-card-head {
        display: grid;
        grid-template-columns: 52px minmax(0, 1fr);
        gap: 12px;
        align-items: start;
        padding-bottom: 14px;
        border-bottom: 1px solid #d8e2ef;
    }
    .company-logo {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        display: grid;
        place-items: center;
        color: #ffffff;
        font-size: 17px;
        font-weight: 950;
        background:
            radial-gradient(circle at 30% 25%, rgba(255,255,255,0.35), transparent 32%),
            linear-gradient(135deg, #0f172a, #0891b2);
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.22);
    }
    .company-title {
        color: #0f172a !important;
        font-size: 1.18rem;
        font-weight: 900;
        line-height: 1.18;
        margin: 0;
        min-height: 2.8em;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .company-meta {
        color: #475569;
        font-size: 0.82rem;
        font-weight: 750;
        margin-top: 4px;
    }
    .ticker-pill {
        display: inline-flex;
        align-items: center;
        color: #f8fafc;
        background: #111827;
        border-radius: 999px;
        padding: 3px 9px;
        margin-right: 7px;
        font-size: 0.76rem;
        font-weight: 900;
        letter-spacing: 0.04em;
    }
    .stock-card-price {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        gap: 12px;
        margin: 16px 0 14px;
        padding-bottom: 14px;
        border-bottom: 1px solid #d8e2ef;
    }
    .stock-card-price .price {
        color: #0f172a;
        font-size: 2rem;
        font-weight: 950;
        line-height: 1;
    }
    .status-chip {
        color: white;
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 0.75rem;
        font-weight: 850;
        white-space: nowrap;
    }
    .stock-card-stats {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        color: #334155;
        font-size: 0.8rem;
        margin-bottom: 12px;
    }
    .stock-card-stats b {
        display: block;
        color: #0f172a;
        font-size: 1rem;
        margin-top: 3px;
    }
    .stock-card-actions {
        display: none;
    }
    .stock-action-chip {
        flex: 1;
        border-radius: 10px;
        padding: 8px;
        text-align: center;
        font-size: 0.78rem;
        font-weight: 850;
    }
    .stock-card-link:hover .company-title {
        color: #0e7490 !important;
    }
    .click-hint {
        color: #64748b;
        font-size: 12px;
        margin-top: 8px;
    }
    .life-entry-wrap {
        min-height: 86vh;
        display: grid;
        align-items: center;
        padding: 36px 0 54px;
    }
    .life-entry {
        position: relative;
        overflow: hidden;
        border-radius: 34px;
        border: 1px solid rgba(148, 163, 184, 0.28);
        background:
            radial-gradient(circle at 66% 18%, rgba(34, 211, 238, 0.22), transparent 26%),
            radial-gradient(circle at 24% 24%, rgba(16, 185, 129, 0.16), transparent 28%),
            linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(17, 24, 39, 0.94) 48%, rgba(4, 9, 15, 0.98));
        box-shadow: 0 32px 90px rgba(0, 0, 0, 0.34);
        padding: clamp(34px, 5vw, 70px);
    }
    .life-entry::before {
        content: "";
        position: absolute;
        inset: 0;
        opacity: 0.30;
        background:
            linear-gradient(90deg, rgba(34,211,238,0.12) 1px, transparent 1px),
            linear-gradient(0deg, rgba(16,185,129,0.09) 1px, transparent 1px);
        background-size: 48px 48px;
        animation: dataSweep 18s linear infinite;
    }
    .life-entry-grid {
        position: relative;
        z-index: 1;
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(340px, 0.86fr);
        gap: clamp(28px, 4vw, 64px);
        align-items: center;
    }
    .life-kicker {
        color: #67e8f9;
        font-size: 0.9rem;
        font-weight: 900;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-bottom: 14px;
    }
    .life-title {
        color: #f8fafc;
        font-size: clamp(3rem, 6vw, 6.6rem);
        line-height: 0.92;
        letter-spacing: 0;
        font-weight: 950;
        margin: 0;
    }
    .life-title span {
        color: #67e8f9;
        text-shadow: 0 0 32px rgba(34, 211, 238, 0.36);
    }
    .life-copy {
        max-width: 760px;
        margin: 24px 0 26px;
        color: #dbe7f3;
        font-size: clamp(1.05rem, 1.8vw, 1.32rem);
        line-height: 1.65;
        font-weight: 700;
    }
    .life-pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
    }
    .life-pill {
        border: 1px solid rgba(103, 232, 249, 0.30);
        background: rgba(15, 23, 42, 0.70);
        color: #e0f2fe;
        border-radius: 999px;
        padding: 8px 13px;
        font-size: 0.86rem;
        font-weight: 850;
    }
    .life-map {
        min-height: 520px;
        border-radius: 30px;
        border: 1px solid rgba(148, 163, 184, 0.26);
        background:
            radial-gradient(circle at 50% 44%, rgba(34, 211, 238, 0.20), transparent 32%),
            linear-gradient(160deg, rgba(15, 23, 42, 0.74), rgba(8, 13, 22, 0.94));
        box-shadow: inset 0 0 46px rgba(34, 211, 238, 0.08);
        position: relative;
        overflow: hidden;
    }
    .life-orbit {
        position: absolute;
        inset: 64px;
        border: 1px solid rgba(148, 163, 184, 0.20);
        border-radius: 50%;
        animation: graphFloat 9s ease-in-out infinite;
    }
    .life-orbit.two {
        inset: 112px;
        animation-delay: -2s;
    }
    .life-core {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        width: 162px;
        height: 162px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        text-align: center;
        color: #f8fafc;
        font-size: 1.05rem;
        font-weight: 950;
        background:
            radial-gradient(circle at 35% 26%, rgba(255,255,255,0.34), transparent 22%),
            linear-gradient(135deg, rgba(34, 211, 238, 0.38), rgba(20, 184, 166, 0.24)),
            rgba(15, 23, 42, 0.92);
        border: 1px solid rgba(103, 232, 249, 0.48);
        box-shadow: 0 0 48px rgba(34, 211, 238, 0.28);
    }
    .life-node {
        position: absolute;
        width: 124px;
        min-height: 70px;
        display: grid;
        place-items: center;
        text-align: center;
        border-radius: 20px;
        padding: 12px;
        color: #e0f2fe;
        font-size: 0.88rem;
        line-height: 1.15;
        font-weight: 900;
        background: rgba(15, 23, 42, 0.74);
        border: 1px solid rgba(148, 163, 184, 0.28);
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.22);
    }
    .life-node.income { left: 44px; top: 72px; }
    .life-node.saving { right: 44px; top: 78px; }
    .life-node.risk { left: 34px; bottom: 88px; }
    .life-node.assets { right: 34px; bottom: 88px; }
    .life-node.goals { left: 50%; top: 32px; transform: translateX(-50%); }
    .life-node.diary { left: 50%; bottom: 32px; transform: translateX(-50%); }
    div[data-testid="stButton"] button[kind="primary"] {
        border-radius: 999px;
        padding: 0.78rem 1.4rem;
        font-weight: 950;
        border: 1px solid rgba(103, 232, 249, 0.48);
        background: linear-gradient(135deg, #22d3ee, #14b8a6);
        color: #06202a;
        box-shadow: 0 18px 42px rgba(34, 211, 238, 0.20);
    }
    @media (max-width: 900px) {
        .life-entry-grid {
            grid-template-columns: 1fr;
        }
        .life-map {
            min-height: 430px;
        }
        .life-node {
            width: 112px;
            font-size: 0.78rem;
        }
    }
    .app-footer {
        border-top: 1px solid rgba(148, 163, 184, 0.24);
        margin-top: 34px;
        padding: 18px 4px 26px;
        color: #cbd5e1;
        font-size: 0.86rem;
        line-height: 1.55;
    }
    .app-footer b {
        color: #f8fafc;
    }
    section[data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 30% 8%, rgba(34, 211, 238, 0.16), transparent 26%),
            linear-gradient(180deg, #0b1220 0%, #111827 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.22);
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] textarea {
        background: #ffffff !important;
        color: #0f172a !important;
        caret-color: #0f766e !important;
        border: 2px solid #22d3ee !important;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_finnhub_api_key() -> str:
    try:
        return str(st.secrets["FINNHUB_API_KEY"]).strip()
    except Exception:
        return os.getenv("FINNHUB_API_KEY", "").strip()


FINNHUB_API_KEY = get_finnhub_api_key()
RISK_FREE_RATE = 0.045
EQUITY_RISK_PREMIUM = 0.045


GUIDE_PDF_PATH = Path(__file__).with_name("LY-STScope_User_Guide.pdf")
GUIDE_SCREENSHOT_DIR = Path(__file__).with_name("guide_assets") / "screenshots"
DEVELOPER_NAME = "Young Lee"
DEVELOPER_EMAIL = "lyn0109@gmail.com"


KOREAN_STOCK_MAP = {
    "삼성전자": "005930.KS",
    "samsung electronics": "005930.KS",
    "sk하이닉스": "000660.KS",
    "sk hynix": "000660.KS",
    "lg에너지솔루션": "373220.KS",
    "lg energy solution": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "samsung biologics": "207940.KS",
    "현대차": "005380.KS",
    "hyundai motor": "005380.KS",
    "기아": "000270.KS",
    "kia": "000270.KS",
    "셀트리온": "068270.KS",
    "celltrion": "068270.KS",
    "kb금융": "105560.KS",
    "kb financial": "105560.KS",
    "신한지주": "055550.KS",
    "shinhan financial": "055550.KS",
    "posco홀딩스": "005490.KS",
    "posco holdings": "005490.KS",
    "naver": "035420.KS",
    "네이버": "035420.KS",
    "카카오": "035720.KS",
    "kakao": "035720.KS",
    "삼성sdi": "006400.KS",
    "samsung sdi": "006400.KS",
    "lg화학": "051910.KS",
    "lg chem": "051910.KS",
    "현대모비스": "012330.KS",
    "hyundai mobis": "012330.KS",
    "삼성물산": "028260.KS",
    "samsung c&t": "028260.KS",
    "포스코퓨처엠": "003670.KS",
    "posco future m": "003670.KS",
    "하나금융지주": "086790.KS",
    "hana financial": "086790.KS",
    "삼성생명": "032830.KS",
    "samsung life": "032830.KS",
    "lg전자": "066570.KS",
    "lg electronics": "066570.KS",
    "sk이노베이션": "096770.KS",
    "sk innovation": "096770.KS",
    "한화에어로스페이스": "012450.KS",
    "hanwha aerospace": "012450.KS",
    "hd현대중공업": "329180.KS",
    "hd hyundai heavy industries": "329180.KS",
    "삼성화재": "000810.KS",
    "samsung fire": "000810.KS",
    "kt&g": "033780.KS",
    "케이티앤지": "033780.KS",
    "우리금융지주": "316140.KS",
    "woori financial": "316140.KS",
    "하이브": "352820.KS",
    "hybe": "352820.KS",
    "크래프톤": "259960.KS",
    "krafton": "259960.KS",
    "sk텔레콤": "017670.KS",
    "sk telecom": "017670.KS",
    "기업은행": "024110.KS",
    "ibk": "024110.KS",
    "고려아연": "010130.KS",
    "korea zinc": "010130.KS",
    "삼성전기": "009150.KS",
    "samsung electro-mechanics": "009150.KS",
    "카카오뱅크": "323410.KS",
    "kakaobank": "323410.KS",
    "카카오페이": "377300.KS",
    "kakaopay": "377300.KS",
    "삼성에스디에스": "018260.KS",
    "samsung sds": "018260.KS",
    "lg": "003550.KS",
    "한국전력": "015760.KS",
    "kepco": "015760.KS",
    "kt": "030200.KS",
    "대한항공": "003490.KS",
    "korean air": "003490.KS",
    "아모레퍼시픽": "090430.KS",
    "amorepacific": "090430.KS",
    "넷마블": "251270.KS",
    "netmarble": "251270.KS",
    "엔씨소프트": "036570.KS",
    "ncsoft": "036570.KS",
    "롯데케미칼": "011170.KS",
    "lotte chemical": "011170.KS",
    "s-oil": "010950.KS",
    "에쓰오일": "010950.KS",
    "현대건설": "000720.KS",
    "hyundai engineering construction": "000720.KS",
    "두산에너빌리티": "034020.KS",
    "doosan enerbility": "034020.KS",
    "lg생활건강": "051900.KS",
    "lg h&h": "051900.KS",
    "한미약품": "128940.KS",
    "hanmi pharm": "128940.KS",
    "유한양행": "000100.KS",
    "yuhan": "000100.KS",
    "녹십자": "006280.KS",
    "gc pharma": "006280.KS",
    "한화솔루션": "009830.KS",
    "hanwha solutions": "009830.KS",
    "현대글로비스": "086280.KS",
    "hyundai glovis": "086280.KS",
    "cj제일제당": "097950.KS",
    "cj cheiljedang": "097950.KS",
    "오리온": "271560.KS",
    "orion": "271560.KS",
    "삼양식품": "003230.KS",
    "samyang foods": "003230.KS",
    "농심": "004370.KS",
    "nongshim": "004370.KS",
    "대한전선": "001440.KS",
    "taihan cable": "001440.KS",
    "현대로템": "064350.KS",
    "hyundai rotem": "064350.KS",
    "lg이노텍": "011070.KS",
    "lg innotek": "011070.KS",
    "ls electric": "010120.KS",
    "ls일렉트릭": "010120.KS",
    "코웨이": "021240.KS",
    "coway": "021240.KS",
    "미래에셋증권": "006800.KS",
    "mirae asset securities": "006800.KS",
    "삼성증권": "016360.KS",
    "samsung securities": "016360.KS",
    "한국금융지주": "071050.KS",
    "korea investment holdings": "071050.KS",
    "메리츠금융지주": "138040.KS",
    "meritz financial": "138040.KS",
    "에코프로비엠": "247540.KQ",
    "ecopro bm": "247540.KQ",
    "에코프로": "086520.KQ",
    "ecopro": "086520.KQ",
    "알테오젠": "196170.KQ",
    "alteogen": "196170.KQ",
    "hpsp": "403870.KQ",
    "에이치피에스피": "403870.KQ",
    "레인보우로보틱스": "277810.KQ",
    "rainbow robotics": "277810.KQ",
    "리노공업": "058470.KQ",
    "leeno": "058470.KQ",
    "셀트리온제약": "068760.KQ",
    "celltrion pharm": "068760.KQ",
    "hlb": "028300.KQ",
    "에스엠": "041510.KQ",
    "sm entertainment": "041510.KQ",
    "jyp ent": "035900.KQ",
    "jyp": "035900.KQ",
    "카카오게임즈": "293490.KQ",
    "kakao games": "293490.KQ",
    "펄어비스": "263750.KQ",
    "pearl abyss": "263750.KQ",
    "스튜디오드래곤": "253450.KQ",
    "studio dragon": "253450.KQ",
    "천보": "278280.KQ",
    "chunbo": "278280.KQ",
    "동진쎄미켐": "005290.KQ",
    "dongjin semichem": "005290.KQ",
    "솔브레인": "357780.KQ",
    "soulbrain": "357780.KQ",
    "원익ips": "240810.KQ",
    "wonik ips": "240810.KQ",
    "파마리서치": "214450.KQ",
    "pharma research": "214450.KQ",
    "삼천당제약": "000250.KQ",
    "samyangdang pharm": "000250.KQ",
    "휴젤": "145020.KQ",
    "hugel": "145020.KQ",
    "메디톡스": "086900.KQ",
    "medytox": "086900.KQ",
    "클래시스": "214150.KQ",
    "classys": "214150.KQ",
    "씨젠": "096530.KQ",
    "seegene": "096530.KQ",
    "오스템임플란트": "048260.KQ",
    "osstem implant": "048260.KQ",
    "파두": "440110.KQ",
    "fadu": "440110.KQ",
    "기가비스": "420770.KQ",
    "gigavis": "420770.KQ",
    "이오테크닉스": "039030.KQ",
    "eo technics": "039030.KQ",
    "제이앤티씨": "204270.KQ",
    "jntc": "204270.KQ",
    "hd한국조선해양": "009540.KS",
    "hd korea shipbuilding": "009540.KS",
    "삼성중공업": "010140.KS",
    "samsung heavy industries": "010140.KS",
    "한화오션": "042660.KS",
    "hanwha ocean": "042660.KS",
    "hmm": "011200.KS",
    "팬오션": "028670.KS",
    "pan ocean": "028670.KS",
    "ls": "006260.KS",
    "db하이텍": "000990.KS",
    "db hitek": "000990.KS",
    "db손해보험": "005830.KS",
    "db insurance": "005830.KS",
    "현대해상": "001450.KS",
    "hyundai marine fire": "001450.KS",
    "강원랜드": "035250.KS",
    "kangwon land": "035250.KS",
}


def init_state() -> None:
    st.session_state.setdefault("stocks", {})
    st.session_state.setdefault("compare", [])
    st.session_state.setdefault("portfolio", {})
    st.session_state.setdefault("portfolio_weighting_mode", "Share-based")
    st.session_state.setdefault("portfolio_base_currency", "USD")
    st.session_state.setdefault("manual_usdkrw", 1350.0)
    st.session_state.setdefault("use_live_fx", True)
    st.session_state.setdefault("last_query", "")
    st.session_state.setdefault("selected_detail", None)
    st.session_state.setdefault("comments", [])
    st.session_state.setdefault("financial_diary", [])
    st.session_state.setdefault("life_entry_complete", False)


@st.cache_data(ttl=300, show_spinner=False)
def finnhub_get(path: str, **params: Any) -> Any:
    if not FINNHUB_API_KEY:
        raise RuntimeError("FINNHUB_API_KEY is not configured in Streamlit secrets.")

    params["token"] = FINNHUB_API_KEY
    response = requests.get(
        f"https://finnhub.io/api/v1/{path}",
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def fmt_money(value: float | int | None, currency: str = "USD") -> str:
    if value is None:
        return "N/A"
    if currency == "KRW":
        return f"₩{value:,.0f}"
    return f"${value:,.2f}"


def stock_money(stock: dict[str, Any], value: float | int | None) -> str:
    return fmt_money(value, stock.get("currency", "USD"))


def fmt_number(value: float | int | None, digits: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.{digits}f}"


def fmt_market_cap(value: float | int | None, currency: str = "USD") -> str:
    if not value:
        return "N/A"
    # Finnhub profile marketCapitalization is in millions.
    if currency == "KRW":
        trillions = float(value) / 1_000_000
        return f"₩{trillions:,.2f}T"
    billions = float(value) / 1000
    return f"${billions:,.2f}B"


@st.cache_data(ttl=3600, show_spinner=False)
def load_live_usdkrw() -> dict[str, Any]:
    try:
        history = yf.download(
            "KRW=X",
            period="5d",
            interval="1d",
            progress=False,
            auto_adjust=False,
            threads=False,
        )
    except Exception:
        return {"rate": None, "date": None, "source": "Unavailable"}

    clean = normalize_price_history(history.reset_index() if not history.empty else history)
    if clean.empty:
        return {"rate": None, "date": None, "source": "Unavailable"}

    latest = clean.iloc[-1]
    return {
        "rate": float(latest["Close"]),
        "date": latest["Date"].strftime("%Y-%m-%d"),
        "source": "Yahoo Finance KRW=X",
    }


def effective_usdkrw() -> tuple[float, str, str]:
    manual_rate = float(st.session_state.get("manual_usdkrw", 1350.0) or 1350.0)
    if st.session_state.get("use_live_fx", True):
        live = load_live_usdkrw()
        if live.get("rate"):
            return float(live["rate"]), str(live.get("source") or "Yahoo Finance KRW=X"), str(live.get("date") or "Latest")
    return manual_rate, "Manual fallback", "User input"


def convert_value(value: float, from_currency: str, to_currency: str, usdkrw: float) -> float:
    if from_currency == to_currency:
        return value
    if from_currency == "USD" and to_currency == "KRW":
        return value * usdkrw
    if from_currency == "KRW" and to_currency == "USD":
        return value / usdkrw if usdkrw > 0 else 0.0
    return value


def normalize_company_query(query: str) -> str:
    return " ".join(query.strip().lower().split())


def is_korean_symbol(symbol: str) -> bool:
    clean = symbol.strip().upper()
    return clean.endswith(".KS") or clean.endswith(".KQ")


def resolve_korean_ticker(query: str) -> str | None:
    clean = query.strip()
    normalized = normalize_company_query(clean)
    if normalized in KOREAN_STOCK_MAP:
        return KOREAN_STOCK_MAP[normalized]

    upper = clean.upper()
    if is_korean_symbol(upper):
        return upper

    if clean.isdigit() and len(clean) == 6:
        known_symbols = set(KOREAN_STOCK_MAP.values())
        kosdaq_symbol = f"{clean}.KQ"
        kospi_symbol = f"{clean}.KS"
        if kosdaq_symbol in known_symbols:
            return kosdaq_symbol
        return kospi_symbol

    return None


def company_name_for_korean_symbol(symbol: str) -> str:
    for name, mapped_symbol in KOREAN_STOCK_MAP.items():
        if mapped_symbol == symbol and any(ord(char) > 127 for char in name):
            return name
    return symbol


def resolve_ticker(query: str) -> str:
    query = query.strip().upper()
    data = finnhub_get("search", q=query)
    results = data.get("result", [])
    if not results:
        return query

    exact = next((item for item in results if item.get("symbol") == query), None)
    common = next((item for item in results if item.get("type") == "Common Stock"), None)
    return (exact or common or results[0]).get("symbol", query)


def safe_metric(symbol: str) -> dict[str, Any]:
    try:
        data = finnhub_get("stock/metric", symbol=symbol, metric="all")
        return data.get("metric", {}) if isinstance(data, dict) else {}
    except Exception:
        return {}


def average_peer_pe(symbol: str) -> tuple[float, list[str]]:
    try:
        peers = finnhub_get("stock/peers", symbol=symbol)
    except Exception:
        peers = []

    top_peers = [item for item in peers if item != symbol][:3] if isinstance(peers, list) else []
    pe_values = []
    for peer in top_peers:
        metric = safe_metric(peer)
        pe = metric.get("peExclExtraTTM") or metric.get("peBasicExclExtraTTM")
        if pe and 0 < pe < 150:
            pe_values.append(float(pe))

    return (sum(pe_values) / len(pe_values) if pe_values else 15.0), top_peers


@st.cache_data(ttl=900, show_spinner=False)
def load_price_history(symbol: str, days: int = 180) -> pd.DataFrame:
    finnhub_history = normalize_price_history(load_price_history_from_finnhub(symbol, days))
    if not finnhub_history.empty:
        return finnhub_history
    return normalize_price_history(load_price_history_from_yahoo(symbol, days))


def normalize_price_history(history: pd.DataFrame) -> pd.DataFrame:
    if history.empty:
        return pd.DataFrame()

    history = history.copy()
    if isinstance(history.columns, pd.MultiIndex):
        history.columns = [
            "_".join(str(part) for part in col if str(part))
            for col in history.columns.to_flat_index()
        ]

    if "Date" not in history.columns:
        history = history.reset_index()

    date_col = next((col for col in history.columns if str(col).lower() in {"date", "datetime"}), None)
    close_col = next((col for col in history.columns if str(col).lower() == "close" or str(col).lower().startswith("close_")), None)

    if not date_col or not close_col:
        return pd.DataFrame()

    clean = history[[date_col, close_col]].copy()
    clean.columns = ["Date", "Close"]
    clean["Date"] = pd.to_datetime(clean["Date"], errors="coerce")
    clean["Close"] = pd.to_numeric(clean["Close"], errors="coerce")
    clean = clean.dropna(subset=["Date", "Close"])
    return clean.sort_values("Date")


def load_price_history_from_finnhub(symbol: str, days: int) -> pd.DataFrame:
    end = datetime.now()
    start = end - timedelta(days=days)
    try:
        data = finnhub_get(
            "stock/candle",
            symbol=symbol,
            resolution="D",
            **{"from": int(start.timestamp()), "to": int(end.timestamp())},
        )
    except Exception:
        return pd.DataFrame()

    if not isinstance(data, dict) or data.get("s") != "ok":
        return pd.DataFrame()

    closes = data.get("c") or []
    timestamps = data.get("t") or []
    if not closes or not timestamps:
        return pd.DataFrame()

    return pd.DataFrame(
        {
            "Date": [datetime.fromtimestamp(ts).date() for ts in timestamps],
            "Close": closes,
        }
    )


def load_price_history_from_yahoo(symbol: str, days: int) -> pd.DataFrame:
    try:
        history = yf.download(
            symbol,
            period=f"{max(days, 30)}d",
            interval="1d",
            progress=False,
            auto_adjust=True,
            threads=False,
        )
    except Exception:
        return pd.DataFrame()

    if history.empty:
        return pd.DataFrame()
    return history.reset_index()


def calculate_valuation(stock: dict[str, Any]) -> dict[str, Any]:
    beta = float(stock.get("beta") or 1.0)
    eps = float(stock.get("eps") or 0)
    dividend = float(stock.get("dividend") or 0)
    growth = float(stock.get("growth_rate") or 0.05)
    book_value = float(stock.get("book_value") or 0)
    peer_pe = float(stock.get("peer_average_pe") or 15)
    price = float(stock.get("price") or 0)

    expected_return = RISK_FREE_RATE + beta * EQUITY_RISK_PREMIUM
    max_implied_pe = 50
    values = []

    income_value = 0.0
    income_model = "N/A"
    if dividend > 0 and expected_return > growth:
        income_value = (dividend * (1 + growth)) / (expected_return - growth)
        income_model = "GGM"
    elif eps > 0:
        adjusted_growth = min(growth, expected_return - 0.02)
        if adjusted_growth > 0 and expected_return > adjusted_growth:
            implied_pe = (1 + adjusted_growth) / (expected_return - adjusted_growth)
        else:
            implied_pe = 1 / expected_return if expected_return > 0 else 0
        income_value = eps * min(implied_pe, max_implied_pe)
        income_model = "ECM"
    if income_value > 0:
        values.append(income_value)

    graham_value = 0.0
    if eps > 0 and book_value > 0:
        graham_value = (22.5 * book_value * eps) ** 0.5
        values.append(graham_value)

    relative_value = 0.0
    if eps > 0 and peer_pe > 0:
        relative_value = eps * peer_pe
        values.append(relative_value)

    fair_price = sum(values) / len(values) if values else 0.0
    if fair_price <= 0 or price <= 0:
        status = "Fair Value"
    else:
        diff_ratio = (price - fair_price) / fair_price
        if diff_ratio > 0.05:
            status = "Overvalued"
        elif diff_ratio < -0.05:
            status = "Undervalued"
        else:
            status = "Fair Value"

    stock.update(
        {
            "expected_return": expected_return,
            "fair_price": fair_price,
            "valuation_status": status,
            "triangulation": {
                "income_model": income_model,
                "income_value": income_value,
                "asset_value": graham_value,
                "market_value": relative_value,
                "valid_models": len(values),
            },
        }
    )
    return stock


def load_korean_stock(query: str) -> dict[str, Any]:
    symbol = resolve_korean_ticker(query)
    if not symbol:
        raise ValueError(f"{query} is not recognized as a Korean stock.")

    ticker = yf.Ticker(symbol)
    history = load_price_history_from_yahoo(symbol, days=30)
    if history.empty:
        raise ValueError(f"No Yahoo Finance price history was returned for {symbol}.")

    history = normalize_price_history(history)
    closes = history["Close"].astype(float).tolist()
    price = closes[-1] if closes else 0.0
    if price <= 0:
        raise ValueError(f"No current price was returned for {symbol}.")

    previous = closes[-2] if len(closes) >= 2 else price
    change_pct = ((price - previous) / previous * 100) if previous else 0.0

    try:
        info = ticker.get_info()
    except Exception:
        info = {}

    market_cap = info.get("marketCap")
    market_cap_millions = float(market_cap) / 1_000_000 if market_cap else None
    trailing_eps = info.get("trailingEps") or 0
    book_value = info.get("bookValue") or 0
    dividend_rate = info.get("dividendRate") or 0
    dividend_yield = (float(info.get("dividendYield") or 0) * 100)
    pe = info.get("trailingPE") or info.get("forwardPE")
    beta = info.get("beta") or 1.0
    growth_rate = info.get("earningsGrowth")
    if growth_rate is None:
        growth_rate = info.get("revenueGrowth")
    if growth_rate is None:
        growth_rate = 0.05

    name = (
        info.get("longName")
        or info.get("shortName")
        or company_name_for_korean_symbol(symbol)
    )
    industry = info.get("industry") or info.get("sector") or "Korean Equity"
    peer_pe = pe if pe and 0 < float(pe) < 100 else 15.0

    stock = {
        "symbol": symbol,
        "name": name,
        "industry": industry,
        "price": price,
        "change_pct": change_pct,
        "market_cap": market_cap_millions,
        "pe": pe,
        "dividend_yield": dividend_yield,
        "beta": beta,
        "eps": trailing_eps,
        "dividend": dividend_rate,
        "growth_rate": growth_rate,
        "book_value": book_value,
        "peer_average_pe": peer_pe,
        "peers": [],
        "market": "Korea",
        "currency": "KRW",
    }
    return calculate_valuation(stock)


def load_stock(query: str) -> dict[str, Any]:
    korean_symbol = resolve_korean_ticker(query)
    if korean_symbol:
        return load_korean_stock(korean_symbol)

    symbol = resolve_ticker(query)
    profile = finnhub_get("stock/profile2", symbol=symbol)
    quote = finnhub_get("quote", symbol=symbol)
    metric = safe_metric(symbol)
    peer_pe, peers = average_peer_pe(symbol)

    price = float(quote.get("c") or 0)
    if price <= 0:
        raise ValueError(f"No current price was returned for {symbol}.")

    stock = {
        "symbol": symbol,
        "name": profile.get("name") or symbol,
        "industry": profile.get("finnhubIndustry") or "N/A",
        "price": price,
        "change_pct": float(quote.get("dp") or 0),
        "market_cap": profile.get("marketCapitalization"),
        "pe": metric.get("peExclExtraTTM") or metric.get("peBasicExclExtraTTM"),
        "dividend_yield": metric.get("dividendYieldIndicatedAnnual") or 0,
        "beta": metric.get("beta") or 1.0,
        "eps": metric.get("epsExclExtraItemsTTM") or metric.get("epsBasicExclExtraItemsTTM") or 0,
        "dividend": metric.get("dividendPerShareAnnual") or 0,
        "growth_rate": (metric.get("epsGrowth3Y") or 5) / 100,
        "book_value": metric.get("bookValuePerShareAnnual") or 0,
        "peer_average_pe": peer_pe,
        "peers": peers,
        "market": "US",
        "currency": "USD",
    }
    return calculate_valuation(stock)


def status_color(status: str) -> str:
    return {
        "Undervalued": "#10b981",
        "Fair Value": "#f59e0b",
        "Overvalued": "#ef4444",
    }.get(status, "#94a3b8")


def metric_card(label: str, value: str, color: str = "#102033") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value" style="color:{color};">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def guide_image(filename: str, caption: str) -> None:
    image_path = GUIDE_SCREENSHOT_DIR / filename
    if image_path.exists():
        st.image(str(image_path), caption=caption, use_container_width=True)
    else:
        st.caption(f"Guide graphic unavailable: {filename}")


def add_compare(symbol: str) -> None:
    compare = st.session_state.compare
    if symbol in compare:
        compare.remove(symbol)
    elif len(compare) < 3:
        compare.append(symbol)
    else:
        st.warning("You can compare up to 3 stocks at a time.")


def toggle_portfolio(symbol: str) -> None:
    portfolio = st.session_state.portfolio
    if symbol in portfolio:
        del portfolio[symbol]
    else:
        portfolio[symbol] = {"shares": 1.0}


def select_detail(symbol: str) -> None:
    st.session_state.selected_detail = symbol


def sync_selected_detail_from_query() -> None:
    try:
        params = st.query_params
    except Exception:
        params = st.experimental_get_query_params()

    detail = params.get("detail")
    if isinstance(detail, list):
        detail = detail[0] if detail else None
    if detail and detail in st.session_state.stocks:
        st.session_state.selected_detail = detail


def render_stock_card(stock: dict[str, Any]) -> None:
    symbol = stock["symbol"]
    status = stock["valuation_status"]
    compare_active = symbol in st.session_state.compare
    portfolio_active = symbol in st.session_state.portfolio
    detail_href = f"?detail={quote(symbol)}"
    logo_text = symbol[:2].upper()
    with st.container(border=True):
        st.markdown(
            f"""
            <a class="stock-card-link" href="{detail_href}" target="_self">
            <div class="stock-card-panel">
                <div class="stock-card-head">
                    <div class="company-logo">{logo_text}</div>
                    <div>
                        <div class="company-title">{escape(str(stock['name']))}</div>
                        <div class="company-meta"><span class="ticker-pill">{symbol}</span>{stock['industry']}</div>
                    </div>
                </div>
                <div class="stock-card-price">
                    <div>
                        <div class="price">{stock_money(stock, stock['price'])}</div>
                        <div style="color:{'#059669' if stock['change_pct'] >= 0 else '#dc2626'};font-weight:850;margin-top:7px;">{stock['change_pct']:+.2f}% today</div>
                    </div>
                    <span class="status-chip" style="background:{status_color(status)};">{status}</span>
                </div>
                <div class="stock-card-stats">
                    <span>Market Cap<b>{fmt_market_cap(stock['market_cap'], stock.get('currency', 'USD'))}</b></span>
                    <span>PER<b>{fmt_number(stock['pe'])}</b></span>
                </div>
                <div class="click-hint">Click this stock card to view details and price movement.</div>
            </div>
            </a>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        c1.button(
            "Added" if symbol in st.session_state.compare else "Compare",
            key=f"compare_{symbol}",
            on_click=add_compare,
            args=(symbol,),
            use_container_width=True,
        )
        c2.button(
            "In Portfolio" if symbol in st.session_state.portfolio else "Add to Portfolio",
            key=f"portfolio_{symbol}",
            on_click=toggle_portfolio,
            args=(symbol,),
            use_container_width=True,
        )


def render_fair_value(stock: dict[str, Any]) -> None:
    tri = stock["triangulation"]
    st.subheader(f"{stock['name']} ({stock['symbol']})")
    st.metric("Current Price", stock_money(stock, stock["price"]), f"{stock['change_pct']:+.2f}%")
    st.metric("Blended Fair Value", stock_money(stock, stock["fair_price"]) if stock["fair_price"] else "N/A")
    st.write(f"**Status:** {stock['valuation_status']}")
    st.write(f"**Required Return (CAPM):** {stock['expected_return'] * 100:.2f}%")
    st.table(
        {
            "Approach": ["Income", "Asset", "Market"],
            "Model": [tri["income_model"], "Graham Number", "Peer P/E"],
            "Value": [
                stock_money(stock, tri["income_value"]) if tri["income_value"] else "N/A",
                stock_money(stock, tri["asset_value"]) if tri["asset_value"] else "N/A",
                stock_money(stock, tri["market_value"]) if tri["market_value"] else "N/A",
            ],
        }
    )


def render_tradingview_chart(symbol: str) -> None:
    container_id = f"tradingview_{symbol.replace('.', '_').replace('-', '_')}"
    tv_symbol = f"KRX:{symbol[:6]}" if is_korean_symbol(symbol) else symbol
    components.html(
        f"""
        <div class="tradingview-widget-container" style="height:520px;width:100%;">
            <div id="{container_id}" style="height:500px;width:100%;"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
                "autosize": true,
                "symbol": "{tv_symbol}",
                "interval": "D",
                "timezone": "Etc/UTC",
                "theme": "dark",
                "style": "1",
                "locale": "en",
                "toolbar_bg": "#0f172a",
                "enable_publishing": false,
                "hide_top_toolbar": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "save_image": false,
                "calendar": false,
                "container_id": "{container_id}"
            }});
            </script>
        </div>
        """,
        height=540,
    )


def valuation_upside(stock: dict[str, Any]) -> float | None:
    price = float(stock.get("price") or 0)
    fair_price = float(stock.get("fair_price") or 0)
    if price <= 0 or fair_price <= 0:
        return None
    return (fair_price - price) / price * 100


def risk_score_label(stock: dict[str, Any]) -> str:
    beta = float(stock.get("beta") or 1.0)
    if beta < 0.85:
        return "Low"
    if beta < 1.25:
        return "Low-Mid"
    if beta < 1.75:
        return "Mid-High"
    return "High"


def valuation_score_text(stock: dict[str, Any]) -> str:
    status = stock.get("valuation_status", "Fair Value")
    if status == "Undervalued":
        return "Attractive"
    if status == "Overvalued":
        return "Caution"
    return "Neutral"


def candle_heights(symbol: str) -> list[tuple[str, int, int]]:
    history = load_price_history(symbol, days=90).tail(13)
    if history.empty or len(history) < 3:
        fallback = [52, 70, 86, 102, 132, 112, 92, 118, 154, 136, 172, 196, 180]
        return [("up" if idx % 3 != 0 else "down", height, 25 + (height % 55)) for idx, height in enumerate(fallback)]

    closes = history["Close"].astype(float).tolist()
    low = min(closes)
    high = max(closes)
    span = high - low if high > low else 1
    candles = []
    for idx, close in enumerate(closes):
        previous = closes[idx - 1] if idx else close
        direction = "up" if close >= previous else "down"
        height = int(56 + ((close - low) / span) * 142)
        volume_proxy = int(24 + abs(close - previous) / max(abs(previous), 1) * 900)
        candles.append((direction, max(48, min(height, 205)), max(24, min(volume_proxy, 78))))
    return candles


def render_stock_terminal(stock: dict[str, Any]) -> None:
    symbol = escape(str(stock["symbol"]))
    name = escape(str(stock["name"]))
    industry = escape(str(stock.get("industry") or "N/A"))
    status = escape(str(stock.get("valuation_status") or "Fair Value"))
    change = float(stock.get("change_pct") or 0)
    change_class = "green" if change >= 0 else "red"
    upside = valuation_upside(stock)
    upside_text = "N/A" if upside is None else f"{upside:+.1f}%"
    fair_value = stock_money(stock, stock["fair_price"]) if stock.get("fair_price") else "N/A"
    pe_text = fmt_number(stock.get("pe"))
    growth_text = f"{float(stock.get('growth_rate') or 0) * 100:.1f}%"
    beta_text = fmt_number(stock.get("beta"))
    candles = candle_heights(stock["symbol"])
    candle_html = "\n".join(
        f'<div class="candle {direction}" style="height:{height}px"></div>'
        for direction, height, _ in candles
    )
    volume_html = "\n".join(
        f'<div class="vol {direction}" style="height:{volume_height}%"></div>'
        for direction, _, volume_height in candles
    )
    st.markdown(
        f"""
        <div class="terminal-showcase result-terminal">
            <div class="terminal-shell">
                <div class="terminal-topbar">
                    <div class="terminal-mini-logo">LY</div>
                    <div class="terminal-search"><span>Search</span><span>{symbol}</span></div>
                    <div class="terminal-nav">
                        <span class="active">Market</span>
                        <span>Valuation</span>
                        <span>Portfolio</span>
                        <span>Risk</span>
                        <span>Research</span>
                    </div>
                    <div class="terminal-user">{escape(datetime.now().strftime("%b %d, %Y"))}<br><b>Finnhub live data</b></div>
                </div>
                <div class="terminal-body">
                    <div class="terminal-chart-card">
                        <div class="terminal-stock-head">
                            <div>
                                <div class="terminal-symbol">{symbol}</div>
                                <div class="terminal-company">{name} · {industry}</div>
                            </div>
                            <div class="terminal-price">{stock_money(stock, stock["price"])} <span class="{change_class}">{change:+.2f}%</span></div>
                        </div>
                        <div class="terminal-chart-grid">
                            <div class="ma-line ma-green"></div>
                            <div class="ma-line ma-blue"></div>
                            <div class="candle-row">
                                {candle_html}
                            </div>
                        </div>
                        <div class="volume-row">
                            {volume_html}
                        </div>
                    </div>
                    <div class="terminal-side">
                        <div class="terminal-side-card">
                            <div class="side-title">INSTITUTIONAL METRICS: {symbol}</div>
                            <div class="metric-grid-dark">
                                <div><div class="dark-label">Fair Value</div><div class="dark-value">{fair_value}</div></div>
                                <div><div class="dark-label">Upside</div><div class="dark-value {'green' if upside is None or upside >= 0 else 'red'}">{upside_text}</div></div>
                                <div><div class="dark-label">Risk Score</div><div class="dark-value orange">{risk_score_label(stock)}</div></div>
                                <div><div class="dark-label">Valuation</div><div class="dark-value green">{valuation_score_text(stock)}</div></div>
                            </div>
                        </div>
                        <div class="terminal-side-card">
                            <div class="side-title">TRIANGLE VALUATION</div>
                            <div class="radar-wrap"><div class="radar-triangle"></div></div>
                            <div class="radar-scores">
                                <span>PER<b>{pe_text}</b></span>
                                <span>Growth<b>{growth_text}</b></span>
                                <span>Beta<b style="color:#fbbf24;">{beta_text}</b></span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="terminal-status-strip">
                    <span>Status: <b>{status}</b></span>
                    <span>Market Cap: <b>{fmt_market_cap(stock.get("market_cap"), stock.get("currency", "USD"))}</b></span>
                    <span>EPS: <b>{stock_money(stock, float(stock.get("eps") or 0))}</b></span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def clamp_score(value: float, low: float = 0.0, high: float = 10.0) -> float:
    return max(low, min(high, value))


def render_valuation_radar(stock: dict[str, Any]) -> None:
    upside = valuation_upside(stock)
    beta = float(stock.get("beta") or 1.0)
    growth = float(stock.get("growth_rate") or 0.0) * 100
    pe = float(stock.get("pe") or 0)

    value_score = clamp_score(5 + ((upside or 0) / 8))
    risk_score = clamp_score(10 - abs(beta - 1) * 4)
    quality_score = clamp_score(5 + min(growth, 40) / 10 - (max(pe - 25, 0) / 25))

    center_x = 150
    center_y = 150
    max_radius = 96
    axes = [(-90, value_score), (150, risk_score), (30, quality_score)]
    points = []
    for angle, score in axes:
        radius = max_radius * (score / 10)
        radians = math.radians(angle)
        x = center_x + radius * math.cos(radians)
        y = center_y + radius * math.sin(radians)
        points.append(f"{x:.1f},{y:.1f}")

    grid_triangles = []
    for ratio in [0.25, 0.5, 0.75, 1.0]:
        radius = max_radius * ratio
        grid_points = []
        for angle in [-90, 150, 30]:
            radians = math.radians(angle)
            x = center_x + radius * math.cos(radians)
            y = center_y + radius * math.sin(radians)
            grid_points.append(f"{x:.1f},{y:.1f}")
        grid_triangles.append(f'<polygon points="{" ".join(grid_points)}" fill="none" stroke="#cbd5e1" stroke-width="1"/>')

    upside_text = "N/A" if upside is None else f"{upside:+.1f}%"
    st.markdown(
        f"""
        <div class="valuation-radar-card">
            <div>
                <div class="valuation-radar-title">Modern Valuation Radar</div>
                <div class="valuation-radar-copy">
                    This radar summarizes the triangulation result into three readable dimensions:
                    value opportunity, beta-adjusted risk balance, and growth/quality signal.
                </div>
                <div class="valuation-radar-legend">
                    <div><span>Value Opportunity</span><b>{value_score:.1f}/10</b></div>
                    <div><span>Risk Balance</span><b>{risk_score:.1f}/10</b></div>
                    <div><span>Growth / Quality</span><b>{quality_score:.1f}/10</b></div>
                </div>
            </div>
            <svg class="valuation-radar-svg" viewBox="0 0 300 300" role="img" aria-label="Valuation radar chart">
                <defs>
                    <linearGradient id="radarFill" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#22d3ee" stop-opacity="0.62"/>
                        <stop offset="55%" stop-color="#22c55e" stop-opacity="0.46"/>
                        <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.42"/>
                    </linearGradient>
                </defs>
                <rect x="14" y="14" width="272" height="272" rx="28" fill="#f8fbff" stroke="#d8e2ef"/>
                <circle cx="150" cy="150" r="112" fill="#ffffff" stroke="#e2e8f0"/>
                {"".join(grid_triangles)}
                <line x1="150" y1="150" x2="150" y2="54" stroke="#d8e2ef" stroke-width="1"/>
                <line x1="150" y1="150" x2="66.9" y2="198" stroke="#d8e2ef" stroke-width="1"/>
                <line x1="150" y1="150" x2="233.1" y2="198" stroke="#d8e2ef" stroke-width="1"/>
                <polygon points="{" ".join(points)}" fill="url(#radarFill)" stroke="#0891b2" stroke-width="3"/>
                <circle cx="{points[0].split(',')[0]}" cy="{points[0].split(',')[1]}" r="5" fill="#0891b2"/>
                <circle cx="{points[1].split(',')[0]}" cy="{points[1].split(',')[1]}" r="5" fill="#16a34a"/>
                <circle cx="{points[2].split(',')[0]}" cy="{points[2].split(',')[1]}" r="5" fill="#f59e0b"/>
                <text x="150" y="38" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="800">Value {upside_text}</text>
                <text x="54" y="222" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="800">Risk β {fmt_number(beta)}</text>
                <text x="246" y="222" text-anchor="middle" fill="#0f172a" font-size="13" font-weight="800">Growth {growth:.1f}%</text>
            </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stock_detail(stock: dict[str, Any]) -> None:
    tri = stock["triangulation"]
    st.divider()
    st.markdown(
        f"""
        <div class="hero-panel">
            <h2 class="detail-hero-title">{escape(str(stock['name']))}</h2>
            <div class="detail-hero-meta">{escape(str(stock['symbol']))} - {escape(str(stock['industry']))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Current Price", stock_money(stock, stock["price"]))
    with c2:
        metric_card("Daily Change", f"{stock['change_pct']:+.2f}%", "#10b981" if stock["change_pct"] >= 0 else "#ef4444")
    with c3:
        metric_card("Blended Fair Value", stock_money(stock, stock["fair_price"]) if stock["fair_price"] else "N/A")
    with c4:
        metric_card("Valuation", stock["valuation_status"], status_color(stock["valuation_status"]))

    st.markdown("#### Price Movement")
    render_tradingview_chart(stock["symbol"])
    st.caption("Interactive chart powered by TradingView. Financial metrics and valuation data remain powered by Finnhub.")

    st.markdown("#### Key Statistics")
    stats = {
        "Market Cap": fmt_market_cap(stock["market_cap"], stock.get("currency", "USD")),
        "PER (TTM)": fmt_number(stock["pe"]),
        "Dividend Yield": f"{float(stock['dividend_yield'] or 0):.2f}%",
        "Beta": fmt_number(stock["beta"]),
        "EPS": stock_money(stock, float(stock["eps"] or 0)),
        "Growth Rate": f"{float(stock['growth_rate'] or 0) * 100:.1f}%",
    }
    st.dataframe([stats], hide_index=True, use_container_width=True)

    st.markdown("#### Valuation Triangulation")
    st.dataframe(
        [
            {
                "Approach": "Income",
                "Model": tri["income_model"],
                "Value": stock_money(stock, tri["income_value"]) if tri["income_value"] else "N/A",
            },
            {
                "Approach": "Asset",
                "Model": "Graham Number",
                "Value": stock_money(stock, tri["asset_value"]) if tri["asset_value"] else "N/A",
            },
            {
                "Approach": "Market",
                "Model": "Peer P/E",
                "Value": stock_money(stock, tri["market_value"]) if tri["market_value"] else "N/A",
            },
        ],
        hide_index=True,
        use_container_width=True,
    )
    render_valuation_radar(stock)
    st.write(
        f"{stock['name']} belongs to the {stock['industry']} sector. "
        f"The blended fair value is based on {tri['valid_models']} available valuation model(s)."
    )


def search_tab() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">A New Standard for Stock Analysis</h1>
            <div class="hero-muted">Educational finance analytics prototype for valuation, CAPM, portfolio risk, diversification, and correlation analysis.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "LY-STScope is designed for learning and analytical discussion using real market examples. "
        "It is not an investment recommendation or financial advisory service."
    )
    if not FINNHUB_API_KEY:
        st.warning(
            "FINNHUB_API_KEY is not configured, so US live stock search is temporarily unavailable. "
            "Korean stock search and REIT Analysis can still work with Yahoo Finance and educational sample data."
        )
        st.info("Add FINNHUB_API_KEY in Streamlit Cloud > App settings > Secrets to enable live stock analysis.")

    with st.form("stock_search"):
        query = st.text_input(
            "Enter a stock ticker",
            value=st.session_state.last_query,
            placeholder="Enter a ticker or company name, e.g. NVDA, AAPL, 삼성전자, NAVER, SK하이닉스",
        )
        submitted = st.form_submit_button("Analyze Ticker")
    if submitted and query.strip():
        with st.spinner("Loading stock data..."):
            try:
                if not FINNHUB_API_KEY and not resolve_korean_ticker(query):
                    raise ValueError("US stock search requires FINNHUB_API_KEY. Try a Korean stock such as 삼성전자 or 005930.KS, or add the API key in Secrets.")
                stock = load_stock(query)
                st.session_state.stocks[stock["symbol"]] = stock
                st.session_state.last_query = query.strip()
                st.session_state.selected_detail = stock["symbol"]
            except Exception as exc:
                st.error(f"Could not load stock data: {exc}")

    filters = ["All", "Undervalued", "Fair Value", "Overvalued"]
    selected_filter = st.radio("Valuation filter", filters, horizontal=True)

    stocks = list(st.session_state.stocks.values())
    if selected_filter != "All":
        stocks = [s for s in stocks if s["valuation_status"] == selected_filter]

    if not stocks:
        st.info("Enter a ticker above to generate the company analysis dashboard.")
        return

    selected_symbol = st.session_state.selected_detail
    if selected_symbol and selected_symbol in st.session_state.stocks:
        render_stock_detail(st.session_state.stocks[selected_symbol])

    for row_start in range(0, len(stocks), 3):
        cols = st.columns(3)
        for col, stock in zip(cols, stocks[row_start : row_start + 3]):
            with col:
                render_stock_card(stock)


def compare_tab() -> None:
    st.header("Side-by-Side Comparison")
    selected = [st.session_state.stocks[s] for s in st.session_state.compare if s in st.session_state.stocks]
    if not selected:
        st.info("Select stocks to compare from the Search tab. You can compare up to 3 stocks.")
        return

    rows = []
    metrics = [
        ("Current Price", lambda s: stock_money(s, s["price"])),
        ("Change", lambda s: f"{s['change_pct']:+.2f}%"),
        ("Market Cap", lambda s: fmt_market_cap(s["market_cap"], s.get("currency", "USD"))),
        ("PER", lambda s: fmt_number(s["pe"])),
        ("Dividend Yield", lambda s: f"{float(s['dividend_yield'] or 0):.2f}%"),
        ("Beta", lambda s: fmt_number(s["beta"])),
        ("EPS", lambda s: stock_money(s, float(s["eps"] or 0))),
        ("Fair Value", lambda s: stock_money(s, s["fair_price"]) if s["fair_price"] else "N/A"),
        ("Valuation", lambda s: s["valuation_status"]),
    ]
    for label, getter in metrics:
        row = {"Metric": label}
        for stock in selected:
            row[f"{stock['name']} ({stock['symbol']})"] = getter(stock)
        rows.append(row)
    st.dataframe(rows, hide_index=True, use_container_width=True)

    cols = st.columns(len(selected))
    for col, stock in zip(cols, selected):
        col.button("Remove " + stock["symbol"], key=f"remove_compare_{stock['symbol']}", on_click=add_compare, args=(stock["symbol"],))


def portfolio_market_values() -> dict[str, float]:
    values: dict[str, float] = {}
    base_currency = st.session_state.get("portfolio_base_currency", "USD")
    usdkrw, _, _ = effective_usdkrw()
    for symbol, holding in st.session_state.portfolio.items():
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        native_value = float(stock["price"]) * float(holding.get("shares") or 0)
        values[symbol] = convert_value(
            native_value,
            stock.get("currency", "USD"),
            base_currency,
            usdkrw,
        )
    return values


def portfolio_native_market_values() -> dict[str, float]:
    values: dict[str, float] = {}
    for symbol, holding in st.session_state.portfolio.items():
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        values[symbol] = float(stock["price"]) * float(holding.get("shares") or 0)
    return values


def portfolio_currency_breakdown() -> dict[str, float]:
    breakdown: dict[str, float] = {}
    for symbol, value in portfolio_native_market_values().items():
        stock = st.session_state.stocks.get(symbol, {})
        currency = stock.get("currency", "USD")
        breakdown[currency] = breakdown.get(currency, 0.0) + value
    return breakdown


def portfolio_analysis_weights(symbols: list[str] | None = None) -> dict[str, float]:
    selected_symbols = symbols or [
        symbol for symbol in st.session_state.portfolio if symbol in st.session_state.stocks
    ]
    selected_symbols = [symbol for symbol in selected_symbols if symbol in st.session_state.stocks]
    if not selected_symbols:
        return {}

    mode = st.session_state.get("portfolio_weighting_mode", "Share-based")
    if mode == "Equal-weighted":
        equal_weight = 1 / len(selected_symbols)
        return {symbol: equal_weight for symbol in selected_symbols}

    values = portfolio_market_values()
    selected_values = {symbol: values.get(symbol, 0.0) for symbol in selected_symbols}
    total = sum(selected_values.values())
    if total <= 0:
        return {}
    return {symbol: value / total for symbol, value in selected_values.items()}


def portfolio_metrics() -> tuple[float, float, float | None, dict[str, float]]:
    total_value = 0.0
    weighted_beta = 0.0
    weighted_upside = 0.0
    valued_weight = 0.0
    sector_values: dict[str, float] = {}

    holdings = []
    market_values = portfolio_market_values()
    weights = portfolio_analysis_weights()

    for symbol, holding in st.session_state.portfolio.items():
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        shares = float(holding.get("shares") or 0)
        market_value = market_values.get(symbol, 0.0)
        total_value += market_value
        holdings.append((symbol, stock, shares, market_value))

    if not holdings:
        return 0.0, 0.0, None, {}

    for symbol, stock, _, market_value in holdings:
        weight = weights.get(symbol, 0.0)
        weighted_beta += float(stock["beta"] or 0) * weight
        sector_values[stock["industry"]] = sector_values.get(stock["industry"], 0) + market_value
        if stock["fair_price"] > 0 and stock["price"] > 0:
            upside = (stock["fair_price"] - stock["price"]) / stock["price"]
            weighted_upside += upside * weight
            valued_weight += weight

    valuation_score = (weighted_upside / valued_weight) * 100 if valued_weight > 0 else None
    return total_value, weighted_beta, valuation_score, sector_values


def render_sector_pie_chart(sector_values: dict[str, float]) -> None:
    data = pd.DataFrame(
        [{"Sector": sector, "Value": value} for sector, value in sector_values.items()]
    )
    if data.empty:
        return

    data["Weight"] = data["Value"] / data["Value"].sum()
    chart = (
        alt.Chart(data)
        .mark_arc(innerRadius=55, outerRadius=120)
        .encode(
            theta=alt.Theta("Value:Q"),
            color=alt.Color(
                "Sector:N",
                scale=alt.Scale(
                    range=[
                        "#3b82f6",
                        "#10b981",
                        "#f59e0b",
                        "#ef4444",
                        "#8b5cf6",
                        "#ec4899",
                        "#14b8a6",
                    ]
                ),
                legend=alt.Legend(labelColor="#31445f", titleColor="#102033"),
            ),
            tooltip=[
                alt.Tooltip("Sector:N"),
                alt.Tooltip("Value:Q", format="$,.2f"),
                alt.Tooltip("Weight:Q", format=".1%"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)


def portfolio_return_frame(symbols: list[str]) -> pd.DataFrame:
    return_series = []
    for symbol in symbols:
        history = load_price_history(symbol)
        if history.empty:
            continue
        series = history.set_index("Date")["Close"].pct_change().dropna()
        if len(series) >= 5:
            series.name = symbol
            return_series.append(series)

    if len(return_series) < 2:
        return pd.DataFrame()
    return pd.concat(return_series, axis=1).dropna(how="any")


def portfolio_weights(symbols: list[str]) -> dict[str, float]:
    return portfolio_analysis_weights(symbols)


def portfolio_risk_metrics() -> dict[str, Any] | None:
    symbols = [symbol for symbol in st.session_state.portfolio if symbol in st.session_state.stocks]
    returns = portfolio_return_frame(symbols)
    if returns.empty or len(returns.columns) < 2:
        return None

    weights_map = portfolio_weights(list(returns.columns))
    if not weights_map:
        return None

    weights = pd.Series(weights_map).reindex(returns.columns).fillna(0)
    if weights.sum() <= 0:
        return None
    weights = weights / weights.sum()

    portfolio_daily_returns = returns.mul(weights, axis=1).sum(axis=1)
    daily_vol = float(portfolio_daily_returns.std())
    annual_vol = daily_vol * (252 ** 0.5)
    annual_return = float(portfolio_daily_returns.mean()) * 252
    covariance = returns.cov()
    correlation = returns.corr()
    weighted_individual_daily_vol = float((returns.std() * weights).sum())
    diversification_benefit = max(0.0, weighted_individual_daily_vol - daily_vol)

    return {
        "returns": returns,
        "weights": weights,
        "covariance": covariance,
        "correlation": correlation,
        "daily_vol": daily_vol,
        "annual_vol": annual_vol,
        "annual_return": annual_return,
        "weighted_individual_daily_vol": weighted_individual_daily_vol,
        "diversification_benefit": diversification_benefit,
    }


def render_portfolio_risk_analysis() -> None:
    st.subheader("Portfolio Risk")
    st.caption(
        "Portfolio risk uses daily return covariance from available price history: portfolio variance = w' x covariance x w."
    )

    risk = portfolio_risk_metrics()
    if not risk:
        st.info("At least two portfolio stocks with available price history are needed for portfolio risk analysis.")
        return

    risk_color = "#10b981" if risk["annual_vol"] < 0.18 else "#f59e0b" if risk["annual_vol"] < 0.30 else "#ef4444"
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Annualized Portfolio Risk", f"{risk['annual_vol'] * 100:.1f}%", risk_color)
    with c2:
        metric_card("Expected Annual Return", f"{risk['annual_return'] * 100:+.1f}%", "#60a5fa")
    with c3:
        metric_card("Diversification Benefit", f"{risk['diversification_benefit'] * 100:.2f}% daily", "#10b981")

    st.info(
        "This risk is not a simple average of each stock's volatility. "
        "It falls when holdings have lower correlation, because gains and losses offset each other."
    )

    rows = []
    for symbol in risk["returns"].columns:
        stock = st.session_state.stocks.get(symbol, {})
        rows.append(
            {
                "Stock": symbol,
                "Weight": f"{risk['weights'][symbol] * 100:.1f}%",
                "Average Daily Return": f"{risk['returns'][symbol].mean() * 100:.3f}%",
                "Daily SD": f"{risk['returns'][symbol].std() * 100:.3f}%",
                "Beta": fmt_number(stock.get("beta")),
            }
        )
    st.dataframe(rows, hide_index=True, use_container_width=True)


def render_complementarity_analysis() -> None:
    symbols = [symbol for symbol in st.session_state.portfolio if symbol in st.session_state.stocks]
    returns = portfolio_return_frame(symbols)

    st.subheader("Stock Complementarity")
    st.caption(
        "This checks whether holdings move together or offset each other using daily return correlations from available price history."
    )

    if returns.empty or len(returns.columns) < 2:
        st.info(
            "At least two portfolio stocks with available price history are needed for complementarity analysis."
        )
        return

    corr = returns.corr()
    pair_values = []
    for i, first in enumerate(corr.columns):
        for second in corr.columns[i + 1 :]:
            pair_values.append((first, second, float(corr.loc[first, second])))

    avg_pair_corr = sum(item[2] for item in pair_values) / len(pair_values)
    complementarity_score = max(0, min(100, (1 - avg_pair_corr) * 100))
    best_pair = min(pair_values, key=lambda item: item[2])
    crowded_pair = max(pair_values, key=lambda item: item[2])

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Complementarity Score", f"{complementarity_score:.1f}", "#10b981" if complementarity_score >= 60 else "#f59e0b")
    with c2:
        metric_card("Average Pair Correlation", f"{avg_pair_corr:.3f}")
    with c3:
        metric_card("Best Offset Pair", f"{best_pair[0]} / {best_pair[1]}", "#60a5fa")

    st.info(
        f"Lowest co-movement pair: {best_pair[0]} and {best_pair[1]} ({best_pair[2]:.3f}). "
        f"Highest co-movement pair: {crowded_pair[0]} and {crowded_pair[1]} ({crowded_pair[2]:.3f}). "
        "Lower correlation usually means better diversification because holdings may offset each other more effectively."
    )

    rows = []
    for symbol in returns.columns:
        stock = st.session_state.stocks.get(symbol, {})
        peer_corr = corr[symbol].drop(symbol).mean()
        rows.append(
            {
                "Stock": symbol,
                "Avg Daily Return": f"{returns[symbol].mean() * 100:.3f}%",
                "Daily SD": f"{returns[symbol].std() * 100:.3f}%",
                "Avg Correlation": f"{peer_corr:.3f}",
                "Beta": fmt_number(stock.get("beta")),
                "Complement Role": "Diversifier" if peer_corr < 0.35 else "Core mover" if peer_corr < 0.65 else "Highly overlapping",
            }
        )

    st.dataframe(rows, hide_index=True, use_container_width=True)
    st.markdown("#### Correlation Matrix")
    st.caption(
        "Correlation close to +1 means two securities moved together historically. "
        "Correlation near 0 means weak co-movement. Negative correlation means they tended to move in opposite directions. "
        "This is useful for studying diversification, but it does not guarantee future risk reduction."
    )
    st.dataframe(corr.round(3), use_container_width=True)


def portfolio_valuation_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    weights = portfolio_analysis_weights()
    for symbol, holding in st.session_state.portfolio.items():
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        price = float(stock.get("price") or 0)
        fair_price = float(stock.get("fair_price") or 0)
        upside = ((fair_price - price) / price * 100) if price > 0 and fair_price > 0 else None
        weight = weights.get(symbol, 0.0)
        rows.append(
            {
                "Stock": symbol,
                "Name": stock.get("name", symbol),
                "Price": stock_money(stock, price),
                "Fair Value": stock_money(stock, fair_price) if fair_price > 0 else "N/A",
                "Upside / Downside": "N/A" if upside is None else f"{upside:+.1f}%",
                "Analysis Weight": f"{weight * 100:.1f}%",
                "Weighted Contribution": "N/A" if upside is None else f"{upside * weight:+.2f} pts",
                "Valuation": stock.get("valuation_status", "N/A"),
            }
        )
    return rows


def complementarity_summary() -> dict[str, Any] | None:
    symbols = [symbol for symbol in st.session_state.portfolio if symbol in st.session_state.stocks]
    returns = portfolio_return_frame(symbols)
    if returns.empty or len(returns.columns) < 2:
        return None

    corr = returns.corr()
    pair_values = []
    for i, first in enumerate(corr.columns):
        for second in corr.columns[i + 1 :]:
            pair_values.append((first, second, float(corr.loc[first, second])))
    if not pair_values:
        return None

    avg_pair_corr = sum(item[2] for item in pair_values) / len(pair_values)
    best_pair = min(pair_values, key=lambda item: item[2])
    crowded_pair = max(pair_values, key=lambda item: item[2])
    return {
        "average_pair_correlation": avg_pair_corr,
        "complementarity_score": max(0, min(100, (1 - avg_pair_corr) * 100)),
        "best_offset_pair": best_pair,
        "highest_co_movement_pair": crowded_pair,
        "correlation_matrix": corr,
    }


def portfolio_holdings_snapshot() -> list[dict[str, Any]]:
    usdkrw, _, _ = effective_usdkrw()
    base_currency = st.session_state.get("portfolio_base_currency", "USD")
    market_values = portfolio_market_values()
    total_value = sum(market_values.values())
    weights = portfolio_analysis_weights()
    holdings = []
    for symbol, holding in st.session_state.portfolio.items():
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        shares = float(holding.get("shares") or 0)
        native_value = float(stock.get("price") or 0) * shares
        base_value = convert_value(
            native_value,
            stock.get("currency", "USD"),
            base_currency,
            usdkrw,
        )
        holdings.append(
            {
                "symbol": symbol,
                "name": stock.get("name", symbol),
                "currency": stock.get("currency", "USD"),
                "shares": shares,
                "price": float(stock.get("price") or 0),
                "native_market_value": native_value,
                "base_market_value": base_value,
                "base_weight": base_value / total_value if total_value > 0 else 0,
                "analysis_weight": weights.get(symbol, 0.0),
                "valuation_status": stock.get("valuation_status", "N/A"),
            }
        )
    return holdings


def build_financial_snapshot(note: str, mood: str, next_action: str) -> dict[str, Any]:
    total_value, weighted_beta, valuation_score, _ = portfolio_metrics()
    usdkrw, fx_source, fx_date = effective_usdkrw()
    risk = portfolio_risk_metrics()
    comp = complementarity_summary()
    personal_result = st.session_state.get("last_personal_finance_result", {})

    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mood": mood,
        "note": note,
        "next_action": next_action,
        "base_currency": st.session_state.get("portfolio_base_currency", "USD"),
        "usdkrw": usdkrw,
        "fx_source": fx_source,
        "fx_date": fx_date,
        "portfolio": {
            "total_market_value": total_value,
            "weighted_beta": weighted_beta,
            "valuation_score": valuation_score,
            "weighting_mode": st.session_state.get("portfolio_weighting_mode", "Share-based"),
            "holdings": portfolio_holdings_snapshot(),
        },
        "risk": None
        if not risk
        else {
            "annualized_risk": risk["annual_vol"],
            "expected_annual_return": risk["annual_return"],
            "diversification_benefit_daily": risk["diversification_benefit"],
        },
        "complementarity": None
        if not comp
        else {
            "score": comp["complementarity_score"],
            "average_pair_correlation": comp["average_pair_correlation"],
            "best_offset_pair": list(comp["best_offset_pair"]),
            "highest_co_movement_pair": list(comp["highest_co_movement_pair"]),
        },
        "personal_finance": personal_result,
    }


def calculation_details_tab() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">Calculation Details</h1>
            <div class="hero-muted">Review the formulas, data inputs, assumptions, and interpretation logic behind LY-STScope.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "This section is designed for transparency. It explains how the app creates each analytical signal, "
        "so users can understand the assumptions instead of treating the output as a recommendation."
    )

    with st.expander("1. Stock Valuation Triangulation", expanded=True):
        st.markdown(
            """
            **Blended Fair Value** is the average of the valid valuation models available for each stock.

            - **Income Approach:** Gordon Growth Model when dividends are available; otherwise EPS capitalization.
            - **Asset Approach:** Graham Number = square root of `22.5 x EPS x Book Value per Share`.
            - **Market Approach:** `EPS x Peer Average P/E`.
            - **Valuation Status:** if current price is more than 5% above fair value, it is marked Overvalued; if more than 5% below, Undervalued.
            """
        )
        if st.session_state.stocks:
            symbols = list(st.session_state.stocks.keys())
            selected = st.selectbox("Inspect a loaded stock", symbols, key="calc_stock_symbol")
            stock = st.session_state.stocks[selected]
            tri = stock.get("triangulation", {})
            st.dataframe(
                [
                    {"Input": "Current Price", "Value": stock_money(stock, stock.get("price"))},
                    {"Input": "EPS", "Value": stock_money(stock, float(stock.get("eps") or 0))},
                    {"Input": "Book Value / Share", "Value": stock_money(stock, float(stock.get("book_value") or 0))},
                    {"Input": "Dividend / Share", "Value": stock_money(stock, float(stock.get("dividend") or 0))},
                    {"Input": "Beta", "Value": fmt_number(stock.get("beta"))},
                    {"Input": "Growth Rate", "Value": f"{float(stock.get('growth_rate') or 0) * 100:.1f}%"},
                    {"Input": "Peer Average P/E", "Value": fmt_number(stock.get("peer_average_pe"))},
                ],
                hide_index=True,
                use_container_width=True,
            )
            st.dataframe(
                [
                    {"Approach": "Income", "Model": tri.get("income_model", "N/A"), "Value": stock_money(stock, tri.get("income_value")) if tri.get("income_value") else "N/A"},
                    {"Approach": "Asset", "Model": "Graham Number", "Value": stock_money(stock, tri.get("asset_value")) if tri.get("asset_value") else "N/A"},
                    {"Approach": "Market", "Model": "Peer P/E", "Value": stock_money(stock, tri.get("market_value")) if tri.get("market_value") else "N/A"},
                    {"Approach": "Blended", "Model": f"{tri.get('valid_models', 0)} valid model(s)", "Value": stock_money(stock, stock.get("fair_price")) if stock.get("fair_price") else "N/A"},
                ],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.caption("Search stocks first to inspect live valuation inputs.")

    with st.expander("2. Portfolio Valuation Score", expanded=True):
        st.markdown(
            """
            The portfolio valuation score measures weighted upside or downside versus each holding's blended fair value.

            `Portfolio Valuation Score = sum(weight x ((Fair Value - Current Price) / Current Price)) / valued-stock weight`

            Positive means the portfolio appears undervalued under the app assumptions. Negative means the portfolio appears overvalued.
            """
        )
        rows = portfolio_valuation_rows()
        if rows:
            st.dataframe(rows, hide_index=True, use_container_width=True)
        else:
            st.caption("Add holdings to the portfolio to see contribution details.")

    with st.expander("3. Portfolio Risk and Diversification"):
        st.markdown(
            """
            Portfolio risk is calculated from daily return covariance.

            `Portfolio Variance = w' x Covariance Matrix x w`

            `Annualized Risk = Daily Portfolio Standard Deviation x sqrt(252)`

            The calculation uses the selected portfolio weighting mode. For mixed-currency portfolios, weights are calculated in the selected base currency, but daily price returns currently do not include FX return effects.
            """
        )
        risk = portfolio_risk_metrics()
        if risk:
            st.dataframe(
                pd.DataFrame(
                    [
                        {"Metric": "Daily Portfolio SD", "Value": f"{risk['daily_vol'] * 100:.3f}%"},
                        {"Metric": "Annualized Portfolio Risk", "Value": f"{risk['annual_vol'] * 100:.1f}%"},
                        {"Metric": "Expected Annual Return", "Value": f"{risk['annual_return'] * 100:+.1f}%"},
                        {"Metric": "Daily Diversification Benefit", "Value": f"{risk['diversification_benefit'] * 100:.3f}%"},
                    ]
                ),
                hide_index=True,
                use_container_width=True,
            )
            st.markdown("**Weight Vector**")
            st.dataframe(risk["weights"].rename("Weight").to_frame().style.format("{:.2%}"), use_container_width=True)
            st.markdown("**Covariance Matrix**")
            st.dataframe(risk["covariance"].round(6), use_container_width=True)
            st.markdown("**Correlation Matrix**")
            st.dataframe(risk["correlation"].round(3), use_container_width=True)
        else:
            st.caption("At least two portfolio holdings with price history are needed.")

    with st.expander("4. Personal Finance Health Score"):
        st.markdown(
            """
            Personal Finance connects investment readiness with life-level financial health.

            - **Net Worth:** total assets minus total debt.
            - **Monthly Surplus:** income minus fixed expenses, variable expenses, and debt payments.
            - **Emergency Fund:** cash savings divided by monthly living expenses.
            - **Savings Rate:** monthly surplus divided by monthly income.
            - **Debt-to-Income:** monthly debt payment divided by monthly income.
            - **Financial Health Score:** weighted score from liquidity, debt, savings, goal progress, and risk capacity.
            """
        )
        result = st.session_state.get("last_personal_finance_result")
        if result:
            st.dataframe(
                [
                    {"Metric": "Net Worth", "Value": fmt_money(float(result["net_worth"]))},
                    {"Metric": "Monthly Surplus", "Value": fmt_money(float(result["monthly_surplus"]))},
                    {"Metric": "Emergency Fund", "Value": f"{float(result['emergency_months']):.1f} months"},
                    {"Metric": "Savings Rate", "Value": f"{float(result['savings_rate']) * 100:.1f}%"},
                    {"Metric": "Debt-to-Income", "Value": f"{float(result['debt_to_income']) * 100:.1f}%"},
                    {"Metric": "Financial Health Score", "Value": f"{float(result['financial_health_score']):.1f}/100"},
                ],
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.caption("Open the Personal Finance tab first to calculate a personal finance snapshot.")


def financial_diary_tab() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">Financial Diary</h1>
            <div class="hero-muted">Save snapshots of your financial life, portfolio structure, risk signals, and personal notes over time.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Diary entries are stored in the current Streamlit session unless downloaded. Avoid entering sensitive personal information in a public or shared browser."
    )

    mood = st.selectbox(
        "Today's financial feeling",
        ["Calm", "Curious", "Cautious", "Confident", "Concerned", "Planning"],
        key="diary_mood",
    )
    note = st.text_area(
        "Diary note",
        placeholder="Example: I reviewed my portfolio today and noticed that growth stocks still dominate my risk profile.",
        height=130,
        key="diary_note",
    )
    next_action = st.text_input(
        "Next action",
        placeholder="Example: Review cash reserve and reduce concentration risk next week.",
        key="diary_next_action",
    )

    save_col, download_col = st.columns([1, 2])
    with save_col:
        if st.button("Save Financial Snapshot", use_container_width=True):
            snapshot = build_financial_snapshot(note.strip(), mood, next_action.strip())
            st.session_state.financial_diary.append(snapshot)
            st.success("Snapshot saved to your Financial Diary for this session.")

    diary_json = json.dumps(st.session_state.financial_diary, indent=2, ensure_ascii=False)
    with download_col:
        st.download_button(
            "Download Diary JSON",
            data=diary_json,
            file_name=f"ly_stscope_financial_diary_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
            disabled=not bool(st.session_state.financial_diary),
        )

    uploaded = st.file_uploader("Restore diary JSON", type=["json"], key="diary_restore")
    if uploaded is not None:
        try:
            restored = json.loads(uploaded.getvalue().decode("utf-8"))
            if isinstance(restored, list):
                st.session_state.financial_diary = restored
                st.success("Diary restored for this session.")
            else:
                st.warning("The uploaded diary file must contain a list of entries.")
        except Exception as exc:
            st.warning(f"Could not restore diary file: {exc}")

    st.subheader("Saved Entries")
    if not st.session_state.financial_diary:
        st.info("No diary entries yet. Save a snapshot after reviewing your portfolio or personal finance status.")
        return

    summary_rows = []
    for idx, entry in enumerate(st.session_state.financial_diary, start=1):
        portfolio = entry.get("portfolio", {})
        personal = entry.get("personal_finance") or {}
        base_currency = entry.get("base_currency", "USD")
        summary_rows.append(
            {
                "#": idx,
                "Time": entry.get("time"),
                "Mood": entry.get("mood"),
                "Portfolio Value": fmt_money(portfolio.get("total_market_value"), base_currency),
                "Valuation Score": "N/A"
                if portfolio.get("valuation_score") is None
                else f"{float(portfolio.get('valuation_score')):+.1f}%",
                "Financial Health": "N/A"
                if not personal
                else f"{float(personal.get('financial_health_score', 0)):.1f}/100",
            }
        )
    st.dataframe(summary_rows, hide_index=True, use_container_width=True)

    for idx, entry in reversed(list(enumerate(st.session_state.financial_diary, start=1))):
        with st.expander(f"Entry {idx}: {entry.get('time')} - {entry.get('mood')}", expanded=False):
            st.write(f"**Note:** {entry.get('note') or 'No note'}")
            st.write(f"**Next Action:** {entry.get('next_action') or 'No action recorded'}")
            portfolio = entry.get("portfolio", {})
            base_currency = entry.get("base_currency", "USD")
            entry_valuation = portfolio.get("valuation_score")
            valuation_text = "N/A" if entry_valuation is None else f"{float(entry_valuation):+.1f}%"
            st.write(
                f"**Portfolio:** {fmt_money(portfolio.get('total_market_value'), base_currency)} | "
                f"Beta {fmt_number(portfolio.get('weighted_beta'))} | "
                f"Valuation Score {valuation_text}"
            )
            holdings = portfolio.get("holdings") or []
            if holdings:
                st.dataframe(
                    [
                        {
                            "Stock": f"{item['symbol']} - {item['name']}",
                            "Currency": item["currency"],
                            "Shares": item["shares"],
                            "Base Weight": f"{float(item['base_weight']) * 100:.1f}%",
                            "Valuation": item["valuation_status"],
                        }
                        for item in holdings
                    ],
                    hide_index=True,
                    use_container_width=True,
                )


def render_portfolio_charts() -> None:
    symbols = [symbol for symbol in st.session_state.portfolio if symbol in st.session_state.stocks]
    st.subheader("Portfolio Charts")
    st.caption("Select a holding to review its TradingView chart without leaving the Portfolio tab.")

    if not symbols:
        st.info("Add stocks to your portfolio to view holding charts.")
        return

    labels = {
        symbol: f"{symbol} - {st.session_state.stocks[symbol]['name']}"
        for symbol in symbols
    }
    selected = st.selectbox(
        "Select portfolio holding",
        options=symbols,
        format_func=lambda symbol: labels[symbol],
        key="portfolio_chart_symbol",
    )
    render_tradingview_chart(selected)


def portfolio_tab() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">Investment Portfolio</h1>
            <div class="hero-muted">Track weighted risk, return, and valuation across your holdings</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fx_col1, fx_col2, fx_col3 = st.columns(3)
    with fx_col1:
        st.selectbox(
            "Portfolio base currency",
            ["USD", "KRW"],
            key="portfolio_base_currency",
            help="Portfolio totals and weights are calculated after converting each holding into this currency.",
        )
    with fx_col2:
        st.checkbox(
            "Use live USD/KRW",
            key="use_live_fx",
            help="Uses Yahoo Finance KRW=X when available. Manual rate is used as fallback.",
        )
    with fx_col3:
        st.number_input(
            "Manual USD/KRW rate",
            min_value=1.0,
            value=float(st.session_state.get("manual_usdkrw", 1350.0)),
            step=1.0,
            key="manual_usdkrw",
        )

    usdkrw, fx_source, fx_date = effective_usdkrw()
    st.caption(
        f"FX setting: 1 USD = ₩{usdkrw:,.2f} | Source: {fx_source} | Date: {fx_date}. "
        "Portfolio weights use converted base-currency values."
    )

    st.radio(
        "Portfolio weighting mode",
        ["Share-based", "Equal-weighted"],
        horizontal=True,
        key="portfolio_weighting_mode",
        help=(
            "Share-based uses shares x current price. Equal-weighted assigns the same analysis weight "
            "to each holding, which is useful for classroom portfolio analysis."
        ),
    )
    if st.session_state.portfolio_weighting_mode == "Equal-weighted":
        st.info(
            "Equal weighting assigns the same analysis weight to each selected security. "
            "This is useful for classroom analysis and simple backtesting concepts, but maintaining "
            "equal weights in practice requires periodic rebalancing. Trading costs and taxes may reduce actual performance."
        )
    else:
        st.caption(
            "Share-based weighting uses each holding's current market value. A high-priced stock can dominate the portfolio if the share count is similar across holdings."
        )

    total_value, weighted_beta, valuation_score, sector_values = portfolio_metrics()
    c1, c2, c3 = st.columns(3)
    score_text = "N/A" if valuation_score is None else f"{valuation_score:+.1f}%"
    score_color = "#94a3b8"
    if valuation_score is not None:
        score_color = "#10b981" if valuation_score > 5 else "#ef4444" if valuation_score < -5 else "#f59e0b"
    with c1:
        metric_card("Total Market Value", fmt_money(total_value, st.session_state.portfolio_base_currency))
    with c2:
        metric_card("Weighted Beta", fmt_number(weighted_beta))
    with c3:
        metric_card("Portfolio Valuation Score", score_text, score_color)

    st.info(
        "Valuation Score estimates the portfolio's weighted upside or downside versus each stock's blended fair value. "
        "Formula: sum(weight x ((Fair Value - Current Price) / Current Price)) / valued-stock weight. "
        "Positive means undervalued; negative means overvalued. Holdings without valid fair value are excluded. "
        f"Current analysis mode: {st.session_state.portfolio_weighting_mode}."
    )

    if not st.session_state.portfolio:
        st.info("No stocks in your portfolio yet. Add them from the search results.")
        return

    native_breakdown = portfolio_currency_breakdown()
    if len(native_breakdown) > 1:
        st.info(
            "This portfolio includes multiple currencies. Native market values are shown by currency, "
            f"and portfolio weights are calculated in {st.session_state.portfolio_base_currency} using the USD/KRW FX rate above."
        )
    if native_breakdown:
        st.caption(
            "Native currency breakdown: "
            + " | ".join(fmt_money(value, currency) for currency, value in sorted(native_breakdown.items()))
        )

    current_holdings = []
    for symbol, holding in list(st.session_state.portfolio.items()):
        stock = st.session_state.stocks.get(symbol)
        if not stock:
            continue
        shares = st.number_input(
            f"{symbol} shares",
            min_value=0.0,
            value=float(holding.get("shares") or 0),
            step=1.0,
            key=f"shares_{symbol}",
        )
        st.session_state.portfolio[symbol]["shares"] = shares
        native_value = float(stock["price"]) * shares
        base_value = convert_value(
            native_value,
            stock.get("currency", "USD"),
            st.session_state.portfolio_base_currency,
            usdkrw,
        )
        current_holdings.append((symbol, stock, shares, native_value, base_value))

    rows = []
    current_total_value = sum(item[4] for item in current_holdings)
    analysis_weights = portfolio_analysis_weights()
    for symbol, stock, shares, native_value, base_value in current_holdings:
        currency = stock.get("currency", "USD")
        weight = base_value / current_total_value * 100 if current_total_value else 0
        analysis_weight = analysis_weights.get(symbol, 0.0) * 100
        rows.append(
            {
                "Stock": f"{symbol} - {stock['name']}",
                "Currency": currency,
                "Price": stock_money(stock, stock["price"]),
                "Shares": shares,
                "Native Market Value": fmt_money(native_value, currency),
                f"{st.session_state.portfolio_base_currency} Market Value": fmt_money(base_value, st.session_state.portfolio_base_currency),
                "Base Weight": f"{weight:.1f}%",
                "Analysis Weight": f"{analysis_weight:.1f}%",
            }
        )

    st.dataframe(rows, hide_index=True, use_container_width=True)
    remove_cols = st.columns(min(4, len(st.session_state.portfolio)))
    for idx, symbol in enumerate(list(st.session_state.portfolio.keys())):
        remove_cols[idx % len(remove_cols)].button(
            f"Remove {symbol}",
            key=f"remove_portfolio_{symbol}",
            on_click=toggle_portfolio,
            args=(symbol,),
        )

    if sector_values:
        st.subheader("Sector Allocation")
        render_sector_pie_chart(sector_values)

    st.subheader("Backtesting Concept")
    st.info(
        "A simple educational backtest can start with an equal-weighted portfolio, as used in class. "
        "A full professional backtest also needs rebalancing frequency, transaction costs, taxes, benchmark selection, "
        "and survivorship-bias controls. LY-STScope currently focuses on educational portfolio analytics rather than full performance backtesting."
    )
    st.caption(
        "Reference suggested for advanced analysis: Portfolio Visualizer. LY-STScope can use it as a methodological benchmark while keeping this app focused on learning and interpretation."
    )

    render_portfolio_charts()
    render_portfolio_risk_analysis()
    render_complementarity_analysis()


def settings_tab() -> None:
    st.header("Real-Time Financial API Settings")
    st.success("FINNHUB_API_KEY is configured in Streamlit Secrets." if FINNHUB_API_KEY else "FINNHUB_API_KEY is missing.")
    st.write(
        """
        This version keeps the Finnhub API key on the Streamlit server side.
        External users do not need to enter a key, and the token is not stored in their browser.
        """
    )
    st.subheader("Macroeconomic Variables")
    st.write(f"Risk-Free Rate: **{RISK_FREE_RATE * 100:.2f}%**")
    st.write(f"Equity Risk Premium: **{EQUITY_RISK_PREMIUM * 100:.2f}%**")


def guide_tab() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <h1 style="margin:0 0 8px;">LY-STScope User Guide</h1>
            <div class="hero-muted">A practical in-app guide based on the English PDF user guide.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if GUIDE_PDF_PATH.exists():
        st.download_button(
            "Download PDF User Guide",
            data=GUIDE_PDF_PATH.read_bytes(),
            file_name="LY-STScope_User_Guide.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.info("Upload LY-STScope_User_Guide.pdf to the repository to enable PDF download.")

    st.subheader("1. Search and Explore Stocks")
    guide_image("01-search-dashboard.png", "Search dashboard")
    st.write(
        """
        Use the Search tab as the main workspace. Enter a stock ticker, then review
        the stock card for current price, market cap, PER, and valuation status.
        """
    )
    st.markdown(
        """
        - Use valuation filters to focus on Undervalued, Fair Value, or Overvalued stocks.
        - Use **Compare** to add up to three stocks to side-by-side comparison.
        - Use **Add to Portfolio** to include a holding in portfolio tracking.
        - Click a stock card to open the selected stock's TradingView price chart, key statistics, and valuation breakdown.
        """
    )

    st.subheader("2. Compare Selected Stocks")
    guide_image("02-compare.png", "Side-by-side comparison")
    st.write(
        "The Compare tab shows selected stocks side by side across price, daily change, market cap, PER, dividend yield, beta, EPS, fair value, and valuation status."
    )

    st.subheader("3. Track Your Portfolio")
    guide_image("03-portfolio.png", "Portfolio dashboard")
    st.write(
        """
        The Portfolio tab tracks current holdings, share counts, market value, portfolio weight,
        weighted beta, valuation score, sector allocation, portfolio risk, and stock complementarity.
        """
    )
    st.markdown(
        """
        - Sector Allocation is shown as a donut-style pie chart.
        - Share-based mode uses shares x current price, so high-priced stocks can dominate if share counts are similar.
        - Equal-weighted mode assigns the same analysis weight to each holding, matching a simple classroom portfolio method.
        - Portfolio Risk uses the selected analysis weights plus daily return covariance.
        - Stock Complementarity shows whether holdings move together or offset each other.
        """
    )

    st.subheader("4. Portfolio Valuation Score")
    st.info(
        "Score = sum(weight x ((Fair Value - Current Price) / Current Price)) / valued-stock weight"
    )
    st.markdown(
        """
        - A positive score means the valued part of the portfolio appears undervalued overall.
        - A negative score means it appears overvalued overall.
        - Holdings without a valid fair value are excluded from this score.
        - The score follows the selected portfolio weighting mode: Share-based or Equal-weighted.
        - The score is an analytical estimate, not a guaranteed return forecast.
        """
    )

    st.subheader("5. Portfolio Risk")
    st.write(
        """
        Portfolio risk is calculated from each holding's weight and the covariance of daily stock returns.
        This follows the portfolio risk concept from CAPM: diversification works when assets do not move perfectly together.
        """
    )
    st.info("Portfolio variance = w' x covariance matrix x w")
    st.markdown(
        """
        - Annualized Portfolio Risk shows the portfolio's estimated annual volatility.
        - Diversification Benefit compares weighted individual volatility with actual portfolio volatility.
        - Lower correlation between holdings generally improves risk reduction.
        - Equal-weighted analysis is useful for learning, but keeping equal weights in real portfolios requires rebalancing.
        - Rebalancing can create transaction costs and taxes, so LY-STScope presents this as educational analysis rather than a full professional backtest.
        """
    )

    st.subheader("6. Educational Scope")
    st.write(
        """
        LY-STScope is designed to connect finance theory with real market examples. It is not an
        investment recommendation service. The current focus is stock analysis, valuation
        triangulation, CAPM, portfolio variance, covariance, diversification, and correlation.
        Sector-specialized tools such as REIT analysis can be explored as a separate future project.
        """
    )

    st.subheader("7. Stock Detail Page")
    guide_image("04-stock-detail.png", "Stock detail screen")
    st.write(
        "Click a stock card to review the TradingView price chart, current price, fair value, CAPM required return, key statistics, and valuation triangulation."
    )

    st.subheader("8. Calculation Details")
    st.write(
        """
        The Calculation Details tab explains the formulas, assumptions, and data inputs behind valuation,
        portfolio valuation score, portfolio risk, diversification, and personal finance health.
        Use this tab to understand why a result appears, not just what the result says.
        """
    )

    st.subheader("9. Financial Diary")
    st.write(
        """
        The Financial Diary tab saves a point-in-time snapshot of portfolio structure, risk signals,
        personal finance results, and the user's own reflection. Diary data is held in the current
        session unless downloaded as a JSON file.
        """
    )

    st.subheader("10. API and Macro Settings")
    guide_image("05-settings-modal.png", "Settings screen")
    st.write(
        """
        The Finnhub API key is stored in Streamlit Secrets and used only on the server side.
        External users do not need to enter a key, and the token is not stored in their browser.
        """
    )


def remove_sidebar_item(collection: str, symbol: str, key: str) -> None:
    if collection == "compare" and symbol in st.session_state.compare:
        st.session_state.compare.remove(symbol)
    if collection == "portfolio" and symbol in st.session_state.portfolio:
        del st.session_state.portfolio[symbol]
    if key in st.session_state:
        del st.session_state[key]
    st.rerun()


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## LY-STScope")
        st.caption("Open or close this sidebar with the arrow in the upper-left corner.")

        st.markdown("### Ver.2 Module")
        st.caption("Use the REIT Analysis tab in the main screen.")

        st.markdown("### Compare List")
        if st.session_state.compare:
            for symbol in list(st.session_state.compare):
                stock = st.session_state.stocks.get(symbol, {"name": symbol})
                key = f"sidebar_compare_{symbol}"
                checked = st.checkbox(
                    f"{symbol} - {stock.get('name', symbol)}",
                    value=True,
                    key=key,
                )
                if not checked:
                    remove_sidebar_item("compare", symbol, key)
        else:
            st.caption("No stocks selected for comparison.")

        st.markdown("### Portfolio List")
        if st.session_state.portfolio:
            for symbol in list(st.session_state.portfolio.keys()):
                stock = st.session_state.stocks.get(symbol, {"name": symbol})
                shares = st.session_state.portfolio.get(symbol, {}).get("shares", 0)
                key = f"sidebar_portfolio_{symbol}"
                checked = st.checkbox(
                    f"{symbol} - {stock.get('name', symbol)} ({shares:g} shares)",
                    value=True,
                    key=key,
                )
                if not checked:
                    remove_sidebar_item("portfolio", symbol, key)
        else:
            st.caption("No stocks in portfolio.")

        st.divider()
        st.markdown("### Developer")
        st.write(f"**{DEVELOPER_NAME}**")
        st.write(f"Email: `{DEVELOPER_EMAIL}`")

        comment = st.text_area(
            "Send a comment",
            placeholder="Write feedback or an issue to review later.",
            height=110,
            key="sidebar_comment_text",
        )
        if st.button("Save Comment", use_container_width=True):
            clean_comment = comment.strip()
            if clean_comment:
                st.session_state.comments.append(
                    {
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "comment": clean_comment,
                    }
                )
                st.success("Comment saved in this session.")
                st.rerun()
            else:
                st.warning("Please enter a comment first.")

        if st.session_state.comments:
            with st.expander("Saved comments", expanded=False):
                for item in reversed(st.session_state.comments[-5:]):
                    st.caption(f"{item['time']} - {item['comment']}")


def render_footer() -> None:
    st.markdown(
        """
        <div class="app-footer">
            <b>LY-STScope</b> is provided for educational and informational use only and does not constitute
            financial, investment, legal, tax, or professional advice. Market data and charts may be provided
            by third-party services such as Finnhub, TradingView, and Yahoo Finance, subject to their own terms.
            All trademarks, company names, and ticker symbols remain the property of their respective owners.
            This interface uses original CSS/HTML design elements and does not claim ownership of third-party data,
            logos, or trademarks.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_life_entry_screen() -> None:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] { display: none; }
        div[data-testid="collapsedControl"] { display: none; }
        .block-container { max-width: 1480px; padding-top: 1.2rem; }
        </style>
        <div class="life-entry-wrap">
            <div class="life-entry">
                <div class="life-entry-grid">
                    <div>
                        <div class="life-kicker">Personal Life & Financial Intelligence</div>
                        <h1 class="life-title">Design your <span>life</span>, not only your portfolio.</h1>
                        <div class="life-copy">
                            LY-STScope connects income, spending, savings, investments, real estate exposure,
                            risk, and life goals into one educational dashboard. It helps users understand where
                            they stand today and what they may need to protect, improve, and plan next.
                        </div>
                        <div class="life-pill-row">
                            <div class="life-pill">Income & Spending</div>
                            <div class="life-pill">Portfolio Risk</div>
                            <div class="life-pill">Real Estate Lens</div>
                            <div class="life-pill">Life Goals</div>
                            <div class="life-pill">Financial Diary</div>
                        </div>
                    </div>
                    <div class="life-map" aria-label="Life design map">
                        <div class="life-orbit"></div>
                        <div class="life-orbit two"></div>
                        <div class="life-core">Life<br>Design<br>Dashboard</div>
                        <div class="life-node income">Income<br>Cash Flow</div>
                        <div class="life-node saving">Savings<br>Liquidity</div>
                        <div class="life-node risk">Risk<br>Protection</div>
                        <div class="life-node assets">Assets<br>Portfolio</div>
                        <div class="life-node goals">Goals<br>Planning</div>
                        <div class="life-node diary">Diary<br>Reflection</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1.1, 1])
    with c2:
        if st.button("Enter LY-STScope Life Dashboard", type="primary", use_container_width=True):
            st.session_state.life_entry_complete = True
            st.rerun()
        st.caption(
            "Educational and informational use only. LY-STScope is not financial, investment, legal, or tax advice."
        )


init_state()
if not st.session_state.life_entry_complete:
    render_life_entry_screen()
    st.stop()

render_sidebar()

st.markdown(
    """
    <div class="brand-header">
        <div class="brand-mark">
            <div class="brand-icon" aria-hidden="true"></div>
            <div>
                <div class="brand-name">LY-ST<span class="scope-accent">Scope</span></div>
                <div class="brand-subtitle">V 3 5 . 0&nbsp;&nbsp; M A J E S T I C&nbsp;&nbsp; N A V I G A T I O N</div>
            </div>
        </div>
        <div class="brand-badge">Server-side Finnhub data</div>
    </div>
    """,
    unsafe_allow_html=True,
)

sync_selected_detail_from_query()

(
    tab_search,
    tab_compare,
    tab_portfolio,
    tab_reit,
    tab_personal,
    tab_calculation,
    tab_diary,
    tab_settings,
    tab_guide,
) = st.tabs(
    [
        "Search",
        "Compare",
        "Portfolio",
        "REIT Analysis",
        "Personal Finance",
        "Calculation Details",
        "Financial Diary",
        "Settings",
        "User Guide",
    ]
)

with tab_search:
    search_tab()

with tab_compare:
    compare_tab()

with tab_portfolio:
    portfolio_tab()

with tab_reit:
    from reit_analysis_module import main as render_reit_analysis

    render_reit_analysis(include_sidebar=False)

with tab_personal:
    from personal_finance_module import render_personal_finance

    render_personal_finance()

with tab_calculation:
    calculation_details_tab()

with tab_diary:
    financial_diary_tab()

with tab_settings:
    settings_tab()

with tab_guide:
    guide_tab()

render_footer()

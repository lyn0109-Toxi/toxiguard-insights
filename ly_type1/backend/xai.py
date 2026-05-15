"""
backend/xai.py
Explainable AI (SHAP) module for LY‑Type1.

Returns feature‑importance values for a given SMILES string.
Falls back to a simple gradient‑free approximation when SHAP
is not installed.
"""

from __future__ import annotations
from .models import _smiles_features, _get_model, _ALERTS

# Feature names corresponding to _smiles_features()
FEATURE_NAMES = [
    "Length",
    "C count",
    "N count",
    "O count",
    "S count",
    "Double bonds",
    "Triple bonds",
    "Branching",
    "Ring hints",
    "Alert count",
    "Aromatic flag",
    "Charged atom flag",
]


def shap_explain(smiles: str) -> list[dict]:
    """Return per‑feature importance for the toxicity prediction.

    Returns
    -------
    list of dicts  with keys: feature, value, shap_value
    """
    feats = _smiles_features(smiles)
    model = _get_model()

    shap_values: list[float]

    if model is not None:
        try:
            import shap
            import numpy as np
            explainer = shap.TreeExplainer(model)
            sv = explainer.shap_values(np.array(feats).reshape(1, -1))
            # sv[1] = SHAP values for the positive class (mutagenic)
            shap_values = [round(float(v), 4) for v in sv[1][0]]
        except Exception:
            shap_values = _fallback_importance(feats, model)
    else:
        # Heuristic: feature value × hard‑coded weight
        weights = [0.1, 0.05, 0.15, 0.1, 0.1, 0.1, 0.05, 0.05, 0.1, 0.25, 0.1, 0.15]
        shap_values = [round(f * w, 4) for f, w in zip(feats, weights)]

    return [
        {"feature": FEATURE_NAMES[i], "value": feats[i], "shap_value": shap_values[i]}
        for i in range(len(FEATURE_NAMES))
    ]


def _fallback_importance(feats, model) -> list[float]:
    """Use built‑in feature importances when SHAP is unavailable."""
    import numpy as np
    try:
        fi = model.feature_importances_
        # weight by feature value for directionality
        return [round(float(fi[i] * feats[i]), 4) for i in range(len(feats))]
    except Exception:
        return [round(f * 0.1, 4) for f in feats]

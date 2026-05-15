"""
backend/models.py
QSAR toxicity prediction module for LY‑Type1.

Implements a lightweight RDKit‑free fingerprint approach using
simple Morgan‑like bit counts derived from the SMILES string.
Falls back to a deterministic heuristic when scikit‑learn is
unavailable so the UI always returns a result.
"""

from __future__ import annotations
import hashlib
import re


# ──────────────────────────────────────────────────────────────────────
# Feature extraction (no RDKit required)
# ──────────────────────────────────────────────────────────────────────

# Structural alert patterns (simplified ICH M7 / Ames‑positive alerts)
_ALERTS = [
    r"N=N",             # azo group
    r"\[N\+\]",         # quaternary nitrogen / nitro
    r"N\(=O\)",         # N‑oxide / nitro
    r"C=O",             # aldehyde / ketone
    r"Cl|Br|I",         # halogen
    r"n",               # aromatic nitrogen (heteroaromatic)
    r"S\(=O\)",         # sulfoxide/sulfone
    r"\[NH\]",          # secondary amine
    r"CC#N",            # nitrile
    r"O=C\(O\)",        # carboxylic acid
]


def _smiles_features(smiles: str) -> list[float]:
    """Return a simple 12‑element feature vector from a SMILES string."""
    s = smiles.strip()
    feats = [
        len(s),                                # total length
        s.count("C"),                          # carbon count
        s.count("N"),                          # nitrogen count
        s.count("O"),                          # oxygen count
        s.count("S"),                          # sulfur count
        s.count("="),                          # double bonds
        s.count("#"),                          # triple bonds
        s.count("("),                          # branching
        s.count("1") + s.count("2"),           # ring hints
        sum(1 for p in _ALERTS if re.search(p, s)),  # alert count
        int(bool(re.search(r"[a-z]", s))),    # aromaticity flag
        int(bool(re.search(r"\[", s))),        # charged atom flag
    ]
    # Normalise to [0,1]
    max_vals = [80, 40, 10, 10, 5, 10, 5, 10, 6, len(_ALERTS), 1, 1]
    return [min(f / m, 1.0) for f, m in zip(feats, max_vals)]


# ──────────────────────────────────────────────────────────────────────
# Model training / loading
# ──────────────────────────────────────────────────────────────────────

_MODEL = None   # cached trained model


def _get_model():
    """Return a trained RandomForest if scikit‑learn is available."""
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    try:
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np

        # ── Synthetic training data (representative ICH M7 patterns) ─
        # Format: (SMILES, label)  — 1 = mutagenic concern, 0 = clean
        training = [
            # Mutagenic / concern
            ("c1ccc(N=Nc2ccccc2)cc1", 1),        # azo dye
            ("O=Cc1ccccc1", 1),                    # benzaldehyde
            ("CCN(CC)c1ccc(N=O)cc1", 1),           # N‑nitroso
            ("ClCCCl", 1),                         # dichloroethane
            ("BrCCBr", 1),                         # dibromoethane
            ("c1ccc2[nH]ccc2c1", 1),               # indole
            ("N=Cc1ccccc1", 1),                    # schiff base
            ("O=C(O)c1ccccc1N", 1),                # anthranilic acid
            # Non‑mutagenic / clean
            ("c1ccccc1", 0),                       # benzene
            ("CC(C)O", 0),                         # isopropanol
            ("OCC", 0),                            # ethanol
            ("CC(=O)Oc1ccccc1C(=O)O", 0),          # aspirin
            ("CC(C)Cc1ccc(C(C)C(=O)O)cc1", 0),    # ibuprofen
            ("CCOC(=O)c1ccccc1", 0),               # ethyl benzoate
            ("CC(=O)Nc1ccc(O)cc1", 0),             # paracetamol
            ("OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O", 0),  # glucose
        ]

        X = np.array([_smiles_features(s) for s, _ in training])
        y = np.array([label for _, label in training])

        clf = RandomForestClassifier(
            n_estimators=50, random_state=42, max_depth=6
        )
        clf.fit(X, y)
        _MODEL = clf
        return _MODEL
    except ImportError:
        return None


# ──────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────

def predict_toxicity(smiles: str) -> tuple[float, str]:
    """Predict mutagenicity / ADMET risk for a SMILES string.

    Returns
    -------
    (risk_score, label)
        risk_score : float  in [0, 1]
        label      : str    'Low' | 'Moderate' | 'High'
    """
    feats = _smiles_features(smiles)
    model = _get_model()

    if model is not None:
        import numpy as np
        proba = model.predict_proba(np.array(feats).reshape(1, -1))[0]
        score = float(proba[1])
    else:
        # Deterministic heuristic when sklearn is unavailable
        # Uses alert count and halogen presence as a proxy
        alert_count = sum(
            1 for p in _ALERTS if re.search(p, smiles)
        )
        score = min(alert_count / len(_ALERTS), 1.0)

    # Derive label
    if score < 0.33:
        label = "Low"
    elif score < 0.66:
        label = "Moderate"
    else:
        label = "High"

    return round(score, 4), label

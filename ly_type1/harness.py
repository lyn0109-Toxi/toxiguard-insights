# ly_type1 Harness – entry point for local development

"""\
This script provides a lightweight harness to launch the ly_type1 FastAPI backend
with convenient hot‑reload during development. It also offers a simple CLI to
run unit‑test stubs for the OCR, QSAR and XAI modules.
\
Usage::

    python -m ly_type1.harness          # start the API server
    python -m ly_type1.harness test      # execute basic sanity checks
\"""

import argparse
import subprocess
import sys
from pathlib import Path

# The FastAPI application lives in ly_type1/backend/app.py
APP_PATH = Path(__file__).parent / "backend" / "app.py"

def run_server():
    """Start the FastAPI server with uvicorn in development mode."""
    # uvicorn is a runtime dependency – we invoke it via subprocess to avoid
    # import‑time overhead when the harness is used only for tests.
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload",
    ]
    # Change working directory to the folder that contains app.py
    cwd = str(APP_PATH.parent)
    print(f"⚙️  Starting ly_type1 backend (FastAPI) at http://localhost:8000 …")
    subprocess.run(cmd, cwd=cwd, check=True)

def run_tests():
    """Run a minimal sanity‑check suite for the core modules.

    The tests are deliberately lightweight – they only verify that the import
    path works and that each module returns a non‑empty result for a simple
    example input.
    """
    from importlib import import_module
    failures = []

    # 1️⃣ OCR – use a tiny in‑memory PNG (1×1 white pixel) as dummy input
    try:
        ocr = import_module("ly_type1.backend.ocr")
        dummy_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0bIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xc9\x9f\x00\x00\x00\x00IEND\xaeB`\x82"
        res = ocr.process_document(dummy_png, "image/png")
        if not isinstance(res, dict) or "text" not in res:
            failures.append("ocr.process_document output invalid")
    except Exception as e:
        failures.append(f"ocr import/run error: {e}")

    # 2️⃣ QSAR model – simple benzene SMILES
    try:
        models = import_module("ly_type1.backend.models")
        score, label = models.predict_toxicity("c1ccccc1")
        if not (0 <= score <= 1):
            failures.append("models.predict_toxicity score out of range")
    except Exception as e:
        failures.append(f"models import/run error: {e}")

    # 3️⃣ XAI – SHAP explanation for the same SMILES
    try:
        xai = import_module("ly_type1.backend.xai")
        shap_vals = xai.shap_explain("c1ccccc1")
        if not isinstance(shap_vals, list):
            failures.append("xai.shap_explain output invalid")
    except Exception as e:
        failures.append(f"xai import/run error: {e}")

    if failures:
        print("❌  Tests failed:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("✅  All sanity checks passed.")

def main():
    parser = argparse.ArgumentParser(description="ly_type1 development harness")
    parser.add_argument(
        "action",
        nargs="?",
        default="run",
        choices=["run", "test"],
        help="run – start the API server; test – execute sanity checks",
    )
    args = parser.parse_args()
    if args.action == "run":
        run_server()
    else:
        run_tests()

if __name__ == "__main__":
    main()

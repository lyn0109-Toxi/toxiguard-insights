\"\"\"PharmaScope™ Stock Valuation Engine - Entry Point\"\"\"
from pathlib import Path
import sys

# Ensure the root directory is in the path
APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# Import the main application logic
import pharmascope_app

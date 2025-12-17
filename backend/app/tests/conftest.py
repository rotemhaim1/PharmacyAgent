from __future__ import annotations

import sys
from pathlib import Path

# Ensure `backend/` is on sys.path so `import app...` works regardless of how pytest picks rootdir.
BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))



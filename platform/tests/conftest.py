"""Use the same source package in local and Linux CI test runs."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "platform/src"))
sys.path.insert(0, str(ROOT / "platform/scripts"))

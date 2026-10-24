"""BookLeaf Author Support & Communication Portal - Backend Application."""

import sys
from pathlib import Path

# Ensure project root is in sys.path so 'backend.app...' imports always resolve
_backend_dir = Path(__file__).resolve().parent.parent
_project_root = _backend_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

__version__ = "1.0.0"

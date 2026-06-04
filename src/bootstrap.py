"""Make ``src`` importable and initialise the database.

Every Streamlit page imports this first so that `from core...`, `from db...`,
etc. resolve no matter where Streamlit launches the script from.
"""
import os
import sys

_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from db.database import init_db  # noqa: E402

init_db()

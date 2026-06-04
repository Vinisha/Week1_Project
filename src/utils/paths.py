"""Centralised filesystem paths so every module resolves files the same way,
regardless of the current working directory."""
import os

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../src
PROJECT_ROOT = os.path.dirname(SRC_DIR)                                 # project root

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
EXPORTS_DIR = os.path.join(PROJECT_ROOT, "exports")

DB_PATH = os.path.join(DATA_DIR, "nutrition_tracker.db")
FOOD_DB_PATH = os.path.join(DATA_DIR, "food_database.csv")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.yaml")


def ensure_dirs():
    """Create runtime directories if they do not yet exist."""
    for d in (DATA_DIR, CONFIG_DIR, EXPORTS_DIR):
        os.makedirs(d, exist_ok=True)

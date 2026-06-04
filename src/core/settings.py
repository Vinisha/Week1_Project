"""Load user configuration (RDA targets, thresholds, categories) from settings.yaml."""
import yaml

from utils.paths import SETTINGS_PATH

# Nutrient columns tracked everywhere in the app (must match food_database.csv headers
# minus name/category). "calories" is handled alongside but is not a micronutrient.
NUTRIENTS = [
    "calories", "protein", "carbs", "fat", "fiber",
    "iron", "calcium", "vitamin_c", "vitamin_d",
]

# Human-friendly units for display.
UNITS = {
    "calories": "kcal", "protein": "g", "carbs": "g", "fat": "g", "fiber": "g",
    "iron": "mg", "calcium": "mg", "vitamin_c": "mg", "vitamin_d": "mcg",
}

_cache = None


def load_settings() -> dict:
    """Read and cache settings.yaml."""
    global _cache
    if _cache is None:
        with open(SETTINGS_PATH, "r") as f:
            _cache = yaml.safe_load(f)
    return _cache


def get_rda() -> dict:
    return load_settings()["rda"]


def get_categories() -> list:
    return load_settings()["categories"]

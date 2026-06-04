# 🥗 Nutrition Tracker

A fully local nutrition tracker built to follow your meals over a year and beyond.
No cloud, no accounts — your data lives in a SQLite file on your machine.

## What it does

1. **Log daily meals** with ingredients, quantities, and auto-computed calories.
2. **Dashboard charts** — calories per day (with weekly/monthly rollups for long
   ranges) and how much of each category you used (vegetables, lentils, non-veg,
   grains, dairy, fruit, fats).
3. **Deficiency flags** — averages your intake against your daily targets (RDA)
   and flags nutrients that are **Deficient** (<70%) or **Low** (70–90%).
4. **Weekly grocery list** — aggregates the ingredients you logged during a week
   into a single shopping checklist you can download.

## Setup

```bash
cd nutrition-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run src/app.py
```

This opens the app in your browser (usually http://localhost:8501). Use the
sidebar to move between **Log Meal → Dashboard → Deficiencies → Grocery List**.

## Run the tests

```bash
pip install pytest
pytest
```

## Project layout

```
nutrition-tracker/
├── config/settings.yaml        # your profile, RDA targets, thresholds, categories
├── data/
│   ├── food_database.csv       # editable: per-100g nutrients per ingredient
│   └── nutrition_tracker.db    # SQLite (created on first run)
├── src/
│   ├── app.py                  # Streamlit entry point
│   ├── pages/                  # the four feature pages
│   ├── core/                   # calories, ingredients, deficiency, grocery, food data
│   ├── db/                     # SQLite connection + repository (CRUD)
│   ├── charts/                 # Plotly figures
│   └── utils/                  # paths + date helpers
├── tests/                      # pytest unit tests
└── exports/                    # saved grocery lists / reports
```

## Customising

- **Targets & thresholds** — edit `config/settings.yaml` (RDA values, calorie
  band, deficiency cut-offs).
- **Foods** — edit `data/food_database.csv`, or add ingredients from the
  **Log Meal** page (the "New ingredient" panel writes back to the CSV).

## Notes on the numbers

- Nutrient values are per 100 g of the *prepared* food and are approximate
  starter values — adjust them in the CSV to match your sources.
- Deficiency averages count un-logged days as zero intake, so gaps in logging
  will pull averages down. That's intentional: it surfaces chronic shortfalls
  over long periods rather than hiding them.
- The targets here are generic adult defaults and are **not medical advice**.
  Set your own targets in `settings.yaml`.

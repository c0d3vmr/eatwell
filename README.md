# EatWell — Houston food access and meal planning

EatWell is a Streamlit prototype for food-access recommendations and budget-aware meal planning. The first RAG release is scoped to Houston and uses a sourced, updateable resource catalog. The health-education chatbot remains a separate feature and does not use RAG.

## Overview

The first version uses structured retrieval because the Houston catalog is small
and has explicit fields; embeddings are unnecessary for these records. The app
currently combines:

- **Financial Reality**: Weekly budget, SNAP/WIC benefits, income level
- **Geographic Access**: Location, transportation, nearby stores
- **Health Needs**: Optional symptoms, family history, previous conditions
- **Biomarkers**: Optional methylation variants (MTHFR, COMT), lab results

Health and lab fields in the existing prototype are not used for Houston resource retrieval or sent to Gemini for meal-plan generation.

## Project Structure

```
nutrition-project/
├── main.py              # Entry point - run the app
├── user_context.py      # Phase 1: User questionnaire data
├── bio_analyzer.py      # Phase 2: Bio-analytical engine
├── resource_locator.py  # Phase 3: Geographic/financial mapping
├── shopping_planner.py  # Phase 4: Curated shopping list
├── interactive_cli.py   # Phase 5: Interactive feedback
├── rag_pipeline.py      # Houston resource retrieval and meal-plan generation
├── profile_store.py     # Supabase Auth/profile helpers
├── data/
│   └── houston_food_resources.json
├── database/
│   └── supabase_schema.sql
├── sync_houston_resources.py
└── README.md
```

## Usage

### Run the Streamlit app
```bash
streamlit run app.py
```

The resource finder uses the bundled Houston starter data until Supabase is configured. Set `SUPABASE_URL` and `SUPABASE_ANON_KEY` in the app server environment for public, RLS-protected resource reads and email account/profile features. Keep `SUPABASE_SERVICE_ROLE_KEY` only in the trusted sync-script environment; never expose it to the Streamlit app or browser. For local development, Supabase is optional; Gemini is required only to generate the draft meal plan.

For local development, copy `.env.example` to `.env` and enter
`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `GEMINI_API_KEY`, and, optionally,
`ROUTES_API_KEY`. The app loads this file at startup. To sync resources, separately copy `.env.admin.example` to
`.env.admin`, enter the Supabase URL and service-role key, then run the sync
script. Both local secret files are ignored by Git. Never paste real keys into
`.env.example` or commit them.

To configure Supabase:

1. Run [`database/supabase_schema.sql`](./database/supabase_schema.sql) in the Supabase SQL editor.
2. Set `SUPABASE_URL` and `SUPABASE_ANON_KEY` in the app's server environment. Configure `SUPABASE_SERVICE_ROLE_KEY` only when running the trusted admin sync script.
3. Enable email sign-up/sign-in in Supabase Authentication settings and allow the app's URL (for local testing, `http://localhost:8501`).
4. Set `GEMINI_API_KEY` to enable draft meal-plan generation. The app uses the
   current `google-genai` SDK and defaults to `gemini-2.5-flash`; set
   `GEMINI_MODEL` in `.env` only if you need to select another model available
   to your API key.
5. For in-app route estimates, enable **Routes API** in the Google Cloud project
   linked to your Google Maps Platform key, configure billing, and set
   `ROUTES_API_KEY` in the app server's `.env`. Restrict the key to Routes API
   and, where practical, to the server's IP address. Never put this key in
   browser code or commit it. Route estimates are requested only when a user
   clicks the estimate button; the app sends their ZIP code and resource
   addresses to Google. The ZIP code is an approximate origin, not a precise
   user location. Listings without a usable visit address cannot be routed.
   This is optional: the resource finder also provides Google Maps directions
   links that do not require a Routes API key or billing configuration. Google
   Maps calculates the route after the user opens the link; EatWell does not
   show its own route distance or time in this mode.
6. Sync the editable JSON catalog:

```bash
python sync_houston_resources.py
```

The sync script upserts records by `resource_id`, so the catalog can be corrected or refreshed and synced again without changing the app. Public Houston resources can be read without an account. Optional email sign-up/sign-in is available when Supabase is configured. A signed-in user can explicitly save, load, and delete their own profile. RLS restricts profile access to the matching authenticated user. Typed saved-profile fields are limited to budget, household size, ZIP, transportation, SNAP/WIC status, dietary preference, and allergies; symptoms, diagnoses, lab results, genetic data, and name are excluded. Profiles are stored in Supabase only after the user clicks “Save current profile.”

### Meal plans and retrieval

- Houston resource lookup uses structured fields and explicit ranking (ZIP match, free-resource relevance for lower budgets, and source details). It does not invent travel distances or treat missing eligibility/transport data as a negative.
- The store finder offers Google Maps directions links for driving, transit, walking, or bicycling without requiring a Routes API key. In-app Google Routes estimates are optional, start from the user's ZIP-code area, and require API configuration and billing; estimates are approximate, not a promise of actual route or travel time.
- The resource map shows only records with mapped public-facing addresses and valid coordinates. Marker details open on click. Starter address coordinates were geocoded from OpenStreetMap data and may identify an address/building rather than a service entrance; the map displays OpenStreetMap attribution. Confirm the current distribution site with the provider before visiting.
- Gemini drafts a seven-day meal plan from foods already selected for the shopping list and the user's household size, dietary preference, and allergies. User name, exact ZIP, lab values, and genetic data are not included in that request. Portions and whether package quantities are sufficient are not verified.
- The current resource starter does not contain a vetted recipe/nutrition evidence corpus. Meal plans are therefore practical drafts, not nutritionist-validated or medically tailored prescriptions. Food prices in the existing planner are estimates.
- Each location recommendation displays its source link and verification metadata. Users should confirm hours, eligibility, appointments, and service address with the provider before travelling.

To build a recipe-first meal planner, collect reviewed recipe records using the
[recipe data collection guide](./docs/recipe-data-collection.md) and
[recipe JSON template](./data/recipe.template.json). Recipe selection and
shopping-list quantities should be deterministic; the LLM should only help
present the selected recipes.

### Updating sample and resource data

The Houston catalog in [`data/houston_food_resources.json`](./data/houston_food_resources.json) can be edited as providers are reverified; rerun the sync command to publish updates to Supabase. Keep `last_verified`, `updated_at`, and source URLs current. The separate synthetic patient records are test fixtures, not verified clinical data or eligibility determinations. They can be replaced or expanded later; this retrieval path does not store them in Supabase.

### Run focused tests

```bash
python -m unittest discover -s tests -v
```

## Phases

### Phase 1: Questionnaire Data Input
The `UserContext` class stores:
- **Financials**: Weekly budget, SNAP/WIC status, income
- **Logistics**: Zip code, vehicle access, grocery trip frequency
- **Medical**: Family history, previous conditions, current symptoms
- **Lab Results**: Methylation markers, vitamin levels, inflammation markers

### Phase 2: Bio-Analytical Engine
The `analyze_lab_data()` function:
- Analyzes methylation markers (MTHFR, COMT variants)
- Evaluates vitamin/mineral levels
- Assesses inflammation markers (CRP, homocysteine)
- Considers symptoms and family history
- Outputs a prioritized **Nutrient Priority List**

Example output:
- "Requires Methylfolate due to MTHFR C677T variant"
- "Requires Anti-inflammatories due to elevated CRP"

### Phase 3: Houston resource retrieval
The RAG resource lookup uses the curated Houston records and preserves source, eligibility, access, and verification metadata. Exact distance ranking is not available until reliable coordinates or a routing source are added.

### Phase 4: Shopping and draft meal planning
The `generate_shopping_list()` function:
- Matches biological needs with affordable food sources
- Prioritizes cheapest sources for highest-priority nutrients
- Shows sourced Houston food resources separately from shopping estimates
- Filters by SNAP eligibility when applicable
- Respects food allergies

### Phase 5: Interactive Feedback
CLI commands:
- `why [item]` - Explain why a food was recommended
- `explain [nutrient]` - Detail a nutrient's importance
- `markers` - Show methylation/lab analysis
- `budget` - Show budget breakdown
- `list` - Display shopping list
- `stores` - Show store recommendations

## Example Session

```
🤖 Ask me > why spinach

📦 Spinach (frozen bag)
   Price: $1.50
   Priority: CRITICAL

   🔬 BIOLOGICAL CONNECTION:
   → Iron:
     Iron level (50 mcg/dL) is low - may cause fatigue and anemia
     Related markers: serum iron, ferritin, TIBC

   → Methylfolate:
     MTHFR C677T variant detected - reduced ability to convert folic acid
     Related markers: MTHFR, homocysteine

   📊 This food provides: Iron, Methylfolate, Magnesium

   💡 Selection reason: Addresses Iron: Iron level (50 mcg/dL) is low...
```

## Requirements

Install dependencies with `pip install -r requirements.txt`. The app requires Gemini and Supabase environment variables for the respective hosted features; local resource lookup works from the bundled JSON without Supabase credentials.

## Features

- **Health Equity Focus**: Prioritizes accessibility and affordability
- **Methylation-Aware**: Considers MTHFR/COMT variants
- **Budget-Conscious**: Alternatives for tight budgets
- **Transparent**: Users can ask "why?" about any recommendation
- **Source-Transparent**: Houston resource records retain provider links and verification dates

## Sample Data

The demo uses a sample user with:
- $60/week budget with SNAP benefits
- No vehicle, public transit available
- Family history of diabetes, hypertension
- MTHFR C677T variant
- Low vitamin D, elevated CRP

## License

Open source - use freely for health equity initiatives.

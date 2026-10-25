# EatWell Recipe Data Collection Guide

## Purpose

Build a small, well-sourced Houston-appropriate recipe catalog that can support
safe filtering, practical weekly meal plans, and shopping lists. The first
catalog should be curated structured data, not a collection of recipes invented
by an LLM.

The planner should select recipes and calculate needed ingredients first.
Gemini, when configured, may later help explain or format that plan. It should
not be the authority for recipe quantities, food safety, allergen safety,
nutrition values, eligibility, or prices.

## Scope for the first collection

Start with roughly 20-30 reviewed recipes rather than trying to cover every
cuisine or diet. Include a varied set of:

- Breakfasts, lunches, dinners, and a few snacks.
- Low-cost, widely available ingredients.
- Recipes that use pantry staples and shelf-stable, frozen, and fresh foods.
- Vegetarian and vegan choices, plus recipes with poultry, eggs, dairy, or fish.
- Recipes that use overlapping ingredients so a weekly plan can reduce waste.
- Simple preparations, with a range of active time and equipment needs.
- Familiar, culturally varied meals appropriate for Houston's communities.

Do not claim that a recipe is culturally representative based on its name alone.
Where possible, have someone familiar with the cuisine review the title,
ingredients, preparation, and substitutions.

## One record per recipe

Use the JSON structure in [`../data/recipe.template.json`](../data/recipe.template.json)
as the starting template. Keep field names stable. Use `null` when a fact is
unknown; do not fill unknown values with assumptions or an empty string.

### Required recipe identity and provenance

Collect:

- `recipe_id`: stable unique identifier, such as `houston_lentil_soup_001`.
- `title`: clear user-facing name.
- `description`: short factual description, without health claims.
- `source`: original page/book/publisher, author or organization, source URL,
  date accessed, and reuse/license status.
- `source_recipe_id`: optional identifier for the original recipe.
- `adaptation_notes`: what EatWell changed from the source and who made or
  approved the adaptation.
- `language`: language of the instructions.
- `record_version`, `created_at`, `updated_at`, and `review_status`.

Prefer recipes created by EatWell staff, licensed/open recipes, government or
university extension sources, or sources that explicitly permit the intended
use. A publicly viewable webpage is not automatically permission to copy its
full recipe or instructions. Record the source and its permitted use; if full
reuse is not allowed, store original metadata and a link rather than copying
protected text.

### Yield, time, equipment, and steps

Record:

- `yield_servings`: number of portions produced by the whole recipe.
- `serving_description`: plain-language description, if known (for example,
  "one bowl").
- `prep_time_minutes`, `cook_time_minutes`, and `total_time_minutes`, with
  estimates identified as estimates.
- `skill_level` using a small controlled vocabulary such as `beginner`,
  `intermediate`, or `advanced`.
- `equipment`: required equipment only; distinguish optional equipment.
- `steps`: ordered, specific instructions. Each step should describe one
  practical action and include temperatures/times where needed.
- `food_safety_notes`: validated handling/cooking guidance and a supporting
  authoritative source where applicable.

Check that the listed steps can actually be completed with the collected
ingredients and equipment. Do not invent cook temperatures or doneness checks.
For meat, seafood, eggs, and leftovers, have instructions reviewed against
current authoritative food-safety guidance.

### Ingredient data (essential)

For every ingredient, record:

- `ingredient_id`: normalized canonical ingredient name/ID for matching and
  deduplication (for example, `black_beans_canned`).
- `display_name`: exact user-facing ingredient, including meaningful form
  (such as canned, low-sodium, frozen, boneless, or unsalted).
- `quantity`: numeric amount where the source provides one; use `null` if not
  specified.
- `unit`: controlled unit (`g`, `kg`, `ml`, `l`, `tsp`, `tbsp`, `cup`, `piece`,
  `can`, etc.). Do not convert vague amounts into false precision.
- `preparation`: for example, drained, rinsed, chopped, or thawed.
- `optional`: whether omission is allowed without breaking the recipe.
- `group`: optional section name such as "for the sauce".
- `substitution_group`: optional normalized group for reviewed alternatives.
- `notes`: important purchasing or cooking detail.

Keep as-purchased amounts distinct from drained or edible amounts where that
matters. Do not assume package size. Include water, oil, seasonings, and other
ingredients required by the steps, even if they are common pantry items. If a
pantry staple can be omitted, explicitly mark it optional.

Normalize ingredient names so equivalent terms can be matched, but preserve the
original display name. Record ingredient substitutions as explicit alternatives
with their own quantities/units and constraints; do not ask the model to invent
substitutions, especially for allergies.

### Allergens and dietary suitability

For each recipe, collect:

- `allergens.contains`: allergens explicitly present in ingredients.
- `allergens.may_contain`: only source/manufacturer cross-contact statements
  that were actually checked; not a generalized guess.
- `allergens.review_status`: `reviewed`, `not_reviewed`, or `unknown`.
- `dietary_tags`: labels supported by the ingredient list and preparation,
  such as `vegetarian`, `vegan`, `pescatarian`, `dairy_free`, or `gluten_free`.
- `dietary_review_status`: whether a qualified reviewer verified the tags.
- `cross_contact_notes`: handling information only if verified.

Do not label a recipe allergen-safe merely because the recipe itself omits an
allergen. Brand formulations and kitchen cross-contact vary; tell users with
allergies to check product labels and preparation conditions. If allergen status
is unknown, preserve it as unknown and exclude the recipe when a strict
allergen-safe result is required.

Avoid inferring `gluten_free`, `dairy_free`, `vegan`, or similar tags from a
recipe title. Check every ingredient, including sauces, stocks, seasonings,
fortified products, and suggested substitutions.

### Nutrition information (only when sourced)

Nutrition data is optional for the first data-gathering pass. If included,
collect nutrient amounts **per defined serving**, the serving basis, units,
calculation method, database name/version, and ingredient mappings. Useful
fields may include energy (kcal), protein, carbohydrate, fiber, total fat,
saturated fat, sodium, and added sugar.

Prefer values calculated from standardized ingredient quantities using a
recognized food-composition database such as USDA FoodData Central. Keep the
database identifiers and calculation date so values can be reproduced. Identify
whether values are calculated or measured, and document ingredient substitutions
used in the calculation. Do not present a generic ingredient's nutrient values
as a precise value for a complete recipe.

Nutrition numbers and diet labels should be reviewed by a nutrition professional
before EatWell uses them to make individualized nutrition claims. Do not add
claims such as "treats anemia", "reduces inflammation", or "prevents diabetes"
to recipe metadata.

### Affordability and accessibility (optional, but useful)

If estimating recipe cost, collect:

- Price date, currency, source/store or public price dataset.
- Market/package size, purchased quantity, and price per package.
- How the recipe's consumed quantity maps to the purchased package.
- Recipe cost and cost per serving, both explicitly marked as estimates.
- Assumptions for shared pantry staples, rounding, waste, and package remainder.

Never store a timeless price. Prices vary by store, date, brand, promotion, and
neighborhood. Do not imply that a user can afford a recipe based only on one
store's historic price.

Optional practical-access fields include preparation equipment, refrigeration
or freezer requirements, active time, batch/freezer suitability, shelf life
after preparation, and shelf-stable ingredient options. Have storage durations
reviewed; do not infer them from raw ingredient shelf lives.

## Review states and workflow

Use explicit states:

1. `draft`: source and fields are being collected; do not use in recommendations.
2. `source_checked`: source, reuse permission, and transcription were checked.
3. `food_safety_reviewed`: cooking and storage directions checked.
4. `dietary_reviewed`: ingredient-derived dietary/allergen fields checked.
5. `nutritionist_reviewed`: nutrition fields or nutrition-facing guidance
   reviewed by a qualified nutrition professional.
6. `approved_for_testing`: permitted for internal synthetic-user tests.
7. `approved_for_users`: all required review and product approvals complete.
8. `retired`: do not retrieve for new plans; retain provenance for auditability.

Record reviewer role, review date, fields reviewed, and unresolved issues.
Approval should be field-specific: a nutritionist reviewing nutrition values
does not automatically verify source rights, food safety, cost, or allergen
cross-contact.

Suggested collection workflow:

1. Select a recipe from a source whose reuse terms are understood.
2. Capture the source metadata and original recipe reference.
3. Enter ingredients, units, yield, equipment, and instructions without
   silently converting missing or vague amounts.
4. Normalize ingredient IDs and map aliases while retaining source wording.
5. Independently check that ingredient quantities and steps agree.
6. Verify dietary/allergen labels; leave uncertain values unknown.
7. Add cost and nutrition only with reproducible data sources and dates.
8. Obtain the appropriate food-safety and nutrition review.
9. Test scaling, ingredient consolidation, allergy exclusion, and budget
   calculations using synthetic users.
10. Approve only for the intended audience and use; update or retire records
    when source facts or guidance change.

## Minimum acceptance checklist

Do not use a recipe in an EatWell plan unless:

- It has a stable ID, source, source URL/reference, and known reuse status.
- The yield, ingredients, quantities/units when provided, and steps are present.
- The instructions do not require an unlisted ingredient without labeling it
  optional.
- Dietary and allergen tags are verified or the recipe is conservatively
  excluded for the relevant user.
- Food-safety-critical steps are reviewed.
- Its review status permits the intended use.
- Its nutrition and cost fields, if shown, have provenance and are marked with
  their limitations.

## How this supports meal planning

The future planner should:

1. Exclude recipes incompatible with confirmed user restrictions.
2. Prefer recipes whose review state is allowed for the product.
3. Select a mix of meals that fits household size, available preparation time,
   equipment, and budget.
4. Scale ingredient quantities from recipe yield using explicit arithmetic.
5. Consolidate matching ingredients into one shopping list while preserving
   units and package-rounding assumptions.
6. Calculate cost only from dated price data, showing estimates and unknowns.
7. Pass the chosen recipe records to an LLM only for optional plain-language
   presentation; retain the recipe sources in the displayed plan.

Do not let a user-facing LLM response override deterministic allergy exclusions,
food-safety instructions, recipe provenance, or cost calculations.

## Synthetic profiles and recipe testing

Synthetic users can test differences in ZIP code, budget, household size,
transportation, benefits, dietary preferences, and declared allergies. Keep
synthetic flags attached, avoid using synthetic health/lab/genetic fields to
claim clinical performance, and never represent synthetic outputs as validated
personalized nutrition advice. Test cases should assert expected included and
excluded recipe IDs, scaled quantities, and price behavior.

"""Houston resource retrieval and grounded meal-plan generation."""

from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from gemini_service import GeminiRequestError, generate_text
from user_context import UserContext


LOGGER = logging.getLogger(__name__)
RESOURCE_FILE = Path(__file__).parent / "data" / "houston_food_resources.json"


class ResourceLookupError(RuntimeError):
    """Raised when the configured Houston resource source cannot be queried."""


class MealPlanError(RuntimeError):
    """Raised when Gemini cannot produce a meal plan."""


@dataclass
class ResourceSearchResults:
    resources: List[Dict[str, Any]]
    source: str


def _load_local_resources() -> List[Dict[str, Any]]:
    try:
        dataset = json.loads(RESOURCE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResourceLookupError(
            f"Could not load the Houston resource dataset at {RESOURCE_FILE}."
        ) from exc

    if not isinstance(dataset, dict) or not isinstance(dataset.get("resources"), list):
        raise ResourceLookupError("The Houston resource dataset has no resources list.")
    return dataset["resources"]


def _load_supabase_resources() -> List[Dict[str, Any]]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url and not key:
        return _load_local_resources()
    if not url or not key:
        raise ResourceLookupError(
            "Set both SUPABASE_URL and SUPABASE_ANON_KEY, or unset both "
            "to use the bundled Houston starter dataset."
        )

    try:
        from supabase import create_client

        response = (
            create_client(url, key)
            .table("eatwell_resources")
            .select("payload")
            .eq("city", "Houston")
            .eq("state", "TX")
            .execute()
        )
    except Exception as exc:
        LOGGER.exception("Supabase Houston resource query failed")
        raise ResourceLookupError(
            "Could not retrieve Houston resources from Supabase. Check the "
            "connection and eatwell_resources table."
        ) from exc

    rows = response.data or []
    invalid_count = sum(
        1 for row in rows
        if not isinstance(row, dict) or not isinstance(row.get("payload"), dict)
    )
    if invalid_count:
        LOGGER.warning("Skipped %s malformed Supabase resource rows", invalid_count)

    return [
        row["payload"]
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("payload"), dict)
    ]


def _resource_score(resource: Dict[str, Any], user: UserContext) -> Tuple[int, str]:
    """Rank only on facts present in the record; do not infer distance/access."""
    score = 0
    reasons = []

    if resource.get("zip_code") == user.logistics.zip_code:
        score += 20
        reasons.append("ZIP code match")
    elif not resource.get("zip_code"):
        reasons.append("Houston-wide listing; ZIP coverage not specified")

    resource_type = str(resource.get("resource_type", "")).lower()
    if "directory" in resource_type:
        score -= 5
        reasons.append("Directory, not a visit location")

    if (
        user.financials.weekly_budget < 100
        and resource.get("cost_type") == "free"
    ):
        score += 5
        reasons.append("Free food assistance")

    if user.financials.snap_status and resource.get("snap_accepted") is True:
        score += 2
        reasons.append("SNAP acceptance listed")
    if user.financials.wic_status and resource.get("wic_accepted") is True:
        score += 2
        reasons.append("WIC acceptance listed")

    return score, "; ".join(reasons)


def retrieve_houston_resources(user: UserContext, limit: int = 8) -> ResourceSearchResults:
    """Retrieve and rank Houston records without treating unknowns as negatives."""
    zip_code = user.logistics.zip_code.strip()
    if not re.fullmatch(r"77[02]\d{2}", zip_code):
        return ResourceSearchResults(resources=[], source="Houston-only dataset")

    all_resources = _load_supabase_resources()
    city_resources = [
        resource for resource in all_resources
        if str(resource.get("city") or "").casefold() == "houston"
        and str(resource.get("state") or "").casefold() in {"tx", "texas"}
    ]

    ranked = []
    for resource in city_resources:
        score, reason = _resource_score(resource, user)
        ranked.append((score, resource.get("name") or "", resource, reason))
    ranked.sort(key=lambda item: (-item[0], item[1].casefold()))

    results = []
    for score, _, resource, reason in ranked[:limit]:
        result = dict(resource)
        result["match_score"] = score
        result["match_reason"] = reason or "Houston resource"
        results.append(result)

    source = "Supabase" if os.getenv("SUPABASE_URL") and os.getenv(
        "SUPABASE_ANON_KEY"
    ) else "bundled Houston starter dataset"
    return ResourceSearchResults(resources=results, source=source)


def build_meal_plan_prompt(
    user: UserContext,
    food_names: Sequence[str],
) -> str:
    """Build a prompt containing meal-planning constraints, not lab or genetic data."""
    demographics = user.demographics
    preference = (
        demographics.dietary_preference
        if demographics and demographics.dietary_preference
        else "none specified"
    )
    foods = sorted({name.strip() for name in food_names if name.strip()})
    allergies = sorted(set(user.medical.known_allergies))

    return f"""Create a practical, flexible 7-day meal plan for {user.household_size} person(s).
Use these planned shopping-list foods as the only foods assumed to be available:
{json.dumps(foods)}

Dietary preference: {preference}
Allergies/intolerances to avoid: {json.dumps(allergies)}

Requirements:
- Use only the listed foods. If a common pantry staple would help, mark it clearly
  as optional and do not assume the household has it or include it in the budget.
- Do not invent prices, nutrition values, pantry inventory, or resource details.
- Do not make medical, disease-prevention, or nutrient-treatment claims.
- Remind the user to verify ingredient labels and cross-contact risks for allergens.
- Keep recipes simple and reuse ingredients. Do not add a general disclaimer
  about limited variety just because the provided list is short.
- Format as seven day headings with breakfast, lunch, and dinner, followed by a
  short prep note. Keep the wording plain and non-judgmental."""


def generate_meal_plan(
    user: UserContext,
    food_names: Sequence[str],
    api_key: Optional[str] = None,
) -> str:
    """Ask Gemini for a meal-plan draft grounded in the generated shopping list."""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise MealPlanError(
            "Meal-plan generation is unavailable. Configure GEMINI_API_KEY."
        )

    try:
        return generate_text(build_meal_plan_prompt(user, food_names), api_key=key)
    except GeminiRequestError as exc:
        raise MealPlanError(str(exc)) from exc
    except Exception as exc:
        LOGGER.exception("Gemini meal-plan generation failed")
        raise MealPlanError("Gemini meal-plan generation failed unexpectedly.") from exc

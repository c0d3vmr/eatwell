"""Supabase Auth and private user-profile persistence."""

from typing import Any, Dict

from user_context import UserContext


def create_supabase_client(url: str, anon_key: str):
    """Create an app client using the public anon key, never the service role."""
    from supabase import create_client

    return create_client(url, anon_key)


def profile_from_user(user: UserContext) -> Dict[str, Any]:
    """Return only food-access and meal-planning fields approved for persistence."""
    dietary_preference = (
        user.demographics.dietary_preference
        if user.demographics
        else None
    )
    return {
        "weekly_budget": user.financials.weekly_budget,
        "household_size": user.household_size,
        "snap_status": user.financials.snap_status,
        "wic_status": user.financials.wic_status,
        "zip_code": user.logistics.zip_code,
        "has_vehicle": user.logistics.has_vehicle,
        "has_transit": user.logistics.has_public_transit,
        "trips_per_week": user.logistics.grocery_trips_per_week,
        "dietary_preference": dietary_preference,
        "allergies": list(user.medical.known_allergies),
    }


def apply_profile_to_wizard(profile: Dict[str, Any], wizard: Dict[str, Any]) -> None:
    """Apply a saved profile while resetting fields that are not persisted."""
    wizard.update({
        "name": "",
        "weekly_budget": 75,
        "household_size": 1,
        "snap_status": False,
        "wic_status": False,
        "zip_code": "77001",
        "has_vehicle": False,
        "has_transit": True,
        "trips_per_week": 2,
        "age": None,
        "biological_sex": "Prefer not to say",
        "height_feet": None,
        "height_inches": None,
        "weight_lbs": None,
        "activity_level": "Not specified",
        "pregnancy_status": "None",
        "dietary_preference": "None",
        "health_goals": [],
        "family_history": [],
        "current_symptoms": [],
        "allergies": [],
        "mthfr_variant": "Not Tested",
        "comt_variant": "Not Tested",
        "b12_level": 0,
        "vit_d_level": 0,
        "iron_level": 0,
        "crp_level": 0.0,
        "homocysteine": 0.0,
        "glucose": 0,
    })

    wizard["weekly_budget"] = float(profile.get("weekly_budget") or 75)
    wizard["household_size"] = int(profile.get("household_size") or 1)
    wizard["snap_status"] = bool(profile.get("snap_status"))
    wizard["wic_status"] = bool(profile.get("wic_status"))
    wizard["zip_code"] = str(profile.get("zip_code") or "77001")
    wizard["has_vehicle"] = bool(profile.get("has_vehicle", False))
    wizard["has_transit"] = bool(profile.get("has_transit", True))
    wizard["trips_per_week"] = int(profile.get("trips_per_week") or 2)
    diet_labels = {
        "vegetarian": "Vegetarian",
        "vegan": "Vegan",
        "pescatarian": "Pescatarian",
        "keto": "Keto/Low-Carb",
        "mediterranean": "Mediterranean",
    }
    diet = profile.get("dietary_preference")
    wizard["dietary_preference"] = diet_labels.get(
        str(diet).casefold(),
        "None",
    )
    allergy_labels = {
        "gluten": "Gluten",
        "dairy": "Dairy",
        "shellfish": "Shellfish",
        "tree nuts": "Tree Nuts",
        "peanuts": "Peanuts",
        "eggs": "Eggs",
        "soy": "Soy",
        "fish": "Fish",
        "corn": "Corn",
        "sesame": "Sesame",
        "nightshades": "Nightshades",
        "sulfites": "Sulfites",
        "histamine": "Histamine",
        "fodmaps": "FODMAPs",
        "latex-fruit": "Latex-Fruit",
    }
    wizard["allergies"] = [
        allergy_labels.get(str(allergy).casefold(), str(allergy))
        for allergy in profile.get("allergies", [])
    ]

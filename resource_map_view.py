"""Build an interactive map of Houston food resources with mapped addresses."""

from html import escape
from typing import Any, Dict, List, Sequence


def mappable_resources(resources: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return visit-location records with valid coordinates and addresses."""
    mapped = []
    for resource in resources:
        resource_type = str(resource.get("resource_type") or "").casefold()
        if (
            not resource.get("address")
            or "directory" in resource_type
            or "food_bank_and_referral" in resource_type
        ):
            continue

        try:
            latitude = float(resource["latitude"])
            longitude = float(resource["longitude"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            continue

        mapped.append({**resource, "latitude": latitude, "longitude": longitude})
    return mapped


def build_resource_map(resources: Sequence[Dict[str, Any]]):
    """Build a Folium map with click-to-open resource detail popups."""
    import folium

    locations = mappable_resources(resources)
    if not locations:
        return None

    center = [
        sum(resource["latitude"] for resource in locations) / len(locations),
        sum(resource["longitude"] for resource in locations) / len(locations),
    ]
    resource_map = folium.Map(
        location=center,
        zoom_start=11,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    for resource in locations:
        address_parts = [
            resource.get("address"),
            resource.get("city"),
            resource.get("state"),
            resource.get("zip_code"),
        ]
        address = ", ".join(str(part) for part in address_parts if part)
        details = [
            f"<b>{escape(str(resource.get('name') or 'Houston food resource'))}</b>",
            escape(address),
            escape(str(resource.get("resource_type") or "").replace("_", " ").title()),
        ]
        for label, key in (
            ("Details", "description"),
            ("Before you go", "access_notes"),
            ("Eligibility", "eligibility"),
            ("Phone", "phone"),
        ):
            value = resource.get(key)
            if value:
                details.append(f"<b>{label}:</b> {escape(str(value))}")

        source_url = resource.get("source_url")
        if isinstance(source_url, str) and source_url.startswith("https://"):
            details.append(
                f'<a href="{escape(source_url, quote=True)}" target="_blank" '
                'rel="noopener noreferrer">Verify with provider</a>'
            )

        folium.Marker(
            location=[resource["latitude"], resource["longitude"]],
            tooltip=str(resource.get("name") or "Houston food resource"),
            popup=folium.Popup("<br>".join(details), max_width=360),
            icon=folium.Icon(color="green", icon="cutlery", prefix="fa"),
        ).add_to(resource_map)

    return resource_map

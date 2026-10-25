"""Server-side route estimates using Google Maps Platform Routes API."""

from dataclasses import dataclass
import json
import os
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
TRAVEL_MODES = {
    "Driving": "DRIVE",
    "Public transit": "TRANSIT",
    "Walking": "WALK",
    "Bicycling": "BICYCLE",
}
MAPS_URL_TRAVEL_MODES = {
    "Driving": "driving",
    "Public transit": "transit",
    "Walking": "walking",
    "Bicycling": "bicycling",
}


class RouteLookupError(RuntimeError):
    """Raised when Google Routes cannot produce a route estimate."""


@dataclass(frozen=True)
class RouteEstimate:
    distance_meters: int
    duration_seconds: int


def google_maps_directions_url(
    origin: str,
    destination: str,
    travel_mode: str,
) -> str:
    """Build a Google Maps directions link; this does not call a paid API."""
    if travel_mode not in MAPS_URL_TRAVEL_MODES:
        raise ValueError(f"Unsupported travel mode: {travel_mode}")
    if not origin.strip() or not destination.strip():
        raise ValueError("Origin and destination addresses are required.")
    query = urlencode(
        {
            "api": "1",
            "origin": origin.strip(),
            "destination": destination.strip(),
            "travelmode": MAPS_URL_TRAVEL_MODES[travel_mode],
        }
    )
    return f"https://www.google.com/maps/dir/?{query}"


def _format_provider_error(body: bytes) -> str:
    try:
        data = json.loads(body)
        message = data.get("error", {}).get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()[:400]
    except (json.JSONDecodeError, AttributeError):
        pass
    return "Google Maps Platform did not provide details."


def compute_route(
    origin: str,
    destination: str,
    travel_mode: str,
    api_key: str | None = None,
) -> RouteEstimate:
    """Return a route estimate between address strings for a supported mode."""
    key = (api_key or os.getenv("ROUTES_API_KEY", "")).strip()
    if not key:
        raise RouteLookupError(
            "ROUTES_API_KEY is not configured. Add it to .env and restart the app."
        )
    if travel_mode not in TRAVEL_MODES:
        raise ValueError(f"Unsupported travel mode: {travel_mode}")
    if not origin.strip() or not destination.strip():
        raise ValueError("Origin and destination addresses are required.")

    body = json.dumps(
        {
            "origin": {"address": origin.strip()},
            "destination": {"address": destination.strip()},
            "travelMode": TRAVEL_MODES[travel_mode],
        }
    ).encode("utf-8")
    request = Request(
        ROUTES_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read())
    except HTTPError as exc:
        detail = _format_provider_error(exc.read())
        if exc.code in {401, 403}:
            hint = (
                " Check that Routes API is enabled, billing is configured, and "
                "the key allows this API."
            )
        else:
            hint = ""
        raise RouteLookupError(
            f"Google Routes request failed (HTTP {exc.code}): {detail}.{hint}"
        ) from exc
    except (URLError, TimeoutError) as exc:
        raise RouteLookupError(
            "Could not connect to Google Routes. Check the network and try again."
        ) from exc
    except (json.JSONDecodeError, OSError) as exc:
        raise RouteLookupError(
            "Google Routes returned an unreadable response. Try again later."
        ) from exc

    try:
        route = payload["routes"][0]
        distance_meters = route["distanceMeters"]
        duration = route["duration"]
        duration_seconds = int(duration.removesuffix("s"))
        if not isinstance(distance_meters, int) or distance_meters < 0:
            raise ValueError
        if duration_seconds < 0:
            raise ValueError
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RouteLookupError(
            "Google Routes did not return a route for this address and travel mode."
        ) from exc

    return RouteEstimate(
        distance_meters=distance_meters,
        duration_seconds=duration_seconds,
    )

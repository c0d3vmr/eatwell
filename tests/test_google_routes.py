import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from io import BytesIO

from google_routes import (
    RouteLookupError,
    compute_route,
    google_maps_directions_url,
)
from resource_map_view import build_resource_map, mappable_resources


class GoogleRoutesTests(unittest.TestCase):
    def test_google_maps_directions_link_needs_no_api_key(self):
        url = google_maps_directions_url(
            "77009, Houston, TX",
            "3523 Beauchamp St, Houston, TX 77009",
            "Public transit",
        )

        self.assertIn("api=1", url)
        self.assertIn("travelmode=transit", url)
        self.assertIn("origin=77009%2C+Houston%2C+TX", url)
        self.assertIn("destination=3523+Beauchamp+St", url)
        self.assertNotIn("key=", url)

    def test_google_maps_link_rejects_unsupported_mode(self):
        with self.assertRaises(ValueError):
            google_maps_directions_url("Houston, TX", "Houston, TX", "Scooter")

    def test_resource_map_contains_only_valid_public_visit_locations(self):
        resources = [
            {
                "resource_id": "mapped",
                "name": "Mapped Pantry",
                "resource_type": "food_pantry",
                "address": "123 Main St",
                "latitude": 29.7,
                "longitude": -95.3,
            },
            {
                "resource_id": "missing-coordinates",
                "name": "No Coordinates",
                "resource_type": "food_pantry",
                "address": "456 Main St",
                "latitude": None,
                "longitude": None,
            },
            {
                "resource_id": "directory",
                "name": "Provider Directory",
                "resource_type": "directory_not_a_single_location",
                "address": "789 Main St",
                "latitude": 29.7,
                "longitude": -95.3,
            },
            {
                "resource_id": "outside-range",
                "name": "Invalid Coordinates",
                "resource_type": "food_pantry",
                "address": "999 Main St",
                "latitude": 200,
                "longitude": -95.3,
            },
        ]

        mapped = mappable_resources(resources)

        self.assertEqual([resource["resource_id"] for resource in mapped], ["mapped"])
        resource_map = build_resource_map(mapped)
        marker_count = sum(
            child.__class__.__name__ == "Marker"
            for child in resource_map._children.values()
        )
        self.assertEqual(marker_count, 1)
        self.assertIsNone(build_resource_map(resources[1:]))

    @patch("google_routes.urlopen")
    def test_compute_route_sends_mode_and_returns_estimate(self, urlopen):
        response = urlopen.return_value.__enter__.return_value
        response.read.return_value = json.dumps(
            {
                "routes": [
                    {
                        "distanceMeters": 4828,
                        "duration": "900s",
                    }
                ]
            }
        ).encode()

        estimate = compute_route(
            "77009, Houston, TX",
            "3523 Beauchamp St, Houston, TX 77009",
            "Walking",
            api_key="routes-test-key",
        )

        request = urlopen.call_args.args[0]
        self.assertEqual(estimate.distance_meters, 4828)
        self.assertEqual(estimate.duration_seconds, 900)
        self.assertEqual(request.headers["X-goog-api-key"], "routes-test-key")
        self.assertIn(b'"travelMode": "WALK"', request.data)

    @patch("google_routes.urlopen")
    def test_api_error_explains_routes_configuration(self, urlopen):
        urlopen.side_effect = HTTPError(
            "https://routes.googleapis.com",
            403,
            "Forbidden",
            {},
            BytesIO(
                b'{"error":{"message":"Routes API has not been used in project"}}'
            ),
        )

        with self.assertRaises(RouteLookupError) as raised:
            compute_route("Houston, TX 77009", "Houston, TX 77055", "Driving", "key")

        message = str(raised.exception)
        self.assertIn("HTTP 403", message)
        self.assertIn("Routes API has not been used", message)
        self.assertIn("billing is configured", message)

    def test_unsupported_travel_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            compute_route("Houston, TX", "Houston, TX", "Scooter", "key")


if __name__ == "__main__":
    unittest.main()

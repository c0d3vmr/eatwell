import unittest
from unittest.mock import patch
from types import SimpleNamespace

from rag_pipeline import (
    MealPlanError,
    build_meal_plan_prompt,
    generate_meal_plan,
    retrieve_houston_resources,
)
from shopping_planner import (
    FoodItem,
    _matches_allergies,
    _matches_dietary_preference,
)
from profile_store import apply_profile_to_wizard, profile_from_user
from gemini_service import GeminiRequestError, generate_text
from user_context import (
    Demographics,
    Financials,
    Logistics,
    MedicalHistory,
    UserContext,
)


def make_user(zip_code="77009", budget=40):
    return UserContext(
        user_id="test-user",
        name="Test User",
        financials=Financials(weekly_budget=budget),
        logistics=Logistics(zip_code=zip_code),
        medical=MedicalHistory(known_allergies=["peanuts"]),
        household_size=3,
    )


class HoustonRetrievalTests(unittest.TestCase):
    @patch.dict("os.environ", {}, clear=True)
    @patch("rag_pipeline._load_supabase_resources")
    def test_retrieval_prioritizes_matching_free_pantries(self, load_resources):
        load_resources.return_value = [
            {
                "name": "Other Pantry",
                "city": "Houston",
                "state": "TX",
                "zip_code": "77055",
                "resource_type": "food_pantry",
                "cost_type": "free",
            },
            {
                "name": "Nearby Pantry",
                "city": "Houston",
                "state": "TX",
                "zip_code": "77009",
                "resource_type": "food_pantry",
                "cost_type": "free",
            },
            {
                "name": "Austin Pantry",
                "city": "Austin",
                "state": "TX",
                "zip_code": "78701",
                "resource_type": "food_pantry",
                "cost_type": "free",
            },
        ]

        results = retrieve_houston_resources(make_user())

        self.assertEqual([r["name"] for r in results.resources],
                         ["Nearby Pantry", "Other Pantry"])
        self.assertIn("ZIP code match", results.resources[0]["match_reason"])
        self.assertEqual(results.source, "bundled Houston starter dataset")

    def test_meal_prompt_contains_constraints_without_personal_identifiers(self):
        prompt = build_meal_plan_prompt(
            make_user(),
            ["Brown Rice", "Black Beans", "Brown Rice"],
        )

        self.assertIn('"Brown Rice"', prompt)
        self.assertIn('"peanuts"', prompt)
        self.assertIn("3 person(s)", prompt)
        self.assertNotIn("Test User", prompt)
        self.assertIn("Do not make medical", prompt)
        self.assertIn("Do not add a general disclaimer", prompt)
        self.assertNotIn("label any day", prompt)

    @patch.dict("os.environ", {}, clear=True)
    def test_meal_generation_requires_gemini_configuration(self):
        with self.assertRaises(MealPlanError):
            generate_meal_plan(make_user(), ["Oats"])

    @patch("google.genai.Client")
    @patch.dict("os.environ", {"GEMINI_MODEL": "gemini-3.8-flash"})
    def test_gemini_text_helper_returns_generated_text(self, client_class):
        client = client_class.return_value
        client.models.generate_content.return_value = SimpleNamespace(
            text="A generated response."
        )

        result = generate_text("test prompt", api_key="test-key")

        self.assertEqual(result, "A generated response.")
        client.models.generate_content.assert_called_once_with(
            model="gemini-3.8-flash",
            contents="test prompt",
        )

    @patch("google.genai.Client")
    def test_gemini_text_helper_reports_empty_response(self, client_class):
        client_class.return_value.models.generate_content.return_value = (
            SimpleNamespace(text=None)
        )

        with self.assertRaisesRegex(GeminiRequestError, "returned no text"):
            generate_text("test prompt", api_key="test-key")

    @patch("google.genai.Client")
    def test_gemini_error_with_model_word_is_not_misclassified(self, client_class):
        client_class.return_value.models.generate_content.side_effect = RuntimeError(
            "request configuration for model generation was rejected"
        )

        with self.assertRaises(GeminiRequestError) as raised:
            generate_text("test prompt", api_key="test-key")

        self.assertIn("RuntimeError", str(raised.exception))
        self.assertIn("request configuration", str(raised.exception))
        self.assertNotIn("unavailable for this API key", str(raised.exception))

    @patch("google.genai.Client")
    def test_gemini_404_includes_provider_detail_and_redacts_key(self, client_class):
        client_class.return_value.models.generate_content.side_effect = RuntimeError(
            "404 NOT_FOUND: model is not available for generateContent"
        )

        with self.assertRaises(GeminiRequestError) as raised:
            generate_text("test prompt", api_key="private-test-key")

        self.assertIn("Gemini returned a 404", str(raised.exception))
        self.assertIn("not available for generateContent", str(raised.exception))
        self.assertNotIn("private-test-key", str(raised.exception))

    def test_vegan_filter_excludes_animal_products(self):
        user = make_user()
        user.demographics = Demographics(dietary_preference="vegan")

        self.assertFalse(
            _matches_dietary_preference(
                FoodItem("Eggs (dozen)", "dairy", 3.50), user
            )
        )
        self.assertTrue(
            _matches_dietary_preference(
                FoodItem("Black Beans (canned)", "canned", 0.89), user
            )
        )

    def test_allergy_filter_handles_plural_peanut_names(self):
        self.assertFalse(
            _matches_allergies(
                FoodItem("Peanut Butter", "dry goods", 3.00),
                make_user(),
            )
        )

    def test_saved_profile_excludes_clinical_and_identity_data(self):
        user = make_user()
        profile = profile_from_user(user)

        self.assertIn("zip_code", profile)
        self.assertIn("allergies", profile)
        self.assertNotIn("name", profile)
        self.assertNotIn("labs", profile)
        self.assertNotIn("symptoms", profile)
        self.assertNotIn("genetics", profile)

    def test_loading_profile_resets_unsaved_health_fields(self):
        wizard = {
            "current_symptoms": ["Fatigue"],
            "family_history": ["Diabetes"],
            "b12_level": 500,
        }

        apply_profile_to_wizard(
            {"weekly_budget": 90, "zip_code": "77009", "allergies": ["peanuts"]},
            wizard,
        )

        self.assertEqual(wizard["weekly_budget"], 90)
        self.assertEqual(wizard["zip_code"], "77009")
        self.assertEqual(wizard["allergies"], ["Peanuts"])
        self.assertEqual(wizard["current_symptoms"], [])
        self.assertEqual(wizard["family_history"], [])
        self.assertEqual(wizard["b12_level"], 0)

    @patch("rag_pipeline._load_supabase_resources")
    def test_retrieval_does_not_show_houston_records_for_other_zip_codes(
        self, load_resources
    ):
        results = retrieve_houston_resources(make_user(zip_code="78701"))

        load_resources.assert_not_called()
        self.assertEqual(results.resources, [])
        self.assertEqual(results.source, "Houston-only dataset")

    @patch.dict("os.environ", {}, clear=True)
    def test_bundled_dataset_returns_cited_zip_match(self):
        results = retrieve_houston_resources(make_user(zip_code="77009", budget=75))

        self.assertTrue(results.resources)
        self.assertTrue(
            any(
                resource.get("zip_code") == "77009"
                and resource.get("source_url")
                for resource in results.resources
            )
        )


if __name__ == "__main__":
    unittest.main()

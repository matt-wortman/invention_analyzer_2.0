import unittest
import os
import json
from unittest.mock import patch, MagicMock

try:
    # Import the module itself to call functions like ai_analyzer.analyze_abstract_with_llm
    from . import ai_analyzer
    from . import config # To check if API keys are notionally set / for llm_client in ai_analyzer
    from .simple_database import initialize_database, insert_paper, get_paper_by_pmid, update_paper_ai_analysis, DATABASE_PATH
    from .simple_ncbi import fetch_publication_details # To get a real abstract for testing
except ImportError:
    # Fallback for direct execution or different project structures
    import ai_analyzer
    import config
    from simple_database import initialize_database, insert_paper, get_paper_by_pmid, update_paper_ai_analysis, DATABASE_PATH
    from simple_ncbi import fetch_publication_details


# Helper function to check if API keys are likely configured for chosen provider
def are_api_keys_configured():
    if not ai_analyzer.llm_client: # llm_client is now accessed via the module
        return False
    if config.LLM_PROVIDER == "openai" and config.OPENAI_API_KEY:
        return True
    if config.LLM_PROVIDER == "anthropic" and config.ANTHROPIC_API_KEY:
        return True
    return False

@unittest.skipIf(not are_api_keys_configured(),
                 f"LLM provider '{config.LLM_PROVIDER}' not configured with API key. Skipping live API tests.")
class TestAIAnalysisLiveAPI(unittest.TestCase):
    # This class runs tests that make actual API calls.
    # It will be skipped if API keys are not found in the environment.

    def test_analyze_real_abstract_invention_potential(self):
        """Test AI analysis on a real abstract expected to have invention potential."""
        print("\nTesting live AI analysis on an abstract (potential invention)...")
        # Abstract known to describe a clear invention - e.g., CRISPR discovery paper by Doudna/Charpentier
        # PMID: 22745249 - "A Programmable Dual-RNA-Guided DNA Endonuclease in Adaptive Bacterial Immunity"
        # This is a very famous one, good candidate.
        pmid_invention = "22745249"
        details = fetch_publication_details(pmid_invention, email=config.NCBI_EMAIL)
        self.assertIsNotNone(details, f"Failed to fetch PMID {pmid_invention} for live test.")
        self.assertTrue(details.get("abstract") and details["abstract"] != "N/A", "Abstract is empty or N/A.")

        analysis_result = ai_analyzer.analyze_abstract_with_llm(details["abstract"]) # Call via module

        self.assertIsNotNone(analysis_result, "AI analysis returned None.")
        self.assertIn("is_potential_invention", analysis_result)
        self.assertIn("confidence_score", analysis_result)
        self.assertIn("reasoning", analysis_result)
        self.assertIn("keywords_suggesting_invention", analysis_result)

        print(f"Live analysis for PMID {pmid_invention} (potential invention):")
        print(json.dumps(analysis_result, indent=2))

        # We expect this to be an invention
        self.assertTrue(analysis_result["is_potential_invention"],
                        f"Expected PMID {pmid_invention} to be flagged as potential invention by LLM.")
        self.assertGreater(analysis_result["confidence_score"], 0.5, "Confidence should be reasonably high.")


    def test_analyze_real_abstract_no_invention_potential(self):
        """Test AI analysis on a real abstract expected to NOT have invention potential (e.g., a review or observational study)."""
        print("\nTesting live AI analysis on an abstract (no clear invention)...")
        # PMID for a review article or observational study.
        # e.g., PMID: 29243907 "The role of vitamin D in prevention and treatment of infection" (Review)
        pmid_no_invention = "29243907"
        details = fetch_publication_details(pmid_no_invention, email=config.NCBI_EMAIL)
        self.assertIsNotNone(details, f"Failed to fetch PMID {pmid_no_invention} for live test.")
        self.assertTrue(details.get("abstract") and details["abstract"] != "N/A", "Abstract is empty or N/A.")

        analysis_result = ai_analyzer.analyze_abstract_with_llm(details["abstract"]) # Call via module

        self.assertIsNotNone(analysis_result, "AI analysis returned None.")
        print(f"Live analysis for PMID {pmid_no_invention} (no clear invention):")
        print(json.dumps(analysis_result, indent=2))

        # We expect this to NOT be an invention
        self.assertFalse(analysis_result["is_potential_invention"],
                         f"Expected PMID {pmid_no_invention} (review) NOT to be flagged as potential invention.")


class TestAIAnalysisMocked(unittest.TestCase):
    # This class runs tests with mocked API calls, so it can run without real API keys.

    @patch('literature_invention_search.ai_analyzer.llm_client') # Path to llm_client in ai_analyzer
    def test_analyze_abstract_mocked_invention(self, mock_llm_client):
        print("\nTesting AI analysis with mocked API (invention case)...")

        # Configure the mock based on LLM_PROVIDER
        mock_response_content = {
            "is_potential_invention": True,
            "confidence_score": 0.9,
            "reasoning": "Mocked: Describes a novel method with clear advantages.",
            "keywords_suggesting_invention": ["novel method", "significant improvement"]
        }

        if config.LLM_PROVIDER == "openai":
            mock_chat_completion = MagicMock()
            mock_chat_completion.choices[0].message.content = json.dumps(mock_response_content)
            mock_llm_client.chat.completions.create.return_value = mock_chat_completion
        elif config.LLM_PROVIDER == "anthropic":
            mock_message = MagicMock()
            mock_message.content[0].text = json.dumps(mock_response_content)
            mock_llm_client.messages.create.return_value = mock_message
        else: # Fallback if provider is unknown, though ai_analyzer.llm_client would be None
            self.skipTest(f"Mocking not set up for provider: {config.LLM_PROVIDER}")
            return

        # Ensure ai_analyzer.llm_client is temporarily the mock IF it was None (keys not set)
        # This is tricky because ai_analyzer.llm_client is module-level.
        # The @patch decorator handles replacing it for the duration of this test.
        # We also need to ensure that ai_analyzer.config.LLM_PROVIDER is correctly set for the test.

        with patch('literature_invention_search.ai_analyzer.config.LLM_PROVIDER', config.LLM_PROVIDER), \
             patch('literature_invention_search.ai_analyzer.llm_client', mock_llm_client if ai_analyzer.llm_client is None else ai_analyzer.llm_client): # Use real client if configured, else mock

            # If ai_analyzer.llm_client was None (no API keys), the patch above makes it use our mock_llm_client.
            # If ai_analyzer.llm_client was already initialized (API keys ARE set), then the live tests cover it,
            # but this mocked test should still work by forcing the mock behavior for this one call path.
            # The patch should correctly target 'literature_invention_search.ai_analyzer.llm_client'.
            # If API keys *are* set, this test will still use the MOCKED client due to the patch.

            sample_abstract = "This abstract describes a groundbreaking new widget."
            analysis_result = ai_analyzer.analyze_abstract_with_llm(sample_abstract) # Call via module

            self.assertIsNotNone(analysis_result)
            self.assertTrue(analysis_result["is_potential_invention"])
            self.assertEqual(analysis_result["reasoning"], mock_response_content["reasoning"])
            print(f"Mocked analysis (invention): {json.dumps(analysis_result, indent=2)}")


    def test_handle_empty_or_na_abstract(self):
        """Test that empty, 'N/A', or very short abstracts are handled gracefully without calling LLM."""
        print("\nTesting handling of empty/NA/short abstracts...")

        # No need to mock LLM calls here as they should be skipped by pre-checks in ai_analyzer.analyze_abstract_with_llm

        na_abstract_result = ai_analyzer.analyze_abstract_with_llm("N/A") # Call via module
        self.assertIsNotNone(na_abstract_result)
        self.assertFalse(na_abstract_result["is_potential_invention"])
        self.assertIn("Abstract was empty, N/A, or too short", na_abstract_result["reasoning"])

        empty_abstract_result = ai_analyzer.analyze_abstract_with_llm("") # Call via module
        self.assertIsNotNone(empty_abstract_result)
        self.assertFalse(empty_abstract_result["is_potential_invention"])
        self.assertIn("Abstract was empty", empty_abstract_result["reasoning"])

        short_abstract_result = ai_analyzer.analyze_abstract_with_llm("Too short.") # Call via module
        self.assertIsNotNone(short_abstract_result)
        self.assertFalse(short_abstract_result["is_potential_invention"])
        self.assertIn("too short", short_abstract_result["reasoning"])
        print("Handling of empty/NA/short abstracts successful.")


class TestAIAnalysisIntegrationWithDB(unittest.TestCase):
    DB_FILE_PATH = ""
    TEST_PMID_FOR_AI = "12345678" # Dummy PMID for DB testing

    @classmethod
    def setUpClass(cls):
        cls.DB_FILE_PATH = DATABASE_PATH
        if os.path.exists(cls.DB_FILE_PATH):
            os.remove(cls.DB_FILE_PATH)
        initialize_database()
        print(f"Test database for AI integration tests initialized at: {cls.DB_FILE_PATH}")

        # Add a dummy paper to the DB for testing AI updates
        dummy_paper = {
            "pmid": cls.TEST_PMID_FOR_AI,
            "title": "Test Paper for AI Analysis",
            "abstract": "This is a test abstract about a novel method for testing.",
            "authors": "Tester T, CoTester CT",
            "publication_date": "2024-01-01",
            "download_date": "2024-01-01T00:00:00"
        }
        insert_paper(dummy_paper)

    def setUp(self):
        # Ensure the test paper has no AI analysis results before each test method in this class
        conn = sqlite3.connect(self.DB_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE papers
            SET ai_is_invention_candidate = NULL, ai_confidence = NULL, ai_reasoning = NULL
            WHERE pmid = ?
        """, (self.TEST_PMID_FOR_AI,))
        conn.commit()
        conn.close()

    # We need sqlite3 for the setUp method.
    @classmethod
    def import_sqlite(cls): # Helper to put import inside class if needed by test runner
        global sqlite3
        import sqlite3

    @patch('literature_invention_search.ai_analyzer.analyze_abstract_with_llm') # Patch at the source
    def test_update_paper_with_ai_analysis_results(self, mock_analyze_abstract_arg):
        print("\nTesting update of paper in DB with (mocked) AI analysis results...")
        # The mock_analyze_abstract_arg IS the mock for ai_analyzer.analyze_abstract_with_llm
        # We don't need the diagnostic print anymore if we call it correctly via the module.

        mock_ai_response = {
            "is_potential_invention": True,
            "confidence_score": 0.75,
            "reasoning": "Mocked: AI analysis indicates potential due to novel testing method.",
            "keywords_suggesting_invention": ["novel method", "testing"]
        }
        # Use the passed-in mock argument, which IS the mock object
        mock_analyze_abstract_arg.return_value = mock_ai_response

        paper_before_ai = get_paper_by_pmid(self.TEST_PMID_FOR_AI)
        self.assertIsNotNone(paper_before_ai)
        self.assertIsNotNone(paper_before_ai["abstract"]) # Make sure abstract exists to be "analyzed"

        # "Call" the AI analysis via the (now mocked at source) module.
        ai_results = ai_analyzer.analyze_abstract_with_llm(paper_before_ai["abstract"])
        self.assertIsNotNone(ai_results)

        # Update the database
        update_success = update_paper_ai_analysis(
            pmid=self.TEST_PMID_FOR_AI,
            ai_is_invention_candidate=ai_results["is_potential_invention"],
            ai_confidence=ai_results["confidence_score"],
            ai_reasoning=ai_results["reasoning"]
            # Keywords are not directly stored in the main table per current schema,
            # but could be part of reasoning or a separate field/table if needed.
        )
        self.assertTrue(update_success, "Failed to update paper with AI results in DB.")

        paper_after_ai = get_paper_by_pmid(self.TEST_PMID_FOR_AI)
        self.assertIsNotNone(paper_after_ai)
        self.assertEqual(paper_after_ai["ai_is_invention_candidate"], mock_ai_response["is_potential_invention"])
        self.assertAlmostEqual(paper_after_ai["ai_confidence"], mock_ai_response["confidence_score"])
        self.assertEqual(paper_after_ai["ai_reasoning"], mock_ai_response["reasoning"])

        print("DB update with AI analysis results successful.")


if __name__ == "__main__":
    # This allows running tests like: python -m literature_invention_search.test_analysis
    # It will run all test classes unless API keys are missing for the live tests.
    TestAIAnalysisIntegrationWithDB.import_sqlite() # Ensure sqlite3 is available for the class
    unittest.main()

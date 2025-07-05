import unittest
import os
from datetime import datetime

# Imports assuming the test is run as part of a package, e.g., from the project root:
# python -m unittest literature_invention_search.test_one_paper
# or python -m unittest discover -s literature_invention_search
from .simple_ncbi import fetch_publication_details
from .simple_database import initialize_database, insert_paper, get_paper_by_pmid, DATABASE_PATH


class TestOnePaperPipeline(unittest.TestCase):

    TEST_PMID = "38356490" # A recent, valid PMID for testing
    DB_FILE_PATH = "" # Will be set in setUpClass

    @classmethod
    def setUpClass(cls):
        """
        Set up the database for tests.
        This runs once before any tests in the class.
        """
        # Use the DATABASE_PATH from simple_database.py to ensure consistency
        cls.DB_FILE_PATH = DATABASE_PATH

        # Ensure a clean database for each test run
        if os.path.exists(cls.DB_FILE_PATH):
            os.remove(cls.DB_FILE_PATH)

        initialize_database()
        print(f"Test database initialized at: {cls.DB_FILE_PATH}")

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the database file after all tests are done.
        """
        # if os.path.exists(cls.DB_FILE_PATH):
        #     os.remove(cls.DB_FILE_PATH)
        #     print(f"Test database cleaned up: {cls.DB_FILE_PATH}")
        pass # Keep DB for inspection if needed, or enable removal

    def test_fetch_and_store_one_paper(self):
        """
        Tests fetching metadata for one paper from NCBI and storing it in the SQLite database.
        Verifies that the stored data matches the fetched data.
        """
        print(f"\nTesting with PMID: {self.TEST_PMID}")

        # 1. Fetch publication details from NCBI
        # Provide a dummy email for polite API usage, even if not strictly enforced for small queries
        fetched_details = fetch_publication_details(self.TEST_PMID, email="test@example.com")

        self.assertIsNotNone(fetched_details, f"Failed to fetch details for PMID {self.TEST_PMID}")
        self.assertEqual(fetched_details["pmid"], self.TEST_PMID)
        self.assertTrue(fetched_details["title"] != "N/A" and fetched_details["title"] is not None)
        # Abstract can sometimes be N/A for certain publication types or if not available
        # self.assertTrue(fetched_details["abstract"] != "N/A" and fetched_details["abstract"] is not None)
        print(f"Successfully fetched: {fetched_details['title'][:50]}...")

        # 2. Prepare data for database insertion (add download_date)
        paper_to_store = fetched_details.copy()
        paper_to_store["download_date"] = datetime.now().isoformat()
        # AI fields will be None/NULL by default from schema or insert_paper logic

        # 3. Store in SQLite database
        insertion_success = insert_paper(paper_to_store)
        self.assertTrue(insertion_success, f"Failed to insert paper PMID {self.TEST_PMID} into database.")
        print(f"Successfully inserted PMID {self.TEST_PMID} into database.")

        # 4. Retrieve from database
        stored_paper = get_paper_by_pmid(self.TEST_PMID)
        self.assertIsNotNone(stored_paper, f"Paper PMID {self.TEST_PMID} not found in database after insertion.")
        print(f"Successfully retrieved PMID {self.TEST_PMID} from database.")

        # 5. Verify stored data
        self.assertEqual(stored_paper["pmid"], fetched_details["pmid"])
        self.assertEqual(stored_paper["title"], fetched_details["title"])
        self.assertEqual(stored_paper["abstract"], fetched_details["abstract"])
        self.assertEqual(stored_paper["authors"], fetched_details["authors"])
        self.assertEqual(stored_paper["publication_date"], fetched_details["publication_date"])
        self.assertIn("download_date", stored_paper)
        self.assertIsNotNone(stored_paper["download_date"])

        # Check that AI fields are present and are None initially
        self.assertIn("ai_is_invention_candidate", stored_paper)
        self.assertIsNone(stored_paper["ai_is_invention_candidate"])
        self.assertIn("ai_confidence", stored_paper)
        self.assertIsNone(stored_paper["ai_confidence"])
        self.assertIn("ai_reasoning", stored_paper)
        self.assertIsNone(stored_paper["ai_reasoning"])

        print("Verification of stored data successful.")

if __name__ == "__main__":
    # This allows running the test directly, e.g., python literature_invention_search/test_one_paper.py
    # For this to work, ensure that the CWD is the project root, or adjust PYTHONPATH.
    # If running from project_root: python -m literature_invention_search.test_one_paper

    # If simple_database.DATABASE_PATH is correctly set up (relative to simple_database.py),
    # this should work fine.

    # unittest.main() needs to be able to find the modules.
    # If running from `literature_invention_search` directory: `python test_one_paper.py`
    # If running from project root: `python -m literature_invention_search.test_one_paper`

    # Hack to allow running from `literature_invention_search` dir for convenience during dev
    # if os.path.basename(os.getcwd()) == "literature_invention_search":
    #     # If CWD is the package dir, add parent to path to resolve package-level imports if any
    #     # or to make sibling imports work more like they would in a package context.
    #     # This is generally not needed if using `python -m ...`
    #     pass

    unittest.main()

import unittest
import os
import sqlite3 # For direct DB inspection

try:
    from .batch_processor import process_batch, search_pubmed_pmids
    from .simple_database import initialize_database, get_all_papers, DATABASE_PATH, get_paper_by_pmid
    from . import config
except ImportError:
    from batch_processor import process_batch, search_pubmed_pmids
    from simple_database import initialize_database, get_all_papers, DATABASE_PATH, get_paper_by_pmid
    import config

class TestBatchProcessing(unittest.TestCase):

    DB_FILE_PATH = ""

    @classmethod
    def setUpClass(cls):
        cls.DB_FILE_PATH = DATABASE_PATH
        if os.path.exists(cls.DB_FILE_PATH):
            os.remove(cls.DB_FILE_PATH)
        initialize_database()
        print(f"Test database for batch tests initialized at: {cls.DB_FILE_PATH}")

    def setUp(self):
        # Clean and re-initialize database before each test method
        if os.path.exists(self.DB_FILE_PATH):
            os.remove(self.DB_FILE_PATH)
        initialize_database()
        # print("Database cleared for new test method.")

    @classmethod
    def tearDownClass(cls):
        # if os.path.exists(cls.DB_FILE_PATH):
        #     os.remove(cls.DB_FILE_PATH)
        #     print(f"Test database for batch tests cleaned up: {cls.DB_FILE_PATH}")
        pass

    def test_search_pubmed_pmids(self):
        """Test the ESearch functionality to retrieve PMIDs."""
        print("\nTesting search_pubmed_pmids...")
        # Using a common term that should yield results.
        # "Nature[Journal]" is a good general term.
        # For CCHMC, use the config search term but limit results.
        test_search_term = "Nature[Journal]"
        max_results = 5

        pmids = search_pubmed_pmids(
            term=test_search_term,
            retmax=max_results,
            api_key=config.NCBI_API_KEY,
            email=config.NCBI_EMAIL
        )

        self.assertIsInstance(pmids, list, "ESearch should return a list.")
        self.assertTrue(len(pmids) <= max_results, f"ESearch returned more than {max_results} PMIDs.")
        if len(pmids) > 0: # If any PMIDs were found
            self.assertTrue(all(isinstance(pmid, str) and pmid.isdigit() for pmid in pmids), "All PMIDs should be strings of digits.")
        print(f"search_pubmed_pmids returned {len(pmids)} PMIDs for '{test_search_term}'.")


    def test_process_small_batch(self):
        """Test processing a small batch of new papers."""
        print("\nTesting process_small_batch...")
        max_to_process = 3 # Small number for a quick test

        # Using a specific search term that is likely to yield results
        # CCHMC search term from config
        results_summary = process_batch(
            search_term=config.SEARCH_TERM_AFFILIATION,
            max_papers_to_process=max_to_process,
            check_existing_in_db=True # Default, but explicit
        )

        self.assertLessEqual(results_summary["processed_newly"], max_to_process)
        # It's possible that fewer than max_to_process are found or successfully processed

        db_papers = get_all_papers()
        self.assertEqual(len(db_papers), results_summary["processed_newly"],
                         "Number of papers in DB should match processed_newly count.")

        print(f"process_small_batch results: {results_summary}")
        print(f"Total papers in DB after small batch: {len(db_papers)}")


    def test_process_batch_with_existing_papers(self):
        """Test that batch processing correctly skips already existing papers."""
        print("\nTesting process_batch_with_existing_papers...")
        initial_max_to_process = 2

        # First run: process and store some papers
        print("First run to populate database...")
        summary_first_run = process_batch(
            search_term=config.SEARCH_TERM_AFFILIATION, # Use a consistent search term
            max_papers_to_process=initial_max_to_process
        )
        num_processed_first_run = summary_first_run["processed_newly"]
        self.assertTrue(num_processed_first_run > 0, "First run should process at least one paper to test skipping.")

        papers_after_first_run = get_all_papers()
        self.assertEqual(len(papers_after_first_run), num_processed_first_run)
        print(f"Papers in DB after first run: {num_processed_first_run}")

        # Second run: attempt to process more, some should be skipped
        # Try to process more papers than the first run, using the same search term
        # This should find the same initial papers plus potentially new ones.
        print("\nSecond run, expecting skips...")
        # If the first run got 2, and we ask for 3 now, it should skip 2 and get 1 new one (if available)
        # or just skip 2 and get 0 new ones if no more are found by search.
        target_for_second_run = num_processed_first_run + 1

        summary_second_run = process_batch(
            search_term=config.SEARCH_TERM_AFFILIATION,
            max_papers_to_process=target_for_second_run, # Target total new papers across both runs effectively
            check_existing_in_db=True
        )

        # The number of "existing_skipped" should be at least the number processed in the first run,
        # assuming the search query retrieves those same PMIDs again.
        # This can be tricky if search results are not perfectly stable or if retmax in esearch was too small.
        # For this test, process_batch internally calls search_pubmed_pmids with retmax = max_papers_to_process * 2
        # So it should re-find the initial papers.

        self.assertGreaterEqual(summary_second_run["existing_skipped"], num_processed_first_run,
                                "Second run should have skipped papers from the first run.")

        total_papers_in_db_after_second_run = len(get_all_papers())

        # Total unique papers in DB should be:
        # (papers from 1st run) + (newly processed in 2nd run)
        # newly processed in 2nd run = summary_second_run["processed_newly"]
        # This is NOT target_for_second_run, as that's the *goal* for new papers in this specific call

        # The total number of unique papers in the DB should be sum of new papers from run 1 and run 2
        expected_total_in_db = num_processed_first_run + summary_second_run["processed_newly"]
        self.assertEqual(total_papers_in_db_after_second_run, expected_total_in_db,
                         "Total papers in DB after second run is incorrect.")

        print(f"process_batch_with_existing_papers results (second run): {summary_second_run}")
        print(f"Total papers in DB after second run: {total_papers_in_db_after_second_run}")

    def test_process_batch_limit(self):
        """Test that batch processing respects max_papers_to_process limit."""
        print("\nTesting process_batch_limit...")
        limit = 1 # Process only one new paper

        # Ensure DB is empty for this specific test case regarding "new" papers
        if os.path.exists(self.DB_FILE_PATH):
            os.remove(self.DB_FILE_PATH)
        initialize_database()

        summary = process_batch(
            search_term=config.SEARCH_TERM_AFFILIATION,
            max_papers_to_process=limit
        )

        # It might fetch 0 if no papers match or all fail.
        # If papers are found, it should process at most 'limit'.
        self.assertLessEqual(summary["processed_newly"], limit,
                             "Number of newly processed papers should not exceed the specified limit.")

        papers_in_db = get_all_papers()
        self.assertEqual(len(papers_in_db), summary["processed_newly"])

        print(f"process_batch_limit results: {summary}")
        print(f"Total papers in DB after limit test: {len(papers_in_db)}")


if __name__ == "__main__":
    # To run these tests:
    # From project root: python -m literature_invention_search.test_batch
    # Or from literature_invention_search dir: python test_batch.py (if imports are set up for it)
    unittest.main()

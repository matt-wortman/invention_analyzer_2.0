import time
from typing import List, Optional, Dict, Any
import requests # For ESearch
import xml.etree.ElementTree as ET # For ESearch parsing

# Assuming these modules are in the same directory or package
try:
    from .simple_ncbi import fetch_publication_details, EUTILS_BASE_URL
    from .simple_database import insert_paper, get_paper_by_pmid, initialize_database
    from . import config
except ImportError:
    # Fallback for potential local execution or testing setups
    from simple_ncbi import fetch_publication_details, EUTILS_BASE_URL
    from simple_database import insert_paper, get_paper_by_pmid, initialize_database
    import config


def search_pubmed_pmids(term: str, retmax: int = 20, api_key: Optional[str] = None, email: Optional[str] = None) -> List[str]:
    """
    Searches PubMed for PMIDs matching the given term.

    Args:
        term: The search term (e.g., author, affiliation, keywords).
        retmax: Maximum number of PMIDs to return.
        api_key: NCBI API key.
        email: Email for NCBI.

    Returns:
        A list of PMIDs.
    """
    search_params = {
        "db": "pubmed",
        "term": term,
        "retmax": str(retmax),
        "retmode": "xml", # Get PMIDs in XML format
        "field": "affiliation", # Example: search in affiliation field; consider making this configurable
        # For more complex queries including date ranges, term can be structured like:
        # (("YYYY/MM/DD"[Date - Publication] : "YYYY/MM/DD"[Date - Publication])) AND (your search term)
    }
    if api_key:
        search_params["api_key"] = api_key

    headers = {}
    if email:
        headers["From"] = email

    pmids: List[str] = []
    try:
        response = requests.get(EUTILS_BASE_URL + "esearch.fcgi", params=search_params, headers=headers)
        response.raise_for_status()

        xml_root = ET.fromstring(response.content)
        id_list_node = xml_root.find(".//IdList")
        if id_list_node is not None:
            for id_node in id_list_node.findall(".//Id"):
                if id_node.text:
                    pmids.append(id_node.text)

        count_node = xml_root.find(".//Count")
        total_found = count_node.text if count_node is not None else 'N/A'
        print(f"ESearch found {total_found} PMIDs for term '{term}'. Returning up to {retmax}.")

    except requests.exceptions.RequestException as e:
        print(f"Error during PubMed ESearch: {e}")
    except ET.ParseError as e:
        print(f"Error parsing ESearch XML response: {e}")

    return pmids


def process_batch(
    search_term: str = config.SEARCH_TERM_AFFILIATION,
    max_papers_to_process: int = config.DEFAULT_MAX_PAPERS_TO_PROCESS,
    check_existing_in_db: bool = True,
    delay_between_requests: float = 0.34 # NCBI recommends ~3 requests/second without API key
    ) -> Dict[str, int]:
    """
    Processes a batch of papers: searches PubMed, fetches details, and stores them.

    Args:
        search_term: Term to search on PubMed.
        max_papers_to_process: Max number of new papers to fetch and store.
        check_existing_in_db: If True, skip PMIDs already in the database.
        delay_between_requests: Seconds to wait between NCBI API calls.

    Returns:
        A dictionary with counts of processed, new, existing, and failed papers.
    """
    initialize_database() # Ensure DB and table exist

    print(f"Starting batch processing for term: '{search_term}'")
    print(f"Maximum new papers to process: {max_papers_to_process}")

    # 1. Search PubMed for PMIDs
    # We might need to fetch more PMIDs from esearch than max_papers_to_process
    # if we are skipping already existing ones. Let's fetch a bit more.
    pmids_to_consider_fetching = search_pubmed_pmids(
        term=search_term,
        retmax=max_papers_to_process * 2 if check_existing_in_db else max_papers_to_process, # Fetch more if filtering
        api_key=config.NCBI_API_KEY,
        email=config.NCBI_EMAIL
    )

    if not pmids_to_consider_fetching:
        print("No PMIDs found or ESearch failed. Batch processing stopped.")
        return {"processed": 0, "new": 0, "existing_skipped": 0, "failed": 0}

    new_papers_processed = 0
    existing_skipped_count = 0
    failed_count = 0

    # 2. Fetch and store details for each PMID
    for pmid in pmids_to_consider_fetching:
        if new_papers_processed >= max_papers_to_process:
            print(f"Reached target of {max_papers_to_process} new papers. Stopping.")
            break

        print(f"\nProcessing PMID: {pmid}")

        # Optionally, check if paper already exists in DB
        if check_existing_in_db and get_paper_by_pmid(pmid):
            print(f"PMID {pmid} already exists in the database. Skipping.")
            existing_skipped_count += 1
            continue

        # Fetch details from NCBI
        paper_details = fetch_publication_details(
            pmid,
            api_key=config.NCBI_API_KEY,
            email=config.NCBI_EMAIL
        )

        if paper_details:
            # Store in database
            if insert_paper(paper_details):
                print(f"Successfully fetched and stored PMID {pmid}: {paper_details['title'][:60]}...")
                new_papers_processed += 1
            else:
                print(f"Failed to store PMID {pmid} in database.")
                failed_count += 1
        else:
            print(f"Failed to fetch details for PMID {pmid}.")
            failed_count += 1

        # Respect NCBI API rate limits
        time.sleep(delay_between_requests)

    total_attempted_for_detail_fetch = len(pmids_to_consider_fetching) # Or more accurately, the loop iterations
    print("\nBatch processing summary:")
    print(f"  PMIDs considered from search: {len(pmids_to_consider_fetching)}")
    print(f"  New papers fetched and stored: {new_papers_processed}")
    print(f"  Existing papers skipped: {existing_skipped_count}")
    print(f"  Failed to fetch/store: {failed_count}")

    return {
        "processed_newly": new_papers_processed,
        "existing_skipped": existing_skipped_count,
        "failed": failed_count,
        "total_from_search_list": len(pmids_to_consider_fetching)
    }

if __name__ == '__main__':
    # Example of running the batch processor
    # This will use settings from config.py

    # For a quick test, let's reduce the number of papers to process
    # You can override config defaults by passing arguments to process_batch
    print("Running batch processor example...")
    results = process_batch(
        search_term=config.SEARCH_TERM_AFFILIATION, # Test with the configured affiliation
        max_papers_to_process=5, # Override for a smaller test run
        check_existing_in_db=True
    )
    print(f"\nExample run completed. Results: {results}")

    # To test with a different search term:
    # print("\nRunning batch processor example with a specific author...")
    # results_author = process_batch(
    #     search_term="Eisenstein[Author]", # Example: papers by author "Eisenstein"
    #     max_papers_to_process=3
    # )
    # print(f"\nAuthor search run completed. Results: {results_author}")

import requests
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List, Any

# NCBI E-utilities base URL
EUTILS_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

def fetch_publication_details(pmid: str, api_key: Optional[str] = None, email: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Fetches publication details for a given PubMed ID (PMID).

    Args:
        pmid: The PubMed ID of the publication.
        api_key: NCBI API key (optional but recommended).
        email: Email address for NCBI (optional but recommended for rate limits).

    Returns:
        A dictionary containing publication details (PMID, title, abstract, authors,
        publication_date) or None if an error occurs or the paper is not found.
    """
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml",
        "rettype": "abstract" # Fetch abstract and metadata
    }
    if api_key:
        params["api_key"] = api_key

    headers = {}
    if email:
        headers["From"] = email

    try:
        response = requests.get(EUTILS_BASE_URL + "efetch.fcgi", params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        xml_root = ET.fromstring(response.content)

        article_node = xml_root.find(".//PubmedArticle")
        if article_node is None:
            print(f"No PubmedArticle found for PMID {pmid}")
            return None

        medline_citation_node = article_node.find(".//MedlineCitation")
        if medline_citation_node is None:
            print(f"No MedlineCitation found for PMID {pmid}")
            return None

        article_data_node = medline_citation_node.find(".//Article")
        if article_data_node is None:
            print(f"No Article data found for PMID {pmid}")
            return None

        # Title
        title_node = article_data_node.find(".//ArticleTitle")
        title = title_node.text if title_node is not None and title_node.text else "N/A"

        # Abstract
        abstract_text_parts = []
        abstract_node = article_data_node.find(".//Abstract")
        if abstract_node is not None:
            for part_node in abstract_node.findall(".//AbstractText"):
                if part_node.text:
                    abstract_text_parts.append(part_node.text)
        abstract = " ".join(abstract_text_parts) if abstract_text_parts else "N/A"

        # Authors
        authors_list = []
        author_list_node = article_data_node.find(".//AuthorList")
        if author_list_node is not None:
            for author_node in author_list_node.findall(".//Author"):
                last_name_node = author_node.find(".//LastName")
                fore_name_node = author_node.find(".//ForeName")
                last_name = last_name_node.text if last_name_node is not None else ""
                fore_name = fore_name_node.text if fore_name_node is not None else ""
                if last_name or fore_name: # Only add if there's some name info
                    authors_list.append(f"{fore_name} {last_name}".strip())
        authors_str = ", ".join(authors_list) if authors_list else "N/A"

        # Publication Date
        # Trying to find PubDate, then MedlineDate as fallback
        pub_date_node = article_data_node.find(".//Journal/JournalIssue/PubDate")
        pub_year, pub_month, pub_day = "N/A", "N/A", "N/A"

        if pub_date_node is not None:
            year_node = pub_date_node.find(".//Year")
            month_node = pub_date_node.find(".//Month")
            day_node = pub_date_node.find(".//Day")

            if year_node is not None and year_node.text:
                pub_year = year_node.text
            if month_node is not None and month_node.text:
                # Convert month from text (e.g., Jan) to number if possible, otherwise use as is
                try:
                    month_num = datetime.strptime(month_node.text, "%b").month
                    pub_month = str(month_num).zfill(2)
                except ValueError:
                    pub_month = month_node.text # Keep as text if not recognized format
            if day_node is not None and day_node.text:
                pub_day = day_node.text.zfill(2)

        # Fallback for date if not found in standard PubDate structure
        if pub_year == "N/A":
            medline_date_node = pub_date_node.find(".//MedlineDate") if pub_date_node is not None else None
            if medline_date_node is None: # If pub_date_node was None or MedlineDate not in it
                 medline_date_node = article_data_node.find(".//ArticleDate") # Try ArticleDate
                 if medline_date_node is None:
                     medline_date_node = medline_citation_node.find(".//DateRevised") # Last resort


            if medline_date_node is not None and medline_date_node.text:
                # MedlineDate format is usually "YYYY Mon DD" or "YYYY Season" or "YYYY"
                # This is a simplistic parse, might need refinement
                date_str = medline_date_node.text.split(" ")[0]
                if date_str.isdigit() and len(date_str) == 4:
                    pub_year = date_str
                # Could add more parsing for MedlineDate if necessary

        publication_date_str = f"{pub_year}-{pub_month}-{pub_day}"
        # Clean up if parts are N/A
        if pub_month == "N/A": publication_date_str = pub_year
        elif pub_day == "N/A": publication_date_str = f"{pub_year}-{pub_month}"


        # PMID from MedlineCitation
        pmid_node = medline_citation_node.find(".//PMID")
        extracted_pmid = pmid_node.text if pmid_node is not None and pmid_node.text else pmid

        return {
            "pmid": extracted_pmid,
            "title": title,
            "abstract": abstract,
            "authors": authors_str,
            "publication_date": publication_date_str,
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching PMID {pmid}: {e}")
        return None
    except ET.ParseError as e:
        print(f"Error parsing XML for PMID {pmid}: {e}")
        return None

if __name__ == '__main__':
    # Example usage:
    # Replace with your actual email and API key if you have them
    # For testing, you often don't need them for a few requests.
    TEST_EMAIL = "jules@example.com" # Replace with a real email for polite usage
    TEST_API_KEY = None # Replace with your NCBI API key if you have one

    # Test with a known PMID that has full date components
    # pmid_to_test = "31346167" # Example with Year, Month, Day
    # Test with a PMID that might have MedlineDate
    pmid_to_test = "18233153" # Example that might use MedlineDate or other date forms
    # pmid_to_test = "25505027" # Example from plan - this one is very old, might have issues

    # Test with a newer PMID as per plan's example (40562540 is not a valid PMID format)
    # Let's pick a recent valid one, e.g., from 2023 for "Cincinnati Children's Hospital"
    # A quick search reveals PMID 38017825 as a possibility.
    pmid_to_test_recent = "38017825"


    print(f"Fetching details for PMID: {pmid_to_test}")
    details = fetch_publication_details(pmid_to_test, api_key=TEST_API_KEY, email=TEST_EMAIL)
    if details:
        print(JSON_DETAILS := json.dumps(details, indent=4))
    else:
        print("Failed to retrieve details.")

    print(f"\nFetching details for recent PMID: {pmid_to_test_recent}")
    details_recent = fetch_publication_details(pmid_to_test_recent, api_key=TEST_API_KEY, email=TEST_EMAIL)
    if details_recent:
        print(JSON_DETAILS_RECENT := json.dumps(details_recent, indent=4))
    else:
        print("Failed to retrieve details for recent PMID.")

    # Test case for a paper that might not have a typical abstract structure
    # pmid_no_abstract_example = "17223999" # Example: Review article that might have odd abstract
    # print(f"\nFetching details for PMID with potentially unusual abstract: {pmid_no_abstract_example}")
    # details_no_abstract = fetch_publication_details(pmid_no_abstract_example, api_key=TEST_API_KEY, email=TEST_EMAIL)
    # if details_no_abstract:
    #     print(json.dumps(details_no_abstract, indent=4))
    # else:
    #     print("Failed to retrieve details.")

    # Example of a PMID that might not exist or has an issue
    # pmid_problematic = "99999999"
    # print(f"\nFetching details for problematic PMID: {pmid_problematic}")
    # details_problematic = fetch_publication_details(pmid_problematic, api_key=TEST_API_KEY, email=TEST_EMAIL)
    # if details_problematic:
    #     print(json.dumps(details_problematic, indent=4))
    # else:
    #     print(f"Failed to retrieve details for {pmid_problematic}, as expected for a non-existent PMID.")

    # Example of a PMID that is valid but content might be restricted or different
    # pmid_restricted_example = "123456" # Usually very old PMIDs
    # print(f"\nFetching details for old PMID: {pmid_restricted_example}")
    # details_restricted = fetch_publication_details(pmid_restricted_example, api_key=TEST_API_KEY, email=TEST_EMAIL)
    # if details_restricted:
    #     print(json.dumps(details_restricted, indent=4))
    # else:
    #     print(f"Failed to retrieve details for {pmid_restricted_example}.")
    pass # End of main
# Add datetime import for date parsing
import json # For pretty printing the dict in example
from datetime import datetime # For date parsing

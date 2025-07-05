import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

# Construct the path to the database file relative to this script's location
# This ensures it's always placed inside 'literature_invention_search'
# Assuming this script is in 'literature_invention_search/'
# and 'papers.db' should also be in 'literature_invention_search/'
DATABASE_FILE_NAME = "papers.db"
# Get the directory where simple_database.py is located
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# DATABASE_PATH = os.path.join(SCRIPT_DIR, DATABASE_FILE_NAME)

# Path to the database file, assuming scripts might be run from project root
# or that the 'literature_invention_search' directory will be in PYTHONPATH.
# For direct execution of this script from project root, or for other scripts in project root
# importing this, this path is correct.
# If simple_database.py is run itself from within literature_invention_search,
# then "papers.db" would suffice. The REBUILD_PLAN puts main.py inside this dir.
# Let's ensure the db path is relative to the intended project structure.
# The plan shows: literature_invention_search/papers.db
# If main.py is in literature_invention_search/ and calls functions from here,
# and CWD is literature_invention_search/, then "papers.db" is correct.
# To be safe if scripts are run from parent dir:
DATABASE_PATH = "literature_invention_search/papers.db"
# However, the initial empty papers.db was created at `literature_invention_search/papers.db`
# And this script itself is `literature_invention_search/simple_database.py`.
# If this script is run, and CWD is `literature_invention_search`, then "papers.db" is fine.
# If CWD is project root, then "literature_invention_search/papers.db" is needed.

# Let's assume the structure from REBUILD_PLAN.md where all these .py files
# are in literature_invention_search/ and main.py is also there.
# In that context, "papers.db" is the most direct.
# The `create_file_with_block` for papers.db created it at `literature_invention_search/papers.db`.
# So, if this script is run from the root, it needs the prefix. If run from its own dir, it doesn't.

# To make it robust: resolve path relative to this file's location.
# This ensures that no matter where the script is called from, it finds papers.db
# in the same directory as simple_database.py.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(SCRIPT_DIR, DATABASE_FILE_NAME)


def get_db_connection():
    """Establishes a connection to the SQLite database."""
    # Ensure the directory for the database exists, if it's specified with a path
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir) # Should not be necessary given plan step 1 created the dir

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

def initialize_database():
    """
    Initializes the database by creating the 'papers' table if it doesn't exist.
    The schema includes fields for paper metadata and AI analysis results.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS papers (
        pmid TEXT PRIMARY KEY,
        title TEXT,
        abstract TEXT,
        authors TEXT,
        publication_date TEXT, -- Store as TEXT, e.g., "YYYY-MM-DD" or "YYYY-MM" or "YYYY"
        download_date TEXT,
        -- Fields for AI analysis (added based on plan step 4)
        ai_is_invention_candidate BOOLEAN,
        ai_confidence REAL, -- e.g., 0.0 to 1.0
        ai_reasoning TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_paper(paper_data: Dict[str, Any]) -> bool:
    """
    Inserts or updates a paper's metadata into the database.
    If a paper with the same PMID already exists, it will be updated.

    Args:
        paper_data: A dictionary containing paper details (pmid, title, abstract, etc.).
                    It should also include 'download_date'.

    Returns:
        True if insertion/update was successful, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure download_date is set
    if 'download_date' not in paper_data:
        paper_data['download_date'] = datetime.now().isoformat()

    # Prepare data for insertion or replacement
    # Initialize AI fields to None if not provided
    data_to_insert = {
        "pmid": paper_data.get("pmid"),
        "title": paper_data.get("title"),
        "abstract": paper_data.get("abstract"),
        "authors": paper_data.get("authors"),
        "publication_date": paper_data.get("publication_date"),
        "download_date": paper_data.get("download_date"),
        "ai_is_invention_candidate": paper_data.get("ai_is_invention_candidate"), # Will be None initially
        "ai_confidence": paper_data.get("ai_confidence"), # Will be None initially
        "ai_reasoning": paper_data.get("ai_reasoning") # Will be None initially
    }

    try:
        cursor.execute("""
        INSERT OR REPLACE INTO papers (
            pmid, title, abstract, authors, publication_date, download_date,
            ai_is_invention_candidate, ai_confidence, ai_reasoning
        ) VALUES (:pmid, :title, :abstract, :authors, :publication_date, :download_date,
                  :ai_is_invention_candidate, :ai_confidence, :ai_reasoning)
        """, data_to_insert)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error during insert/replace for PMID {data_to_insert.get('pmid')}: {e}")
        return False
    finally:
        conn.close()

def get_paper_by_pmid(pmid: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a paper from the database by its PMID.

    Args:
        pmid: The PubMed ID of the paper to retrieve.

    Returns:
        A dictionary representing the paper if found, otherwise None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM papers WHERE pmid = ?", (pmid,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_papers() -> List[Dict[str, Any]]:
    """Retrieves all papers from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM papers")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_paper_ai_analysis(pmid: str, ai_is_invention_candidate: bool, ai_confidence: float, ai_reasoning: str) -> bool:
    """
    Updates a paper's record with AI analysis results.

    Args:
        pmid: The PMID of the paper to update.
        ai_is_invention_candidate: Boolean indicating if it's a potential invention.
        ai_confidence: Confidence score from the AI.
        ai_reasoning: Reasoning from the AI.

    Returns:
        True if update was successful, False otherwise.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        UPDATE papers
        SET ai_is_invention_candidate = ?,
            ai_confidence = ?,
            ai_reasoning = ?
        WHERE pmid = ?
        """, (ai_is_invention_candidate, ai_confidence, ai_reasoning, pmid))
        conn.commit()
        return cursor.rowcount > 0 # Check if any row was updated
    except sqlite3.Error as e:
        print(f"Database error during AI analysis update for PMID {pmid}: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    # Example Usage:
    initialize_database() # Ensure table exists

    # Test data
    sample_paper_1 = {
        "pmid": "12345678",
        "title": "Sample Paper Title 1",
        "abstract": "This is the abstract for sample paper 1.",
        "authors": "Author A, Author B",
        "publication_date": "2023-01-15",
        "download_date": datetime.now().isoformat()
    }
    sample_paper_2 = {
        "pmid": "87654321",
        "title": "Sample Paper Title 2",
        "abstract": "Abstract for sample paper 2, discussing innovations.",
        "authors": "Author C, Author D",
        "publication_date": "2022-11-20",
        # download_date will be added by insert_paper
    }

    # Insert papers
    print(f"Inserting paper {sample_paper_1['pmid']}: {insert_paper(sample_paper_1)}")
    print(f"Inserting paper {sample_paper_2['pmid']}: {insert_paper(sample_paper_2)}")

    # Retrieve a paper
    retrieved_paper = get_paper_by_pmid("12345678")
    if retrieved_paper:
        print(f"\nRetrieved paper 12345678: {retrieved_paper['title']}")
        assert retrieved_paper['abstract'] == sample_paper_1['abstract']
    else:
        print("Paper 12345678 not found.")

    # Test duplicate insertion (should update)
    updated_paper_1 = {
        "pmid": "12345678",
        "title": "Sample Paper Title 1 (Updated)",
        "abstract": "This is the updated abstract.",
        "authors": "Author A, Author B, Author E",
        "publication_date": "2023-01-18",
    }
    print(f"Updating paper {updated_paper_1['pmid']}: {insert_paper(updated_paper_1)}")
    retrieved_updated_paper = get_paper_by_pmid("12345678")
    if retrieved_updated_paper:
        print(f"Retrieved updated paper 12345678: {retrieved_updated_paper['title']}")
        assert retrieved_updated_paper['abstract'] == updated_paper_1['abstract']
        assert 'download_date' in retrieved_updated_paper # Should persist or be updated

    # Test AI analysis update
    print(f"\nUpdating AI analysis for {sample_paper_2['pmid']}...")
    ai_update_status = update_paper_ai_analysis(
        pmid="87654321",
        ai_is_invention_candidate=True,
        ai_confidence=0.85,
        ai_reasoning="The abstract mentions novel methods and significant results."
    )
    print(f"AI Update status for 87654321: {ai_update_status}")

    paper_with_ai = get_paper_by_pmid("87654321")
    if paper_with_ai:
        print(f"Paper 87654321 AI candidate: {paper_with_ai['ai_is_invention_candidate']}")
        print(f"Paper 87654321 AI confidence: {paper_with_ai['ai_confidence']}")
        assert paper_with_ai['ai_is_invention_candidate'] == True
        assert paper_with_ai['ai_confidence'] == 0.85

    # List all papers
    all_db_papers = get_all_papers()
    print(f"\nTotal papers in DB: {len(all_db_papers)}")
    for p in all_db_papers:
        print(f"  - {p['pmid']}: {p['title']} (AI candidate: {p.get('ai_is_invention_candidate')})")

    print("\nDatabase tests complete.")

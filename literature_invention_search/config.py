# Configuration for the Academic Publication Search Tool

# NCBI E-utilities related configuration
NCBI_API_KEY = None  # Enter your NCBI API key here if you have one
NCBI_EMAIL = "jules@example.com"  # Replace with a real email for polite API usage

# PubMed search parameters
# Search term for Cincinnati Children's Hospital and its variations.
# Using a common affiliation search tag [Affiliation] or [AD]
# More complex queries can be built, e.g., including date ranges.
# For Phase 1, keeping it simple.
SEARCH_TERM_AFFILIATION = (
    "Cincinnati Children's Hospital Medical Center[Affiliation] OR "
    "Cincinnati Childrens Hospital Medical Center[Affiliation] OR "
    "Cincinnati Children's Hospital[Affiliation] OR "
    "Cincinnati Childrens Hospital[Affiliation]"
)

# Maximum number of records to retrieve in a single search query to esearch
# NCBI default is 20, max is technically 100,000 with usehistory=y, but for efetch, it's usually smaller batches.
# Let's aim for a reasonable number for batch fetching details.
PUBMED_MAX_RESULTS_PER_QUERY = 20 # Max results for a single esearch call that we'll process initially
DEFAULT_MAX_PAPERS_TO_PROCESS = 10 # Default number of papers to download and store in a batch run for testing

# Date range for search (optional, can be added later)
# Example: last 1 year. Format: YYYY/MM/DD
# SEARCH_MINDATE = "2023/01/01"
# SEARCH_MAXDATE = "2023/12/31"

import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
# This is useful for local development to keep API keys out of the code.
# The .env file should be in the project root, alongside this config.py if run directly,
# or in the directory from which the main application is run.
# For this project structure, it's best if main.py is in literature_invention_search/
# and .env is in the parent directory (project root).
# Let's assume .env is in the project root.
# Construct path to .env file assuming this config.py is in literature_invention_search
# and .env is in the parent directory.
# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_dir)
# dotenv_path = os.path.join(project_root, ".env")
# load_dotenv(dotenv_path=dotenv_path)
# Simpler approach: load_dotenv() will search common locations.
# Ensure a .env file can be placed in the root of the project.
load_dotenv()

# AI Analysis related configuration (will be used in ai_analyzer.py)
# Load API keys from environment variables for security
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Choose which LLM to use: "openai" or "anthropic"
# This can also be set via an environment variable if desired, e.g., LLM_PROVIDER_ENV = os.getenv("LLM_PROVIDER")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower() # Default to openai if not set

# Basic check if keys are loaded, can be enhanced
if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    print("Warning: LLM_PROVIDER is 'openai' but OPENAI_API_KEY is not set in environment variables.")
elif LLM_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
    print("Warning: LLM_PROVIDER is 'anthropic' but ANTHROPIC_API_KEY is not set in environment variables.")


# Other settings
CSV_EXPORT_FILENAME = "flagged_potential_inventions.csv"

if __name__ == '__main__':
    # Example of how to access configuration values
    print(f"NCBI Email: {NCBI_EMAIL}")
    print(f"Search Term: {SEARCH_TERM_AFFILIATION}")
    print(f"Max papers to process by default: {DEFAULT_MAX_PAPERS_TO_PROCESS}")
    print(f"LLM Provider: {LLM_PROVIDER}")

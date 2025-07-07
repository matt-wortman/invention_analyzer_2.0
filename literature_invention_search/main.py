import argparse
import csv
import os
from datetime import datetime
from typing import Optional

try:
    # Imports for package execution
    from . import batch_processor
    from . import ai_analyzer
    from . import simple_database
    from . import config
except ImportError:
    # Fallback imports for direct script execution (e.g., python main.py from within the directory)
    import batch_processor
    import ai_analyzer
    import simple_database
    import config

def export_flagged_papers_to_csv(filename: str = config.CSV_EXPORT_FILENAME):
    """
    Exports papers flagged as potential inventions (and have been analyzed) to a CSV file.

    Args:
        filename: The name of the CSV file to create.
    """
    simple_database.initialize_database() # Ensure DB is accessible
    all_papers = simple_database.get_all_papers()

    flagged_papers = [
        paper for paper in all_papers
        if paper.get("ai_is_invention_candidate") is True # Check if True, not just non-None
    ]

    if not flagged_papers:
        print("No papers flagged as potential inventions found to export.")
        return

    # Define CSV headers based on available fields in the database
    # Taking all fields from one paper as representative, but ensuring core ones are first
    if flagged_papers:
        headers = list(flagged_papers[0].keys())
        # Preferred order for some important columns
        preferred_order = ["pmid", "title", "authors", "publication_date", "abstract",
                           "ai_is_invention_candidate", "ai_confidence", "ai_reasoning", "download_date"]
        # Others will be appended after
        final_headers = [h for h in preferred_order if h in headers] + \
                        [h for h in headers if h not in preferred_order]
    else: # Should not happen due to check above, but as a fallback
        headers = ["pmid", "title", "abstract", "authors", "publication_date",
                   "ai_is_invention_candidate", "ai_confidence", "ai_reasoning"]


    # Ensure the path is correct if main.py is inside literature_invention_search
    # If CSV_EXPORT_FILENAME is just a name, it will be created in CWD.
    # If it contains a path, that path will be used.
    # The plan implies main.py is in literature_invention_search, and CSV would be there too or project root.
    # For simplicity, let's make it in the same directory as papers.db (i.e. literature_invention_search/)

    # If config.CSV_EXPORT_FILENAME is just a filename, make it relative to the db path.
    # This is a bit complex if CSV_EXPORT_FILENAME could be an absolute path.
    # Simplest: CSV is created in the CWD when main.py is run.
    # Or, make it always go to the 'literature_invention_search' directory.

    # Let's assume CSV_EXPORT_FILENAME from config is just the filename.
    # We'll save it in the same directory as this script, or specify a path in config.
    # For now, config.CSV_EXPORT_FILENAME is just a name, so it goes to CWD.
    # If main.py is in literature_invention_search, and run from there, CSV is there.
    # If run from project root as `python -m literature_invention_search.main`, CWD is project root.
    # To be consistent with where papers.db is, let's place it there.

    # Get the directory of the database to save CSV nearby
    db_dir = os.path.dirname(simple_database.DATABASE_PATH)
    csv_filepath = os.path.join(db_dir, filename)


    try:
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=final_headers)
            writer.writeheader()
            for paper in flagged_papers:
                writer.writerow(paper)
        print(f"Successfully exported {len(flagged_papers)} flagged papers to {csv_filepath}")
    except IOError as e:
        print(f"Error exporting to CSV: {e}")


def run_full_pipeline(
    search_term: str,
    num_papers: int,
    analyze_with_ai: bool = True,
    year_filter: Optional[int] = None # Number of past years to filter by
    ):
    """
    Runs the full pipeline: batch fetch, (optional) AI analysis, and stores results.
    """
    print("--- Starting Full Pipeline ---")

    # Modify search term if year_filter is provided
    final_search_term = search_term
    if year_filter and year_filter > 0:
        current_year = datetime.now().year
        start_year = current_year - year_filter + 1 # +1 because we want 'last N years' inclusive
        # NCBI date format for esearch: YYYY or YYYY/MM or YYYY/MM/DD
        # We'll filter by publication year.
        # (YYYY[pdat] : YYYY[pdat])
        date_query_part = f" AND (({start_year}[Publication Date] : {current_year}[Publication Date]))"
        final_search_term = f"({search_term}){date_query_part}"
        print(f"Applying year filter: searching from {start_year} to {current_year}.")
        print(f"Modified search term: {final_search_term}")


    # 1. Batch process and fetch papers
    batch_results = batch_processor.process_batch(
        search_term=final_search_term,
        max_papers_to_process=num_papers
    )
    print(f"Batch processing completed. New papers processed: {batch_results.get('processed_newly', 0)}")

    if not analyze_with_ai:
        print("AI analysis skipped by user.")
        print("--- Pipeline Finished ---")
        return

    # 2. AI Analysis for newly added papers or all papers without AI data
    print("\n--- Starting AI Analysis Stage ---")
    if not ai_analyzer.llm_client:
        print("AI Provider not configured (API key likely missing). Skipping AI analysis.")
        print("--- Pipeline Finished ---")
        return

    papers_to_analyze = simple_database.get_all_papers()
    analyzed_count = 0
    failed_ai_count = 0

    for paper in papers_to_analyze:
        # Only analyze if not already analyzed (or if re-analysis is desired, not implemented here)
        if paper.get("ai_is_invention_candidate") is None: # Check if None, meaning not analyzed
            print(f"\nAnalyzing abstract for PMID: {paper['pmid']}")
            print(f"Title: {paper['title'][:80]}...")

            if not paper['abstract'] or paper['abstract'] == "N/A":
                print("Abstract is missing or N/A. Skipping AI analysis for this paper.")
                # Optionally, mark it as not an invention or with specific reasoning
                simple_database.update_paper_ai_analysis(
                    pmid=paper['pmid'],
                    ai_is_invention_candidate=False,
                    ai_confidence=0.0,
                    ai_reasoning="Abstract missing or N/A."
                )
                continue

            ai_result = ai_analyzer.analyze_abstract_with_llm(paper['abstract'])
            if ai_result:
                print(f"AI Result for {paper['pmid']}: Potential Invention? {ai_result.get('is_potential_invention')}, Confidence: {ai_result.get('confidence_score')}")
                simple_database.update_paper_ai_analysis(
                    pmid=paper['pmid'],
                    ai_is_invention_candidate=ai_result.get('is_potential_invention'),
                    ai_confidence=ai_result.get('confidence_score'),
                    ai_reasoning=ai_result.get('reasoning')
                    # Keywords could be stored if schema is extended, e.g., in reasoning or separate field
                )
                analyzed_count +=1
            else:
                print(f"AI analysis failed for PMID {paper['pmid']}.")
                failed_ai_count +=1
        else:
            print(f"PMID {paper['pmid']} already analyzed. Skipping.")

    print(f"\nAI analysis stage completed. Papers newly analyzed: {analyzed_count}. Failed AI calls: {failed_ai_count}.")
    print("--- Pipeline Finished ---")


def main():
    parser = argparse.ArgumentParser(description="Academic Publication Search and Analysis Tool - Phase 1 CLI")

    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # Sub-parser for 'fetch' command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch and store publications from PubMed.")
    fetch_parser.add_argument(
        "--search_term", type=str, default=config.SEARCH_TERM_AFFILIATION,
        help=f"PubMed search term. Default: '{config.SEARCH_TERM_AFFILIATION}'"
    )
    fetch_parser.add_argument(
        "--num_papers", type=int, default=config.DEFAULT_MAX_PAPERS_TO_PROCESS,
        help=f"Number of new papers to fetch and store. Default: {config.DEFAULT_MAX_PAPERS_TO_PROCESS}"
    )
    fetch_parser.add_argument(
        "--years", type=int, default=None,
        help="Filter papers from the last N years (e.g., 1 for last year, 5 for last 5 years)."
    )
    fetch_parser.add_argument(
        "--no_ai", action="store_true",
        help="Skip AI analysis stage after fetching."
    )

    # Sub-parser for 'analyze' command (analyze already fetched papers)
    analyze_parser = subparsers.add_parser("analyze", help="Run AI analysis on stored papers that haven't been analyzed.")
    # No specific arguments for analyze yet, it will process all unanalyzed papers.

    # Sub-parser for 'export' command
    export_parser = subparsers.add_parser("export", help="Export flagged publications to CSV.")
    export_parser.add_argument(
        "--filename", type=str, default=config.CSV_EXPORT_FILENAME,
        help=f"Output CSV filename. Default: {config.CSV_EXPORT_FILENAME}"
    )

    args = parser.parse_args()

    simple_database.initialize_database() # Ensure DB exists for all commands

    if args.command == "fetch":
        print(f"Command: Fetch papers for '{args.search_term}', limit {args.num_papers}, last {args.years} years, AI enabled: {not args.no_ai}")
        run_full_pipeline(
            search_term=args.search_term,
            num_papers=args.num_papers,
            analyze_with_ai=not args.no_ai,
            year_filter=args.years
            )

    elif args.command == "analyze":
        print("Command: Analyze stored papers with AI.")
        # This re-uses part of the run_full_pipeline logic but without fetching.
        # For simplicity, it's similar to run_full_pipeline with num_papers=0 and analyze_with_ai=True
        # but it should scan all papers in DB.
        # The current run_full_pipeline with num_papers=0 would fetch 0 new papers, then analyze all.
        # This is acceptable for Phase 1.
        # A dedicated analyze-only function could be more optimized.

        if not ai_analyzer.llm_client:
            print("AI Provider not configured (API key likely missing). Cannot perform analysis.")
            return

        papers_to_analyze = simple_database.get_all_papers()
        analyzed_count = 0
        failed_ai_count = 0
        print(f"Found {len(papers_to_analyze)} papers in database to check for AI analysis.")

        for paper in papers_to_analyze:
            if paper.get("ai_is_invention_candidate") is None:
                print(f"\nAnalyzing abstract for PMID: {paper['pmid']}")
                print(f"Title: {paper['title'][:80]}...")

                if not paper['abstract'] or paper['abstract'] == "N/A":
                    print("Abstract is missing or N/A. Skipping AI analysis for this paper.")
                    simple_database.update_paper_ai_analysis(
                        pmid=paper['pmid'], ai_is_invention_candidate=False,
                        ai_confidence=0.0, ai_reasoning="Abstract missing or N/A."
                    )
                    continue

                ai_result = ai_analyzer.analyze_abstract_with_llm(paper['abstract'])
                if ai_result:
                    print(f"AI Result for {paper['pmid']}: Potential Invention? {ai_result.get('is_potential_invention')}, Confidence: {ai_result.get('confidence_score')}")
                    simple_database.update_paper_ai_analysis(
                        pmid=paper['pmid'],
                        ai_is_invention_candidate=ai_result.get('is_potential_invention'),
                        ai_confidence=ai_result.get('confidence_score'),
                        ai_reasoning=ai_result.get('reasoning')
                    )
                    analyzed_count +=1
                else:
                    print(f"AI analysis failed for PMID {paper['pmid']}.")
                    failed_ai_count +=1
            else:
                # This can be verbose if many papers, consider a summary or less output
                # print(f"PMID {paper['pmid']} already analyzed. Skipping.")
                pass
        print(f"\nAI analysis command completed. Papers newly analyzed: {analyzed_count}. Failed AI calls: {failed_ai_count}.")


    elif args.command == "export":
        print(f"Command: Export flagged papers to {args.filename}")
        export_flagged_papers_to_csv(args.filename)

if __name__ == "__main__":
    # This allows running: python literature_invention_search/main.py <command> <args>
    # Or if in the dir: python main.py <command> <args>
    # For module execution from project root: python -m literature_invention_search.main <command> <args>
    main()

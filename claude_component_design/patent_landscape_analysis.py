import requests
import json
from datetime import datetime, timedelta
from statistics import median

# Step 1: Extract Technical Concepts from Invention
def extract_technical_concepts(invention_description, llm_call):
    llm_prompt = f"""
Extract the most important technical concepts, keywords, and patent classification terms from this biomedical invention:

{invention_description}

Return as JSON:
{{
  "primary_concepts": ["concept1", "concept2"],
  "technical_keywords": ["keyword1", "keyword2"], 
  "potential_cpc_classes": ["A61K", "G01N"],
  "search_queries": ["query1", "query2"]
}}
"""
    return llm_call(llm_prompt)

# Step 2: PatentsView API Queries
def query_patents_view_api(extracted_concepts, extracted_cpc_classes, primary_concepts):
    base_url = "https://api.patentsview.org/patents/query"
    
    # Query 1: Concept-based search
    concept_query = {
        "q": {"_text_any": {"patent_abstract": extracted_concepts}},
        "f": ["patent_number", "patent_title", "patent_abstract", "patent_date", "assignee_organization", "cpc_subgroup_id"],
        "s": [{"patent_date": "desc"}],
        "o": {"size": 100}
    }
    
    # Query 2: CPC classification search  
    cpc_query = {
        "q": {"cpc_subgroup_id": extracted_cpc_classes},
        "f": ["patent_number", "patent_title", "assignee_organization", "patent_date"],
        "s": [{"patent_date": "desc"}], 
        "o": {"size": 50}
    }
    
    # Query 3: Assignee landscape (major players)
    assignee_query = {
        "q": {"_and": [
            {"_text_any": {"patent_abstract": primary_concepts}},
            {"assignee_type": "2"}  # Corporations only
        ]},
        "f": ["assignee_organization", "patent_count"],
        "s": [{"patent_count": "desc"}],
        "o": {"size": 20}
    }
    
    results = {}
    try:
        response1 = requests.post(base_url, json=concept_query)
        results['concept_patents'] = response1.json().get('patents', [])
        
        response2 = requests.post(base_url, json=cpc_query)
        results['cpc_patents'] = response2.json().get('patents', [])
        
        response3 = requests.post(base_url, json=assignee_query)
        results['assignee_patents'] = response3.json().get('patents', [])
        
    except Exception as e:
        print(f"API query failed: {e}")
        results = {'concept_patents': [], 'cpc_patents': [], 'assignee_patents': []}
    
    return results

# Step 3: Patent Density Analysis
def count_patents_last_5_years(patent_results):
    current_year = datetime.now().year
    recent_count = 0
    
    for patent in patent_results:
        try:
            patent_year = int(patent.get('patent_date', '2000')[:4])
            if patent_year >= (current_year - 5):
                recent_count += 1
        except:
            continue
    
    return recent_count

def calculate_herfindahl_index(assignee_counts):
    total_patents = sum(assignee_counts)
    if total_patents == 0:
        return 0
    
    hhi = sum([(count / total_patents) ** 2 for count in assignee_counts])
    return hhi * 10000  # Scale to 0-10000

def calculate_prior_art_score(patent_results, invention_description, llm_similarity_score):
    # Analyze temporal distribution
    recent_patents = count_patents_last_5_years(patent_results)
    total_patents = len(patent_results)
    
    # Corporate concentration analysis
    assignee_counts = {}
    for patent in patent_results:
        assignee = patent.get('assignee_organization', 'Unknown')
        assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
    
    assignee_concentration = calculate_herfindahl_index(list(assignee_counts.values()))
    
    # Technical similarity scoring (using LLM)
    similarity_scores = []
    for patent in patent_results[:20]:  # Top 20 most relevant
        similarity = llm_similarity_score(invention_description, patent.get('patent_abstract', ''))
        similarity_scores.append(similarity)
    
    # Calculate final score (0-100, lower = better for patenting)
    density_score = (
        (recent_patents / 10) * 30 +  # Recent activity weight
        (total_patents / 100) * 25 +  # Total volume weight  
        (assignee_concentration / 10000) * 25 + # Market concentration
        (max(similarity_scores) if similarity_scores else 0) * 20  # Similarity weight
    )
    
    return min(100, density_score)

# Step 4: Generate Detailed Reasoning
def generate_patent_reasoning(total_patents, recent_patents, top_assignees, max_similarity, concentration_level, llm_call):
    reasoning_prompt = f"""
Based on this patent analysis data, provide detailed reasoning for the prior art density score:

Patent Volume: {total_patents} total, {recent_patents} in last 5 years
Key Competitors: {top_assignees}
Highest Similarity Score: {max_similarity}
Market Concentration: {concentration_level}

Explain:
1. How crowded is this patent space?
2. Who are the major players and their patent strategies?
3. What are the key technical barriers to patentability?
4. Risk assessment for potential interference/infringement
5. Recommendations for patent strategy

Format as structured analysis with specific evidence.
"""
    return llm_call(reasoning_prompt)

# Step 5: Data Structure for Storage
def create_patent_analysis_result(density_score, total_patents, recent_patents, top_assignees, 
                                most_similar_patent, assignee_concentration, llm_reasoning, 
                                search_queries, patent_sample_for_reference):
    patent_analysis_result = {
        "prior_art_density_score": density_score,
        "total_relevant_patents": total_patents,
        "recent_patent_activity": recent_patents,
        "key_competitors": top_assignees,
        "highest_similarity_patent": most_similar_patent,
        "market_concentration_index": assignee_concentration,
        "detailed_reasoning": llm_reasoning,
        "search_queries_used": search_queries,
        "api_call_timestamp": datetime.now(),
        "patents_analyzed": patent_sample_for_reference
    }
    return patent_analysis_result

# Main function to orchestrate the patent landscape analysis
def analyze_patent_landscape(invention_description, llm_call, llm_similarity_score):
    """
    Complete patent landscape analysis workflow
    
    Args:
        invention_description (str): Description of the invention to analyze
        llm_call (function): Function to make LLM API calls
        llm_similarity_score (function): Function to calculate similarity between texts
    
    Returns:
        dict: Complete patent analysis results
    """
    
    # Step 1: Extract technical concepts
    concepts = extract_technical_concepts(invention_description, llm_call)
    
    # Step 2: Query patent databases
    patent_results = query_patents_view_api(
        concepts.get('primary_concepts', []),
        concepts.get('potential_cpc_classes', []),
        concepts.get('primary_concepts', [])
    )
    
    # Combine all patent results
    all_patents = (patent_results['concept_patents'] + 
                   patent_results['cpc_patents'] + 
                   patent_results['assignee_patents'])
    
    # Step 3: Calculate density score
    density_score = calculate_prior_art_score(all_patents, invention_description, llm_similarity_score)
    
    # Extract key metrics
    total_patents = len(all_patents)
    recent_patents = count_patents_last_5_years(all_patents)
    
    # Get top assignees
    assignee_counts = {}
    for patent in all_patents:
        assignee = patent.get('assignee_organization', 'Unknown')
        assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
    
    top_assignees = sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Find most similar patent
    max_similarity = 0
    most_similar_patent = None
    for patent in all_patents[:20]:
        similarity = llm_similarity_score(invention_description, patent.get('patent_abstract', ''))
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_patent = patent
    
    # Step 4: Generate reasoning
    reasoning = generate_patent_reasoning(
        total_patents, recent_patents, [a[0] for a in top_assignees], 
        max_similarity, calculate_herfindahl_index([a[1] for a in top_assignees]), llm_call
    )
    
    # Step 5: Create final result
    result = create_patent_analysis_result(
        density_score, total_patents, recent_patents, top_assignees,
        most_similar_patent, calculate_herfindahl_index([a[1] for a in top_assignees]),
        reasoning, concepts.get('search_queries', []), all_patents[:10]
    )
    
    return result
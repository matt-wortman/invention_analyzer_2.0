import requests
import json
from datetime import datetime
import xml.etree.ElementTree as ET

# Step 1: Extract Technical Innovation Elements
def extract_technical_innovation_elements(invention_description, llm_call):
    novelty_extraction_prompt = f"""
Analyze this biomedical invention and extract technical innovation elements:

{invention_description}

Return as JSON:
{{
  "core_technical_concepts": ["CRISPR gene editing", "nanoparticle delivery"],
  "methodological_innovations": ["novel synthesis method", "new detection algorithm"],
  "technical_fields": ["molecular biology", "bioengineering", "diagnostics"],
  "research_keywords": ["keyword1", "keyword2"],
  "innovation_type": "incremental|significant|breakthrough",
  "technical_complexity": "low|medium|high",
  "interdisciplinary_elements": ["field1", "field2"],
  "pubmed_search_terms": ["term1", "term2"],
  "arxiv_categories": ["q-bio.BM", "physics.med-ph"]
}}
"""
    return llm_call(novelty_extraction_prompt)

# Step 2: Research Publication Analysis
def analyze_research_landscape(search_terms, search_pubmed, years_back=10):
    publication_analysis = {}
    
    # Historical publication trend analysis
    for year in range(2024-years_back, 2025):
        yearly_query = f"({' OR '.join(search_terms)}) AND {year}[PDAT]"
        results = search_pubmed(yearly_query, retmax=1000)
        
        publication_analysis[year] = {
            "count": len(results),
            "paper_ids": [r.get('pmid', '') for r in results[:50]]  # Top 50 for detailed analysis
        }
    
    return publication_analysis

def assess_field_maturity(publication_data):
    def calculate_publication_growth_rate(publication_data):
        years = sorted(publication_data.keys())
        if len(years) < 2:
            return 0
        
        growth_rates = []
        for i in range(1, len(years)):
            prev_count = publication_data[years[i-1]]['count']
            curr_count = publication_data[years[i]]['count']
            if prev_count > 0:
                growth_rate = (curr_count - prev_count) / prev_count
                growth_rates.append(growth_rate)
        
        return sum(growth_rates) / len(growth_rates) if growth_rates else 0
    
    total_papers = sum([data['count'] for data in publication_data.values()])
    recent_papers = sum([publication_data[year]['count'] for year in [2023, 2024] if year in publication_data])
    
    # Calculate research velocity and maturity indicators
    growth_rate = calculate_publication_growth_rate(publication_data)
    research_velocity = recent_papers / max(1, total_papers) * 100
    
    # Field maturity score (0-100, higher = more mature/established)
    maturity_score = min(100, (total_papers / 100) * 40 + (1 - abs(growth_rate)) * 60)
    
    return {
        "total_publications": total_papers,
        "recent_activity": recent_papers,
        "growth_rate": growth_rate,
        "research_velocity": research_velocity,
        "field_maturity_score": maturity_score
    }

# Step 3: Citation Analysis and Impact Assessment
def analyze_citation_landscape(search_terms):
    europe_pmc_base = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    
    # Search for highly cited papers in the field
    citation_query = {
        "query": f"({' OR '.join(search_terms)}) AND OPEN_ACCESS:y",
        "format": "json",
        "pageSize": 100,
        "sort": "CITED desc"
    }
    
    try:
        response = requests.get(europe_pmc_base, params=citation_query)
        papers = response.json()['resultList']['result']
    except Exception as e:
        print(f"Europe PMC API failed: {e}")
        papers = []
    
    # Analyze citation patterns
    citation_metrics = []
    for paper in papers[:50]:  # Top 50 most cited
        paper_data = {
            "pmid": paper.get('pmid'),
            "title": paper.get('title'),
            "citation_count": paper.get('citedByCount', 0),
            "publication_year": paper.get('pubYear'),
            "journal": paper.get('journalTitle'),
            "authors": paper.get('authorString', '').split(', ')[:5]  # First 5 authors
        }
        citation_metrics.append(paper_data)
    
    return citation_metrics

def identify_innovation_gaps(citation_data, invention_description, llm_call):
    def format_citation_data(citation_data):
        formatted = []
        for paper in citation_data:
            formatted.append(f"- {paper.get('title', 'No title')} ({paper.get('publication_year', 'Unknown year')}) - {paper.get('citation_count', 0)} citations")
        return '\n'.join(formatted)
    
    gap_analysis_prompt = f"""
    Based on this highly cited research in the field and the proposed invention:
    
    Recent High-Impact Papers:
    {format_citation_data(citation_data[:10])}
    
    Proposed Invention:
    {invention_description}
    
    Analyze:
    1. What technical gaps does this invention address?
    2. How does it advance beyond current state-of-the-art?
    3. What novel technical approaches are used?
    4. Rate the technical advancement level (1-10)
    5. Identify potential technical risks/challenges
    
    Return as JSON with detailed technical assessment.
    """
    
    return llm_call(gap_analysis_prompt)

# Step 4: Cross-Disciplinary Innovation Assessment
def analyze_interdisciplinary_innovation(technical_fields, search_terms):
    arxiv_base = "http://export.arxiv.org/api/query"
    
    def parse_arxiv_response(xml_text):
        papers = []
        try:
            root = ET.fromstring(xml_text)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            
            for entry in entries:
                title = entry.find('{http://www.w3.org/2005/Atom}title')
                published = entry.find('{http://www.w3.org/2005/Atom}published')
                
                paper_data = {
                    'title': title.text if title is not None else '',
                    'submitted': published.text if published is not None else ''
                }
                papers.append(paper_data)
        except ET.ParseError as e:
            print(f"Error parsing arXiv response: {e}")
        
        return papers
    
    interdisciplinary_scores = {}
    
    for field in technical_fields:
        # Search arXiv for relevant preprints
        arxiv_query = {
            "search_query": f"cat:{field} AND ({' OR '.join(search_terms)})",
            "start": 0,
            "max_results": 100,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        try:
            response = requests.get(arxiv_base, params=arxiv_query)
            papers = parse_arxiv_response(response.text)
        except Exception as e:
            print(f"arXiv API failed: {e}")
            papers = []
        
        # Calculate field activity and innovation indicators
        recent_papers = len([p for p in papers if p['submitted'] > '2023-01-01'])
        interdisciplinary_scores[field] = {
            "total_papers": len(papers),
            "recent_papers": recent_papers,
            "innovation_velocity": recent_papers / max(1, len(papers))
        }
    
    return interdisciplinary_scores

def assess_technical_complexity(invention_description, related_papers, llm_call):
    def format_paper_abstracts(papers):
        formatted = []
        for paper in papers[:5]:
            formatted.append(f"- {paper.get('title', 'No title')}")
        return '\n'.join(formatted)
    
    complexity_prompt = f"""
    Assess the technical complexity and innovation level of this invention:
    
    Invention: {invention_description}
    
    Related Research Context: {format_paper_abstracts(related_papers)}
    
    Rate on scales of 1-100:
    1. Technical Complexity: How technically challenging is the implementation?
    2. Innovation Level: How novel is the technical approach?
    3. Scientific Rigor: How well-grounded is the scientific foundation?
    4. Implementation Feasibility: How practical is the technical approach?
    5. Competitive Advantage: How difficult would this be to replicate?
    
    Provide detailed technical justification for each score.
    """
    
    return llm_call(complexity_prompt)

# Step 5: Research Trajectory and Future Potential Analysis
def analyze_research_trajectory(publication_data, citation_data):
    def calculate_research_momentum(publication_data):
        recent_years = [2022, 2023, 2024]
        early_years = [2019, 2020, 2021]
        
        recent_total = sum([publication_data.get(year, {}).get('count', 0) for year in recent_years])
        early_total = sum([publication_data.get(year, {}).get('count', 0) for year in early_years])
        
        if early_total == 0:
            return 50  # Neutral score if no early data
        
        momentum = (recent_total / early_total - 1) * 100
        return max(0, min(100, momentum + 50))  # Normalize to 0-100
    
    def analyze_citation_growth_patterns(citation_data):
        if not citation_data:
            return 0
        
        recent_citations = [p for p in citation_data if p.get('publication_year', 0) >= 2020]
        total_citations = sum([p.get('citation_count', 0) for p in recent_citations])
        
        return min(100, total_citations / 100)  # Scale to 0-100
    
    def identify_emerging_research_topics(citation_data):
        topics = []
        for paper in citation_data[:10]:
            if paper.get('title'):
                # Simple keyword extraction (could be enhanced with NLP)
                words = paper['title'].lower().split()
                topics.extend([word for word in words if len(word) > 5])
        
        # Count frequency and return top topics
        topic_counts = {}
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def identify_key_researchers(citation_data):
        researchers = []
        for paper in citation_data[:20]:
            authors = paper.get('authors', [])
            researchers.extend(authors)
        
        # Count frequency and return top researchers
        researcher_counts = {}
        for researcher in researchers:
            researcher_counts[researcher] = researcher_counts.get(researcher, 0) + 1
        
        return sorted(researcher_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def analyze_institutional_research(citation_data):
        # Simplified analysis - would need more detailed affiliation data
        return {"institutional_diversity": len(citation_data)}
    
    trajectory_analysis = {
        "research_momentum": calculate_research_momentum(publication_data),
        "citation_growth": analyze_citation_growth_patterns(citation_data),
        "emerging_topics": identify_emerging_research_topics(citation_data),
        "research_leaders": identify_key_researchers(citation_data),
        "institutional_activity": analyze_institutional_research(citation_data)
    }
    
    return trajectory_analysis

def analyze_future_potential(trajectory_data, invention_description, llm_call):
    def format_trajectory_data(trajectory_data):
        return f"""
Research Momentum: {trajectory_data['research_momentum']}/100
Citation Growth: {trajectory_data['citation_growth']}/100
Top Emerging Topics: {[topic[0] for topic in trajectory_data['emerging_topics'][:3]]}
Key Researchers: {[researcher[0] for researcher in trajectory_data['research_leaders'][:3]]}
"""
    
    future_potential_prompt = f"""
    Based on this research trajectory analysis:
    
    {format_trajectory_data(trajectory_data)}
    
    Proposed Invention: {invention_description}
    
    Assess:
    1. How well-positioned is this invention for future research trends?
    2. What is the potential for follow-on innovations?
    3. How likely is this field to continue growing?
    4. What are the key technical bottlenecks this addresses?
    5. Rate the future potential score (1-100)
    
    Provide quantitative assessment with supporting evidence.
    """
    
    return llm_call(future_potential_prompt)

# Step 6: Technical Novelty Scoring Algorithm
def calculate_technical_novelty_score(field_data, citation_data, complexity_data, trajectory_data):
    def calculate_interdisciplinary_score(field_data):
        # Simple calculation based on field diversity
        if 'interdisciplinary_scores' in field_data:
            scores = [data['innovation_velocity'] for data in field_data['interdisciplinary_scores'].values()]
            return sum(scores) / len(scores) * 100 if scores else 50
        return 50
    
    # Weighted scoring components
    components = {
        "field_innovation_gap": (100 - field_data['field_maturity_score']) * 0.25,
        "technical_advancement": complexity_data.get('innovation_level', 50) * 0.20,
        "scientific_rigor": complexity_data.get('scientific_rigor', 50) * 0.15,
        "research_momentum": trajectory_data['research_momentum'] * 0.15,
        "competitive_advantage": complexity_data.get('competitive_advantage', 50) * 0.10,
        "interdisciplinary_value": calculate_interdisciplinary_score(field_data) * 0.10,
        "future_potential": trajectory_data.get('future_potential_score', 50) * 0.05
    }
    
    total_score = sum(components.values())
    
    # Confidence assessment based on data quality
    confidence_factors = [
        field_data['total_publications'] > 50,
        len(citation_data) > 20,
        trajectory_data['research_momentum'] > 0,
        complexity_data.get('technical_complexity', 0) > 30
    ]
    confidence_level = sum(confidence_factors) / len(confidence_factors) * 100
    
    return {
        "technical_novelty_score": round(total_score, 1),
        "component_scores": components,
        "confidence_level": confidence_level
    }

# Step 7: Generate Technical Assessment Report
def generate_technical_reasoning(field_maturity_score, total_publications, recent_papers, 
                                citation_data, technical_complexity, innovation_level, 
                                research_momentum, field_assessment, innovation_gaps, 
                                advancement_level, future_potential, llm_call):
    novelty_reasoning_prompt = f"""
Based on this comprehensive technical analysis, provide detailed reasoning for the technical novelty score:

Field Maturity: {field_maturity_score}/100 ({total_publications} total papers, {recent_papers} recent)
Citation Landscape: {len(citation_data)} highly cited papers analyzed
Technical Complexity: {technical_complexity}/100
Innovation Level: {innovation_level}/100
Research Momentum: {research_momentum}/100

Key Findings:
- Field maturity assessment: {field_assessment}
- Innovation gaps identified: {innovation_gaps}
- Technical advancement level: {advancement_level}
- Future research potential: {future_potential}

Provide:
1. Technical innovation significance assessment
2. Competitive technical advantages
3. Scientific foundation strength
4. Implementation feasibility analysis
5. Long-term technical potential
6. Risk factors and technical challenges

Include specific quantitative evidence and research citations.
"""
    return llm_call(novelty_reasoning_prompt)

# Step 8: Data Structure for Storage
def create_technical_analysis_result(novelty_score, total_publications, field_maturity_score, 
                                   growth_rate, research_velocity, citation_data, 
                                   citation_growth_trend, key_researchers, technical_complexity, 
                                   innovation_level, scientific_rigor, feasibility_score, 
                                   research_momentum, future_potential, emerging_topics, 
                                   interdisciplinary_scores, technical_reasoning, confidence_level):
    def calculate_average_citations(citation_data):
        if not citation_data:
            return 0
        total_citations = sum([paper.get('citation_count', 0) for paper in citation_data])
        return total_citations / len(citation_data)
    
    technical_analysis_result = {
        "technical_novelty_score": novelty_score,
        "field_analysis": {
            "total_publications": total_publications,
            "field_maturity_score": field_maturity_score,
            "research_growth_rate": growth_rate,
            "research_velocity": research_velocity
        },
        "citation_analysis": {
            "highly_cited_papers": len(citation_data),
            "average_citations": calculate_average_citations(citation_data),
            "citation_growth_trend": citation_growth_trend,
            "key_researchers": key_researchers
        },
        "technical_complexity": {
            "complexity_score": technical_complexity,
            "innovation_level": innovation_level,
            "scientific_rigor": scientific_rigor,
            "implementation_feasibility": feasibility_score
        },
        "research_trajectory": {
            "momentum_score": research_momentum,
            "future_potential": future_potential,
            "emerging_topics": emerging_topics
        },
        "interdisciplinary_assessment": interdisciplinary_scores,
        "detailed_reasoning": technical_reasoning,
        "confidence_score": confidence_level,
        "key_citations": citation_data[:10],
        "api_call_timestamp": datetime.now()
    }
    return technical_analysis_result

# Main function to orchestrate technical novelty analysis
def analyze_technical_novelty(invention_description, llm_call, search_pubmed):
    """
    Complete technical novelty analysis workflow
    
    Args:
        invention_description (str): Description of the invention to analyze
        llm_call (function): Function to make LLM API calls
        search_pubmed (function): Function to search PubMed
    
    Returns:
        dict: Complete technical novelty analysis results
    """
    
    # Step 1: Extract technical innovation elements
    innovation_elements = extract_technical_innovation_elements(invention_description, llm_call)
    
    # Step 2: Analyze research landscape
    publication_data = analyze_research_landscape(
        innovation_elements.get('pubmed_search_terms', []), 
        search_pubmed
    )
    
    field_maturity = assess_field_maturity(publication_data)
    
    # Step 3: Analyze citation landscape
    citation_data = analyze_citation_landscape(innovation_elements.get('research_keywords', []))
    
    innovation_gaps = identify_innovation_gaps(citation_data, invention_description, llm_call)
    
    # Step 4: Analyze interdisciplinary innovation
    interdisciplinary_data = analyze_interdisciplinary_innovation(
        innovation_elements.get('technical_fields', []),
        innovation_elements.get('research_keywords', [])
    )
    
    complexity_assessment = assess_technical_complexity(invention_description, citation_data, llm_call)
    
    # Step 5: Analyze research trajectory
    trajectory_data = analyze_research_trajectory(publication_data, citation_data)
    
    future_potential_data = analyze_future_potential(trajectory_data, invention_description, llm_call)
    trajectory_data['future_potential_score'] = future_potential_data.get('future_potential_score', 50)
    
    # Step 6: Calculate technical novelty score
    field_data_enhanced = {**field_maturity, 'interdisciplinary_scores': interdisciplinary_data}
    
    score_result = calculate_technical_novelty_score(
        field_data_enhanced, citation_data, complexity_assessment, trajectory_data
    )
    
    # Step 7: Generate reasoning
    reasoning = generate_technical_reasoning(
        field_maturity['field_maturity_score'],
        field_maturity['total_publications'],
        field_maturity['recent_activity'],
        citation_data,
        complexity_assessment.get('technical_complexity', 50),
        complexity_assessment.get('innovation_level', 50),
        trajectory_data['research_momentum'],
        "Field assessment",  # Simplified
        innovation_gaps,
        complexity_assessment.get('innovation_level', 50),
        trajectory_data.get('future_potential_score', 50),
        llm_call
    )
    
    # Step 8: Create final result
    result = create_technical_analysis_result(
        score_result['technical_novelty_score'],
        field_maturity['total_publications'],
        field_maturity['field_maturity_score'],
        field_maturity['growth_rate'],
        field_maturity['research_velocity'],
        citation_data,
        trajectory_data['citation_growth'],
        [r[0] for r in trajectory_data['research_leaders'][:5]],
        complexity_assessment.get('technical_complexity', 50),
        complexity_assessment.get('innovation_level', 50),
        complexity_assessment.get('scientific_rigor', 50),
        complexity_assessment.get('implementation_feasibility', 50),
        trajectory_data['research_momentum'],
        trajectory_data.get('future_potential_score', 50),
        [t[0] for t in trajectory_data['emerging_topics'][:5]],
        interdisciplinary_data,
        reasoning,
        score_result['confidence_level']
    )
    
    return result
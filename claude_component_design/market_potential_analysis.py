import requests
import json
from datetime import datetime, timedelta
from statistics import median

# Step 1: Extract Market-Relevant Information
def extract_market_parameters(invention_description, llm_call):
    market_extraction_prompt = f"""
Analyze this biomedical invention and extract market-relevant information:

{invention_description}

Return as JSON:
{{
  "therapeutic_areas": ["oncology", "cardiology"],
  "target_conditions": ["diabetes", "hypertension"],
  "invention_type": "diagnostic_device|therapeutic|drug|medical_device",
  "target_population": "pediatric|adult|geriatric|all",
  "clinical_endpoints": ["mortality", "quality_of_life"],
  "regulatory_pathway": "FDA_510k|FDA_PMA|FDA_Drug|EU_CE",
  "search_terms_clinical": ["diabetes treatment", "glucose monitoring"],
  "icd10_codes": ["E11", "I10"],
  "mesh_terms": ["Diabetes Mellitus", "Hypertension"]
}}
"""
    return llm_call(market_extraction_prompt)

# Step 2: Clinical Trial Landscape Analysis
def analyze_clinical_trials(target_conditions, search_terms_clinical):
    clinical_trials_base = "https://clinicaltrials.gov/api/v2/studies"
    
    # Query 1: Current competitive trials
    competitive_trials_query = {
        "query.cond": target_conditions,
        "query.term": search_terms_clinical,
        "filter.overallStatus": ["RECRUITING", "ACTIVE_NOT_RECRUITING", "COMPLETED"],
        "postFilter.studyType": "INTERVENTIONAL",
        "pageSize": 100,
        "countTotal": True
    }
    
    # Query 2: Temporal trend analysis
    temporal_query = {
        "query.cond": target_conditions,
        "postFilter.studyStartDate": "01/01/2019,12/31/2024",
        "aggFilters": "studyStartDate:1y",
        "pageSize": 0,
        "countTotal": True
    }
    
    # Query 3: Funding source analysis
    funding_query = {
        "query.cond": target_conditions,
        "postFilter.fundingType": ["INDUSTRY", "NIH", "OTHER_GOV"],
        "aggFilters": "fundingType",
        "pageSize": 50
    }
    
    results = {}
    try:
        response1 = requests.get(clinical_trials_base, params=competitive_trials_query)
        results['competitive_trials'] = response1.json()
        
        response2 = requests.get(clinical_trials_base, params=temporal_query)
        results['temporal_trends'] = response2.json()
        
        response3 = requests.get(clinical_trials_base, params=funding_query)
        results['funding_analysis'] = response3.json()
        
    except Exception as e:
        print(f"Clinical trials API query failed: {e}")
        results = {'competitive_trials': {}, 'temporal_trends': {}, 'funding_analysis': {}}
    
    return results

# Step 3: FDA Approval Pathway Analysis
def analyze_fda_pathway(invention_type, therapeutic_area):
    fda_drugs_url = "https://api.fda.gov/drug/drugsfda.json"
    fda_device_url = "https://api.fda.gov/device/classification.json"
    
    results = {}
    
    # Query recent approvals in therapeutic area
    fda_approvals_query = {
        "search": f"openfda.indication.exact:{therapeutic_area}",
        "limit": 50
    }
    
    # FDA Device Classification for medical devices
    device_query = {
        "search": f"medical_specialty.exact:{therapeutic_area}",
        "limit": 100
    }
    
    try:
        if invention_type in ["therapeutic", "drug"]:
            response = requests.get(fda_drugs_url, params=fda_approvals_query)
            results['drug_approvals'] = response.json()
        
        if invention_type in ["device", "diagnostic"]:
            response = requests.get(fda_device_url, params=device_query)
            results['device_classifications'] = response.json()
            
    except Exception as e:
        print(f"FDA API query failed: {e}")
        results = {'drug_approvals': {}, 'device_classifications': {}}
    
    return results

def analyze_regulatory_pathway(invention_type, therapeutic_area):
    # Calculate approval timelines and success rates
    def get_historical_approval_times(invention_type, therapeutic_area):
        # Placeholder for historical data analysis
        approval_times_map = {
            "FDA_510k": [6, 12, 18, 24],
            "FDA_PMA": [12, 18, 24, 36],
            "FDA_Drug": [60, 84, 120, 144],
            "therapeutic": [60, 84, 120, 144]
        }
        return approval_times_map.get(invention_type, [12, 18, 24, 36])
    
    def calculate_approval_success_rates(invention_type, therapeutic_area):
        # Placeholder for success rate calculation
        success_rates_map = {
            "FDA_510k": 0.85,
            "FDA_PMA": 0.70,
            "FDA_Drug": 0.30,
            "therapeutic": 0.30
        }
        return success_rates_map.get(invention_type, 0.60)
    
    approval_times = get_historical_approval_times(invention_type, therapeutic_area)
    success_rates = calculate_approval_success_rates(invention_type, therapeutic_area)
    
    return {
        "median_approval_time_months": median(approval_times),
        "approval_success_rate": success_rates,
        "regulatory_complexity_score": calculate_complexity_score(invention_type)
    }

def calculate_complexity_score(invention_type):
    complexity_map = {
        "FDA_510k": 30,
        "FDA_PMA": 70,
        "FDA_Drug": 90,
        "therapeutic": 90,
        "diagnostic": 40
    }
    return complexity_map.get(invention_type, 50)

# Step 4: Disease Prevalence and Market Size Analysis
def analyze_funding_trends(search_terms_clinical):
    nih_reporter_url = "https://api.reporter.nih.gov/v2/projects/search"
    
    funding_trend_query = {
        "criteria": {
            "terms": search_terms_clinical,
            "fiscal_years": [2020, 2021, 2022, 2023, 2024],
            "agencies": ["NIH"]
        },
        "include_fields": ["fiscal_year", "award_amount", "project_title"],
        "limit": 200
    }
    
    try:
        response = requests.post(nih_reporter_url, json=funding_trend_query)
        return response.json()
    except Exception as e:
        print(f"NIH Reporter API failed: {e}")
        return {"results": []}

def estimate_market_potential(conditions, funding_data, clinical_trials):
    def normalize_funding_level(annual_funding):
        # Normalize funding to 0-100 scale
        return min(100, annual_funding / 10000000)  # $10M as reference
    
    def normalize_trial_activity(active_trials):
        # Normalize trial count to 0-100 scale
        return min(100, active_trials * 5)  # 20 trials = 100 score
    
    def normalize_industry_interest(industry_trials):
        # Normalize industry trial count
        return min(100, industry_trials * 10)  # 10 industry trials = 100 score
    
    def normalize_funding_trend(funding_trend):
        # Normalize growth rate to 0-100 scale
        return max(0, min(100, (funding_trend + 1) * 50))  # -100% to +100% growth
    
    def calculate_funding_growth_rate(funding_data):
        # Calculate year-over-year growth rate
        yearly_totals = {}
        for project in funding_data.get('results', []):
            year = project.get('fiscal_year')
            amount = project.get('award_amount', 0)
            yearly_totals[year] = yearly_totals.get(year, 0) + amount
        
        years = sorted(yearly_totals.keys())
        if len(years) < 2:
            return 0
        
        growth_rates = []
        for i in range(1, len(years)):
            if yearly_totals[years[i-1]] > 0:
                growth = (yearly_totals[years[i]] - yearly_totals[years[i-1]]) / yearly_totals[years[i-1]]
                growth_rates.append(growth)
        
        return sum(growth_rates) / len(growth_rates) if growth_rates else 0
    
    # Research funding as market interest proxy
    funding_results = funding_data.get('results', [])
    annual_funding = sum([project.get('award_amount', 0) for project in funding_results])
    funding_trend = calculate_funding_growth_rate(funding_data)
    
    # Clinical trial activity as market validation
    trial_data = clinical_trials.get('competitive_trials', {})
    active_trials = trial_data.get('totalCount', 0)
    
    # Estimate industry trials (simplified)
    industry_trials = active_trials * 0.3  # Assume 30% industry-sponsored
    
    # Calculate market potential score
    market_score = (
        normalize_funding_level(annual_funding) * 0.3 +
        normalize_trial_activity(active_trials) * 0.3 +
        normalize_industry_interest(industry_trials) * 0.2 +
        normalize_funding_trend(funding_trend) * 0.2
    )
    
    return min(100, market_score)

# Step 5: Publication Trend Analysis
def analyze_publication_trends(mesh_terms, search_pubmed, years=5):
    publication_counts = {}
    
    for year in range(2024-years, 2025):
        search_query = f"({' OR '.join(mesh_terms)}) AND {year}[PDAT]"
        
        # Use existing PubMed API connection
        results = search_pubmed(search_query, retmax=10000)
        publication_counts[year] = len(results)
    
    # Calculate trend metrics
    def calculate_linear_trend(publication_counts):
        years = sorted(publication_counts.keys())
        if len(years) < 2:
            return 0
        
        # Simple linear regression slope
        n = len(years)
        sum_x = sum(years)
        sum_y = sum(publication_counts.values())
        sum_xy = sum([year * publication_counts[year] for year in years])
        sum_x2 = sum([year * year for year in years])
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def normalize_publication_activity(recent_activity):
        return min(100, recent_activity / 100)  # 100 papers = max score
    
    trend_slope = calculate_linear_trend(publication_counts)
    recent_activity = publication_counts.get(2024, 0) + publication_counts.get(2023, 0)
    
    return {
        "annual_publications": publication_counts,
        "trend_slope": trend_slope,
        "recent_activity_score": normalize_publication_activity(recent_activity)
    }

# Step 6: Market Potential Scoring Algorithm
def calculate_market_potential_score(clinical_data, regulatory_data, funding_data, publication_data):
    def normalize_trial_count(trial_count):
        return min(100, trial_count / 20 * 100)  # 20 trials = 100 score
    
    def normalize_industry_trials(industry_trial_count):
        return min(100, industry_trial_count / 10 * 100)  # 10 industry trials = 100 score
    
    def normalize_funding(annual_funding):
        return min(100, annual_funding / 50000000 * 100)  # $50M = 100 score
    
    def normalize_growth_rate(growth_rate):
        return max(0, min(100, (growth_rate + 0.5) * 100))  # -50% to +50% normalized
    
    def calculate_confidence_level(clinical_data, funding_data):
        confidence_factors = [
            clinical_data.get('active_trials', 0) > 5,
            funding_data.get('annual_funding', 0) > 1000000,
            len(funding_data.get('results', [])) > 10,
            publication_data.get('recent_activity_score', 0) > 20
        ]
        return sum(confidence_factors) / len(confidence_factors) * 100
    
    # Weighted scoring components
    components = {
        "clinical_trial_activity": normalize_trial_count(clinical_data.get('active_trials', 0)) * 0.25,
        "industry_investment": normalize_industry_trials(clinical_data.get('industry_trials', 0)) * 0.20,
        "research_funding_level": normalize_funding(funding_data.get('annual_funding', 0)) * 0.20,
        "funding_growth_trend": normalize_growth_rate(funding_data.get('growth_rate', 0)) * 0.15,
        "publication_trend": publication_data.get('trend_slope', 0) * 10 * 0.10,  # Scale trend slope
        "regulatory_favorability": (100 - regulatory_data.get('complexity_score', 50)) * 0.10
    }
    
    total_score = sum(components.values())
    
    return {
        "market_potential_score": round(total_score, 1),
        "component_scores": components,
        "confidence_level": calculate_confidence_level(clinical_data, funding_data)
    }

# Step 7: Generate Market Analysis Report
def generate_market_reasoning(active_trials, industry_trials, annual_funding, funding_trend, 
                            publication_trend, recent_publications, regulatory_pathway, 
                            approval_time, llm_call):
    market_reasoning_prompt = f"""
Based on this market analysis data, provide detailed reasoning for the market potential score:

Clinical Trial Activity: {active_trials} active trials, {industry_trials} industry-sponsored
Research Funding: ${annual_funding:,.0f} annually, {funding_trend:+.1%} growth
Publication Trend: {publication_trend} ({recent_publications} recent papers)
Regulatory Pathway: {regulatory_pathway} (estimated {approval_time} months)

Analyze:
1. Market size and growth indicators
2. Competitive landscape intensity
3. Industry investment confidence
4. Regulatory barriers and timeline
5. Market access considerations
6. Revenue potential assessment

Provide specific evidence and quantitative justification.
"""
    return llm_call(market_reasoning_prompt)

# Step 8: Data Structure for Storage
def create_market_analysis_result(market_score, clinical_trials, annual_funding, funding_trend, 
                                top_funders, regulatory_pathway, approval_time, complexity_score, 
                                publication_data, market_reasoning, confidence_level, trial_growth_rate):
    market_analysis_result = {
        "market_potential_score": market_score,
        "clinical_trial_landscape": {
            "total_trials": len(clinical_trials),
            "active_trials": clinical_trials.get('competitive_trials', {}).get('totalCount', 0),
            "industry_sponsored": int(clinical_trials.get('competitive_trials', {}).get('totalCount', 0) * 0.3),
            "trial_growth_rate": trial_growth_rate
        },
        "research_funding_analysis": {
            "annual_funding": annual_funding,
            "funding_trend": funding_trend,
            "major_funders": top_funders
        },
        "regulatory_assessment": {
            "pathway": regulatory_pathway,
            "estimated_timeline": approval_time,
            "complexity_score": complexity_score
        },
        "publication_metrics": publication_data,
        "detailed_reasoning": market_reasoning,
        "confidence_score": confidence_level,
        "api_call_timestamp": datetime.now()
    }
    return market_analysis_result

# Main function to orchestrate market potential analysis
def analyze_market_potential(invention_description, llm_call, search_pubmed):
    """
    Complete market potential analysis workflow
    
    Args:
        invention_description (str): Description of the invention to analyze
        llm_call (function): Function to make LLM API calls
        search_pubmed (function): Function to search PubMed
    
    Returns:
        dict: Complete market analysis results
    """
    
    # Step 1: Extract market parameters
    market_params = extract_market_parameters(invention_description, llm_call)
    
    # Step 2: Analyze clinical trials
    clinical_data = analyze_clinical_trials(
        market_params.get('target_conditions', []),
        market_params.get('search_terms_clinical', [])
    )
    
    # Step 3: Analyze FDA pathway
    fda_data = analyze_fda_pathway(
        market_params.get('invention_type', 'device'),
        market_params.get('therapeutic_areas', ['general'])[0] if market_params.get('therapeutic_areas') else 'general'
    )
    
    regulatory_analysis = analyze_regulatory_pathway(
        market_params.get('regulatory_pathway', 'FDA_510k'),
        market_params.get('therapeutic_areas', ['general'])[0] if market_params.get('therapeutic_areas') else 'general'
    )
    
    # Step 4: Analyze funding trends
    funding_data = analyze_funding_trends(market_params.get('search_terms_clinical', []))
    
    # Calculate funding metrics
    funding_results = funding_data.get('results', [])
    annual_funding = sum([project.get('award_amount', 0) for project in funding_results])
    
    # Step 5: Analyze publication trends
    publication_data = analyze_publication_trends(
        market_params.get('mesh_terms', []), 
        search_pubmed
    )
    
    # Step 6: Calculate market potential score
    clinical_metrics = {
        'active_trials': clinical_data.get('competitive_trials', {}).get('totalCount', 0),
        'industry_trials': int(clinical_data.get('competitive_trials', {}).get('totalCount', 0) * 0.3)
    }
    
    funding_metrics = {
        'annual_funding': annual_funding,
        'growth_rate': 0  # Simplified for this example
    }
    
    score_result = calculate_market_potential_score(
        clinical_metrics, regulatory_analysis, funding_metrics, publication_data
    )
    
    # Step 7: Generate reasoning
    reasoning = generate_market_reasoning(
        clinical_metrics['active_trials'],
        clinical_metrics['industry_trials'],
        annual_funding,
        funding_metrics['growth_rate'],
        publication_data.get('trend_slope', 0),
        publication_data.get('recent_activity_score', 0),
        market_params.get('regulatory_pathway', 'FDA_510k'),
        regulatory_analysis.get('median_approval_time_months', 24),
        llm_call
    )
    
    # Step 8: Create final result
    result = create_market_analysis_result(
        score_result['market_potential_score'],
        clinical_data,
        annual_funding,
        funding_metrics['growth_rate'],
        ['NIH'],  # Simplified
        market_params.get('regulatory_pathway', 'FDA_510k'),
        regulatory_analysis.get('median_approval_time_months', 24),
        regulatory_analysis.get('regulatory_complexity_score', 50),
        publication_data,
        reasoning,
        score_result['confidence_level'],
        0  # Simplified trial growth rate
    )
    
    return result
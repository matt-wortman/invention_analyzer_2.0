import requests
import json
from datetime import datetime, timedelta
from statistics import median

# Step 1: Extract Commercial Development Parameters
def extract_commercial_parameters(invention_description, llm_call):
    commercial_extraction_prompt = f"""
Analyze this biomedical invention and extract commercial development parameters:

{invention_description}

Return as JSON:
{{
  "development_stage": "concept|preclinical|clinical_trials|fda_approval|market_ready",
  "technology_readiness_level": 1-9,
  "regulatory_pathway": "FDA_510k|FDA_PMA|FDA_Drug_IND|FDA_Biologics|EU_CE|Other",
  "manufacturing_complexity": "low|medium|high",
  "scalability_requirements": "laboratory|pilot|commercial",
  "target_market_segment": "hospitals|clinics|home_use|research",
  "competitive_positioning": "first_mover|fast_follower|differentiated|commodity",
  "key_development_milestones": ["milestone1", "milestone2"],
  "potential_barriers": ["regulatory", "manufacturing", "market_access"],
  "resource_requirements": "low|medium|high",
  "clinical_evidence_needed": "none|limited|extensive",
  "market_access_channels": ["direct_sales", "distributors", "partnerships"]
}}
"""
    return llm_call(commercial_extraction_prompt)

# Step 2: Technology Readiness Level Assessment
def assess_technology_readiness(invention_concepts, clinical_keywords, search_pubmed):
    trl_indicators = {}
    
    # Search for different stages of development
    development_queries = {
        "basic_research": f"({' OR '.join(invention_concepts)}) AND (basic research OR fundamental)",
        "preclinical": f"({' OR '.join(invention_concepts)}) AND (preclinical OR in vitro OR animal model)",
        "clinical_trials": f"({' OR '.join(invention_concepts)}) AND (clinical trial OR human study)",
        "fda_approval": f"({' OR '.join(invention_concepts)}) AND (FDA approval OR regulatory approval)",
        "commercial": f"({' OR '.join(invention_concepts)}) AND (commercial OR market OR clinical practice)"
    }
    
    for stage, query in development_queries.items():
        results = search_pubmed(query, retmax=100)
        trl_indicators[stage] = {
            "paper_count": len(results),
            "recent_papers": len([r for r in results if int(r.get('pub_year', 0)) >= 2022])
        }
    
    # Calculate TRL score based on evidence distribution
    trl_score = calculate_trl_from_literature(trl_indicators)
    
    return {
        "estimated_trl": trl_score,
        "development_evidence": trl_indicators,
        "stage_distribution": analyze_stage_distribution(trl_indicators)
    }

def calculate_trl_from_literature(indicators):
    # Weight different development stages
    stage_weights = {
        "basic_research": 2,
        "preclinical": 4, 
        "clinical_trials": 7,
        "fda_approval": 8,
        "commercial": 9
    }
    
    weighted_score = 0
    total_papers = sum([data['paper_count'] for data in indicators.values()])
    
    if total_papers > 0:
        for stage, data in indicators.items():
            weight = data['paper_count'] / total_papers
            weighted_score += stage_weights[stage] * weight
    
    return min(9, max(1, round(weighted_score)))

def analyze_stage_distribution(trl_indicators):
    total_papers = sum([data['paper_count'] for data in trl_indicators.values()])
    if total_papers == 0:
        return {}
    
    distribution = {}
    for stage, data in trl_indicators.items():
        distribution[stage] = data['paper_count'] / total_papers
    
    return distribution

# Step 3: Regulatory Pathway Complexity Analysis
def analyze_regulatory_complexity(invention_type, therapeutic_area, device_class=None):
    fda_device_api = "https://api.fda.gov/device/510k.json"
    fda_drug_api = "https://api.fda.gov/drug/drugsfda.json"
    
    regulatory_metrics = {}
    
    if invention_type in ["medical_device", "diagnostic"]:
        # Query FDA 510(k) database for similar devices
        device_query = {
            "search": f"medical_specialty_description:{therapeutic_area}",
            "limit": 100
        }
        
        try:
            response = requests.get(fda_device_api, params=device_query)
            devices = response.json()['results']
            
            # Analyze approval timelines and requirements
            approval_times = []
            for device in devices:
                decision_date = device.get('decision_date')
                date_received = device.get('date_received') 
                if decision_date and date_received:
                    timeline = calculate_days_between(date_received, decision_date)
                    approval_times.append(timeline)
            
            regulatory_metrics['device_analysis'] = {
                "median_approval_days": median(approval_times) if approval_times else 180,
                "similar_devices": len(devices),
                "approval_success_rate": calculate_success_rate(devices)
            }
        except:
            regulatory_metrics['device_analysis'] = {"error": "API unavailable"}
    
    elif invention_type in ["therapeutic", "drug", "biologic"]:
        # Query FDA drugs database
        drug_query = {
            "search": f"products.marketing_status:Prescription",
            "limit": 50
        }
        
        try:
            response = requests.get(fda_drug_api, params=drug_query)
            drugs = response.json()['results']
            
            regulatory_metrics['drug_analysis'] = {
                "approval_complexity": "high",
                "estimated_timeline_years": estimate_drug_approval_timeline(therapeutic_area),
                "clinical_trial_phases_required": get_required_phases(invention_type)
            }
        except:
            regulatory_metrics['drug_analysis'] = {"error": "API unavailable"}
    
    return regulatory_metrics

def calculate_days_between(date1, date2):
    try:
        d1 = datetime.strptime(date1, '%Y-%m-%d')
        d2 = datetime.strptime(date2, '%Y-%m-%d')
        return abs((d2 - d1).days)
    except:
        return 180  # Default 6 months

def calculate_success_rate(devices):
    approved = len([d for d in devices if d.get('decision_description', '').lower() == 'substantially equivalent'])
    total = len(devices)
    return approved / total if total > 0 else 0.8

def estimate_drug_approval_timeline(therapeutic_area):
    # Simplified mapping of therapeutic areas to typical timelines
    timeline_map = {
        "oncology": 8,
        "cardiology": 7,
        "neurology": 9,
        "infectious_disease": 6
    }
    return timeline_map.get(therapeutic_area, 7)

def get_required_phases(invention_type):
    phase_map = {
        "therapeutic": ["Phase I", "Phase II", "Phase III"],
        "drug": ["Phase I", "Phase II", "Phase III"],
        "biologic": ["Phase I", "Phase II", "Phase III"],
        "medical_device": ["Preclinical", "Clinical"]
    }
    return phase_map.get(invention_type, ["Preclinical"])

def calculate_regulatory_complexity_score(regulatory_data, invention_type):
    complexity_factors = {
        "FDA_510k": 20,  # Lower complexity
        "FDA_PMA": 60,   # Higher complexity  
        "FDA_Drug_IND": 80,  # Very high complexity
        "FDA_Biologics": 85,  # Highest complexity
        "EU_CE": 30
    }
    
    base_complexity = complexity_factors.get(invention_type, 50)
    
    # Adjust based on historical data
    if 'device_analysis' in regulatory_data:
        timeline_factor = min(50, regulatory_data['device_analysis']['median_approval_days'] / 10)
        complexity_score = base_complexity + timeline_factor
    else:
        complexity_score = base_complexity
    
    return min(100, complexity_score)

# Step 4: Manufacturing and Scalability Assessment
def assess_manufacturing_readiness(invention_description, development_stage, llm_call):
    manufacturing_prompt = f"""
    Assess the manufacturing and scalability readiness for this biomedical invention:
    
    Invention: {invention_description}
    Current Development Stage: {development_stage}
    
    Evaluate on scales of 1-100:
    1. Manufacturing Complexity: How difficult is production?
    2. Scalability Potential: How easily can production be scaled?
    3. Quality Control Requirements: How stringent are QC needs?
    4. Supply Chain Complexity: How complex is the supply chain?
    5. Capital Requirements: How much investment is needed for manufacturing?
    6. Regulatory Manufacturing Requirements: How strict are manufacturing regulations?
    
    Also assess:
    - Technology transfer feasibility
    - Contract manufacturing availability
    - Key manufacturing bottlenecks
    - Time to establish manufacturing
    
    Return as JSON with detailed manufacturing assessment.
    """
    
    return llm_call(manufacturing_prompt)

def analyze_market_access_barriers(target_market, therapeutic_area):
    access_barriers = {
        "reimbursement_complexity": assess_reimbursement_landscape(therapeutic_area),
        "distribution_challenges": assess_distribution_requirements(target_market),
        "adoption_barriers": assess_adoption_challenges(therapeutic_area),
        "competitive_barriers": assess_competitive_landscape_barriers(therapeutic_area)
    }
    
    return access_barriers

def assess_reimbursement_landscape(therapeutic_area, llm_call):
    reimbursement_prompt = f"""
    Assess reimbursement and insurance coverage complexity for {therapeutic_area}:
    
    Consider:
    1. Historical coverage patterns for similar technologies
    2. Value-based care trends in this area
    3. Cost-effectiveness requirements
    4. Payer decision timelines
    5. Evidence requirements for coverage
    
    Rate reimbursement complexity (1-100, higher = more complex)
    Provide detailed justification.
    """
    
    return llm_call(reimbursement_prompt)

def assess_distribution_requirements(target_market):
    distribution_complexity = {
        "hospitals": 60,
        "clinics": 40,
        "home_use": 80,
        "research": 30
    }
    return distribution_complexity.get(target_market, 50)

def assess_adoption_challenges(therapeutic_area):
    adoption_map = {
        "oncology": 70,
        "cardiology": 50,
        "neurology": 60,
        "infectious_disease": 40
    }
    return adoption_map.get(therapeutic_area, 50)

def assess_competitive_landscape_barriers(therapeutic_area):
    competitive_map = {
        "oncology": 80,
        "cardiology": 70,
        "neurology": 60,
        "infectious_disease": 50
    }
    return competitive_map.get(therapeutic_area, 60)

# Step 5: Development Timeline and Resource Analysis
def analyze_development_resources(invention_concepts, therapeutic_area):
    nih_api = "https://api.reporter.nih.gov/v2/projects/search"
    
    # Query NIH funding for similar technologies
    funding_query = {
        "criteria": {
            "terms": invention_concepts,
            "agencies": ["NIH"],
            "fiscal_years": list(range(2019, 2025))
        },
        "include_fields": ["fiscal_year", "award_amount", "project_title", "activity", "agency_ic_admin"],
        "limit": 200
    }
    
    try:
        response = requests.post(nih_api, json=funding_query)
        funding_data = response.json()['results']
        
        # Analyze funding patterns
        development_metrics = {
            "total_funding": sum([project['award_amount'] for project in funding_data]),
            "average_grant_size": calculate_average_grant_size(funding_data),
            "funding_trend": analyze_funding_trend(funding_data),
            "development_phases": categorize_development_phases(funding_data),
            "key_funding_agencies": identify_key_funders(funding_data)
        }
        
        return development_metrics
    except:
        return {"error": "NIH API unavailable"}

def calculate_average_grant_size(funding_data):
    if not funding_data:
        return 0
    
    total_amount = sum([project.get('award_amount', 0) for project in funding_data])
    return total_amount / len(funding_data)

def analyze_funding_trend(funding_data):
    yearly_totals = {}
    for project in funding_data:
        year = project.get('fiscal_year')
        amount = project.get('award_amount', 0)
        yearly_totals[year] = yearly_totals.get(year, 0) + amount
    
    years = sorted(yearly_totals.keys())
    if len(years) < 2:
        return 0
    
    # Calculate trend over time
    first_year_total = yearly_totals[years[0]]
    last_year_total = yearly_totals[years[-1]]
    
    if first_year_total == 0:
        return 0
    
    return (last_year_total - first_year_total) / first_year_total

def categorize_development_phases(funding_data):
    phases = {"basic": 0, "translational": 0, "clinical": 0}
    
    for project in funding_data:
        title = project.get('project_title', '').lower()
        if any(term in title for term in ['basic', 'fundamental', 'mechanism']):
            phases["basic"] += 1
        elif any(term in title for term in ['translational', 'development', 'pilot']):
            phases["translational"] += 1
        elif any(term in title for term in ['clinical', 'trial', 'patient']):
            phases["clinical"] += 1
    
    return phases

def identify_key_funders(funding_data):
    funders = {}
    for project in funding_data:
        agency = project.get('agency_ic_admin', 'Unknown')
        funders[agency] = funders.get(agency, 0) + 1
    
    return sorted(funders.items(), key=lambda x: x[1], reverse=True)[:5]

def estimate_development_timeline(trl_level, regulatory_pathway, manufacturing_complexity):
    base_timelines = {
        "FDA_510k": {"low": 12, "medium": 18, "high": 24},  # months
        "FDA_PMA": {"low": 24, "medium": 36, "high": 48},
        "FDA_Drug_IND": {"low": 60, "medium": 84, "high": 120},  # Phase I-III + approval
        "FDA_Biologics": {"low": 72, "medium": 96, "high": 144}
    }
    
    base_timeline = base_timelines.get(regulatory_pathway, {"medium": 36})[manufacturing_complexity]
    
    # Adjust based on TRL
    trl_adjustments = {
        1: 2.0, 2: 1.8, 3: 1.6, 4: 1.4, 5: 1.2,
        6: 1.0, 7: 0.8, 8: 0.6, 9: 0.4
    }
    
    adjusted_timeline = base_timeline * trl_adjustments.get(trl_level, 1.0)
    
    return {
        "estimated_months_to_market": round(adjusted_timeline),
        "development_phases": break_down_development_phases(adjusted_timeline, regulatory_pathway),
        "key_milestones": identify_key_milestones(regulatory_pathway),
        "resource_requirements": estimate_resource_needs(adjusted_timeline, regulatory_pathway)
    }

def break_down_development_phases(total_timeline, regulatory_pathway):
    phase_ratios = {
        "FDA_510k": {"preclinical": 0.3, "clinical": 0.4, "regulatory": 0.3},
        "FDA_PMA": {"preclinical": 0.25, "clinical": 0.5, "regulatory": 0.25},
        "FDA_Drug_IND": {"preclinical": 0.2, "phase_i": 0.15, "phase_ii": 0.25, "phase_iii": 0.3, "regulatory": 0.1}
    }
    
    ratios = phase_ratios.get(regulatory_pathway, {"development": 0.7, "regulatory": 0.3})
    
    phases = {}
    for phase, ratio in ratios.items():
        phases[phase] = round(total_timeline * ratio)
    
    return phases

def identify_key_milestones(regulatory_pathway):
    milestone_map = {
        "FDA_510k": ["Prototype completion", "Preclinical testing", "510(k) submission", "FDA clearance"],
        "FDA_PMA": ["IND submission", "Clinical trials", "PMA submission", "FDA approval"],
        "FDA_Drug_IND": ["IND submission", "Phase I completion", "Phase II completion", "Phase III completion", "NDA submission"]
    }
    
    return milestone_map.get(regulatory_pathway, ["Development", "Testing", "Regulatory submission", "Approval"])

def estimate_resource_needs(timeline_months, regulatory_pathway):
    resource_map = {
        "FDA_510k": {"funding": timeline_months * 50000, "team_size": 5},
        "FDA_PMA": {"funding": timeline_months * 100000, "team_size": 10},
        "FDA_Drug_IND": {"funding": timeline_months * 500000, "team_size": 20}
    }
    
    return resource_map.get(regulatory_pathway, {"funding": timeline_months * 75000, "team_size": 8})

# Step 6: Commercial Readiness Scoring Algorithm
def calculate_commercial_readiness_score(trl_data, regulatory_data, manufacturing_data, 
                                       timeline_data, market_access_data):
    def calculate_timeline_score(months_to_market):
        # Score based on reasonable commercial timelines
        if months_to_market <= 12:
            return 90
        elif months_to_market <= 24:
            return 75
        elif months_to_market <= 36:
            return 60
        elif months_to_market <= 60:
            return 40
        else:
            return 20
    
    def assess_resource_accessibility(resource_requirements):
        funding_needed = resource_requirements.get('funding', 1000000)
        if funding_needed <= 500000:
            return 80
        elif funding_needed <= 2000000:
            return 60
        elif funding_needed <= 10000000:
            return 40
        else:
            return 20
    
    def identify_commercial_risks(trl_data, regulatory_data, manufacturing_data):
        risks = []
        
        if trl_data['estimated_trl'] < 5:
            risks.append("Low technology readiness")
        
        if regulatory_data.get('complexity_score', 50) > 70:
            risks.append("High regulatory complexity")
        
        if manufacturing_data.get('manufacturing_complexity', 50) > 70:
            risks.append("Manufacturing challenges")
        
        return risks
    
    def calculate_risk_penalty(risk_factors):
        return len(risk_factors) * 10  # 10 point penalty per risk factor
    
    # Weighted scoring components
    components = {
        "technology_readiness": (trl_data['estimated_trl'] / 9) * 100 * 0.25,
        "regulatory_feasibility": (100 - regulatory_data.get('complexity_score', 50)) * 0.20,
        "manufacturing_readiness": manufacturing_data.get('scalability_potential', 50) * 0.15,
        "timeline_feasibility": calculate_timeline_score(timeline_data['estimated_months_to_market']) * 0.15,
        "market_access_viability": (100 - market_access_data.get('total_barrier_score', 50)) * 0.10,
        "resource_accessibility": assess_resource_accessibility(timeline_data['resource_requirements']) * 0.10,
        "competitive_positioning": manufacturing_data.get('competitive_advantage', 50) * 0.05
    }
    
    total_score = sum(components.values())
    
    # Risk adjustments
    risk_factors = identify_commercial_risks(trl_data, regulatory_data, manufacturing_data)
    risk_adjustment = calculate_risk_penalty(risk_factors)
    
    final_score = max(0, total_score - risk_adjustment)
    
    return {
        "commercial_readiness_score": round(final_score, 1),
        "component_scores": components,
        "risk_factors": risk_factors,
        "risk_adjustment": risk_adjustment
    }

# Step 7: Generate Commercial Readiness Report
def generate_commercial_reasoning(trl_level, stage_distribution, regulatory_pathway, timeline_months, 
                                manufacturing_complexity, scalability_score, market_access_barriers, 
                                resource_level, estimated_funding_needed, development_phases, 
                                risk_factors, llm_call):
    commercial_reasoning_prompt = f"""
Based on this comprehensive commercial readiness analysis, provide detailed reasoning:

Technology Readiness: TRL {trl_level}/9 ({stage_distribution})
Regulatory Pathway: {regulatory_pathway} (estimated {timeline_months} months)
Manufacturing: {manufacturing_complexity} complexity, {scalability_score}/100 scalability
Market Access: {market_access_barriers}
Resource Requirements: {resource_level} ({estimated_funding_needed})

Development Timeline Breakdown:
{format_development_phases(development_phases)}

Key Risk Factors:
{format_risk_factors(risk_factors)}

Provide:
1. Commercial viability assessment
2. Key development milestones and timeline
3. Resource and funding requirements
4. Market entry strategy considerations
5. Major risk factors and mitigation strategies
6. Competitive positioning analysis
7. Regulatory strategy recommendations

Include specific quantitative evidence and realistic timelines.
"""
    return llm_call(commercial_reasoning_prompt)

def format_development_phases(development_phases):
    formatted = []
    for phase, duration in development_phases.items():
        formatted.append(f"- {phase}: {duration} months")
    return '\n'.join(formatted)

def format_risk_factors(risk_factors):
    if not risk_factors:
        return "No major risk factors identified"
    return '\n'.join([f"- {risk}" for risk in risk_factors])

# Step 8: Data Structure for Storage
def create_commercial_readiness_result(readiness_score, trl_level, development_stage, 
                                     trl_indicators, technology_maturity_score, regulatory_pathway, 
                                     regulatory_complexity, regulatory_timeline, approval_probability, 
                                     manufacturing_complexity, scalability_score, capital_requirements, 
                                     manufacturing_timeline, total_timeline, development_phases, 
                                     key_milestones, critical_path, market_barriers, reimbursement_score, 
                                     distribution_score, adoption_timeline, development_cost, 
                                     funding_availability, resource_needs, risk_factors, 
                                     mitigation_strategies, overall_risk_score, commercial_reasoning, 
                                     confidence_level):
    commercial_readiness_result = {
        "commercial_readiness_score": readiness_score,
        "technology_readiness": {
            "estimated_trl": trl_level,
            "development_stage": development_stage,
            "stage_evidence": trl_indicators,
            "technology_maturity": technology_maturity_score
        },
        "regulatory_assessment": {
            "pathway": regulatory_pathway,
            "complexity_score": regulatory_complexity,
            "estimated_timeline_months": regulatory_timeline,
            "approval_success_probability": approval_probability
        },
        "manufacturing_analysis": {
            "complexity_level": manufacturing_complexity,
            "scalability_score": scalability_score,
            "capital_requirements": capital_requirements,
            "time_to_manufacturing": manufacturing_timeline
        },
        "development_timeline": {
            "total_months_to_market": total_timeline,
            "development_phases": development_phases,
            "key_milestones": key_milestones,
            "critical_path_items": critical_path
        },
        "market_access": {
            "barrier_assessment": market_barriers,
            "reimbursement_complexity": reimbursement_score,
            "distribution_challenges": distribution_score,
            "adoption_timeline": adoption_timeline
        },
        "resource_requirements": {
            "estimated_development_cost": development_cost,
            "funding_availability": funding_availability,
            "key_resource_needs": resource_needs
        },
        "risk_assessment": {
            "major_risks": risk_factors,
            "risk_mitigation_strategies": mitigation_strategies,
            "overall_risk_level": overall_risk_score
        },
        "detailed_reasoning": commercial_reasoning,
        "confidence_score": confidence_level,
        "api_call_timestamp": datetime.now()
    }
    return commercial_readiness_result

# Main function to orchestrate commercial readiness analysis
def analyze_commercial_readiness(invention_description, llm_call, search_pubmed):
    """
    Complete commercial readiness analysis workflow
    
    Args:
        invention_description (str): Description of the invention to analyze
        llm_call (function): Function to make LLM API calls
        search_pubmed (function): Function to search PubMed
    
    Returns:
        dict: Complete commercial readiness analysis results
    """
    
    # Step 1: Extract commercial parameters
    commercial_params = extract_commercial_parameters(invention_description, llm_call)
    
    # Step 2: Assess technology readiness
    trl_data = assess_technology_readiness(
        [invention_description],  # Simplified concept extraction
        [invention_description],
        search_pubmed
    )
    
    # Step 3: Analyze regulatory complexity
    regulatory_data = analyze_regulatory_complexity(
        commercial_params.get('development_stage', 'medical_device'),
        'general'  # Simplified therapeutic area
    )
    
    regulatory_complexity_score = calculate_regulatory_complexity_score(
        regulatory_data,
        commercial_params.get('regulatory_pathway', 'FDA_510k')
    )
    
    # Step 4: Assess manufacturing readiness
    manufacturing_data = assess_manufacturing_readiness(
        invention_description,
        commercial_params.get('development_stage', 'concept'),
        llm_call
    )
    
    # Step 5: Analyze development resources
    resource_data = analyze_development_resources(
        [invention_description],
        'general'
    )
    
    timeline_data = estimate_development_timeline(
        trl_data['estimated_trl'],
        commercial_params.get('regulatory_pathway', 'FDA_510k'),
        commercial_params.get('manufacturing_complexity', 'medium')
    )
    
    # Analyze market access barriers
    market_access_data = analyze_market_access_barriers(
        commercial_params.get('target_market_segment', 'hospitals'),
        'general'
    )
    
    market_access_data['total_barrier_score'] = sum(market_access_data.values()) / len(market_access_data)
    
    # Step 6: Calculate commercial readiness score
    regulatory_data_enhanced = {'complexity_score': regulatory_complexity_score}
    
    score_result = calculate_commercial_readiness_score(
        trl_data, regulatory_data_enhanced, manufacturing_data, timeline_data, market_access_data
    )
    
    # Step 7: Generate reasoning
    reasoning = generate_commercial_reasoning(
        trl_data['estimated_trl'],
        trl_data['stage_distribution'],
        commercial_params.get('regulatory_pathway', 'FDA_510k'),
        timeline_data['estimated_months_to_market'],
        commercial_params.get('manufacturing_complexity', 'medium'),
        manufacturing_data.get('scalability_potential', 50),
        market_access_data,
        commercial_params.get('resource_requirements', 'medium'),
        timeline_data['resource_requirements'].get('funding', 1000000),
        timeline_data['development_phases'],
        score_result['risk_factors'],
        llm_call
    )
    
    # Step 8: Create final result
    result = create_commercial_readiness_result(
        score_result['commercial_readiness_score'],
        trl_data['estimated_trl'],
        commercial_params.get('development_stage', 'concept'),
        trl_data['development_evidence'],
        50,  # Simplified technology maturity score
        commercial_params.get('regulatory_pathway', 'FDA_510k'),
        regulatory_complexity_score,
        timeline_data['estimated_months_to_market'],
        0.7,  # Simplified approval probability
        commercial_params.get('manufacturing_complexity', 'medium'),
        manufacturing_data.get('scalability_potential', 50),
        timeline_data['resource_requirements'].get('funding', 1000000),
        12,  # Simplified manufacturing timeline
        timeline_data['estimated_months_to_market'],
        timeline_data['development_phases'],
        timeline_data['key_milestones'],
        ['Regulatory approval'],  # Simplified critical path
        market_access_data,
        50,  # Simplified reimbursement score
        50,  # Simplified distribution score
        12,  # Simplified adoption timeline
        timeline_data['resource_requirements'].get('funding', 1000000),
        'Medium',  # Simplified funding availability
        resource_data,
        score_result['risk_factors'],
        ['Risk mitigation strategy'],  # Simplified mitigation strategies
        len(score_result['risk_factors']) * 20,  # Simplified overall risk score
        reasoning,
        75  # Simplified confidence level
    )
    
    return result
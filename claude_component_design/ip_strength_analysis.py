import requests
import json
from datetime import datetime, timedelta

# Step 1: Extract Patent-Specific Technical Elements
def extract_ip_elements(invention_description, llm_call):
    ip_extraction_prompt = f"""
Analyze this biomedical invention for intellectual property strength assessment:

{invention_description}

Return as JSON:
{{
  "patentable_subject_matter": "composition|method|device|system|combination",
  "core_inventive_concepts": ["concept1", "concept2"],
  "technical_features": ["feature1", "feature2"],
  "potential_claim_elements": ["element1", "element2"],
  "novelty_aspects": ["novel_aspect1", "novel_aspect2"],
  "non_obvious_combinations": ["combination1", "combination2"],
  "utility_applications": ["application1", "application2"],
  "dependent_claim_opportunities": ["opportunity1", "opportunity2"],
  "patent_classification_codes": ["A61K", "G01N"],
  "prior_art_search_terms": ["term1", "term2"],
  "potential_design_arounds": ["workaround1", "workaround2"],
  "blocking_patent_risks": ["risk1", "risk2"],
  "defensive_applications": ["defense1", "defense2"]
}}
"""
    return llm_call(ip_extraction_prompt)

# Step 2: Comprehensive Prior Art Analysis for Patentability
def conduct_comprehensive_prior_art_search(inventive_concepts, claim_elements, cpc_codes):
    prior_art_results = {}
    
    # PatentsView API - US Patents
    patentsview_queries = [
        # Exact concept matches
        {
            "q": {"_text_any": {"patent_abstract": inventive_concepts}},
            "f": ["patent_number", "patent_title", "patent_abstract", "patent_date", 
                  "assignee_organization", "cpc_subgroup_id", "uspc_class_id"],
            "s": [{"patent_date": "desc"}],
            "o": {"size": 200}
        },
        # CPC classification search
        {
            "q": {"cpc_subgroup_id": cpc_codes},
            "f": ["patent_number", "patent_title", "patent_abstract", "patent_date"],
            "s": [{"patent_date": "desc"}],
            "o": {"size": 100}
        },
        # Claim element combinations
        {
            "q": {"_text_all": {"patent_claims": claim_elements[:3]}},  # Top 3 most important
            "f": ["patent_number", "patent_title", "patent_claims", "patent_date"],
            "s": [{"patent_date": "desc"}],
            "o": {"size": 100}
        }
    ]
    
    prior_art_results['us_patents'] = []
    for query in patentsview_queries:
        try:
            response = requests.post("https://api.patentsview.org/patents/query", json=query)
            if response.status_code == 200:
                prior_art_results['us_patents'].extend(response.json()['patents'])
        except Exception as e:
            print(f"PatentsView query failed: {e}")
    
    # European Patent Office OPS API
    epo_api_base = "https://ops.epo.org/3.2/rest-services"
    
    # Search EPO for international prior art
    epo_query = f"txt=({' OR '.join(inventive_concepts[:5])}) AND cl=({' OR '.join(cpc_codes)})"
    
    try:
        epo_response = requests.get(f"{epo_api_base}/published-data/search", 
                                  params={"q": epo_query, "Range": "1-50"})
        prior_art_results['epo_patents'] = parse_epo_response(epo_response)
    except:
        prior_art_results['epo_patents'] = []
    
    return prior_art_results

def parse_epo_response(epo_response):
    # Simplified EPO response parsing
    try:
        # This would need proper XML parsing for real implementation
        return []
    except:
        return []

def assess_patentability_strength(invention_description, prior_art_results, llm_call):
    def format_prior_art_abstracts(patents):
        formatted = []
        for patent in patents[:5]:
            formatted.append(f"- {patent.get('patent_title', 'No title')} ({patent.get('patent_date', 'Unknown date')})")
        return '\n'.join(formatted)
    
    patentability_prompt = f"""
    Conduct a detailed patentability analysis for this invention against prior art:
    
    Invention: {invention_description}
    
    Prior Art Found:
    US Patents: {len(prior_art_results['us_patents'])} relevant patents
    International Patents: {len(prior_art_results['epo_patents'])} relevant patents
    
    Most Relevant Prior Art:
    {format_prior_art_abstracts(prior_art_results['us_patents'])}
    
    Assess each patentability requirement (scale 1-100):
    1. Novelty: How novel is this invention compared to prior art?
    2. Non-Obviousness: How non-obvious are the inventive combinations?
    3. Utility: How clear and substantial is the utility?
    4. Enablement: How well can this be enabled by the description?
    5. Written Description: How adequate is the technical description?
    
    Also evaluate:
    - Specific novelty aspects that distinguish from prior art
    - Non-obvious combinations of known elements
    - Potential obviousness rejections and responses
    - Claim differentiation opportunities
    - Prior art gaps that support patentability
    
    Return as JSON with detailed patentability assessment.
    """
    
    return llm_call(patentability_prompt)

# Step 3: Claim Scope and Breadth Analysis
def analyze_claim_scope_potential(invention_description, prior_art_landscape, llm_call):
    def summarize_prior_art_landscape(prior_art_landscape):
        us_count = len(prior_art_landscape.get('us_patents', []))
        epo_count = len(prior_art_landscape.get('epo_patents', []))
        return f"{us_count} US patents, {epo_count} international patents"
    
    claim_scope_prompt = f"""
    Analyze the potential claim scope and breadth for this invention:
    
    Invention: {invention_description}
    
    Prior Art Landscape: {summarize_prior_art_landscape(prior_art_landscape)}
    
    Evaluate potential claim strategies:
    
    1. Independent Claim Breadth (1-100): How broad can the main claims be?
    2. Dependent Claim Opportunities (1-100): How many valuable dependent claims possible?
    3. Method Claim Potential (1-100): Strength of method/process claims?
    4. Apparatus Claim Potential (1-100): Strength of device/system claims?
    5. Composition Claim Potential (1-100): Strength of composition claims?
    6. Design Around Difficulty (1-100): How hard to design around these claims?
    
    Provide specific claim strategy recommendations:
    - Suggested independent claim scope
    - Key dependent claim elements
    - Alternative claim approaches
    - Claim differentiation from prior art
    - Potential claim limitations needed
    
    Return as JSON with detailed claim analysis.
    """
    
    return llm_call(claim_scope_prompt)

def analyze_patent_family_opportunities(inventive_concepts, claim_potential, llm_call):
    family_strategy_prompt = f"""
    Analyze patent family and continuation opportunities:
    
    Core Inventive Concepts: {inventive_concepts}
    Claim Potential Assessment: {claim_potential}
    
    Evaluate:
    1. Continuation Application Potential: How many continuation applications viable?
    2. Divisional Application Opportunities: Natural divisions of the invention?
    3. Continuation-in-Part Potential: How likely are improvement opportunities?
    4. International Filing Value: PCT and foreign filing recommendations?
    5. Patent Family Monetization: Licensing and enforcement potential?
    
    Provide strategic recommendations for:
    - Optimal filing strategy
    - Patent family development timeline  
    - Geographic filing priorities
    - Claim strategy across family members
    
    Return as JSON with strategic recommendations.
    """
    
    return llm_call(family_strategy_prompt)

# Step 4: Freedom to Operate (FTO) Analysis
def conduct_freedom_to_operate_analysis(invention_description, prior_art_results, llm_call):
    # Identify potentially blocking patents
    blocking_patents = []
    
    for patent in prior_art_results['us_patents']:
        # Check if patent is still active (not expired)
        patent_date = datetime.strptime(patent['patent_date'], '%Y-%m-%d')
        expiry_date = patent_date + timedelta(days=20*365)  # 20 years from filing
        
        if datetime.now() < expiry_date:
            # Analyze potential infringement risk
            infringement_risk = assess_infringement_risk(invention_description, patent, llm_call)
            if infringement_risk['risk_score'] > 50:
                blocking_patents.append({
                    'patent_number': patent['patent_number'],
                    'risk_score': infringement_risk['risk_score'],
                    'risk_analysis': infringement_risk['analysis'],
                    'expiry_date': expiry_date.strftime('%Y-%m-%d')
                })
    
    # Generate FTO assessment
    def format_blocking_patents(blocking_patents):
        formatted = []
        for patent in blocking_patents:
            formatted.append(f"- {patent['patent_number']} (Risk: {patent['risk_score']}/100)")
        return '\n'.join(formatted)
    
    fto_prompt = f"""
    Conduct Freedom to Operate analysis for this invention:
    
    Invention: {invention_description}
    
    Potentially Blocking Patents Found: {len(blocking_patents)}
    
    High-Risk Patents:
    {format_blocking_patents(blocking_patents[:5])}
    
    Assess:
    1. Overall FTO Risk Level (1-100, higher = more risk)
    2. Infringement Likelihood for each blocking patent
    3. Design-around feasibility for high-risk patents
    4. Licensing negotiation likelihood and costs
    5. Prior art invalidation opportunities
    6. Commercial freedom assessment
    
    Provide:
    - Specific infringement risk analysis
    - Design-around strategies
    - Licensing requirement assessment
    - Prior art invalidation potential
    - Risk mitigation recommendations
    
    Return as JSON with detailed FTO analysis.
    """
    
    return llm_call(fto_prompt)

def assess_infringement_risk(invention_description, patent, llm_call):
    infringement_prompt = f"""
    Assess infringement risk between this invention and the existing patent:
    
    Invention: {invention_description}
    
    Existing Patent: {patent.get('patent_title', 'No title')}
    Patent Abstract: {patent.get('patent_abstract', 'No abstract')}
    
    Rate infringement risk (1-100) and provide analysis.
    Return as JSON with risk_score and analysis.
    """
    
    return llm_call(infringement_prompt)

def analyze_patent_competitive_landscape(prior_art_results, invention_concepts):
    # Identify key patent holders in the space
    assignee_analysis = {}
    
    for patent in prior_art_results['us_patents']:
        assignee = patent.get('assignee_organization', 'Individual')
        if assignee not in assignee_analysis:
            assignee_analysis[assignee] = {
                'patent_count': 0,
                'recent_patents': 0,
                'patent_numbers': []
            }
        
        assignee_analysis[assignee]['patent_count'] += 1
        assignee_analysis[assignee]['patent_numbers'].append(patent['patent_number'])
        
        if int(patent.get('patent_date', '2000')[:4]) >= 2020:
            assignee_analysis[assignee]['recent_patents'] += 1
    
    # Rank by patent activity
    top_assignees = sorted(assignee_analysis.items(), 
                          key=lambda x: x[1]['patent_count'], 
                          reverse=True)[:10]
    
    def calculate_herfindahl_index(patent_counts):
        total_patents = sum(patent_counts)
        if total_patents == 0:
            return 0
        
        hhi = sum([(count / total_patents) ** 2 for count in patent_counts])
        return hhi * 10000
    
    competitive_landscape = {
        'total_assignees': len(assignee_analysis),
        'top_patent_holders': top_assignees,
        'market_concentration': calculate_herfindahl_index([a[1]['patent_count'] for a in top_assignees]),
        'recent_activity_leaders': sorted(top_assignees, 
                                        key=lambda x: x[1]['recent_patents'], 
                                        reverse=True)[:5]
    }
    
    return competitive_landscape

# Step 5: Defensive Patent Value Assessment
def assess_defensive_patent_value(invention_description, competitive_landscape, market_data, llm_call):
    def format_top_assignees(top_assignees):
        formatted = []
        for assignee, data in top_assignees[:5]:
            formatted.append(f"- {assignee}: {data['patent_count']} patents")
        return '\n'.join(formatted)
    
    defensive_value_prompt = f"""
    Assess the defensive patent value for this invention:
    
    Invention: {invention_description}
    
    Competitive Landscape:
    Top Patent Holders: {format_top_assignees(competitive_landscape['top_patent_holders'])}
    Market Concentration: {competitive_landscape['market_concentration']}
    
    Market Context: {market_data.get('market_potential_score', 50)}/100 market potential
    
    Evaluate defensive value aspects (scale 1-100):
    1. Blocking Potential: How well could this block competitors?
    2. Cross-Licensing Value: Value in licensing negotiations?
    3. Litigation Defense: Strength as defensive patent in litigation?
    4. Market Position Protection: How well does this protect market position?
    5. Technology Development Freedom: Protection of future R&D directions?
    6. Strategic Patent Portfolio Value: Contribution to overall IP strategy?
    
    Consider:
    - Likelihood competitors will need to license this technology
    - Strength as counter-assertion patent in litigation
    - Value in defensive patent pools
    - Protection of key commercial pathways
    - Future technology development protection
    
    Return as JSON with detailed defensive value assessment.
    """
    
    return llm_call(defensive_value_prompt)

def assess_patent_monetization_potential(claim_scope_data, market_data, competitive_data):
    def assess_enforcement_feasibility(claim_scope_data):
        breadth = claim_scope_data.get('independent_claim_breadth', 50)
        strength = claim_scope_data.get('design_around_difficulty', 50)
        return (breadth + strength) / 2
    
    def assess_licensing_potential(monetization_factors):
        market_factor = monetization_factors['market_size_factor']
        claim_factor = monetization_factors['claim_strength_factor']
        return (market_factor + claim_factor) / 2
    
    def assess_enforcement_potential(monetization_factors):
        enforcement_factor = monetization_factors['enforcement_feasibility']
        design_around_factor = monetization_factors['design_around_difficulty']
        return (enforcement_factor + design_around_factor) / 2
    
    monetization_factors = {
        'market_size_factor': min(100, market_data.get('market_potential_score', 50)),
        'claim_strength_factor': claim_scope_data.get('independent_claim_breadth', 50),
        'design_around_difficulty': claim_scope_data.get('design_around_difficulty', 50),
        'competitive_landscape_density': min(100, len(competitive_data.get('top_patent_holders', [])) * 10),
        'enforcement_feasibility': assess_enforcement_feasibility(claim_scope_data)
    }
    
    # Calculate weighted monetization score
    monetization_score = (
        monetization_factors['market_size_factor'] * 0.25 +
        monetization_factors['claim_strength_factor'] * 0.25 +
        monetization_factors['design_around_difficulty'] * 0.20 +
        monetization_factors['enforcement_feasibility'] * 0.20 +
        (100 - monetization_factors['competitive_landscape_density']) * 0.10
    )
    
    return {
        'monetization_score': monetization_score,
        'monetization_factors': monetization_factors,
        'licensing_potential': assess_licensing_potential(monetization_factors),
        'enforcement_potential': assess_enforcement_potential(monetization_factors)
    }

# Step 6: IP Strength Scoring Algorithm
def calculate_ip_strength_score(patentability_data, claim_scope_data, fto_data, 
                               defensive_value_data, monetization_data):
    def calculate_ip_confidence(patentability_data, fto_data):
        confidence_factors = [
            len(fto_data.get('blocking_patents', [])) > 0,  # Comprehensive FTO analysis
            patentability_data.get('prior_art_coverage', 0) > 50,  # Good prior art coverage
            patentability_data.get('novelty', 0) > 60,  # Strong novelty
            fto_data.get('overall_fto_risk_level', 100) < 70  # Manageable FTO risk
        ]
        
        return sum(confidence_factors) / len(confidence_factors) * 100
    
    # Weighted scoring components
    components = {
        "patentability_strength": (
            patentability_data.get('novelty', 50) * 0.3 +
            patentability_data.get('non_obviousness', 50) * 0.3 +
            patentability_data.get('utility', 50) * 0.2 +
            patentability_data.get('enablement', 50) * 0.2
        ) * 0.30,
        
        "claim_scope_strength": (
            claim_scope_data.get('independent_claim_breadth', 50) * 0.4 +
            claim_scope_data.get('dependent_claim_opportunities', 50) * 0.3 +
            claim_scope_data.get('design_around_difficulty', 50) * 0.3
        ) * 0.25,
        
        "freedom_to_operate": (100 - fto_data.get('overall_fto_risk_level', 50)) * 0.20,
        
        "defensive_value": (
            defensive_value_data.get('blocking_potential', 50) * 0.3 +
            defensive_value_data.get('cross_licensing_value', 50) * 0.25 +
            defensive_value_data.get('litigation_defense', 50) * 0.25 +
            defensive_value_data.get('strategic_portfolio_value', 50) * 0.2
        ) * 0.15,
        
        "monetization_potential": monetization_data.get('monetization_score', 50) * 0.10
    }
    
    total_score = sum(components.values())
    
    # Risk adjustments for IP strength
    risk_penalties = {
        'high_fto_risk': max(0, fto_data.get('overall_fto_risk_level', 50) - 70) * 0.5,
        'weak_patentability': max(0, 50 - min(patentability_data.get('novelty', 50), 
                                             patentability_data.get('non_obviousness', 50))) * 0.3,
        'narrow_claim_scope': max(0, 50 - claim_scope_data.get('independent_claim_breadth', 50)) * 0.2
    }
    
    total_penalty = sum(risk_penalties.values())
    final_score = max(0, total_score - total_penalty)
    
    return {
        "ip_strength_score": round(final_score, 1),
        "component_scores": components,
        "risk_penalties": risk_penalties,
        "confidence_level": calculate_ip_confidence(patentability_data, fto_data)
    }

# Step 7: Generate IP Strength Report
def generate_ip_reasoning(novelty_score, non_obviousness_score, prior_art_count, claim_breadth, 
                        design_around_difficulty, family_potential, fto_risk, blocking_patent_count, 
                        design_around_feasibility, defensive_value, monetization_score, 
                        competitive_density, major_holders, prosecution_strategy, 
                        licensing_outlook, llm_call):
    ip_reasoning_prompt = f"""
Based on this comprehensive IP strength analysis, provide detailed reasoning:

Patentability Assessment:
- Novelty: {novelty_score}/100
- Non-Obviousness: {non_obviousness_score}/100  
- Prior Art Analysis: {prior_art_count} relevant patents analyzed

Claim Scope Analysis:
- Independent Claim Breadth: {claim_breadth}/100
- Design-Around Difficulty: {design_around_difficulty}/100
- Patent Family Potential: {family_potential}

Freedom to Operate:
- FTO Risk Level: {fto_risk}/100
- Blocking Patents: {blocking_patent_count}
- Design-Around Feasibility: {design_around_feasibility}

Defensive Value: {defensive_value}/100
Monetization Potential: {monetization_score}/100

Key Findings:
- Patent landscape competitive density: {competitive_density}
- Major patent holders: {major_holders}
- Patent prosecution strategy: {prosecution_strategy}
- Licensing and enforcement outlook: {licensing_outlook}

Provide:
1. Overall IP strength assessment and strategic value
2. Patent prosecution strategy recommendations
3. Freedom to operate risk mitigation plan
4. Defensive patent portfolio contribution
5. Monetization and licensing potential
6. Competitive positioning through IP
7. Long-term IP strategy considerations

Include specific patent numbers, claim strategies, and quantitative justifications.
"""
    return llm_call(ip_reasoning_prompt)

# Step 8: Data Structure for Storage
def create_ip_strength_result(ip_score, novelty_score, non_obviousness_score, utility_score, 
                            enablement_score, written_description_score, prior_art_results, 
                            most_relevant_patents, novelty_gaps, claim_breadth, dependent_opportunities, 
                            method_claims, apparatus_claims, composition_claims, design_around_difficulty, 
                            family_strategy, fto_risk_level, blocking_patents, infringement_risks, 
                            design_around_strategies, licensing_requirements, invalidation_opportunities, 
                            top_assignees, market_concentration, recent_activity, patent_density, 
                            blocking_potential, cross_licensing_value, litigation_defense, 
                            portfolio_value, licensing_potential, enforcement_feasibility, 
                            market_leverage, revenue_potential, ip_reasoning, confidence_level, 
                            total_patents_analyzed, search_queries):
    ip_strength_result = {
        "ip_strength_score": ip_score,
        "patentability_assessment": {
            "novelty_score": novelty_score,
            "non_obviousness_score": non_obviousness_score,
            "utility_score": utility_score,
            "enablement_score": enablement_score,
            "written_description_score": written_description_score,
            "prior_art_analysis": {
                "us_patents_found": len(prior_art_results.get('us_patents', [])),
                "international_patents_found": len(prior_art_results.get('epo_patents', [])),
                "most_relevant_patents": most_relevant_patents,
                "novelty_gaps_identified": novelty_gaps
            }
        },
        "claim_scope_analysis": {
            "independent_claim_breadth": claim_breadth,
            "dependent_claim_opportunities": dependent_opportunities,
            "method_claim_potential": method_claims,
            "apparatus_claim_potential": apparatus_claims,
            "composition_claim_potential": composition_claims,
            "design_around_difficulty": design_around_difficulty,
            "patent_family_strategy": family_strategy
        },
        "freedom_to_operate": {
            "overall_risk_level": fto_risk_level,
            "blocking_patents": blocking_patents,
            "infringement_risks": infringement_risks,
            "design_around_strategies": design_around_strategies,
            "licensing_requirements": licensing_requirements,
            "prior_art_invalidation_opportunities": invalidation_opportunities
        },
        "competitive_landscape": {
            "major_patent_holders": top_assignees,
            "market_concentration_index": market_concentration,
            "recent_patent_activity": recent_activity,
            "competitive_patent_density": patent_density
        },
        "defensive_value": {
            "blocking_potential": blocking_potential,
            "cross_licensing_value": cross_licensing_value,
            "litigation_defense_strength": litigation_defense,
            "strategic_portfolio_value": portfolio_value
        },
        "monetization_potential": {
            "licensing_potential": licensing_potential,
            "enforcement_feasibility": enforcement_feasibility,
            "market_leverage": market_leverage,
            "revenue_potential": revenue_potential
        },
        "detailed_reasoning": ip_reasoning,
        "confidence_score": confidence_level,
        "api_call_timestamp": datetime.now(),
        "patent_analysis_metadata": {
            "patents_analyzed": total_patents_analyzed,
            "search_queries_used": search_queries,
            "api_sources_used": ["PatentsView", "EPO", "USPTO"]
        }
    }
    return ip_strength_result

# Main function to orchestrate IP strength analysis
def analyze_ip_strength(invention_description, llm_call, market_data=None):
    """
    Complete IP strength analysis workflow
    
    Args:
        invention_description (str): Description of the invention to analyze
        llm_call (function): Function to make LLM API calls
        market_data (dict): Market potential data from previous analysis
    
    Returns:
        dict: Complete IP strength analysis results
    """
    
    if market_data is None:
        market_data = {'market_potential_score': 50}
    
    # Step 1: Extract IP elements
    ip_elements = extract_ip_elements(invention_description, llm_call)
    
    # Step 2: Conduct comprehensive prior art search
    prior_art_results = conduct_comprehensive_prior_art_search(
        ip_elements.get('core_inventive_concepts', []),
        ip_elements.get('potential_claim_elements', []),
        ip_elements.get('patent_classification_codes', [])
    )
    
    patentability_assessment = assess_patentability_strength(
        invention_description, prior_art_results, llm_call
    )
    
    # Step 3: Analyze claim scope potential
    claim_scope_analysis = analyze_claim_scope_potential(
        invention_description, prior_art_results, llm_call
    )
    
    family_opportunities = analyze_patent_family_opportunities(
        ip_elements.get('core_inventive_concepts', []),
        claim_scope_analysis,
        llm_call
    )
    
    # Step 4: Conduct FTO analysis
    fto_analysis = conduct_freedom_to_operate_analysis(
        invention_description, prior_art_results, llm_call
    )
    
    competitive_landscape = analyze_patent_competitive_landscape(
        prior_art_results,
        ip_elements.get('core_inventive_concepts', [])
    )
    
    # Step 5: Assess defensive patent value
    defensive_value_assessment = assess_defensive_patent_value(
        invention_description, competitive_landscape, market_data, llm_call
    )
    
    monetization_assessment = assess_patent_monetization_potential(
        claim_scope_analysis, market_data, competitive_landscape
    )
    
    # Step 6: Calculate IP strength score
    ip_score_result = calculate_ip_strength_score(
        patentability_assessment, claim_scope_analysis, fto_analysis,
        defensive_value_assessment, monetization_assessment
    )
    
    # Step 7: Generate reasoning
    reasoning = generate_ip_reasoning(
        patentability_assessment.get('novelty', 50),
        patentability_assessment.get('non_obviousness', 50),
        len(prior_art_results.get('us_patents', [])),
        claim_scope_analysis.get('independent_claim_breadth', 50),
        claim_scope_analysis.get('design_around_difficulty', 50),
        family_opportunities,
        fto_analysis.get('overall_fto_risk_level', 50),
        len(fto_analysis.get('blocking_patents', [])),
        fto_analysis.get('design_around_feasibility', 50),
        defensive_value_assessment.get('blocking_potential', 50),
        monetization_assessment.get('monetization_score', 50),
        competitive_landscape.get('market_concentration', 0),
        [a[0] for a in competitive_landscape.get('top_patent_holders', [])[:3]],
        "Standard prosecution strategy",  # Simplified
        "Moderate licensing potential",   # Simplified
        llm_call
    )
    
    # Step 8: Create final result
    result = create_ip_strength_result(
        ip_score_result['ip_strength_score'],
        patentability_assessment.get('novelty', 50),
        patentability_assessment.get('non_obviousness', 50),
        patentability_assessment.get('utility', 50),
        patentability_assessment.get('enablement', 50),
        patentability_assessment.get('written_description', 50),
        prior_art_results,
        prior_art_results.get('us_patents', [])[:5],  # Most relevant
        patentability_assessment.get('novelty_gaps', []),
        claim_scope_analysis.get('independent_claim_breadth', 50),
        claim_scope_analysis.get('dependent_claim_opportunities', 50),
        claim_scope_analysis.get('method_claim_potential', 50),
        claim_scope_analysis.get('apparatus_claim_potential', 50),
        claim_scope_analysis.get('composition_claim_potential', 50),
        claim_scope_analysis.get('design_around_difficulty', 50),
        family_opportunities,
        fto_analysis.get('overall_fto_risk_level', 50),
        fto_analysis.get('blocking_patents', []),
        fto_analysis.get('infringement_risks', []),
        fto_analysis.get('design_around_strategies', []),
        fto_analysis.get('licensing_requirements', []),
        fto_analysis.get('invalidation_opportunities', []),
        competitive_landscape.get('top_patent_holders', []),
        competitive_landscape.get('market_concentration', 0),
        competitive_landscape.get('recent_activity_leaders', []),
        len(prior_art_results.get('us_patents', [])),
        defensive_value_assessment.get('blocking_potential', 50),
        defensive_value_assessment.get('cross_licensing_value', 50),
        defensive_value_assessment.get('litigation_defense', 50),
        defensive_value_assessment.get('strategic_portfolio_value', 50),
        monetization_assessment.get('licensing_potential', 50),
        monetization_assessment.get('enforcement_potential', 50),
        monetization_assessment.get('monetization_score', 50),
        monetization_assessment.get('monetization_score', 50),
        reasoning,
        ip_score_result['confidence_level'],
        len(prior_art_results.get('us_patents', [])) + len(prior_art_results.get('epo_patents', [])),
        ip_elements.get('prior_art_search_terms', [])
    )
    
    return result
# literature_invention_search/invention_prompt.py

# Consistent prompt for LLM to identify potential inventions in research paper abstracts.

# Note: This prompt is a starting point and may need refinement based on testing
# and desired specificity of "invention potential."

INVENTION_ANALYSIS_PROMPT_TEMPLATE = """\
You are an expert in identifying potential inventions and patentable ideas from biomedical research.
Analyze the following research paper abstract to determine if it describes a potential invention.

A potential invention may include, but is not limited to:
- Novel compounds, materials, or compositions of matter.
- New methods, processes, or techniques (e.g., diagnostic, therapeutic, manufacturing).
- Novel devices, systems, or apparatus.
- New uses for existing compounds, methods, or devices.
- Software or algorithms with a specific technical application in the biomedical field.
- Genetically modified organisms or novel genetic constructs with practical applications.

Consider the following aspects:
- **Novelty**: Does the abstract suggest something new or an unexpected result?
- **Utility/Applicability**: Does it describe a practical application, solve a problem, or offer a significant improvement over existing solutions?
- **Non-obviousness (Inventive Step)**: While hard to judge from an abstract alone, look for surprising findings or solutions that are not merely incremental adjustments.

Abstract:
---
{abstract_text}
---

Based on the abstract, please provide your analysis in JSON format with the following fields:
- "is_potential_invention": boolean (true if you believe there's potential for an invention, false otherwise)
- "confidence_score": float (your confidence in this assessment, from 0.0 to 1.0)
- "reasoning": string (a brief explanation for your assessment, highlighting specific phrases or ideas from the abstract that support your conclusion. If not an invention, explain why.)
- "keywords_suggesting_invention": list of strings (specific keywords or phrases from the abstract that point towards novelty or inventive aspects, if any)

Example JSON Output:
{{
  "is_potential_invention": true,
  "confidence_score": 0.85,
  "reasoning": "The abstract describes a novel gene editing technique (XYZ-Cas) that shows significantly higher efficiency and lower off-target effects for treating disease Y. This suggests a new and improved method with clear therapeutic utility.",
  "keywords_suggesting_invention": ["novel gene editing technique", "XYZ-Cas", "higher efficiency", "lower off-target effects", "treating disease Y"]
}}

If the abstract is too vague, lacks specific details about a new method/compound/device, or primarily describes observational findings without a clear inventive step or application, it is less likely to be a potential invention. An abstract that only states "further research is needed" without presenting a concrete new solution is also less likely to be an invention.

Provide only the JSON output.
"""

# Example of how to use the template:
# paper_abstract = "This paper details the discovery of compound X..."
# filled_prompt = INVENTION_ANALYSIS_PROMPT_TEMPLATE.format(abstract_text=paper_abstract)

if __name__ == '__main__':
    sample_abstract = """
    We report the development of a novel biodegradable polymer, PolyInventX, for controlled drug delivery.
    Experiments demonstrate PolyInventX's superior biocompatibility and tunable degradation rates,
    achieving sustained release of therapeutic agents for up to 90 days. This represents a significant
    advancement over existing delivery systems.
    """

    formatted_prompt = INVENTION_ANALYSIS_PROMPT_TEMPLATE.format(abstract_text=sample_abstract)
    print("Formatted Prompt Example:")
    print(formatted_prompt)

    print("\nExpected JSON structure (for guidance):")
    expected_json_guidance = {
        "is_potential_invention": True, # or False
        "confidence_score": 0.0, # 0.0 to 1.0
        "reasoning": "Brief explanation...",
        "keywords_suggesting_invention": ["keyword1", "phrase2"] # or empty list
    }
    import json
    print(json.dumps(expected_json_guidance, indent=2))

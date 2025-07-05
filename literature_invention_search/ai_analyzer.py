import json
import os
from typing import Dict, Any, Optional

try:
    from . import config
    from .invention_prompt import INVENTION_ANALYSIS_PROMPT_TEMPLATE
except ImportError:
    # Fallback for direct execution or different project structures
    import config
    from invention_prompt import INVENTION_ANALYSIS_PROMPT_TEMPLATE

# Initialize clients based on loaded configuration
# This part will only work if the respective libraries are installed and keys are set
llm_client = None
if config.LLM_PROVIDER == "openai" and config.OPENAI_API_KEY:
    try:
        from openai import OpenAI
        llm_client = OpenAI(api_key=config.OPENAI_API_KEY)
    except ImportError:
        print("OpenAI library not installed. Please install it to use OpenAI as a provider.")
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
elif config.LLM_PROVIDER == "anthropic" and config.ANTHROPIC_API_KEY:
    try:
        from anthropic import Anthropic
        llm_client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    except ImportError:
        print("Anthropic library not installed. Please install it to use Anthropic as a provider.")
    except Exception as e:
        print(f"Failed to initialize Anthropic client: {e}")

def analyze_abstract_with_llm(abstract_text: str) -> Optional[Dict[str, Any]]:
    """
    Analyzes a research paper abstract using the configured LLM provider to identify
    potential inventions.

    Args:
        abstract_text: The text of the research paper abstract.

    Returns:
        A dictionary containing the LLM's analysis (is_potential_invention,
        confidence_score, reasoning, keywords_suggesting_invention) or None if
        analysis fails or the LLM client is not configured (unless abstract is invalid first).
    """
    # First, check abstract validity. This should happen before checking LLM client.
    if not abstract_text or abstract_text.strip() == "N/A" or len(abstract_text.strip()) < 50: # Basic check for valid abstract
        print("Abstract is empty, N/A, or too short. Returning predefined analysis.")
        return {
            "is_potential_invention": False,
            "confidence_score": 0.0,
            "reasoning": "Abstract was empty, N/A, or too short for meaningful analysis.",
            "keywords_suggesting_invention": []
        }

    # If abstract is valid, then check for LLM client configuration.
    if not llm_client:
        print(f"LLM client for provider '{config.LLM_PROVIDER}' is not initialized. "
              "Check API key and library installation.")
        return None

    # Correctly placed and single filled_prompt line
    filled_prompt = INVENTION_ANALYSIS_PROMPT_TEMPLATE.format(abstract_text=abstract_text)

    try:
        if config.LLM_PROVIDER == "openai":
            # Using OpenAI's chat completions endpoint
            # Model choice can be made configurable too, e.g., "gpt-3.5-turbo" or "gpt-4"
            # For cost/speed, "gpt-3.5-turbo" is often a good start.
            response = llm_client.chat.completions.create(
                model="gpt-3.5-turbo-0125", # Or another suitable model
                messages=[
                    {"role": "system", "content": "You are an expert in identifying potential inventions. Your output must be a valid JSON object."},
                    {"role": "user", "content": filled_prompt}
                ],
                response_format={"type": "json_object"}, # Enforce JSON output
                temperature=0.2, # Lower temperature for more deterministic output
            )
            # Ensure response content is not None and is a string
            json_string = response.choices[0].message.content
            if json_string is None:
                print("OpenAI response content is None.")
                return None

        elif config.LLM_PROVIDER == "anthropic":
            # Using Anthropic's messages endpoint
            # Model choice like "claude-3-opus-20240229", "claude-3-sonnet-20240229", etc.
            # "claude-3-haiku-20240307" is often good for speed/cost.
            # Anthropic's API expects the system prompt separately.
            system_prompt_anthropic = "You are an expert in identifying potential inventions. Your output must be a valid JSON object enclosed in ```json ... ``` tags if necessary, but preferably just the JSON object itself."
            user_message_anthropic = INVENTION_ANALYSIS_PROMPT_TEMPLATE.format(abstract_text=abstract_text) # The prompt already asks for JSON

            response = llm_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024, # Adjust as needed
                system=system_prompt_anthropic,
                messages=[
                    {"role": "user", "content": user_message_anthropic}
                ]
            )
            json_string = response.content[0].text
            if json_string is None:
                print("Anthropic response content is None.")
                return None

            # Anthropic might wrap JSON in ```json ... ```, try to extract it
            if json_string.strip().startswith("```json"):
                json_string = json_string.strip()[7:-3].strip()
            elif json_string.strip().startswith("```"): # More general removal of backticks
                 json_string = json_string.strip()[3:-3].strip()


        else:
            print(f"Unsupported LLM provider: {config.LLM_PROVIDER}")
            return None

        # Parse the JSON string response from the LLM
        analysis_result = json.loads(json_string)

        # Validate the structure of the analysis_result (optional but good practice)
        expected_keys = {"is_potential_invention", "confidence_score", "reasoning", "keywords_suggesting_invention"}
        if not expected_keys.issubset(analysis_result.keys()):
            print(f"LLM output missing expected keys. Received: {analysis_result.keys()}")
            # Attempt to salvage if possible, or return error
            # For now, just log and return as is, or could return a structured error.
            # To be robust, one might try to fill missing keys with default values.

        return analysis_result

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from LLM response: {e}")
        print(f"LLM Raw Response was: {json_string}") # Log the raw response for debugging
        return None
    except Exception as e:
        # Catch other potential API errors or issues
        print(f"Error during LLM API call for provider {config.LLM_PROVIDER}: {e}")
        return None

if __name__ == '__main__':
    # This main block is for testing the ai_analyzer.py script directly.
    # Ensure you have a .env file in the project root with your API keys, e.g.:
    # OPENAI_API_KEY="sk-..."
    # LLM_PROVIDER="openai"
    # OR
    # ANTHROPIC_API_KEY="sk-ant-..."
    # LLM_PROVIDER="anthropic"

    if not llm_client:
        print("LLM client not configured. Please set API keys in .env file and choose a provider.")
    else:
        print(f"Testing AI analysis with provider: {config.LLM_PROVIDER}")

        sample_abstract_invention = """
        We describe a novel photovoltaic cell design incorporating quantum dots embedded
        within a perovskite matrix. This hybrid structure achieves a certified power
        conversion efficiency of 28.5%, surpassing current single-junction silicon cells.
        The fabrication process is scalable and utilizes low-cost materials.
        """

        sample_abstract_non_invention = """
        This study reviews the current literature on the effects of caffeine on student
        test performance. We analyzed 50 peer-reviewed articles published between 2010 and
        2023. Results indicate a moderate positive correlation, but further research is
        needed to establish causality and optimal dosage.
        """

        sample_abstract_na = "N/A"


        print("\n--- Analyzing potential invention abstract ---")
        analysis1 = analyze_abstract_with_llm(sample_abstract_invention)
        if analysis1:
            print(json.dumps(analysis1, indent=2))
            assert analysis1.get("is_potential_invention") is True # Expected
        else:
            print("Analysis 1 failed.")

        print("\n--- Analyzing non-invention abstract ---")
        analysis2 = analyze_abstract_with_llm(sample_abstract_non_invention)
        if analysis2:
            print(json.dumps(analysis2, indent=2))
            assert analysis2.get("is_potential_invention") is False # Expected
        else:
            print("Analysis 2 failed.")

        print("\n--- Analyzing N/A abstract ---")
        analysis3 = analyze_abstract_with_llm(sample_abstract_na)
        if analysis3:
            print(json.dumps(analysis3, indent=2))
            assert analysis3.get("is_potential_invention") is False # Expected
            assert "Abstract was empty" in analysis3.get("reasoning")
        else:
            print("Analysis 3 failed (or correctly returned None for N/A abstract if not handled to return dict).")

        print("\n--- Analyzing short abstract ---")
        analysis4 = analyze_abstract_with_llm("Short abstract.")
        if analysis4:
            print(json.dumps(analysis4, indent=2))
            assert analysis4.get("is_potential_invention") is False # Expected
            assert "too short" in analysis4.get("reasoning")
        else:
            print("Analysis 4 failed.")

        # Test with an empty string
        print("\n--- Analyzing empty abstract ---")
        analysis5 = analyze_abstract_with_llm("")
        if analysis5:
            print(json.dumps(analysis5, indent=2))
            assert analysis5.get("is_potential_invention") is False
            assert "Abstract was empty" in analysis5.get("reasoning")
        else:
            print("Analysis 5 failed.")

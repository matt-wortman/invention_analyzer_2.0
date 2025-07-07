# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Setup GUI environment (WSL/Linux)
source gui_setup.sh

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Test GUI functionality
python test_qt_gui.py

# Test individual components
python literature_invention_search/test_analysis.py
python literature_invention_search/test_batch.py
python literature_invention_search/test_one_paper.py

# Run pytest for unit tests
pytest
```

### Main Application Usage
```bash
# Run from project root as module
python -m literature_invention_search.main fetch --search_term "your search" --num_papers 10

# Available commands:
# fetch: Search and download papers from PubMed
# analyze: Run AI analysis on stored papers
# export: Export flagged papers to CSV

# Example: Fetch last 2 years of papers
python -m literature_invention_search.main fetch --years 2 --num_papers 50
```

## Architecture Overview

### Core Components
- **literature_invention_search/**: Main application package
  - `main.py`: CLI interface with fetch/analyze/export commands
  - `config.py`: Configuration management and environment variable loading
  - `simple_ncbi.py`: NCBI E-utilities API wrapper for PubMed data
  - `ai_analyzer.py`: LLM integration for invention analysis (OpenAI/Anthropic)
  - `simple_database.py`: SQLite database operations
  - `batch_processor.py`: Batch processing pipeline
  - `invention_prompt.py`: AI prompt templates

### Advanced Analysis Components
- **claude_component_design/**: Enhanced invention evaluation system
  - Advanced patent landscape analysis
  - Market potential assessment
  - Technical novelty scoring
  - Commercial readiness evaluation
  - IP strength analysis

### Data Flow
1. **Search**: Query PubMed via NCBI E-utilities for Cincinnati Children's Hospital papers
2. **Store**: Save metadata and abstracts to local SQLite database
3. **Analyze**: Use configured LLM (OpenAI/Anthropic) to identify potential inventions
4. **Export**: Generate CSV reports of flagged papers

## Configuration

### Environment Variables (.env file)
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=openai  # or "anthropic"
NCBI_API_KEY=your_ncbi_key  # optional but recommended
NCBI_EMAIL=your@email.com   # required for NCBI API
```

### Database Location
- Database file: `literature_invention_search/papers.db`
- CSV exports: Same directory as database

## Development Principles

### Line Ending Issues (WSL)
Use `echo` commands to build scripts line by line instead of creating multi-line files to avoid CRLF issues:
```bash
# GOOD - No line ending issues
echo '# Simple script' > script.sh
echo 'source venv/bin/activate' >> script.sh

# BAD - Creates line ending problems  
cat > script.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
EOF
```

### Virtual Environment Activation
Create scripts designed to be sourced rather than executed:
```bash
# For scripts that need to persist environment changes
source gui_setup.sh  # NOT ./gui_setup.sh
```

### Error Handling
- Always check for API key configuration before making LLM calls
- Handle network timeouts gracefully for NCBI API calls
- Validate abstract content before AI analysis
- Return structured error responses rather than None

## Testing Strategy

### Real Data Testing
- Use actual NCBI PMIDs for testing: 38017825, 18233153
- Test with various abstract formats including N/A and empty abstracts
- Verify AI analysis with both potential invention and non-invention abstracts

### Component Testing
- Test NCBI API integration with known PMIDs
- Test AI analysis with sample abstracts
- Test database operations with mock data
- Test batch processing with small paper sets

## Dependencies

### Core Libraries
- `biopython>=1.80`: NCBI E-utilities integration
- `requests>=2.28.0`: HTTP API calls
- `PySide6>=6.4.0`: Qt GUI framework
- `openai>=1.0.0` or `anthropic>=0.7.0`: LLM integration
- `python-dotenv>=0.20.0`: Environment variable management

### Development Tools
- `pytest>=7.0.0`: Testing framework
- `pytest-cov>=4.0.0`: Coverage reporting

## Common Issues

### GUI Setup
If GUI tests fail, ensure X11 forwarding is properly configured in WSL:
```bash
export DISPLAY=:0
```

### API Rate Limits
- NCBI API: 3 requests/second without API key, 10/second with key
- OpenAI/Anthropic: Check your plan's rate limits
- Add delays between batch requests if needed

### Database Schema
The SQLite database includes AI analysis fields:
- `ai_is_invention_candidate`: Boolean flag
- `ai_confidence`: Confidence score (0.0-1.0)
- `ai_reasoning`: Explanation of AI decision
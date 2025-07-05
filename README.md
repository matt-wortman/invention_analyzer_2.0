# Academic Publication Search Tool

A simple, reliable tool to help Cincinnati Children's Hospital researchers identify potential inventions in their published research papers.

## Quick Start

### 1. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Activate GUI Environment (WSL/Linux)
```bash
source gui_setup.sh
```

### 3. Test GUI Works
```bash
python test_qt_gui.py
```

## Project Documentation

- **[PROJECT_GOALS.md](PROJECT_GOALS.md)** - Requirements and success criteria
- **[REBUILD_PLAN.md](REBUILD_PLAN.md)** - 4-week implementation timeline
- **[PROJECT_PROTOCOLS.md](PROJECT_PROTOCOLS.md)** - Development workflows
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed environment setup
- **[LESSONS_LEARNED.md](LESSONS_LEARNED.md)** - Critical patterns and anti-patterns

## Core Functionality

### What It Does
1. **Search PubMed** for Cincinnati Children's Hospital publications
2. **Store metadata** in local SQLite database
3. **Analyze abstracts** with AI to identify potential inventions
4. **Export results** to CSV for review

### What It Doesn't Do
- Complex database architectures
- Real-time monitoring
- Multi-user collaboration
- Enterprise features

## Development Principles

- **Start simple** - Get basic functionality working first
- **Test with real data** - Use actual NCBI publications
- **Incremental complexity** - Add features only when needed
- **Keep dependencies minimal** - Prefer standard library

## Current Status

**Phase**: Project restart with clean architecture  
**Next Steps**: Implement Phase 1 MVP (see REBUILD_PLAN.md)  
**Timeline**: 4 weeks to full functionality

### Advanced Components Available
- **`claude_component_design/`** - Enhanced invention evaluation system
  - Prior art analysis
  - Market potential assessment  
  - Technical novelty scoring
  - Commercial readiness evaluation
  - IP strength analysis

## Dependencies

```bash
pip install -r requirements.txt
```

Core libraries:
- `requests` - HTTP API calls
- `biopython` - NCBI E-utilities
- `PySide6` - Qt GUI framework
- `openai` or `anthropic` - AI analysis

---

*This is a research tool focused on simplicity and reliability over enterprise features.*

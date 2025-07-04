# Project Goals and Requirements

## Primary Goal
Create a **simple, reliable tool** to help Cincinnati Children's Hospital researchers identify potential inventions in their published research papers.

## Success Criteria
1. **Download publications** from PubMed for Cincinnati Children's Hospital
2. **Store basic metadata** in a local database
3. **Analyze abstracts** using AI to flag potential inventions
4. **Generate reports** of flagged publications for review

## Functional Requirements

### Core Functions (Must Have)
1. **Publication Search**
   - Search PubMed using institutional affiliation
   - Filter by date range (last 1-10 years)
   - Limit results (10-1000 papers)
   - Handle Cincinnati Children's Hospital name variations

2. **Data Storage**
   - Store PMID, title, authors, abstract, publication date
   - Track download date and source
   - Prevent duplicate entries
   - Simple SQLite database

3. **AI Analysis**
   - Send abstracts to OpenAI or Anthropic API
   - Use consistent prompt for invention detection
   - Store analysis results and confidence scores
   - Handle API rate limits and errors

4. **Results Export**
   - Export flagged publications to CSV
   - Include analysis reasoning
   - Sort by confidence score

### Enhanced Functions (Nice to Have)
1. **Full Text Processing**
   - Download full text from PMC when available
   - Analyze full text instead of just abstracts
   - Extract methods and results sections

2. **Batch Processing**
   - Process multiple years of publications
   - Resume interrupted downloads
   - Progress tracking

3. **Simple GUI**
   - Basic search interface
   - Results table with sorting
   - Export button

## Non-Functional Requirements

### Reliability
- **Fail gracefully**: Network errors shouldn't crash the program
- **Resume capability**: Should be able to restart after interruption
- **Data integrity**: No partial or corrupted records

### Performance
- **Reasonable speed**: Process 100 papers in under 10 minutes
- **Memory efficient**: Handle 1000+ papers without excessive memory use
- **API compliance**: Respect NCBI and LLM API rate limits

### Usability
- **Simple setup**: Single command to install and run
- **Clear output**: Obvious what the program is doing
- **Helpful errors**: Clear error messages with suggested fixes

### Maintainability
- **Simple code**: Easy to understand and modify
- **Minimal dependencies**: Avoid complex third-party libraries
- **Clear documentation**: README with examples

## Technical Constraints

### APIs
- **NCBI E-utilities**: Free tier, rate limits, requires email
- **OpenAI/Anthropic**: Paid APIs, rate limits, API key required
- **No web scraping**: Use only official APIs

### Data
- **Local storage only**: No cloud databases
- **Privacy compliance**: No sensitive data storage
- **Audit trail**: Track all API calls and changes

### Environment
- **Cross-platform**: Windows, macOS, Linux
- **Python 3.9+**: Use standard library when possible
- **Virtual Environment**: Required for package management (venv)
- **WSL GUI Support**: X11 forwarding for Linux GUI testing
- **Offline capable**: Should work without internet after initial setup

## Out of Scope

### What We Won't Build
- **Real-time monitoring**: No continuous publication tracking
- **User management**: Single-user tool only
- **Complex analytics**: No statistical analysis or reporting
- **Patent searching**: Focus only on publications
- **Collaboration features**: No sharing or multi-user support

### What We Won't Use
- **Complex databases**: No PostgreSQL, MongoDB, etc.
- **Web frameworks**: No Django, Flask, FastAPI
- **Enterprise patterns**: No factories, dependency injection, etc.
- **Complex configuration**: No YAML, environment files, etc.

## Research Software Principles

### Reproducibility
- **Version everything**: Code, data, and analysis results
- **Document parameters**: All analysis settings recorded
- **Consistent results**: Same input should produce same output

### Transparency
- **Open methodology**: Clear how decisions are made
- **Audit trail**: Track all data sources and processing steps
- **Error reporting**: Log all failures and their causes

### Incremental Development
- **Start simple**: Get basic functionality working first
- **Add complexity gradually**: Only when needed
- **Validate each step**: Test thoroughly before adding features

## Acceptance Criteria

### Minimum Viable Product (MVP)
- [ ] Download 10 Cincinnati Children's papers from last year
- [ ] Store in SQLite database
- [ ] Analyze abstracts with ChatGPT
- [ ] Export results to CSV
- [ ] Complete process in under 5 minutes

### Full Version
- [ ] Process 1000+ papers efficiently
- [ ] Handle network interruptions gracefully
- [ ] Provide clear progress indication
- [ ] Generate summary reports
- [ ] Simple GUI interface

## Timeline
- **Week 1**: MVP working end-to-end
- **Week 2**: Error handling and reliability
- **Week 3**: Batch processing and GUI
- **Week 4**: Testing and documentation
# Concrete Rebuild Plan

## Phase 1: Minimal Working Prototype (Week 1)

### Goal: Get basic functionality working end-to-end

#### Day 1-2: Core Data Pipeline
**Objective**: Download and store one paper

**Files to create**:
- `simple_ncbi.py` - Basic NCBI API client
- `simple_database.py` - SQLite operations
- `test_one_paper.py` - Test with PMID 40562540

**Success criteria**:
- [ ] Download metadata for one paper
- [ ] Store in SQLite database
- [ ] Retrieve and display stored data

#### Day 3-4: Batch Processing
**Objective**: Process multiple papers

**Files to create**:
- `batch_processor.py` - Handle multiple papers
- `config.py` - Simple configuration dictionary
- `test_batch.py` - Test with 10 papers

**Success criteria**:
- [ ] Search for Cincinnati Children's papers
- [ ] Download and store 10 papers
- [ ] Handle duplicate prevention

#### Day 5-7: AI Analysis
**Objective**: Analyze papers for inventions

**Files to create**:
- `ai_analyzer.py` - OpenAI/Anthropic integration
- `invention_prompt.py` - Consistent analysis prompt
- `test_analysis.py` - Test AI analysis

**Success criteria**:
- [ ] Send abstracts to AI API
- [ ] Store analysis results
- [ ] Export flagged papers to CSV

### Phase 1 File Structure
```
literature_invention_search/
├── simple_ncbi.py          # NCBI API client
├── simple_database.py      # SQLite operations
├── ai_analyzer.py          # AI analysis
├── batch_processor.py      # Main processing logic
├── config.py              # Configuration
├── test_one_paper.py      # Unit tests
├── test_batch.py          # Integration tests
├── main.py                # Command-line interface
├── requirements.txt       # Dependencies
└── papers.db             # SQLite database
```

### Phase 1 Dependencies
```
# requirements.txt
requests>=2.28.0
openai>=1.0.0
anthropic>=0.7.0
biopython>=1.80
```

## Phase 2: Reliability and Polish (Week 2)

### Goal: Make it production-ready

#### Day 8-10: Error Handling
**Objective**: Handle all failure modes gracefully

**Enhancements**:
- Network timeout handling
- API rate limit compliance
- Database connection errors
- Malformed data handling

**Files to modify**:
- All existing files + comprehensive error handling
- Add `error_handler.py` for centralized error management

#### Day 11-12: Logging and Monitoring
**Objective**: Track all operations

**Files to create**:
- `logger.py` - Centralized logging
- `progress_tracker.py` - Progress monitoring

**Success criteria**:
- [ ] Log all API calls and errors
- [ ] Track processing progress
- [ ] Generate summary reports

#### Day 13-14: Testing and Validation
**Objective**: Comprehensive testing

**Files to create**:
- `test_suite.py` - Complete test suite
- `test_data.py` - Test data management
- `validate_results.py` - Data validation

**Success criteria**:
- [ ] >80% test coverage
- [ ] Automated test suite
- [ ] Data validation checks

## Phase 3: Enhanced Features (Week 3)

### Goal: Add advanced functionality

#### Day 15-17: Full Text Processing
**Objective**: Download and analyze full text

**Files to create**:
- `fulltext_downloader.py` - PMC full text retrieval
- `text_processor.py` - Extract sections from full text
- `enhanced_analyzer.py` - Analyze full text instead of abstracts

#### Day 18-19: Batch Operations
**Objective**: Process large datasets efficiently

**Files to create**:
- `batch_manager.py` - Large batch processing
- `resume_processor.py` - Resume interrupted jobs
- `performance_monitor.py` - Performance tracking

#### Day 20-21: Export and Reporting
**Objective**: Generate useful reports

**Files to create**:
- `report_generator.py` - Generate analysis reports
- `export_manager.py` - Multiple export formats
- `summary_stats.py` - Generate statistics

## Phase 4: User Interface (Week 4)

### Goal: Simple GUI for researchers

#### Day 22-24: Basic GUI
**Objective**: Replace command-line with GUI

**Files to create**:
- `gui_main.py` - Main window
- `search_dialog.py` - Search parameters
- `results_table.py` - Display results
- `progress_dialog.py` - Progress indicator

#### Day 25-26: GUI Polish
**Objective**: User-friendly interface

**Enhancements**:
- Export buttons
- Search history
- Settings dialog
- Help documentation

#### Day 27-28: Testing and Documentation
**Objective**: Complete the project

**Files to create**:
- `USER_GUIDE.md` - End-user documentation
- `DEVELOPER_GUIDE.md` - Technical documentation
- Complete test suite for GUI

## Implementation Strategy

### Start Fresh
1. **Create new directory**: `literature_search_v2/`
2. **Copy working XML code**: Extract any working functions from current codebase
3. **Build incrementally**: Start with simplest possible version

### Daily Workflow
1. **Morning**: Review previous day's work
2. **Planning**: Define specific day's goals
3. **Implementation**: Code in Terminal 1
4. **Testing**: Validate in Terminal 2
5. **Evening**: Commit and push progress

### Risk Management
- **Daily commits**: Never lose more than one day's work
- **Working prototypes**: Always have a working version
- **Incremental testing**: Test each component independently

## Success Metrics

### Phase 1 Success
- [ ] Process 10 Cincinnati Children's papers
- [ ] Store in database successfully
- [ ] Generate AI analysis
- [ ] Export to CSV
- [ ] Complete process in <5 minutes

### Phase 2 Success
- [ ] Handle network errors gracefully
- [ ] Process 100 papers without crashing
- [ ] Comprehensive logging
- [ ] >80% test coverage

### Phase 3 Success
- [ ] Download full text when available
- [ ] Process 1000+ papers efficiently
- [ ] Generate summary reports
- [ ] Resume interrupted processing

### Phase 4 Success
- [ ] Functional GUI interface
- [ ] User-friendly for researchers
- [ ] Complete documentation
- [ ] Ready for deployment

## Key Principles

### Keep It Simple
- **One file per responsibility**
- **Minimal dependencies**
- **Clear function names**
- **Obvious data flow**

### Test Everything
- **Test with real data**
- **Test error conditions**
- **Test edge cases**
- **Test performance**

### Document As You Go
- **Update README daily**
- **Comment complex logic**
- **Track design decisions**
- **Document lessons learned**

## Next Steps

1. **Review this plan** - Make any necessary adjustments
2. **Create new directory** - Start with clean slate
3. **Begin Phase 1** - Start with `simple_ncbi.py`
4. **Test immediately** - Verify each component works
5. **Commit frequently** - Never lose progress

This plan prioritizes **working software** over **perfect architecture**. Each phase builds on the previous one, ensuring you always have a functional system.
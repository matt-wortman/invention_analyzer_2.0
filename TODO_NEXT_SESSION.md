# TODO List for Next Development Session

## 🔥 Critical Fixes (Must Do)

### 1. Fix Anthropic API Provider Switching
**Issue**: GUI allows selection of Anthropic but still uses OpenAI  
**Location**: `gui_app2.py` - provider selection logic  
**Priority**: HIGH  
**Details**: The LLM provider combo box shows Anthropic option but the backend doesn't actually switch providers

### 2. Default Database View
**Issue**: GUI starts with empty results table, requires clicking "View All Papers"  
**Location**: `gui_app2.py` - `setup_results_tab()` method  
**Priority**: HIGH  
**Fix**: Set `self.view_all_checkbox.setChecked(True)` by default

### 3. Add NCBI API Key Input Field
**Issue**: Settings tab missing NCBI API key field (only has email)  
**Location**: `gui_app2.py` - `setup_settings_tab()` method  
**Priority**: MEDIUM  
**Details**: Need input field similar to OpenAI/Anthropic key fields

## 🚀 Feature Enhancements

### 4. PubMed Central Full Text Capability
**Goal**: Pull full article text from PMC when available  
**Priority**: HIGH  
**Benefits**: More comprehensive AI analysis than just abstracts  
**Implementation Plan**:
- Add PMC API integration to `simple_ncbi.py`
- Modify database schema to store full text
- Update AI analysis to use full text when available
- Add UI option to enable/disable full text retrieval

### 5. Enhanced Search Options
**Goal**: Better search capabilities  
**Priority**: MEDIUM  
**Ideas**:
- Save/load search presets
- Advanced query builder
- Institution-specific filters

### 6. Export Improvements
**Goal**: More export options  
**Priority**: LOW  
**Ideas**:
- Excel format export
- JSON export for data analysis
- Include full text in exports

## 🐛 Minor Fixes

### 7. Better Error Handling
- Improve API key validation
- Better user feedback for network errors
- Validate email format for NCBI

### 8. UI Polish
- Add tooltips for complex fields
- Improve progress indicators
- Add keyboard shortcuts

## 📋 Technical Debt

### 9. Code Organization
- Separate GUI components into modules
- Add unit tests for GUI components
- Improve documentation

### 10. Performance
- Optimize database queries
- Add caching for repeated searches
- Lazy loading for large result sets

## 🎯 Quick Win Tasks (15 min each)

1. **Fix default database view** - One line change
2. **Add NCBI API key field** - Copy existing API key field pattern
3. **Fix Anthropic provider switching** - Update provider selection logic
4. **Add tooltips to complex fields** - Improve user experience

## 📁 Files to Focus On

- `literature_invention_search/gui_app2.py` - Main GUI fixes
- `literature_invention_search/simple_ncbi.py` - PMC integration
- `literature_invention_search/ai_analyzer.py` - Provider switching fix
- `literature_invention_search/config.py` - Configuration updates

## 🧪 Testing Checklist

- [ ] Anthropic API actually works when selected
- [ ] Database shows all papers on startup
- [ ] NCBI API key saves and loads correctly
- [ ] Full text retrieval works without breaking existing functionality
- [ ] All API key types can be edited and saved
- [ ] Export functions work with new data fields

## 💡 Future Ideas

- Integration with patent databases
- Automated invention scoring algorithms
- Collaboration features for research teams
- Integration with institutional databases
- Mobile-responsive web interface option
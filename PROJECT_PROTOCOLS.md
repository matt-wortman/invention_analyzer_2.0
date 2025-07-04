# Project Development Protocols

## Git and Version Control

### Branch Strategy
- **main**: Production-ready code only
- **develop**: Active development branch
- **feature/[name]**: Individual features
- **hotfix/[name]**: Critical bug fixes

### Commit Guidelines
- **When to commit**: After each working feature or significant progress
- **Commit messages**: Use clear, descriptive messages
  - `feat: add NCBI publication search`
  - `fix: handle network timeout errors`
  - `docs: update setup guide`
  - `test: add database connection tests`

### Push Strategy
- **Daily pushes**: Push working code at end of each session
- **Feature completion**: Push when feature is complete and tested
- **Before major changes**: Push current state before architectural changes

## Development Workflow

### Two-Terminal Setup
- **Terminal 1**: Development with Claude Code
  - File editing and code generation
  - Git operations
  - Documentation updates
  - No virtual environment needed

- **Terminal 2**: Testing and validation
  - Virtual environment activated
  - GUI testing and validation
  - Manual testing of features
  - Database operations

### Daily Workflow
1. **Start**: Pull latest changes from git
2. **Plan**: Review TODO list and current goals
3. **Develop**: Use Terminal 1 for coding
4. **Test**: Use Terminal 2 for validation
5. **Commit**: Save working progress
6. **Push**: At end of session

## Testing Strategy

### Test-Driven Development
- **Write tests first**: Before implementing features
- **Test early, test often**: After each significant change
- **Test in isolation**: Each component independently

### Testing Levels
1. **Unit Tests**: Individual functions and classes
2. **Integration Tests**: API calls and database operations
3. **System Tests**: End-to-end workflows
4. **GUI Tests**: User interface functionality

### Test Data
- **Use real data**: Test with actual NCBI publications
- **Standard test case**: PMID 40562540 (confirmed working)
- **Edge cases**: Empty results, network errors, malformed data

## Code Quality Standards

### Simplicity First
- **Readable code**: Clear variable names, simple logic
- **Minimal dependencies**: Use standard library when possible
- **No over-engineering**: Avoid unnecessary abstractions
- **Think first**: Define exactly what needs to happen before coding
- **See LESSONS_LEARNED.md**: Critical patterns and anti-patterns

### Error Handling
- **Graceful failures**: Never crash on expected errors
- **Helpful messages**: Clear error descriptions for users
- **Logging**: Record all significant events and errors

### Documentation
- **Code comments**: Only for complex logic
- **Docstrings**: For all public functions
- **README updates**: Keep setup instructions current

## Research Software Standards

### Reproducibility
- **Version everything**: Code, data, configuration
- **Document parameters**: All analysis settings
- **Consistent results**: Same input = same output

### Data Management
- **Local storage**: All data stored locally
- **Data provenance**: Track source of all data
- **Backup strategy**: Regular backups of database

### Scientific Integrity
- **Audit trail**: Log all operations
- **Transparent methods**: Clear analysis methodology
- **Peer review**: Code review for critical components

## Configuration Management

### Environment Variables
- **API keys**: Never commit to git
- **Local configuration**: Use config files or environment variables
- **Default values**: Sensible defaults for all settings

### Dependencies
- **Pin versions**: Exact version numbers in requirements.txt
- **Virtual environment**: Always use isolated environments
- **Regular updates**: Keep dependencies current

## Deployment and Distribution

### Packaging
- **Minimal setup**: Single command installation
- **Cross-platform**: Windows, macOS, Linux support
- **Documentation**: Clear setup instructions

### Release Strategy
- **Semantic versioning**: Major.Minor.Patch
- **Release notes**: Document all changes
- **Backwards compatibility**: Maintain data compatibility

## Communication and Collaboration

### Progress Tracking
- **Daily updates**: Document progress and blockers
- **Issue tracking**: Use GitHub issues for bugs and features
- **Documentation**: Keep all docs current

### Code Review
- **Self-review**: Review your own code before committing
- **Peer review**: Have others review critical components
- **Standards compliance**: Check against project standards

## Crisis Management

### When Things Break
1. **Don't panic**: Step back and assess
2. **Isolate the problem**: Identify root cause
3. **Rollback if needed**: Return to working state
4. **Fix incrementally**: Small, testable changes
5. **Document lessons learned**: Update protocols

### Backup Strategy
- **Git history**: Complete version history
- **Database backups**: Regular exports
- **Configuration backups**: Save working configurations

## Success Metrics

### Technical Metrics
- **Test coverage**: >80% code coverage
- **Error rate**: <5% API call failures
- **Performance**: Process 100 papers in <10 minutes

### Research Metrics
- **Data quality**: >95% successful publication downloads
- **Analysis accuracy**: Consistent invention detection
- **Reproducibility**: Same results from same data

## Review and Improvement

### Regular Reviews
- **Weekly**: Review progress against goals
- **Monthly**: Evaluate protocols and processes
- **Quarterly**: Major architecture decisions

### Continuous Improvement
- **Learn from failures**: Document what went wrong
- **Adapt protocols**: Update based on experience
- **Stay current**: Keep up with best practices
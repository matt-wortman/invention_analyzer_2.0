# Lessons Learned

## Critical Development Principles

### 1. **THINK FIRST, CODE SECOND**
- **Always** define exactly what needs to happen before writing code
- Ask: "What is the simplest way to accomplish this goal?"
- Don't add complexity until it's actually needed

### 2. **Line Ending Issues in WSL**
**Problem**: Scripts created by Claude often have Windows CRLF line endings, causing "command not found" errors even when the file exists.

**Solution**: Use `echo` commands to build scripts line by line instead of creating multi-line files:
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

### 3. **Virtual Environment Activation**
**Problem**: Scripts that execute (./script.sh) run in subshells and don't persist environment changes.

**Solution**: Create scripts designed to be sourced:
```bash
# GOOD - Stays active
source gui_setup.sh

# BAD - Doesn't persist
./startup_gui.sh
```

### 4. **Shell Prompt Display**
**Problem**: `VIRTUAL_ENV_DISABLE_PROMPT=1` hides the (venv) prefix.

**Solution**: Always unset this variable when setting up development environments:
```bash
unset VIRTUAL_ENV_DISABLE_PROMPT
```

## Working GUI Setup Pattern

### The Simple Approach That Works
```bash
# gui_setup.sh - 6 lines that actually work
source venv/bin/activate
unset VIRTUAL_ENV_DISABLE_PROMPT  
export DISPLAY=:0
export QT_QPA_PLATFORM=xcb
echo "✅ GUI environment ready"
```

**Usage**: `source gui_setup.sh`

### Why This Works
1. **Simple**: Does exactly what's needed, nothing more
2. **Sourceable**: Runs in current shell, changes persist
3. **No line endings**: Built with echo commands
4. **Visible feedback**: Shows when environment is ready

## Development Anti-Patterns to Avoid

### ❌ Over-Engineering
- Don't create complex scripts when simple ones work
- Don't add features "just in case"
- Don't abstract until you need to

### ❌ Ignoring Environment Details
- WSL has specific quirks (line endings, display variables)
- Virtual environments need specific handling
- Shell vs subshell execution matters

### ❌ Not Testing Incrementally
- Test each piece as you build it
- Don't create complex systems without validating components
- Always have a working fallback

## Research Software Principles

### Start With Working Code
1. Get the simplest version working first
2. Test with real data immediately  
3. Add complexity only when needed
4. Always maintain a working version

### Document Failures
- Record what didn't work and why
- Note the working solutions
- Update documentation with lessons learned
- Prevent repeating the same mistakes

### Keep Dependencies Minimal
- Use standard library when possible
- Avoid complex third-party solutions
- Prefer simple, obvious approaches
- Document all requirements clearly

## Quick Reference

### WSL GUI Setup (Working Version)
```bash
source gui_setup.sh
python test_qt_gui.py  # Should open and stay open
```

### Troubleshooting Scripts
1. Check line endings: `file script.sh` (should not show CRLF)
2. Use `source` not `./` for environment scripts
3. Test each command individually first
4. Keep scripts under 10 lines when possible

## Future Development Guidelines

### Before Writing Any Script
1. What exactly does this need to accomplish?
2. What's the simplest way to do it?
3. Does it need to persist changes? (Use `source`)
4. Can I test each piece individually?

### Code Review Checklist
- [ ] Is this the simplest approach?
- [ ] Are line endings correct?
- [ ] Does it work when sourced?
- [ ] Is each component testable?
- [ ] Is it documented clearly?

**Remember**: Simple solutions that work are infinitely better than complex solutions that don't.
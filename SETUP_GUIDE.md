# Development Setup Guide

## Virtual Environment Setup

### Initial Setup (One-time)
```bash
# Navigate to project directory
cd /home/matt/invention-july1/literature_invention_search

# Install required system packages
sudo apt install python3-venv python3-full python3-tk x11-apps

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install required X11 libraries for Qt
sudo apt install -y libxcb-cursor0 libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xfixes0 libxkbcommon-x11-0 libxkbcommon0

# Install Python dependencies
pip install PySide6
pip install -r requirements.txt  # When available
```

### Daily Development Workflow

#### Terminal 1 (Development)
- Used for code editing, file operations, git
- No special setup needed

#### Terminal 2 (GUI Testing)

**Recommended: Simple Setup Script**
```bash
# Navigate to project
cd /home/matt/invention-july1/literature_invention_search

# Set up GUI environment (shows (venv) in prompt)
source gui_setup.sh

# Test Qt GUI
python test_qt_gui.py

# Run actual application  
python run_gui.py
```

**Alternative: Manual Setup**
```bash
# Navigate to project
cd /home/matt/invention-july1/literature_invention_search

# Activate virtual environment
source venv/bin/activate

# Enable venv prompt display
unset VIRTUAL_ENV_DISABLE_PROMPT

# Set display and Qt platform for GUI (WSL)
export DISPLAY=:0
export QT_QPA_PLATFORM=xcb
```

## WSL GUI Requirements

### Prerequisites
- Windows 11 with latest updates
- WSL2 installed and configured
- X11 forwarding enabled (automatic in recent WSL versions)

### Verification
```bash
# Check display is set
echo $DISPLAY  # Should show IP:0.0 or :0

# Test X11 works
xeyes

# Test Qt works
python test_qt_gui.py
```

## Common Issues

### "externally-managed-environment" Error
- **Solution**: Always use virtual environment (`source venv/bin/activate`)
- **Never use**: `pip install --break-system-packages`

### GUI Not Opening
- **Check**: `echo $DISPLAY` shows a value
- **Fix**: `export DISPLAY=:0`
- **Test**: `xeyes` should show moving eyes

### Virtual Environment Not Found
- **Fix**: Recreate with `python3 -m venv venv`
- **Then**: `source venv/bin/activate`

## File Structure
```
literature_invention_search/
├── venv/                 # Virtual environment (don't commit)
├── test_qt_gui.py       # Qt GUI test
├── requirements.txt     # Python dependencies
├── PROJECT_GOALS.md     # Project requirements
└── SETUP_GUIDE.md      # This file
```
#!/bin/bash
# MP-Lib Installation Script for Linux/Unix/macOS
# This script installs mp_lib and makes the CLI globally available

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/nielrya4/mp_lib.git"
INSTALL_DIR="$HOME/.local/share/mp_lib"
BIN_DIR="$HOME/.local/bin"
CLI_NAME="mp-cli"

# Functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}           MP-Lib Installation Script          ${NC}"
    echo -e "${BLUE}     Microplastics Analysis Library & CLI     ${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    required_version="3.8"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_error "Python $python_version found, but Python 3.8+ is required."
        exit 1
    fi
    
    print_status "Python $python_version found ✓"
    
    # Check pip
    if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
        print_error "pip is not installed. Please install pip for Python 3."
        exit 1
    fi
    
    print_status "pip found ✓"
    
    # Check git
    if ! command -v git &> /dev/null; then
        print_error "git is not installed. Please install git."
        exit 1
    fi
    
    print_status "git found ✓"
}

create_directories() {
    print_status "Creating installation directories..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    
    print_status "Directories created ✓"
}

install_mp_lib() {
    print_status "Installing mp_lib..."
    
    # Remove existing installation if it exists
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Removing existing installation..."
        rm -rf "$INSTALL_DIR"
        mkdir -p "$INSTALL_DIR"
    fi
    
    # Clone repository
    print_status "Downloading mp_lib..."
    git clone "$REPO_URL" "$INSTALL_DIR" 2>/dev/null || {
        print_warning "Git clone failed. Trying to download directly..."
        
        # Alternative: direct download (for when repo isn't available)
        print_status "Using local installation..."
        
        # Create a simple installation from current directory
        if [ -f "setup.py" ]; then
            cp -r . "$INSTALL_DIR/"
        else
            print_error "No installation source found. Please check the repository URL."
            exit 1
        fi
    }
    
    cd "$INSTALL_DIR"
    
    # Install Python package
    print_status "Installing Python dependencies..."
    
    # Check if we're in a virtual environment
    if [[ -n "$VIRTUAL_ENV" ]] || [[ -n "$CONDA_DEFAULT_ENV" ]] || python3 -c "import sys; exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)" 2>/dev/null; then
        print_status "Virtual environment detected, installing without --user flag"
        python3 -m pip install -e . || {
            print_error "Failed to install Python package"
            exit 1
        }
    else
        # Try --user installation first
        if python3 -m pip install --user -e . 2>/dev/null; then
            print_status "Installed with --user flag"
        else
            print_warning "Standard installation failed. Trying alternative methods..."
            
            # Check if pipx is available
            if command -v pipx &> /dev/null; then
                print_status "Using pipx for installation..."
                pipx install -e . || {
                    print_error "pipx installation failed"
                    exit 1
                }
            else
                # Last resort: use --break-system-packages (with user confirmation)
                print_warning "This system has externally-managed Python environment."
                print_warning "Options:"
                print_warning "1. Install using --break-system-packages (not recommended)"
                print_warning "2. Use pipx (install with: python3 -m pip install --user pipx)"
                print_warning "3. Create a virtual environment"
                echo
                read -p "Do you want to proceed with --break-system-packages? [y/N]: " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    python3 -m pip install --user --break-system-packages -e . || {
                        print_error "Failed to install Python package even with --break-system-packages"
                        exit 1
                    }
                else
                    print_error "Installation cancelled. Please use a virtual environment or install pipx."
                    exit 1
                fi
            fi
        fi
    fi
    
    print_status "mp_lib installed ✓"
}

create_cli_wrapper() {
    print_status "Creating CLI wrapper..."
    
    # Determine the Python command to use
    local python_cmd="python3"
    if [[ -n "$VIRTUAL_ENV" ]]; then
        # In virtual environment, use the virtual environment's python
        python_cmd="$VIRTUAL_ENV/bin/python"
    fi
    
    # Create the CLI wrapper script
    cat > "$BIN_DIR/$CLI_NAME" << EOF
#!/bin/bash
# MP-CLI Wrapper Script
# Automatically generated by install.sh

# Try to run the CLI
if command -v mp_cli &> /dev/null; then
    # CLI installed via pip
    exec mp_cli "\$@"
elif [ -f "\$HOME/.local/share/mp_lib/mp_cli.py" ]; then
    # CLI from local installation
    exec "$python_cmd" "\$HOME/.local/share/mp_lib/mp_cli.py" "\$@"
else
    # Try as Python module
    exec "$python_cmd" -m mp_cli "\$@" 2>/dev/null || {
        echo "Error: mp-cli not found. Please reinstall mp_lib."
        exit 1
    }
fi
EOF
    
    chmod +x "$BIN_DIR/$CLI_NAME"
    print_status "CLI wrapper created ✓"
}

update_path() {
    print_status "Updating PATH..."
    
    # Add to PATH in various shell configs
    for shell_config in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
        if [ -f "$shell_config" ]; then
            # Check if already added
            if ! grep -q "$BIN_DIR" "$shell_config"; then
                echo "" >> "$shell_config"
                echo "# Added by mp_lib installer" >> "$shell_config"
                echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$shell_config"
                print_status "Updated $shell_config ✓"
            fi
        fi
    done
    
    # Also export for current session
    export PATH="$BIN_DIR:$PATH"
}

test_installation() {
    print_status "Testing installation..."
    
    # Test if CLI is accessible
    if command -v "$CLI_NAME" &> /dev/null; then
        print_status "CLI is accessible globally ✓"
        
        # Test CLI functionality
        if "$CLI_NAME" --help &> /dev/null; then
            print_status "CLI functionality test passed ✓"
        else
            print_warning "CLI accessible but functionality test failed"
        fi
    else
        print_warning "CLI not immediately accessible. You may need to restart your shell."
    fi
}

print_completion() {
    echo
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}         Installation completed successfully!   ${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo
    echo -e "${BLUE}Quick Start:${NC}"
    echo "  1. Restart your terminal or run: source ~/.bashrc"
    echo "  2. Test installation: $CLI_NAME --help"
    echo "  3. Analyze data: $CLI_NAME --input data.xlsx info"
    echo
    echo -e "${BLUE}CLI Commands:${NC}"
    echo "  $CLI_NAME info          - Show data information"
    echo "  $CLI_NAME dist          - Distribution analysis" 
    echo "  $CLI_NAME unmix         - Source unmixing"
    echo "  $CLI_NAME mds           - MDS analysis"
    echo "  $CLI_NAME analyze       - Complete analysis"
    echo
    echo -e "${BLUE}Examples:${NC}"
    echo "  $CLI_NAME --input data.xlsx info --summary"
    echo "  $CLI_NAME --input data.xlsx dist --plot --cdf"
    echo "  $CLI_NAME --input data.xlsx analyze --all"
    echo
    echo -e "${BLUE}Documentation:${NC} https://github.com/nielrya4/mp_lib"
    echo -e "${BLUE}Issues:${NC} https://github.com/nielrya4/mp_lib/issues"
    echo
}

# Main installation process
main() {
    print_header
    
    check_requirements
    create_directories
    install_mp_lib
    create_cli_wrapper
    update_path
    test_installation
    print_completion
}

# Handle Ctrl+C
trap 'echo -e "\n${RED}Installation cancelled.${NC}"; exit 1' INT

# Check if running with --uninstall
if [ "$1" = "--uninstall" ]; then
    print_status "Uninstalling mp_lib..."
    
    # Remove installation directory
    rm -rf "$INSTALL_DIR"
    
    # Remove CLI wrapper
    rm -f "$BIN_DIR/$CLI_NAME"
    
    # Remove from PATH (basic removal)
    for shell_config in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
        if [ -f "$shell_config" ]; then
            sed -i '/Added by mp_lib installer/,+1d' "$shell_config" 2>/dev/null || true
        fi
    done
    
    print_status "mp_lib uninstalled successfully"
    echo "You may need to restart your terminal for PATH changes to take effect."
    exit 0
fi

# Run main installation
main
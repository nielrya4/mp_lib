# MP-Lib Installation Script for Windows PowerShell
# This script installs mp_lib and makes the CLI globally available

param(
    [switch]$Uninstall,
    [string]$InstallPath = "$env:LOCALAPPDATA\mp_lib",
    [string]$BinPath = "$env:LOCALAPPDATA\Microsoft\WindowsApps"
)

# Configuration
$RepoUrl = "https://github.com/nielrya4/mp_lib.git"
$CliName = "mp-cli"

# Colors for output
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-Header {
    Write-Host "================================================" -ForegroundColor $Blue
    Write-Host "           MP-Lib Installation Script          " -ForegroundColor $Blue
    Write-Host "     Microplastics Analysis Library & CLI     " -ForegroundColor $Blue
    Write-Host "================================================" -ForegroundColor $Blue
    Write-Host ""
}

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

function Test-Requirements {
    Write-Status "Checking system requirements..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        if (-not $pythonVersion) {
            $pythonVersion = python3 --version 2>$null
        }
        
        if (-not $pythonVersion) {
            Write-Error "Python is not installed or not in PATH. Please install Python 3.8 or higher."
            exit 1
        }
        
        # Extract version number
        $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
        if ($versionMatch) {
            $majorVersion = [int]$Matches[1]
            $minorVersion = [int]$Matches[2]
            
            if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 8)) {
                Write-Error "Python $majorVersion.$minorVersion found, but Python 3.8+ is required."
                exit 1
            }
            
            Write-Status "Python $majorVersion.$minorVersion found ✓"
        }
    }
    catch {
        Write-Error "Failed to check Python version: $_"
        exit 1
    }
    
    # Check pip
    try {
        $pipVersion = pip --version 2>$null
        if (-not $pipVersion) {
            $pipVersion = python -m pip --version 2>$null
        }
        
        if (-not $pipVersion) {
            Write-Error "pip is not installed. Please install pip for Python."
            exit 1
        }
        
        Write-Status "pip found ✓"
    }
    catch {
        Write-Error "Failed to check pip: $_"
        exit 1
    }
    
    # Check git (optional)
    try {
        $gitVersion = git --version 2>$null
        if ($gitVersion) {
            Write-Status "git found ✓"
        } else {
            Write-Warning "git not found. Will try alternative installation method."
        }
    }
    catch {
        Write-Warning "git not available. Will try alternative installation method."
    }
}

function New-InstallationDirectories {
    Write-Status "Creating installation directories..."
    
    if (-not (Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    }
    
    if (-not (Test-Path $BinPath)) {
        New-Item -ItemType Directory -Path $BinPath -Force | Out-Null
    }
    
    Write-Status "Directories created ✓"
}

function Install-MpLib {
    Write-Status "Installing mp_lib..."
    
    # Remove existing installation if it exists
    if (Test-Path $InstallPath) {
        Write-Warning "Removing existing installation..."
        Remove-Item -Path $InstallPath -Recurse -Force
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    }
    
    # Try git clone first
    try {
        Write-Status "Downloading mp_lib..."
        Set-Location $InstallPath
        git clone $RepoUrl . 2>$null
        
        if (-not (Test-Path "setup.py")) {
            throw "Git clone failed or incomplete"
        }
    }
    catch {
        Write-Warning "Git clone failed. Trying alternative installation..."
        
        # Alternative: try to copy from current directory if setup.py exists
        $currentDir = Get-Location
        if (Test-Path "$currentDir\setup.py") {
            Write-Status "Using local installation..."
            Copy-Item -Path "$currentDir\*" -Destination $InstallPath -Recurse -Force
        } else {
            Write-Error "No installation source found. Please check the repository URL or run from the mp_lib directory."
            exit 1
        }
    }
    
    # Install Python package
    try {
        Write-Status "Installing Python dependencies..."
        Set-Location $InstallPath
        
        # Check if we're in a virtual environment
        $inVirtualEnv = $false
        if ($env:VIRTUAL_ENV -or $env:CONDA_DEFAULT_ENV) {
            $inVirtualEnv = $true
        } else {
            # Check using Python
            try {
                $venvCheck = python -c "import sys; print(hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))" 2>$null
                if ($venvCheck -eq "True") {
                    $inVirtualEnv = $true
                }
            }
            catch {
                # If python command fails, try python3
                try {
                    $venvCheck = python3 -c "import sys; print(hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))" 2>$null
                    if ($venvCheck -eq "True") {
                        $inVirtualEnv = $true
                    }
                }
                catch {
                    # Default to false if we can't detect
                    $inVirtualEnv = $false
                }
            }
        }
        
        if ($inVirtualEnv) {
            Write-Status "Virtual environment detected, installing without --user flag"
        }
        
        # Try different Python commands
        $installSuccess = $false
        $pythonCommands = @("python", "python3", "py")
        
        foreach ($pythonCmd in $pythonCommands) {
            try {
                if ($inVirtualEnv) {
                    & $pythonCmd -m pip install -e . 2>$null
                    $installSuccess = $true
                    break
                } else {
                    # Try --user installation first
                    try {
                        & $pythonCmd -m pip install --user -e . 2>$null
                        Write-Status "Installed with --user flag"
                        $installSuccess = $true
                        break
                    }
                    catch {
                        Write-Warning "Standard installation failed. Trying alternative methods..."
                        
                        # Check if pipx is available
                        if (Get-Command pipx -ErrorAction SilentlyContinue) {
                            Write-Status "Using pipx for installation..."
                            try {
                                pipx install -e . 2>$null
                                $installSuccess = $true
                                break
                            }
                            catch {
                                Write-Warning "pipx installation failed"
                            }
                        }
                        
                        # Last resort: ask user about --break-system-packages
                        Write-Warning "This system has externally-managed Python environment."
                        Write-Warning "Options:"
                        Write-Warning "1. Install using --break-system-packages (not recommended)"
                        Write-Warning "2. Use pipx (install with: python -m pip install --user pipx)"
                        Write-Warning "3. Create a virtual environment"
                        Write-Host ""
                        
                        $response = Read-Host "Do you want to proceed with --break-system-packages? [y/N]"
                        if ($response -match "^[Yy]$") {
                            try {
                                & $pythonCmd -m pip install --user --break-system-packages -e . 2>$null
                                $installSuccess = $true
                                break
                            }
                            catch {
                                Write-Error "Failed to install Python package even with --break-system-packages"
                            }
                        } else {
                            Write-Error "Installation cancelled. Please use a virtual environment or install pipx."
                            exit 1
                        }
                    }
                }
            }
            catch {
                continue
            }
        }
        
        if (-not $installSuccess) {
            Write-Error "Failed to install Python package. Please check your Python/pip installation."
            exit 1
        }
        
        Write-Status "mp_lib installed ✓"
    }
    catch {
        Write-Error "Failed to install Python package: $_"
        exit 1
    }
}

function New-CliWrapper {
    Write-Status "Creating CLI wrapper..."
    
    $wrapperContent = @"
@echo off
REM MP-CLI Wrapper Script
REM Automatically generated by install.ps1

REM Try different Python commands and CLI methods
python -c "import mp_cli; mp_cli.main()" %* 2>nul && goto :eof
python3 -c "import mp_cli; mp_cli.main()" %* 2>nul && goto :eof
py -c "import mp_cli; mp_cli.main()" %* 2>nul && goto :eof

REM Try as installed command
mp_cli %* 2>nul && goto :eof

REM Try from installation directory
python "$env:LOCALAPPDATA\mp_lib\mp_cli.py" %* 2>nul && goto :eof

echo Error: mp-cli not found. Please reinstall mp_lib.
exit /b 1
"@
    
    $wrapperPath = Join-Path $BinPath "$CliName.cmd"
    $wrapperContent | Out-File -FilePath $wrapperPath -Encoding ASCII
    
    Write-Status "CLI wrapper created ✓"
}

function Update-Path {
    Write-Status "Updating PATH..."
    
    # Get current user PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    
    # Check if BinPath is already in PATH
    if ($currentPath -notlike "*$BinPath*") {
        $newPath = "$BinPath;$currentPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Status "PATH updated ✓"
        
        # Update current session PATH
        $env:Path = "$BinPath;$env:Path"
    } else {
        Write-Status "PATH already contains installation directory ✓"
    }
}

function Test-Installation {
    Write-Status "Testing installation..."
    
    # Refresh PATH for current session
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
    
    # Test if CLI is accessible
    try {
        $helpOutput = & "$CliName" --help 2>$null
        if ($helpOutput) {
            Write-Status "CLI functionality test passed ✓"
        } else {
            Write-Warning "CLI accessible but functionality test failed"
        }
    }
    catch {
        Write-Warning "CLI not immediately accessible. You may need to restart PowerShell."
    }
}

function Write-Completion {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor $Green
    Write-Host "         Installation completed successfully!   " -ForegroundColor $Green
    Write-Host "================================================" -ForegroundColor $Green
    Write-Host ""
    Write-Host "Quick Start:" -ForegroundColor $Blue
    Write-Host "  1. Restart PowerShell or open a new terminal"
    Write-Host "  2. Test installation: $CliName --help"
    Write-Host "  3. Analyze data: $CliName --input data.xlsx info"
    Write-Host ""
    Write-Host "CLI Commands:" -ForegroundColor $Blue
    Write-Host "  $CliName info          - Show data information"
    Write-Host "  $CliName dist          - Distribution analysis"
    Write-Host "  $CliName unmix         - Source unmixing"
    Write-Host "  $CliName mds           - MDS analysis"
    Write-Host "  $CliName analyze       - Complete analysis"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor $Blue
    Write-Host "  $CliName --input data.xlsx info --summary"
    Write-Host "  $CliName --input data.xlsx dist --plot --cdf"
    Write-Host "  $CliName --input data.xlsx analyze --all"
    Write-Host ""
    Write-Host "Documentation:" -ForegroundColor $Blue -NoNewline
    Write-Host " https://github.com/nielrya4/mp_lib"
    Write-Host "Issues:" -ForegroundColor $Blue -NoNewline
    Write-Host " https://github.com/nielrya4/mp_lib/issues"
    Write-Host ""
}

function Remove-Installation {
    Write-Status "Uninstalling mp_lib..."
    
    # Remove installation directory
    if (Test-Path $InstallPath) {
        Remove-Item -Path $InstallPath -Recurse -Force
        Write-Status "Removed installation directory"
    }
    
    # Remove CLI wrapper
    $wrapperPath = Join-Path $BinPath "$CliName.cmd"
    if (Test-Path $wrapperPath) {
        Remove-Item -Path $wrapperPath -Force
        Write-Status "Removed CLI wrapper"
    }
    
    # Remove from PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $newPath = $currentPath -replace [regex]::Escape("$BinPath;"), ""
    $newPath = $newPath -replace [regex]::Escape(";$BinPath"), ""
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    
    Write-Status "mp_lib uninstalled successfully"
    Write-Host "You may need to restart PowerShell for PATH changes to take effect."
}

# Main execution
try {
    if ($Uninstall) {
        Write-Header
        Remove-Installation
        exit 0
    }
    
    Write-Header
    Test-Requirements
    New-InstallationDirectories
    Install-MpLib
    New-CliWrapper
    Update-Path
    Test-Installation
    Write-Completion
}
catch {
    Write-Error "Installation failed: $_"
    Write-Host "Please check the error message above and try again."
    Write-Host "For support, visit: https://github.com/nielrya4/mp_lib/issues"
    exit 1
}

# Handle Ctrl+C
trap {
    Write-Host ""
    Write-Error "Installation cancelled."
    exit 1
}
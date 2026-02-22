#!/usr/bin/env python3
"""
Setup Script for AD-HTC System
Installs all dependencies permanently to avoid reinstallation issues
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd, description, cwd=None):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def setup_python_dependencies():
    """Install all Python dependencies"""
    print("\n" + "="*60)
    print("🐍 SETTING UP PYTHON DEPENDENCIES")
    print("="*60)
    
    # Install backend dependencies
    if Path('backend/requirements.txt').exists():
        run_command(f"{sys.executable} -m pip install --user -r backend/requirements.txt", 
                   "Installing Backend Dependencies")
    
    # Install Python frontend dependencies (simplified)
    if Path('frontend_python/requirements_python_frontend_simple.txt').exists():
        run_command(f"{sys.executable} -m pip install --user -r frontend_python/requirements_python_frontend_simple.txt", 
                   "Installing Python Frontend Dependencies")
    
    # Install additional packages that might be missing
    additional_packages = ['matplotlib', 'numpy', 'pillow', 'scipy']
    for package in additional_packages:
        run_command(f"{sys.executable} -m pip install --user {package}", 
                   f"Installing {package}")

def setup_javascript_dependencies():
    """Install all JavaScript dependencies"""
    print("\n" + "="*60)
    print("🌐 SETTING UP JAVASCRIPT DEPENDENCIES")
    print("="*60)
    
    if Path('frontend/package.json').exists():
        run_command("npm install", "Installing React Dependencies", cwd='frontend')
        run_command("npm install --save-dev react-scripts", "Installing React Scripts", cwd='frontend')

def create_persistent_config():
    """Create persistent configuration"""
    print("\n" + "="*60)
    print("⚙️ CREATING PERSISTENT CONFIGURATION")
    print("="*60)
    
    config = {
        "python_path": sys.executable,
        "dependencies_installed": True,
        "installation_date": subprocess.check_output(['date'], shell=True).decode().strip() if os.name != 'nt' else "Windows System"
    }
    
    with open('installation_config.json', 'w') as f:
        import json
        json.dump(config, f, indent=2)
    
    print("✅ Persistent configuration created")

def create_startup_scripts():
    """Create startup scripts for different platforms"""
    print("\n" + "="*60)
    print("📝 CREATING STARTUP SCRIPTS")
    print("="*60)
    
    # Windows batch file
    if os.name == 'nt':
        with open('start_adhtc.bat', 'w') as f:
            f.write(f"""@echo off
echo Starting AD-HTC System...
cd /d "{os.getcwd()}"
python launcher_fixed.py
pause
""")
        print("✅ Created start_adhtc.bat for Windows")
        
        with open('start_python_frontend.bat', 'w') as f:
            f.write(f"""@echo off
echo Starting Python Frontend Only...
cd /d "{os.getcwd()}\frontend_python"
python adhtc_gui_simple.py
pause
""")
        print("✅ Created start_python_frontend.bat for Windows")
    
    # Unix shell script
    else:
        with open('start_adhtc.sh', 'w') as f:
            f.write(f"""#!/bin/bash
echo "Starting AD-HTC System..."
cd "{os.getcwd()}"
python3 launcher_fixed.py
""")
        os.chmod('start_adhtc.sh', 0o755)
        print("✅ Created start_adhtc.sh for Unix/Linux")

def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("🚀 AD-HTC SYSTEM SETUP")
    print("This will install all dependencies permanently")
    print("="*60)
    
    response = input("\nProceed with setup? (y/N): ")
    if response.lower() != 'y':
        print("Setup cancelled.")
        return
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required!")
        return
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Run setup steps
    setup_python_dependencies()
    setup_javascript_dependencies()
    create_persistent_config()
    create_startup_scripts()
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\nTo run the system:")
    if os.name == 'nt':
        print("- Double-click start_adhtc.bat for full launcher")
        print("- Double-click start_python_frontend.bat for Python-only mode")
    else:
        print("- Run: ./start_adhtc.sh")
    print("- Or run: python launcher_fixed.py")
    print("\nAll dependencies are now installed permanently!")
    print("You should not need to reinstall them again.")

if __name__ == "__main__":
    main()
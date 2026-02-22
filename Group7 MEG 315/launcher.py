#!/usr/bin/env python3
"""
AD-HTC System Launcher
Provides a user-friendly interface to choose between React and Python frontends
with automatic requirements checking
"""

import sys
import os
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_packages(requirements_file):
    """Check if Python packages are installed"""
    try:
        with open(requirements_file, 'r') as f:
            packages = [line.strip().split('>=')[0].split(';')[0].split('[')[0] for line in f if line.strip() and not line.startswith('#')]
        
        missing = []
        for package in packages:
            package = package.strip()
            if package == 'tkinter':
                try:
                    import tkinter
                except ImportError:
                    missing.append('tkinter')
            else:
                try:
                    __import__(package)
                except ImportError:
                    missing.append(package)
        
        return missing
    except FileNotFoundError:
        return []

def check_npm_packages():
    """Check if npm and React packages are available"""
    try:
        # Check if npm is available
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            return ['npm not found']
        
        # Check if node_modules exists
        frontend_dir = Path('frontend')
        if not frontend_dir.exists():
            return ['frontend directory not found']
        
        node_modules = frontend_dir / 'node_modules'
        if not node_modules.exists():
            return ['node_modules not found (run npm install)']
        
        return []
    except FileNotFoundError:
        return ['npm not found']

def check_backend():
    """Check if backend is running"""
    try:
        import requests
        response = requests.get('http://localhost:8000/docs', timeout=2)
        return response.status_code == 200
    except:
        return False

def install_python_requirements(requirements_file):
    """Install Python requirements"""
    print(f"Installing Python requirements from {requirements_file}...")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_file], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Python requirements installed successfully!")
            return True
        else:
            print(f"❌ Error installing requirements: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def install_npm_requirements():
    """Install npm requirements"""
    print("Installing npm requirements...")
    try:
        result = subprocess.run(['npm', 'install'], cwd='frontend', capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ npm requirements installed successfully!")
            return True
        else:
            print(f"❌ Error installing npm requirements: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def start_backend():
    """Start the backend server"""
    print("Starting backend server...")
    try:
        # Check if backend main.py exists
        if not Path('backend/main.py').exists():
            print("❌ Backend main.py not found!")
            return None
        
        # Start backend in background
        process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit to see if it starts successfully
        time.sleep(3)
        if process.poll() is None:
            print("✅ Backend server started successfully!")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Backend failed to start: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_react_frontend():
    """Start React frontend"""
    print("Starting React frontend...")
    try:
        # Check if package.json exists
        if not Path('frontend/package.json').exists():
            print("❌ frontend/package.json not found!")
            return None
        
        # Start React dev server
        process = subprocess.Popen(['npm', 'start'], cwd='frontend', 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ React frontend started!")
        print("🌐 Opening browser to http://localhost:3000...")
        time.sleep(5)
        webbrowser.open('http://localhost:3000')
        return process
    except Exception as e:
        print(f"❌ Error starting React frontend: {e}")
        return None

def start_python_frontend():
    """Start Python frontend"""
    print("Starting Python frontend...")
    try:
        # Check if Python frontend exists
        if not Path('frontend_python/adhtc_gui.py').exists():
            print("❌ frontend_python/adhtc_gui.py not found!")
            return None
        
        # Start Python GUI
        process = subprocess.Popen([sys.executable, 'adhtc_gui.py'], cwd='frontend_python',
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Python frontend started!")
        return process
    except Exception as e:
        print(f"❌ Error starting Python frontend: {e}")
        return None

def start_enhanced_python_frontend():
    """Start Enhanced Python frontend with backend integration"""
    print("Starting Enhanced Python frontend with backend integration...")
    try:
        # Check if enhanced Python frontend exists
        if not Path('adhtc_gui_enhanced.py').exists():
            print("❌ adhtc_gui_enhanced.py not found!")
            return None
        
        # Start Enhanced Python GUI from root directory
        process = subprocess.Popen([sys.executable, 'adhtc_gui_enhanced.py'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Enhanced Python frontend started!")
        print("📊 Features: Large results display, interactive charts, backend integration")
        return process
    except Exception as e:
        print(f"❌ Error starting Enhanced Python frontend: {e}")
        return None

def main():
    """Main launcher function"""
    print("\n" + "="*60)
    print("🚀 230404035 GROUP 7 - AD-HTC SYSTEM LAUNCHER")
    print("="*60)
    
    # Check system requirements
    print("\n🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required!")
        return
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check backend requirements
    print("\n🔧 Checking backend requirements...")
    backend_missing = check_python_packages('backend/requirements.txt') if Path('backend/requirements.txt').exists() else []
    if backend_missing:
        print(f"❌ Missing backend packages: {', '.join(backend_missing)}")
        response = input("Install missing backend packages? (y/N): ")
        if response.lower() == 'y':
            if Path('backend/requirements.txt').exists():
                if not install_python_requirements('backend/requirements.txt'):
                    print("Failed to install backend requirements. Exiting.")
                    return
            else:
                print("backend/requirements.txt not found. Please install manually.")
                return
    else:
        print("✅ Backend requirements satisfied")
    
    # Start backend
    print("\n🖥️  Starting backend server...")
    backend_process = None
    if not check_backend():
        response = input("Backend not running. Start it? (Y/n): ")
        if response.lower() != 'n':
            backend_process = start_backend()
            if not backend_process:
                print("Failed to start backend. Continuing anyway...")
        else:
            print("⚠️  Backend not started. Frontend may not work properly.")
    else:
        print("✅ Backend is already running")
    
    # Frontend selection
    print("\n🖥️  Frontend Options:")
    print("1. React Frontend (Modern, full-featured)")
    print("2. Python Frontend (Lightweight, no Node.js required)")
    print("3. Enhanced Python Frontend (Large results + Charts + Backend)")
    print("4. Check requirements only")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == '1':
        # React frontend
        print("\n🌐 Checking React frontend requirements...")
        npm_missing = check_npm_packages()
        if npm_missing:
            print(f"❌ Issues found: {', '.join(npm_missing)}")
            response = input("Fix these issues? (y/N): ")
            if response.lower() == 'y':
                if 'npm install' in npm_missing or 'node_modules not found' in npm_missing:
                    install_npm_requirements()
                else:
                    print("Please install Node.js and npm, then run 'npm install' in the frontend directory.")
                    return
        
        start_react_frontend()
        
    elif choice == '2':
        # Python frontend
        print("\n🐍 Checking Python frontend requirements...")
        python_missing = check_python_packages('frontend_python/requirements_python_frontend.txt')
        if python_missing:
            print(f"❌ Missing Python frontend packages: {', '.join(python_missing)}")
            response = input("Install missing packages? (y/N): ")
            if response.lower() == 'y':
                install_python_requirements('frontend_python/requirements_python_frontend.txt')
            else:
                return
        
        start_python_frontend()
        
    elif choice == '3':
        # Enhanced Python frontend
        print("\n🚀 Starting Enhanced Python frontend with backend integration...")
        
        # Check if matplotlib is available for charts
        try:
            import matplotlib
            print("✅ Matplotlib available - charts will be enabled")
        except ImportError:
            print("⚠️  Matplotlib not available - charts will be text-based")
            print("   To enable charts: pip install matplotlib")
        
        enhanced_process = start_enhanced_python_frontend()
        if not enhanced_process:
            print("❌ Failed to start Enhanced Python frontend")
            return
        
    elif choice == '4':
        # Requirements check only
        print("\n📋 Running comprehensive requirements check...")
        try:
            subprocess.run([sys.executable, 'check_requirements.py'], check=True)
        except:
            print("❌ Could not run requirements checker")
        
    elif choice == '5':
        print("👋 Goodbye!")
        return
    
    else:
        print("❌ Invalid choice")
        return
    
    # Keep the script running
    print("\n" + "="*60)
    print("✅ System launched successfully!")
    print("Press Ctrl+C to stop all services")
    print("="*60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        if backend_process:
            backend_process.terminate()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
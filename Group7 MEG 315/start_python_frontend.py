#!/usr/bin/env python3
"""
Simple startup script for Python-based AD-HTC Frontend
For lecturers who prefer a simple Python solution without Node.js dependencies
"""

import sys
import subprocess
import os

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['tkinter', 'matplotlib', 'numpy', 'requests']
    missing = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def install_requirements():
    """Install missing requirements"""
    print("Installing required packages...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_python_frontend.txt'], 
                      check=True, cwd='frontend_python')
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def main():
    """Main function"""
    print("\n" + "="*50)
    print("🐍 AD-HTC Python Frontend - Simple Startup")
    print("="*50)
    
    # Check requirements
    print("\n🔍 Checking requirements...")
    missing = check_requirements()
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        response = input("Install missing packages? (Y/n): ")
        if response.lower() != 'n':
            if not install_requirements():
                print("Failed to install requirements. Please install manually:")
                print("pip install matplotlib numpy requests")
                return
        else:
            print("Cannot proceed without required packages.")
            return
    else:
        print("✅ All requirements satisfied")
    
    # Check if backend is running
    print("\n🖥️  Checking backend status...")
    try:
        import requests
        response = requests.get('http://localhost:8000/docs', timeout=2)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("⚠️  Backend may not be running properly")
    except:
        print("⚠️  Backend not detected at http://localhost:8000")
        print("   Please start the backend first:")
        print("   cd backend && python -m uvicorn main:app --reload")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Start the Python frontend
    print("\n🚀 Starting Python frontend...")
    try:
        os.chdir('frontend_python')
        subprocess.run([sys.executable, 'adhtc_gui.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")
    except FileNotFoundError:
        print("❌ adhtc_gui.py not found in frontend_python directory")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
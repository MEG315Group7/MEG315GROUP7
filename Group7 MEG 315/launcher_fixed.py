#!/usr/bin/env python3
"""
Fixed AD-HTC System Launcher
Addresses dependency installation issues and provides persistent setup
"""

import sys
import os
import subprocess
import webbrowser
import time
import json
from pathlib import Path

class PersistentLauncher:
    def __init__(self):
        self.config_file = Path('launcher_config.json')
        self.config = self.load_config()
        
    def load_config(self):
        """Load launcher configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {'auto_install': True, 'last_check': 0}
        return {'auto_install': True, 'last_check': 0}
    
    def save_config(self):
        """Save launcher configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except:
            pass
    
    def check_python_packages_persistent(self, requirements_file):
        """Check Python packages with persistent installation"""
        try:
            with open(requirements_file, 'r') as f:
                packages = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('tkinter'):
                        package = line.split('>=')[0].split(';')[0].split('[')[0].strip()
                        packages.append(package)
            
            missing = []
            for package in packages:
                try:
                    __import__(package)
                except ImportError:
                    missing.append(package)
            
            return missing
        except FileNotFoundError:
            return []
    
    def install_python_requirements_persistent(self, requirements_file, force=False):
        """Install Python requirements with better error handling"""
        print(f"Installing Python requirements from {requirements_file}...")
        try:
            # Use pip install with --user flag for persistent installation
            cmd = [sys.executable, '-m', 'pip', 'install', '--user', '-r', requirements_file]
            if force:
                cmd.append('--force-reinstall')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Python requirements installed successfully!")
                return True
            else:
                print(f"❌ Error installing requirements: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def check_npm_packages_persistent(self):
        """Check npm packages with persistent installation"""
        try:
            # Check if npm is available
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                return ['npm not found']
            
            # Check if package.json exists
            frontend_dir = Path('frontend')
            if not frontend_dir.exists():
                return ['frontend directory not found']
            
            package_json = frontend_dir / 'package.json'
            if not package_json.exists():
                return ['package.json not found']
            
            # Check if node_modules exists
            node_modules = frontend_dir / 'node_modules'
            if not node_modules.exists():
                return ['node_modules not found']
            
            return []
        except FileNotFoundError:
            return ['npm not found']
    
    def install_npm_requirements_persistent(self, force=False):
        """Install npm requirements with better error handling"""
        print("Installing npm requirements...")
        try:
            cmd = ['npm', 'install']
            if force:
                cmd.append('--force')
            
            result = subprocess.run(cmd, cwd='frontend', capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ npm requirements installed successfully!")
                return True
            else:
                print(f"❌ Error installing npm requirements: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def ensure_dependencies(self):
        """Ensure all dependencies are installed"""
        print("🔧 Ensuring all dependencies are installed...")
        
        # Check and install Python dependencies
        python_files = [
            ('backend/requirements.txt', 'Backend'),
            ('frontend_python/requirements_python_frontend.txt', 'Python Frontend')
        ]
        
        for req_file, name in python_files:
            if Path(req_file).exists():
                missing = self.check_python_packages_persistent(req_file)
                if missing:
                    print(f"📦 Installing missing {name} packages: {', '.join(missing)}")
                    self.install_python_requirements_persistent(req_file)
        
        # Check and install npm dependencies
        if Path('frontend/package.json').exists():
            npm_missing = self.check_npm_packages_persistent()
            if npm_missing:
                print(f"📦 Installing missing npm packages")
                self.install_npm_requirements_persistent()
        
        self.save_config()
        print("✅ Dependencies check complete!")
    
    def start_backend(self):
        """Start backend server"""
        print("Starting backend server...")
        try:
            if not Path('backend/main.py').exists():
                print("❌ Backend main.py not found!")
                return None
            
            # Start backend in background
            process = subprocess.Popen([
                sys.executable, '-m', 'uvicorn', 'backend.main:app', 
                '--reload', '--host', '0.0.0.0', '--port', '8000'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
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
    
    def start_react_frontend(self):
        """Start React frontend"""
        print("Starting React frontend...")
        try:
            if not Path('frontend/package.json').exists():
                print("❌ frontend/package.json not found!")
                return None
            
            # Start React dev server
            process = subprocess.Popen(['npm', 'start'], cwd='frontend', 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print("✅ React frontend started!")
            print("🌐 Opening browser to http://localhost:3000...")
            time.sleep(8)  # Wait longer for React to start
            webbrowser.open('http://localhost:3000')
            return process
        except Exception as e:
            print(f"❌ Error starting React frontend: {e}")
            return None
    
    def start_python_frontend(self, standalone=False):
        """Start Python frontend"""
        print("Starting Python frontend...")
        try:
            frontend_file = 'adhtc_gui_simple.py' if standalone else 'adhtc_gui.py'
            frontend_path = Path(f'frontend_python/{frontend_file}')
            
            if not frontend_path.exists():
                print(f"❌ {frontend_path} not found!")
                return None
            
            # Start Python GUI
            process = subprocess.Popen([sys.executable, frontend_file], 
                                     cwd='frontend_python',
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print(f"✅ Python frontend ({frontend_file}) started!")
            return process
        except Exception as e:
            print(f"❌ Error starting Python frontend: {e}")
            return None
    
    def main(self):
        """Main launcher function"""
        print("\n" + "="*60)
        print("🚀 FIXED AD-HTC SYSTEM LAUNCHER")
        print("="*60)
        
        # Check Python version
        if sys.version_info < (3, 7):
            print("❌ Python 3.7+ required!")
            return
        print(f"✅ Python {sys.version.split()[0]} detected")
        
        # Ensure dependencies are installed
        self.ensure_dependencies()
        
        # Main menu
        while True:
            print("\n🖥️  Launch Options:")
            print("1. React Frontend (Full-featured, requires backend)")
            print("2. Python Frontend (Standalone, no backend needed)")
            print("3. Python Frontend (Original, requires backend)")
            print("4. Start Backend Only")
            print("5. Check Requirements")
            print("6. Force Reinstall All Dependencies")
            print("7. Exit")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == '1':
                # React frontend
                backend_process = self.start_backend()
                if backend_process:
                    frontend_process = self.start_react_frontend()
                    if frontend_process:
                        print("\n✅ System launched successfully!")
                        print("Press Ctrl+C to stop all services")
                        try:
                            while True:
                                time.sleep(1)
                        except KeyboardInterrupt:
                            print("\n🛑 Shutting down...")
                            backend_process.terminate()
                            frontend_process.terminate()
                    else:
                        print("❌ Failed to start React frontend")
                        backend_process.terminate()
                else:
                    print("❌ Failed to start backend")
                
            elif choice == '2':
                # Standalone Python frontend
                frontend_process = self.start_python_frontend(standalone=True)
                if frontend_process:
                    print("\n✅ Standalone Python frontend launched!")
                    print("Press Ctrl+C to stop")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n🛑 Shutting down...")
                        frontend_process.terminate()
                
            elif choice == '3':
                # Original Python frontend
                backend_process = self.start_backend()
                if backend_process:
                    frontend_process = self.start_python_frontend(standalone=False)
                    if frontend_process:
                        print("\n✅ Python frontend system launched!")
                        print("Press Ctrl+C to stop all services")
                        try:
                            while True:
                                time.sleep(1)
                        except KeyboardInterrupt:
                            print("\n🛑 Shutting down...")
                            backend_process.terminate()
                            frontend_process.terminate()
                    else:
                        print("❌ Failed to start Python frontend")
                        backend_process.terminate()
                else:
                    print("❌ Failed to start backend")
                
            elif choice == '4':
                # Backend only
                backend_process = self.start_backend()
                if backend_process:
                    print("\n✅ Backend server running!")
                    print("Press Ctrl+C to stop")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n🛑 Shutting down...")
                        backend_process.terminate()
                
            elif choice == '5':
                # Check requirements
                print("\n📋 Running comprehensive requirements check...")
                try:
                    subprocess.run([sys.executable, 'check_requirements.py'], check=True)
                except:
                    print("❌ Could not run requirements checker")
                
            elif choice == '6':
                # Force reinstall
                print("\n🔧 Force reinstalling all dependencies...")
                python_files = [
                    ('backend/requirements.txt', 'Backend'),
                    ('frontend_python/requirements_python_frontend.txt', 'Python Frontend')
                ]
                
                for req_file, name in python_files:
                    if Path(req_file).exists():
                        print(f"Force reinstalling {name} packages...")
                        self.install_python_requirements_persistent(req_file, force=True)
                
                if Path('frontend/package.json').exists():
                    print("Force reinstalling npm packages...")
                    self.install_npm_requirements_persistent(force=True)
                
            elif choice == '7':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice")

if __name__ == "__main__":
    launcher = PersistentLauncher()
    launcher.main()
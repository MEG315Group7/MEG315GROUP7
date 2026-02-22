#!/usr/bin/env python3
"""
Requirements Checker for 230404035 Group 7 AD-HTC System
Checks for missing dependencies and provides installation instructions
"""

import sys
import subprocess
import importlib
from typing import Dict, List, Tuple

class RequirementsChecker:
    def __init__(self):
        self.requirements = {
            'backend': {
                'fastapi': 'FastAPI web framework',
                'uvicorn': 'ASGI server',
                'numpy': 'Numerical computing',
                'pydantic': 'Data validation',
                'python-multipart': 'Form data handling'
            },
            'frontend_js': {
                'react': 'JavaScript UI library',
                'react-dom': 'React DOM renderer',
                'recharts': 'Charting library',
                'axios': 'HTTP client'
            },
            'frontend_python': {
                'tkinter': 'GUI framework (usually built-in)',
                'matplotlib': 'Plotting library',
                'numpy': 'Numerical computing',
                'requests': 'HTTP client'
            },
            'optional': {
                'three': '3D visualization',
                'plotly': 'Interactive charts',
                'dash': 'Web-based Python dashboard'
            }
        }
    
    def check_python_package(self, package_name: str) -> Tuple[bool, str]:
        """Check if a Python package is installed"""
        try:
            importlib.import_module(package_name)
            return True, f"✅ {package_name} is installed"
        except ImportError:
            return False, f"❌ {package_name} is not installed"
    
    def check_npm_package(self, package_name: str) -> Tuple[bool, str]:
        """Check if an npm package is installed"""
        try:
            result = subprocess.run(['npm', 'list', package_name], 
                                  capture_output=True, text=True, cwd='frontend')
            if result.returncode == 0:
                return True, f"✅ {package_name} is installed"
            else:
                return False, f"❌ {package_name} is not installed"
        except FileNotFoundError:
            return False, f"⚠️  npm not found - cannot check {package_name}"
    
    def check_system_requirements(self) -> Dict[str, any]:
        """Check all system requirements"""
        results = {
            'python_version': sys.version,
            'backend': {},
            'frontend_python': {},
            'frontend_js': {},
            'optional': {},
            'recommendations': []
        }
        
        # Check Python version
        if sys.version_info < (3, 7):
            results['recommendations'].append("⚠️  Python 3.7+ required. Current version is too old.")
        
        # Check backend requirements
        print("🔍 Checking Backend Requirements...")
        for package, description in self.requirements['backend'].items():
            installed, message = self.check_python_package(package)
            results['backend'][package] = {'installed': installed, 'description': description, 'message': message}
        
        # Check frontend Python requirements
        print("🔍 Checking Python Frontend Requirements...")
        for package, description in self.requirements['frontend_python'].items():
            if package == 'tkinter':
                try:
                    import tkinter
                    results['frontend_python'][package] = {'installed': True, 'description': description, 'message': f"✅ {package} is available"}
                except ImportError:
                    results['frontend_python'][package] = {'installed': False, 'description': description, 'message': f"❌ {package} is not available"}
            else:
                installed, message = self.check_python_package(package)
                results['frontend_python'][package] = {'installed': installed, 'description': description, 'message': message}
        
        # Check frontend JS requirements (if frontend directory exists)
        import os
        if os.path.exists('frontend'):
            print("🔍 Checking JavaScript Frontend Requirements...")
            for package, description in self.requirements['frontend_js'].items():
                installed, message = self.check_npm_package(package)
                results['frontend_js'][package] = {'installed': installed, 'description': description, 'message': message}
        else:
            results['recommendations'].append("ℹ️  Frontend directory not found. Skipping JS package checks.")
        
        # Check optional requirements
        print("🔍 Checking Optional Requirements...")
        for package, description in self.requirements['optional'].items():
            if package in ['plotly', 'dash']:
                installed, message = self.check_python_package(package)
                results['optional'][package] = {'installed': installed, 'description': description, 'message': message}
            else:
                # For npm packages
                installed, message = self.check_npm_package(package)
                results['optional'][package] = {'installed': installed, 'description': description, 'message': message}
        
        return results
    
    def generate_install_commands(self, results: Dict) -> List[str]:
        """Generate installation commands for missing packages"""
        commands = []
        
        # Backend packages
        missing_backend = [pkg for pkg, info in results['backend'].items() if not info['installed']]
        if missing_backend:
            commands.append(f"pip install {' '.join(missing_backend)}")
        
        # Frontend Python packages
        missing_py_frontend = [pkg for pkg, info in results['frontend_python'].items() if not info['installed'] and pkg != 'tkinter']
        if missing_py_frontend:
            commands.append(f"pip install {' '.join(missing_py_frontend)}")
        
        # Frontend JS packages
        missing_js_frontend = [pkg for pkg, info in results['frontend_js'].items() if not info['installed']]
        if missing_js_frontend:
            commands.append(f"cd frontend && npm install {' '.join(missing_js_frontend)}")
        
        # Optional packages
        missing_optional = [pkg for pkg, info in results['optional'].items() if not info['installed'] and pkg in ['plotly', 'dash']]
        if missing_optional:
            commands.append(f"pip install {' '.join(missing_optional)}")
        
        return commands
    
    def display_results(self, results: Dict):
        """Display the check results in a user-friendly format"""
        print("\n" + "="*60)
        print("🔧 230404035 GROUP 7 - AD-HTC SYSTEM REQUIREMENTS CHECK")
        print("="*60)
        
        print(f"\n🐍 Python Version: {results['python_version']}")
        
        # Backend section
        print(f"\n🔧 Backend Requirements:")
        for package, info in results['backend'].items():
            print(f"  {info['message']} - {info['description']}")
        
        # Frontend Python section
        print(f"\n🖥️  Python Frontend Requirements:")
        for package, info in results['frontend_python'].items():
            print(f"  {info['message']} - {info['description']}")
        
        # Frontend JS section
        if results['frontend_js']:
            print(f"\n🌐 JavaScript Frontend Requirements:")
            for package, info in results['frontend_js'].items():
                print(f"  {info['message']} - {info['description']}")
        
        # Optional section
        print(f"\n⭐ Optional Requirements:")
        for package, info in results['optional'].items():
            print(f"  {info['message']} - {info['description']}")
        
        # Recommendations
        if results['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in results['recommendations']:
                print(f"  {rec}")
        
        # Installation commands
        commands = self.generate_install_commands(results)
        if commands:
            print(f"\n📦 Installation Commands:")
            for cmd in commands:
                print(f"  {cmd}")
        
        # Overall status
        all_installed = all(info['installed'] for category in ['backend', 'frontend_python'] 
                          for info in results[category].values())
        
        if all_installed:
            print(f"\n✅ All essential requirements are met! You can run the system.")
        else:
            print(f"\n⚠️  Some requirements are missing. Please install them using the commands above.")
        
        print("\n" + "="*60)

def main():
    """Main function to run the requirements checker"""
    checker = RequirementsChecker()
    results = checker.check_system_requirements()
    checker.display_results(results)
    
    # Ask if user wants to install missing packages
    import os
    if any(not info['installed'] for category in ['backend', 'frontend_python'] 
           for info in results[category].values()):
        response = input("\nWould you like to install missing packages automatically? (y/N): ")
        if response.lower() == 'y':
            commands = checker.generate_install_commands(results)
            for cmd in commands:
                print(f"\nRunning: {cmd}")
                try:
                    result = subprocess.run(cmd, shell=True, check=True)
                    print(f"✅ Successfully installed: {cmd}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to install: {cmd}")
                    print(f"Error: {e}")

if __name__ == "__main__":
    main()
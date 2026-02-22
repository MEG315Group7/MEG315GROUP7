#!/usr/bin/env python3
"""
Requirements checker with popup notification for missing system components.
This script checks for required Python packages and system dependencies,
and displays a user-friendly popup if anything is missing.
"""

import subprocess
import sys
import os
import json
from typing import Dict, List, Tuple

def check_python_package(package_name: str) -> bool:
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def check_system_command(command: str) -> bool:
    """Check if a system command is available"""
    try:
        subprocess.run([command, '--version'], 
                        capture_output=True, 
                        check=True, 
                        timeout=5)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False

def install_python_package(package_name: str) -> bool:
    """Install a Python package using pip"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', package_name], 
                      check=True, 
                      capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def show_requirements_popup(missing_components: Dict[str, List[str]]) -> None:
    """Show a popup window with missing components and installation instructions"""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
        
        # Create main window
        root = tk.Tk()
        root.title("System Requirements Check")
        root.geometry("600x400")
        
        # Make window appear on top
        root.attributes('-topmost', True)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="System Requirements Check",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status message
        if not missing_components:
            status_label = ttk.Label(main_frame, 
                                   text="✅ All system requirements are satisfied!",
                                   font=('Arial', 12),
                                   foreground='green')
            status_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
            
            # Close button
            close_btn = ttk.Button(main_frame, 
                                  text="Continue",
                                  command=root.destroy)
            close_btn.grid(row=2, column=0, columnspan=2, pady=(20, 0))
            
        else:
            status_label = ttk.Label(main_frame, 
                                   text="⚠️ The following components are missing or need attention:",
                                   font=('Arial', 12),
                                   foreground='orange')
            status_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
            
            # Create text widget for missing components
            text_widget = tk.Text(main_frame, height=15, width=70)
            text_widget.grid(row=2, column=0, columnspan=2, pady=(0, 20))
            
            # Insert missing components information
            for category, items in missing_components.items():
                text_widget.insert(tk.END, f"\n{category.upper()}:\n")
                for item in items:
                    text_widget.insert(tk.END, f"  • {item}\n")
                text_widget.insert(tk.END, "\n")
            
            # Installation instructions
            text_widget.insert(tk.END, "INSTALLATION INSTRUCTIONS:\n")
            text_widget.insert(tk.END, "1. Python packages: Run the auto-installer or use 'pip install <package_name>'\n")
            text_widget.insert(tk.END, "2. System commands: Install the required software and ensure it's in your PATH\n")
            text_widget.insert(tk.END, "3. After installation, restart this application\n")
            
            # Make text widget read-only
            text_widget.config(state=tk.DISABLED)
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
            
            # Auto-install button
            auto_install_btn = ttk.Button(buttons_frame, 
                                         text="Auto-install Python Packages",
                                         command=lambda: auto_install_packages(root, missing_components))
            auto_install_btn.grid(row=0, column=0, padx=(0, 10))
            
            # Manual install button
            manual_btn = ttk.Button(buttons_frame, 
                                   text="Manual Installation",
                                   command=lambda: show_manual_installation(root, missing_components))
            manual_btn.grid(row=0, column=1, padx=(10, 0))
            
            # Close button
            close_btn = ttk.Button(buttons_frame, 
                                  text="Continue Anyway",
                                  command=root.destroy)
            close_btn.grid(row=0, column=2, padx=(10, 0))
        
        # Center the window on screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Run the GUI
        root.mainloop()
        
    except ImportError:
        # Fallback to console output if tkinter is not available
        print("\n" + "="*60)
        print("SYSTEM REQUIREMENTS CHECK")
        print("="*60)
        
        if not missing_components:
            print("✅ All system requirements are satisfied!")
        else:
            print("⚠️ The following components are missing or need attention:")
            for category, items in missing_components.items():
                print(f"\n{category.upper()}:")
                for item in items:
                    print(f"  • {item}")
            
            print("\nINSTALLATION INSTRUCTIONS:")
            print("1. Python packages: Run 'pip install <package_name>'")
            print("2. System commands: Install the required software")
            print("3. After installation, restart this application")
        
        print("="*60 + "\n")

def auto_install_packages(root, missing_components):
    """Attempt to automatically install missing Python packages"""
    if 'python_packages' in missing_components:
        packages = missing_components['python_packages']
        installed = []
        failed = []
        
        for package in packages:
            print(f"Installing {package}...")
            if install_python_package(package):
                installed.append(package)
            else:
                failed.append(package)
        
        # Show results
        message = f"Installation Results:\n"
        if installed:
            message += f"✅ Successfully installed: {', '.join(installed)}\n"
        if failed:
            message += f"❌ Failed to install: {', '.join(failed)}\n"
            message += "Please install manually using pip."
        
        from tkinter import messagebox
        messagebox.showinfo("Installation Results", message)

def show_manual_installation(root, missing_components):
    """Show manual installation instructions"""
    instructions = "MANUAL INSTALLATION INSTRUCTIONS:\n\n"
    
    if 'python_packages' in missing_components:
        instructions += "Python Packages:\n"
        for package in missing_components['python_packages']:
            instructions += f"  pip install {package}\n"
        instructions += "\n"
    
    if 'system_commands' in missing_components:
        instructions += "System Commands:\n"
        for command in missing_components['system_commands']:
            instructions += f"  Install {command} and ensure it's in your PATH\n"
        instructions += "\n"
    
    instructions += "After installation, restart this application."
    
    from tkinter import messagebox
    messagebox.showinfo("Manual Installation", instructions)

def main():
    """Main function to check requirements and show popup if needed"""
    
    # Define required components
    required_python_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'python-multipart',
        'numpy', 'matplotlib', 'requests', 'tkinter'
    ]
    
    required_system_commands = [
        'python', 'pip', 'npm'  # npm is optional, mainly for React frontend
    ]
    
    missing_components = {
        'python_packages': [],
        'system_commands': []
    }
    
    # Check Python packages
    for package in required_python_packages:
        if package == 'tkinter':
            # Special handling for tkinter
            try:
                import tkinter
            except ImportError:
                missing_components['python_packages'].append('tkinter (usually included with Python)')
        else:
            if not check_python_package(package):
                missing_components['python_packages'].append(package)
    
    # Check system commands
    for command in required_system_commands:
        if not check_system_command(command):
            missing_components['system_commands'].append(command)
    
    # Remove empty categories
    missing_components = {k: v for k, v in missing_components.items() if v}
    
    # Show popup if there are missing components
    if missing_components:
        show_requirements_popup(missing_components)
        return False
    else:
        # Show success popup briefly
        show_requirements_popup(missing_components)
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
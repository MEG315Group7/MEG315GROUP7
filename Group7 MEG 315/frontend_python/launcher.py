#!/usr/bin/env python3
"""
Launcher for AD-HTC Python Frontend
Provides options to run standalone version or with backend server
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
import time
import requests

def check_backend_status():
    """Check if backend server is running"""
    try:
        response = requests.get('http://localhost:8000/', timeout=2)
        return response.status_code == 200
    except:
        return False

def start_backend_server():
    """Start the backend server"""
    try:
        # Change to backend directory and start server
        backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
        
        # Try to start with uvicorn first
        try:
            subprocess.Popen([
                sys.executable, '-m', 'uvicorn', 'main:app', 
                '--reload', '--port', '8000'
            ], cwd=backend_dir, shell=True)
        except:
            # Fallback to direct Python execution
            subprocess.Popen([
                sys.executable, 'main.py'
            ], cwd=backend_dir, shell=True)
        
        return True
    except Exception as e:
        messagebox.showerror("Backend Error", f"Failed to start backend server: {e}")
        return False

def run_standalone():
    """Run the standalone Python frontend"""
    try:
        frontend_path = os.path.join(os.path.dirname(__file__), 'adhtc_gui_standalone.py')
        
        if os.path.exists(frontend_path):
            # Import and run directly
            sys.path.insert(0, os.path.dirname(__file__))
            
            # Import the standalone module
            spec = __import__('adhtc_gui_standalone', fromlist=['ADHTCStandaloneFrontend'])
            app = spec.ADHTCStandaloneFrontend()
            app.run()
        else:
            messagebox.showerror("File Error", "Standalone frontend not found!")
            
    except Exception as e:
        messagebox.showerror("Launch Error", f"Failed to launch standalone frontend: {e}")

def run_with_backend():
    """Run with backend server"""
    try:
        # Check if backend is running
        if not check_backend_status():
            messagebox.showinfo("Backend Status", "Starting backend server...")
            if not start_backend_server():
                return
            
            # Wait a bit for server to start
            time.sleep(3)
            
            # Check again
            if not check_backend_status():
                messagebox.showerror("Backend Error", "Backend server failed to start!")
                return
        
        # Run original frontend
        frontend_path = os.path.join(os.path.dirname(__file__), 'adhtc_gui.py')
        
        if os.path.exists(frontend_path):
            subprocess.Popen([sys.executable, frontend_path], shell=True)
        else:
            messagebox.showerror("File Error", "Original frontend not found!")
            
    except Exception as e:
        messagebox.showerror("Launch Error", f"Failed to launch frontend: {e}")

def create_launcher_gui():
    """Create the launcher GUI"""
    root = tk.Tk()
    root.title("AD-HTC Python Frontend Launcher")
    root.geometry("400x300")
    root.configure(bg='#F0F8FF')
    
    # Colors
    colors = {
        'primary': '#2E8B57',
        'secondary': '#4682B4',
        'background': '#F0F8FF',
        'surface': '#FFFFFF'
    }
    
    # Header
    header_frame = tk.Frame(root, bg=colors['primary'], height=60)
    header_frame.pack(fill=tk.X)
    
    title_label = tk.Label(header_frame, 
                          text="AD-HTC Frontend Launcher",
                          font=('Inter', 14, 'bold'),
                          bg=colors['primary'],
                          fg='white')
    title_label.pack(pady=15)
    
    # Main content
    main_frame = tk.Frame(root, bg=colors['background'])
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Backend status
    status_frame = tk.LabelFrame(main_frame, text="Backend Status",
                                bg=colors['surface'], font=('Inter', 10, 'bold'))
    status_frame.pack(fill=tk.X, pady=10)
    
    def update_status():
        if check_backend_status():
            status_label.config(text="✅ Backend Running", fg='green')
            status_btn.config(text="Stop Backend", command=stop_backend)
        else:
            status_label.config(text="❌ Backend Stopped", fg='red')
            status_btn.config(text="Start Backend", command=start_backend)
    
    status_label = tk.Label(status_frame, text="Checking...", 
                           bg=colors['surface'], font=('Inter', 9))
    status_label.pack(pady=5)
    
    status_btn = tk.Button(status_frame, text="Check Status",
                          command=update_status, bg=colors['secondary'], fg='white')
    status_btn.pack(pady=5)
    
    # Launch options
    launch_frame = tk.LabelFrame(main_frame, text="Launch Options",
                                bg=colors['surface'], font=('Inter', 10, 'bold'))
    launch_frame.pack(fill=tk.X, pady=10)
    
    tk.Label(launch_frame, 
            text="Choose how to run the AD-HTC frontend:",
            bg=colors['surface'], font=('Inter', 9)).pack(pady=5)
    
    # Standalone button
    standalone_btn = tk.Button(launch_frame, 
                              text="Run Standalone\n(No Backend Required)",
                              command=lambda: [root.destroy(), run_standalone()],
                              bg=colors['primary'], fg='white',
                              height=2, font=('Inter', 9, 'bold'))
    standalone_btn.pack(pady=5, fill=tk.X)
    
    # Backend button
    backend_btn = tk.Button(launch_frame,
                           text="Run with Backend Server\n(Full Features)",
                           command=lambda: [root.destroy(), run_with_backend()],
                           bg=colors['secondary'], fg='white',
                           height=2, font=('Inter', 9, 'bold'))
    backend_btn.pack(pady=5, fill=tk.X)
    
    # Instructions
    info_frame = tk.LabelFrame(main_frame, text="Info",
                              bg=colors['surface'], font=('Inter', 10, 'bold'))
    info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    info_text = tk.Text(info_frame, height=4, width=40, bg=colors['surface'],
                        font=('Inter', 8), wrap=tk.WORD)
    info_text.pack(pady=5, padx=5)
    
    info_text.insert(tk.END, "Standalone Mode:\n")
    info_text.insert(tk.END, "• Uses built-in calculation modules\n")
    info_text.insert(tk.END, "• No server dependencies\n")
    info_text.insert(tk.END, "• Perfect for offline use\n\n")
    info_text.insert(tk.END, "Backend Mode:\n")
    info_text.insert(tk.END, "• Full calculation capabilities\n")
    info_text.insert(tk.END, "• Requires backend server\n")
    info_text.insert(tk.END, "• Advanced optimization features")
    
    info_text.config(state=tk.DISABLED)
    
    # Initial status update
    update_status()
    
    return root

def stop_backend():
    """Stop the backend server"""
    try:
        # Try to stop uvicorn gracefully
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'uvicorn' in ' '.join(cmdline):
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        messagebox.showinfo("Backend", "Backend server stopped!")
    except:
        messagebox.showinfo("Backend", "Could not stop backend automatically.")

def start_backend():
    """Start backend and update UI"""
    if start_backend_server():
        time.sleep(2)
        # Update status would be called by the UI

def main():
    """Main function"""
    root = create_launcher_gui()
    root.mainloop()

if __name__ == "__main__":
    main()
import os
import sys
import subprocess
import time
import webbrowser
from threading import Timer

def open_browser():
    """Opens the local browser to the application URL"""
    time.sleep(3)  # Wait for server to start
    url = "http://127.0.0.1:8000"
    print(f"\nLaunching browser at {url}...")
    webbrowser.open(url)

def run_application():
    """Main launcher logic"""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    venv_python = os.path.join(backend_dir, ".venv", "Scripts", "python.exe")
    
    if not os.path.exists(venv_python):
        # Fallback for systems where venv might be in the root or named differently
        venv_python = "python" # Hope it's in path
        print(f"Warning: Virtual environment python not found at {venv_python}. Using system python.")

    print("\n" + "="*50)
    print("HAIR and SCALP DISEASE PREDICTION SYSTEM")
    print("="*50)
    print("\nStarting Neural Inference Engine...")
    
    # Run migrations
    print("Synchronizing vault database...")
    subprocess.run([venv_python, "manage.py", "migrate"], cwd=backend_dir)
    
    # Start browser in a background thread
    Timer(3, open_browser).start()
    
    # Start Django server
    print("Ignite: Initializing Django Development Server...")
    try:
        subprocess.run([venv_python, "manage.py", "runserver"], cwd=backend_dir)
    except KeyboardInterrupt:
        print("\n\nSystem shutdown sequence complete.")

if __name__ == "__main__":
    run_application()

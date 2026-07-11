#!/usr/bin/env python3
"""
Script to run citation tracker notebook via nbconvert
This version is compatible with GitHub Actions and headless environments.
"""

import warnings
import subprocess
import sys
import os
from pathlib import Path

# Suppress specific warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*Proactor event loop.*")

def run_notebook_as_script():
    """
    Convert notebook to Python script and execute it
    This approach is more reliable in GitHub Actions
    """
    print("Running citation tracker as Python script...")
    
    # First, try to run the direct Python script
    script_path = Path('script.py')
    if script_path.exists():
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True)
        return result
    else:
        print(f"Error: {script_path} not found")
        return None

def convert_and_run_notebook():
    """
    Convert Jupyter notebook to Python script and run it
    """
    notebook_path = Path('script.ipynb')
    
    if not notebook_path.exists():
        print(f"Error: Notebook {notebook_path} not found")
        return None
    
    print(f"Converting and running notebook: {notebook_path}")
    
    # Convert notebook to Python script
    convert_cmd = [
        'jupyter', 'nbconvert', 
        '--to', 'python',
        '--execute',
        '--stdout',
        str(notebook_path)
    ]
    
    try:
        result = subprocess.run(convert_cmd, capture_output=True, text=True, timeout=300)
        return result
    except subprocess.TimeoutExpired:
        print("Error: Notebook execution timed out after 5 minutes")
        return None
    except FileNotFoundError:
        print("Error: jupyter nbconvert not found. Make sure Jupyter is installed.")
        return None

def execute_notebook_in_place():
    """
    Execute notebook in place (original approach)
    """
    notebook_path = Path('script.ipynb')
    
    if not notebook_path.exists():
        print(f"Error: Notebook {notebook_path} not found")
        return None
    
    print(f"Executing notebook in place: {notebook_path}")
    
    # Set matplotlib backend for headless environment
    os.environ['MPLBACKEND'] = 'Agg'
    
    command = [
        'jupyter', 'nbconvert',
        '--execute',
        '--inplace',
        '--to', 'notebook',
        str(notebook_path)
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        return result
    except subprocess.TimeoutExpired:
        print("Error: Notebook execution timed out after 5 minutes")
        return None
    except FileNotFoundError:
        print("Error: jupyter nbconvert not found. Make sure Jupyter is installed.")
        return None

def main():
    """Main execution function with fallback strategies"""
    
    print("Citation Tracker - Notebook Runner")
    print("=" * 40)
    
    # Strategy 1: Try to run the Python script directly (most reliable)
    print("\n1. Attempting to run Python script directly...")
    result = run_notebook_as_script()
    
    if result and result.returncode == 0:
        print("✅ Python script executed successfully!")
        print("\nScript Output:")
        if result.stdout:
            print(result.stdout)
        return True
    elif result:
        print("❌ Python script execution failed.")
        if result.stderr:
            print("Error Output:")
            print(result.stderr)
    
    # Strategy 2: Try to convert and run notebook
    print("\n2. Attempting to convert and run notebook...")
    result = convert_and_run_notebook()
    
    if result and result.returncode == 0:
        print("✅ Notebook converted and executed successfully!")
        return True
    elif result:
        print("❌ Notebook conversion failed.")
        if result.stderr:
            print("Error Output:")
            print(result.stderr)
    
    # Strategy 3: Try to execute notebook in place
    print("\n3. Attempting to execute notebook in place...")
    result = execute_notebook_in_place()
    
    if result and result.returncode == 0:
        print("✅ Notebook executed in place successfully!")
        return True
    elif result:
        print("❌ Notebook execution failed.")
        if result.stderr:
            print("Error Output:")
            print(result.stderr)
    
    print("\n❌ All execution strategies failed.")
    return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    
    # Check if output files were created
    output_dir = Path('output')
    if output_dir.exists():
        output_files = list(output_dir.glob('*'))
        if output_files:
            print(f"\n✅ Output files created: {[f.name for f in output_files]}")
        else:
            print(f"\n⚠️  Output directory exists but is empty")
    else:
        print(f"\n⚠️  No output directory found")
    
    print("\n🎉 Citation tracker completed!")
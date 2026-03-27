"""
RetailMind AI Agent — Entry Point
====================================
Launches the Streamlit application.
Run with: python run.py

This is the single entry point for the evaluator to launch the application.
It starts the Streamlit server which serves the app.py interface.
"""

import subprocess
import sys
import os

def main():
    """Launch the RetailMind AI Agent Streamlit application."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")
    
    print("=" * 60)
    print("  🛍️  RetailMind AI — Product Intelligence Agent")
    print("  Starting Streamlit server...")
    print("=" * 60)
    print()
    
    # Launch Streamlit with the app
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--theme.primaryColor", "#667eea",
        "--theme.backgroundColor", "#ffffff",
        "--theme.secondaryBackgroundColor", "#f5f7fa",
        "--theme.textColor", "#1a202c"
    ])

if __name__ == "__main__":
    main()

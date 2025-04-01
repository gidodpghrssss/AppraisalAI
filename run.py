"""
Run script for the Appraisal AI Agent application.
"""
import os
import argparse
import uvicorn
import asyncio
import threading
import webbrowser
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_fastapi():
    """Run the FastAPI server."""
    from app.main import app
    
    port = int(os.getenv("PORT", "8001"))  # Changed default port to 8001
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port)

def run_gradio():
    """Run the Gradio UI."""
    from app.ui.gradio_app import app
    
    # Use a different port for Gradio
    port = 7861  
    host = "0.0.0.0"
    
    # Always use share=True to avoid localhost access issues
    app.launch(server_name=host, server_port=port, share=True)

def open_browser(api_port, ui_port, delay=2):
    """Open browser tabs after a delay."""
    time.sleep(delay)
    webbrowser.open(f"http://localhost:{ui_port}")
    webbrowser.open(f"http://localhost:{api_port}/api/v1/docs")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Appraisal AI Agent application")
    parser.add_argument("--api-only", action="store_true", help="Run only the API server")
    parser.add_argument("--ui-only", action="store_true", help="Run only the UI server")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    
    args = parser.parse_args()
    
    api_port = int(os.getenv("PORT", "8001"))  # Changed default port to 8001
    ui_port = 7861  
    
    if not args.ui_only and not args.api_only:
        # Run both API and UI
        print(f"Starting API server on port {api_port}...")
        api_thread = threading.Thread(target=run_fastapi)
        api_thread.daemon = True
        api_thread.start()
        
        print(f"Starting UI server on port {ui_port}...")
        ui_thread = threading.Thread(target=run_gradio)
        ui_thread.daemon = True
        ui_thread.start()
        
        if not args.no_browser:
            browser_thread = threading.Thread(target=open_browser, args=(api_port, ui_port))
            browser_thread.daemon = True
            browser_thread.start()
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
    
    elif args.api_only:
        # Run only API
        print(f"Starting API server on port {api_port}...")
        run_fastapi()
    
    elif args.ui_only:
        # Run only UI
        print(f"Starting UI server on port {ui_port}...")
        run_gradio()

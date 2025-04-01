"""
Web interface configuration for the Appraisal AI application.
"""
import os
import logging
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)

def get_templates_directory():
    """
    Get the templates directory with robust path resolution.
    """
    # Try multiple methods to find the templates directory
    possible_paths = [
        # Method 1: Relative to this file
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "app", "templates"),
        # Method 2: Relative to current working directory
        os.path.join(os.getcwd(), "app", "templates"),
        # Method 3: Absolute path for Render deployment
        "/opt/render/project/src/app/templates"
    ]
    
    # Try each path and use the first one that exists
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Using templates directory: {path}")
            return path
    
    # If no path exists, log a warning and use the first path anyway
    logger.warning(f"No templates directory found. Tried: {possible_paths}")
    return possible_paths[0]

# Get the templates directory
templates_dir = get_templates_directory()

# Initialize Jinja2Templates
templates = Jinja2Templates(directory=templates_dir)

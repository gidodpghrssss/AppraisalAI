"""
Web controllers for the Apeko website.
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Form, File, UploadFile, Query, Path
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Dict, Any
import os
import json
import random
from datetime import datetime, timedelta
import httpx
import logging
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

from app.db.session import get_db
from app.services.rag_service import RAGService
from app.models.rag import Document, WebsiteUsage
from app.models.user import User, UserRole
from app.services.dependencies import get_llm_service

# Initialize templates
templates_dir = os.path.join(os.getcwd(), "app", "templates")
templates = Jinja2Templates(directory=templates_dir)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """
    Render the home page of the Apeko website.
    """
    # Log website visit
    try:
        usage = WebsiteUsage(
            page_visited="home",
            session_id=request.cookies.get("session_id", "unknown"),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        db.add(usage)
        db.commit()
    except Exception as e:
        # Log the error but continue rendering the page
        print(f"Error logging website visit: {e}")
    
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Render the admin dashboard.
    """
    try:
        # Import the necessary models
        from app.models.client import Client
        from app.models.property import Property
        from app.models.project import Project, ProjectStatus
        from app.models.document import Document, DocumentType
        from sqlalchemy import func, desc
        
        # Get dashboard statistics with error handling
        try:
            total_clients = db.query(Client).count()
        except Exception as e:
            logger.error(f"Error getting client count: {e}")
            total_clients = 0
        
        try:
            total_appraisals = db.query(Project).count()
        except Exception as e:
            logger.error(f"Error getting appraisal count: {e}")
            total_appraisals = 0
        
        try:
            active_projects = db.query(Project).filter(
                Project.status.in_([ProjectStatus.IN_PROGRESS, ProjectStatus.REVIEW])
            ).count()
        except Exception as e:
            logger.error(f"Error getting active projects count: {e}")
            active_projects = 0
        
        try:
            pending_requests = db.query(Project).filter(
                Project.status == ProjectStatus.DRAFT
            ).count()
        except Exception as e:
            logger.error(f"Error getting pending requests count: {e}")
            pending_requests = 0
        
        # Calculate real revenue if possible
        try:
            # Get total estimated value of all completed projects
            total_revenue = db.query(func.sum(Project.estimated_value)).filter(
                Project.status == ProjectStatus.COMPLETED
            ).scalar()
            
            # If we have revenue data, calculate monthly revenue (average per month)
            if total_revenue:
                # Get the earliest project date
                earliest_project = db.query(Project).order_by(Project.created_at.asc()).first()
                if earliest_project and earliest_project.created_at:
                    # Calculate months since first project
                    import datetime
                    now = datetime.datetime.now()
                    months_diff = (now.year - earliest_project.created_at.year) * 12 + (now.month - earliest_project.created_at.month)
                    months_diff = max(1, months_diff)  # Ensure at least 1 month
                    monthly_revenue = int(total_revenue / months_diff)
                else:
                    monthly_revenue = int(total_revenue / 12)  # Default to yearly average
            else:
                monthly_revenue = 15000  # Fallback to mock value
                
            # Calculate revenue change percentage (mock for now)
            monthly_revenue_change = 15  # Mock change percentage
        except Exception as e:
            logger.error(f"Error calculating revenue: {e}")
            monthly_revenue = 15000  # Mock value
            monthly_revenue_change = 15  # Mock change percentage
            
        # Calculate website visits (mock since we don't have real analytics)
        website_visits = 1250  # Mock value
        website_visits_change = 8  # Mock change percentage
        
        # Prepare stats dictionary for the template
        stats = {
            "total_clients": total_clients,
            "total_clients_change": 5,  # Mock change percentage
            "total_appraisals": total_appraisals,
            "active_projects": active_projects,
            "pending_requests": pending_requests,
            "website_visits": website_visits,
            "website_visits_change": website_visits_change,
            "total_reports": total_appraisals,
            "total_reports_change": 5,  # Mock change percentage
            "monthly_revenue": monthly_revenue,
            "monthly_revenue_change": monthly_revenue_change,
        }
        
        # Get recent activities from real data
        try:
            # Get recent projects with client information
            recent_projects = db.query(Project).order_by(desc(Project.created_at)).limit(4).all()
            
            recent_activities = []
            for project in recent_projects:
                # Get client name
                client_name = "Unknown Client"
                try:
                    if project.client_id:
                        client = db.query(Client).filter(Client.id == project.client_id).first()
                        if client:
                            client_name = client.name
                except Exception as e:
                    logger.error(f"Error getting client for project {project.id}: {e}")
                
                # Format date
                date_str = "Unknown Date"
                if hasattr(project, "created_at") and project.created_at:
                    date_str = project.created_at.strftime("%Y-%m-%d")
                
                # Format status
                status_str = "unknown"
                if hasattr(project, "status"):
                    if hasattr(project.status, "value"):
                        status_str = project.status.value
                    else:
                        status_str = str(project.status)
                
                recent_activities.append({
                    "id": project.id,
                    "title": getattr(project, "title", "Untitled Project"),
                    "client": client_name,
                    "date": date_str,
                    "status": status_str
                })
        except Exception as e:
            logger.error(f"Error getting recent activities: {e}")
            # Mock data for recent activities
            recent_activities = [
                {"id": 1, "title": "Commercial Property Appraisal", "client": "ABC Corp", "date": "2025-03-28", "status": "in_progress"},
                {"id": 2, "title": "Residential Valuation", "client": "John Smith", "date": "2025-03-27", "status": "completed"},
                {"id": 3, "title": "Market Analysis Report", "client": "XYZ Investments", "date": "2025-03-26", "status": "review"},
                {"id": 4, "title": "Property Development Assessment", "client": "123 Properties", "date": "2025-03-25", "status": "draft"}
            ]
        
        # Add recent activities to stats
        stats["recent_activities"] = recent_activities
        
        # Get RAG statistics with real data
        try:
            # Get document type distribution
            document_counts = db.query(
                Document.type, 
                func.count(Document.id).label('count')
            ).group_by(Document.type).all()
            
            # Convert to dictionary for easier template access
            document_data = {}
            for doc_type, count in document_counts:
                type_name = doc_type.value if hasattr(doc_type, "value") else str(doc_type)
                document_data[type_name] = count
                
            # If no documents found, use mock data
            if not document_data:
                document_data = {
                    "APPRAISAL_REPORT": 45,
                    "PROPERTY_RECORD": 30,
                    "MARKET_ANALYSIS": 15,
                    "TAX_DOCUMENT": 10
                }
        except Exception as e:
            logger.error(f"Error getting document statistics: {e}")
            # Use mock data if query fails
            document_data = {
                "APPRAISAL_REPORT": 45,
                "PROPERTY_RECORD": 30,
                "MARKET_ANALYSIS": 15,
                "TAX_DOCUMENT": 10
            }
        
        # Add document data to stats
        stats["document_data"] = document_data
        
        return templates.TemplateResponse(
            "admin/dashboard.html",
            {"request": request, "active_page": "dashboard", "stats": stats}
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        # Return a simplified dashboard with error message
        return templates.TemplateResponse(
            "admin/dashboard.html",
            {
                "request": request, 
                "active_page": "dashboard",
                "error": f"Error loading dashboard data: {str(e)}",
                "stats": {
                    "total_clients": 0,
                    "total_clients_change": 0,
                    "total_appraisals": 0,
                    "active_projects": 0,
                    "pending_requests": 0,
                    "website_visits": 0,
                    "website_visits_change": 0,
                    "total_reports": 0,
                    "total_reports_change": 0,
                    "monthly_revenue": 0,
                    "monthly_revenue_change": 0,
                    "recent_activities": [],
                    "document_data": {}
                }
            }
        )

@router.get("/admin/file-explorer", response_class=HTMLResponse)
async def admin_file_explorer(request: Request, db: Session = Depends(get_db)):
    """
    Render the admin file explorer.
    """
    # In a real application, you would check authentication here
    
    return templates.TemplateResponse(
        "admin/file_explorer.html",
        {"request": request, "active_page": "file-explorer"}
    )

@router.get("/admin/clients", response_class=HTMLResponse)
async def admin_clients(request: Request, db: Session = Depends(get_db)):
    """
    Render the admin clients page.
    """
    # In a real application, you would check authentication here
    
    # Import necessary models
    from app.models.client import Client
    from app.models.project import Project
    
    # Get all clients from the database
    clients = db.query(Client).all()
    
    # Get project counts for each client
    client_data = []
    for client in clients:
        project_count = db.query(Project).filter(Project.client_id == client.id).count()
        client_data.append({
            "id": client.id,
            "name": client.name,
            "company": client.company or "",
            "email": client.email,
            "phone": client.phone or "",
            "project_count": project_count
        })
    
    return templates.TemplateResponse(
        "admin/clients.html",
        {"request": request, "active_page": "clients", "clients": client_data}
    )

@router.post("/admin/clients/add", response_class=RedirectResponse)
async def add_client(
    request: Request, 
    name: str = Form(...),
    company: str = Form(None),
    email: str = Form(...),
    phone: str = Form(None),
    address: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Add a new client to the database.
    """
    # Import necessary models
    from app.models.client import Client
    
    # Create a new client
    new_client = Client(
        name=name,
        company=company,
        email=email,
        phone=phone,
        address=address
    )
    
    # Add to database
    db.add(new_client)
    db.commit()
    
    return RedirectResponse(url="/admin/clients", status_code=303)

@router.get("/admin/clients/{client_id}", response_class=HTMLResponse)
async def view_client(request: Request, client_id: int, db: Session = Depends(get_db)):
    """
    View a specific client's details.
    """
    # Import necessary models
    from app.models.client import Client
    from app.models.project import Project
    
    # Get the client
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get the client's projects
    projects = db.query(Project).filter(Project.client_id == client_id).all()
    
    # Format project data
    project_data = []
    for project in projects:
        project_data.append({
            "id": project.id,
            "title": project.title,
            "status": project.status,
            "created_at": project.created_at.strftime("%b %d, %Y") if project.created_at else "Not set",
            "due_date": "Not set"  # The Project model doesn't have a due_date field
        })
    
    return templates.TemplateResponse(
        "admin/client_detail.html",
        {
            "request": request, 
            "active_page": "clients",
            "client": client,
            "projects": project_data
        }
    )

@router.get("/admin/appraisals", response_class=HTMLResponse)
async def admin_appraisals(request: Request, db: Session = Depends(get_db)):
    """
    Render the admin appraisals page.
    """
    try:
        # Import the necessary models
        from app.models.client import Client
        from app.models.property import Property
        from app.models.project import Project, ProjectStatus
        
        # Get appraisals data with error handling
        try:
            # Get projects without joins first to avoid join errors
            projects = db.query(Project).all()
            
            # Process the projects to create a list of appraisals
            appraisals = []
            for project in projects:
                try:
                    # Get client name if available
                    client_name = "Unknown Client"
                    try:
                        if hasattr(project, 'client_id') and project.client_id:
                            client = db.query(Client).filter(Client.id == project.client_id).first()
                            if client and hasattr(client, 'name'):
                                client_name = client.name
                    except Exception as e:
                        logger.error(f"Error getting client for project {project.id}: {e}")
                    
                    # Get property address if available
                    property_address = "Unknown Property"
                    try:
                        if hasattr(project, 'property_id') and project.property_id:
                            property_obj = db.query(Property).filter(Property.id == project.property_id).first()
                            if property_obj:
                                property_address = getattr(property_obj, "address", "Unknown Address")
                                if hasattr(property_obj, "city"):
                                    property_address += f", {property_obj.city}"
                    except Exception as e:
                        logger.error(f"Error getting property for project {project.id}: {e}")
                    
                    # Format the status for display
                    status_display = "Unknown"
                    if hasattr(project, "status"):
                        if hasattr(project.status, "value"):
                            status_display = project.status.value
                        else:
                            status_display = str(project.status)
                    
                    # Format the date
                    date_display = "Unknown"
                    if hasattr(project, "created_at") and project.created_at:
                        date_display = project.created_at.strftime("%Y-%m-%d")
                    
                    # Format the value
                    value_display = "Not Estimated"
                    if hasattr(project, "estimated_value") and project.estimated_value:
                        value_display = f"${project.estimated_value:,.2f}"
                    
                    # Create appraisal entry
                    appraisal = {
                        "id": project.id,
                        "title": getattr(project, "title", "Untitled Project"),
                        "client": client_name,
                        "property": property_address,
                        "status": status_display,
                        "date": date_display,
                        "value": value_display
                    }
                    appraisals.append(appraisal)
                except Exception as e:
                    logger.error(f"Error processing project {project.id}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            # Use mock data if database query fails
            appraisals = [
                {"id": 1, "title": "Commercial Property Appraisal", "client": "ABC Corp", "property": "123 Main St", "status": "in_progress", "date": "2025-03-28", "value": "$750,000.00"},
                {"id": 2, "title": "Residential Valuation", "client": "John Smith", "property": "456 Oak Ave", "status": "completed", "date": "2025-03-27", "value": "$350,000.00"},
                {"id": 3, "title": "Market Analysis Report", "client": "XYZ Investments", "property": "789 Market Blvd", "status": "review", "date": "2025-03-26", "value": "$1,200,000.00"},
                {"id": 4, "title": "Property Development Assessment", "client": "123 Properties", "property": "101 Development Rd", "status": "draft", "date": "2025-03-25", "value": "Not Estimated"}
            ]
        
        return templates.TemplateResponse(
            "admin/appraisals.html",
            {
                "request": request,
                "appraisals": appraisals,
                "active_page": "appraisals"
            }
        )
    except Exception as e:
        logger.error(f"Error rendering appraisals page: {e}")
        # Return a simplified appraisals page with error message
        return templates.TemplateResponse(
            "admin/appraisals.html",
            {
                "request": request,
                "error": f"Error loading appraisals data: {str(e)}",
                "appraisals": [
                    {"id": 1, "title": "Commercial Property Appraisal", "client": "ABC Corp", "property": "123 Main St", "status": "in_progress", "date": "2025-03-28", "value": "$750,000.00"},
                    {"id": 2, "title": "Residential Valuation", "client": "John Smith", "property": "456 Oak Ave", "status": "completed", "date": "2025-03-27", "value": "$350,000.00"},
                    {"id": 3, "title": "Market Analysis Report", "client": "XYZ Investments", "property": "789 Market Blvd", "status": "review", "date": "2025-03-26", "value": "$1,200,000.00"},
                    {"id": 4, "title": "Property Development Assessment", "client": "123 Properties", "property": "101 Development Rd", "status": "draft", "date": "2025-03-25", "value": "Not Estimated"}
                ],
                "active_page": "appraisals"
            }
        )

@router.get("/admin/appraisals/{project_id}", response_class=HTMLResponse)
async def view_project(request: Request, project_id: int, db: Session = Depends(get_db)):
    """
    View a specific appraisal project.
    """
    try:
        # Import the necessary models
        from app.models.project import Project
        from app.models.client import Client
        from app.models.property import Property
        
        try:
            # Get the project without joins first
            project = db.query(Project).filter(Project.id == project_id).first()
            
            if not project:
                return templates.TemplateResponse(
                    "admin/error.html",
                    {"request": request, "error": f"Project with ID {project_id} not found", "active_page": "appraisals"}
                )
            
            # Process the project to create a detailed view
            try:
                # Get client information if available
                client_info = {
                    "name": "Unknown Client",
                    "email": "unknown@example.com",
                    "phone": "N/A"
                }
                
                try:
                    if hasattr(project, 'client_id') and project.client_id:
                        client = db.query(Client).filter(Client.id == project.client_id).first()
                        if client:
                            client_info = {
                                "name": getattr(client, "name", "Unknown Client"),
                                "email": getattr(client, "email", "unknown@example.com"),
                                "phone": getattr(client, "phone", "N/A")
                            }
                except Exception as e:
                    logger.error(f"Error getting client for project {project_id}: {e}")
                
                # Get property information if available
                property_info = {
                    "address": "Unknown Address",
                    "city": "Unknown City",
                    "state": "Unknown State",
                    "zip_code": "Unknown Zip",
                    "property_type": "Unknown Type"
                }
                
                try:
                    if hasattr(project, 'property_id') and project.property_id:
                        property_obj = db.query(Property).filter(Property.id == project.property_id).first()
                        if property_obj:
                            property_info = {
                                "address": getattr(property_obj, "address", "Unknown Address"),
                                "city": getattr(property_obj, "city", "Unknown City"),
                                "state": getattr(property_obj, "state", "Unknown State"),
                                "zip_code": getattr(property_obj, "zip_code", "Unknown Zip"),
                                "property_type": getattr(property_obj, "property_type", "Unknown Type")
                            }
                except Exception as e:
                    logger.error(f"Error getting property for project {project_id}: {e}")
                
                # Format the status for display
                status_display = "Unknown"
                if hasattr(project, "status"):
                    if hasattr(project.status, "value"):
                        status_display = project.status.value
                    else:
                        status_display = str(project.status)
                
                # Format the date
                date_display = "Unknown"
                if hasattr(project, "created_at") and project.created_at:
                    date_display = project.created_at.strftime("%Y-%m-%d")
                
                # Format the value
                value_display = "Not Estimated"
                if hasattr(project, "estimated_value") and project.estimated_value:
                    value_display = f"${project.estimated_value:,.2f}"
                
                # Create the project details
                project_details = {
                    "id": project.id,
                    "title": getattr(project, "title", "Untitled Project"),
                    "description": getattr(project, "description", "No description available"),
                    "status": status_display,
                    "date": date_display,
                    "value": value_display,
                    "client": client_info,
                    "property": property_info
                }
                
                return templates.TemplateResponse(
                    "admin/view_project.html",
                    {
                        "request": request,
                        "project": project_details,
                        "active_page": "appraisals"
                    }
                )
            except Exception as e:
                logger.error(f"Error processing project {project_id}: {e}")
                return templates.TemplateResponse(
                    "admin/error.html",
                    {"request": request, "error": f"Error processing project: {str(e)}", "active_page": "appraisals"}
                )
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {e}")
            return templates.TemplateResponse(
                "admin/error.html",
                {"request": request, "error": f"Error retrieving project: {str(e)}", "active_page": "appraisals"}
            )
    except Exception as e:
        logger.error(f"Error in view_project: {e}")
        return templates.TemplateResponse(
            "admin/error.html",
            {"request": request, "error": f"An unexpected error occurred: {str(e)}", "active_page": "appraisals"}
        )

@router.get("/admin/appraisals/{project_id}/edit", response_class=HTMLResponse)
async def edit_project_form(request: Request, project_id: int, db: Session = Depends(get_db)):
    """
    Render the edit project form.
    """
    try:
        # Import necessary models
        from app.models.project import Project, ProjectStatus
        from app.models.client import Client
        from app.models.property import Property
        
        # Get the project without joins to avoid potential schema issues
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get all clients for the dropdown
        try:
            clients = db.query(Client).all()
        except Exception as e:
            logger.error(f"Error getting clients: {e}")
            clients = []
        
        return templates.TemplateResponse(
            "admin/edit_project.html",
            {
                "request": request, 
                "active_page": "appraisals", 
                "project": project,
                "clients": clients,
                "ProjectStatus": ProjectStatus
            }
        )
    except Exception as e:
        logger.error(f"Error rendering edit project form: {e}")
        return templates.TemplateResponse(
            "admin/error.html",
            {"request": request, "error": f"Error loading edit form: {str(e)}", "active_page": "appraisals"}
        )

@router.post("/admin/appraisals/{project_id}/edit", response_class=HTMLResponse)
async def edit_project(
    request: Request, 
    project_id: int, 
    title: str = Form(...),
    description: str = Form(None),
    status: str = Form(...),
    client_id: int = Form(...),
    estimated_value: float = Form(None),
    db: Session = Depends(get_db)
):
    """
    Update a project.
    """
    try:
        # Import necessary models
        from app.models.project import Project, ProjectStatus
        
        # Get the project
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update the project with error handling for each field
        try:
            project.title = title
        except Exception as e:
            logger.error(f"Error updating title: {e}")
        
        try:
            project.description = description
        except Exception as e:
            logger.error(f"Error updating description: {e}")
        
        try:
            # Handle status as string or enum
            if hasattr(ProjectStatus, status):
                project.status = getattr(ProjectStatus, status)
            else:
                project.status = status
        except Exception as e:
            logger.error(f"Error updating status: {e}")
        
        try:
            project.client_id = client_id
        except Exception as e:
            logger.error(f"Error updating client_id: {e}")
        
        try:
            project.estimated_value = estimated_value
        except Exception as e:
            logger.error(f"Error updating estimated_value: {e}")
        
        # Save the changes
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error committing changes: {e}")
            return templates.TemplateResponse(
                "admin/error.html",
                {"request": request, "error": f"Error saving changes: {str(e)}", "active_page": "appraisals"}
            )
        
        # Redirect to the project view
        return RedirectResponse(url=f"/admin/appraisals/{project_id}", status_code=303)
    except Exception as e:
        logger.error(f"Error in edit_project: {e}")
        return templates.TemplateResponse(
            "admin/error.html",
            {"request": request, "error": f"An unexpected error occurred: {str(e)}", "active_page": "appraisals"}
        )

@router.get("/admin/appraisals/{project_id}/pdf", response_class=HTMLResponse)
async def generate_project_pdf(request: Request, project_id: int, db: Session = Depends(get_db)):
    """
    Generate a PDF report for a project.
    """
    # In a real application, you would check authentication here
    
    # Import necessary models
    from app.models.project import Project
    from app.models.client import Client
    from app.models.property import Property
    
    # Get the project with client and property information
    project = db.query(Project).filter(Project.id == project_id).join(Client).join(Property).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # For now, we'll just render a template that shows the PDF would be generated
    # In a real application, you would generate a PDF file here
    
    # Get current date for the template
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    current_year = datetime.datetime.now().year
    
    return templates.TemplateResponse(
        "admin/pdf_preview.html",
        {
            "request": request, 
            "active_page": "appraisals", 
            "project": project,
            "current_date": current_date,
            "current_year": current_year
        }
    )

@router.get("/admin/ai-agent", response_class=HTMLResponse)
async def admin_ai_agent(request: Request, db: Session = Depends(get_db)):
    """
    Render the admin AI agent page.
    """
    # In a real application, you would check authentication here
    
    return templates.TemplateResponse(
        "admin/ai_agent.html",
        {"request": request, "active_page": "ai-agent"}
    )

@router.get("/admin/agent-chat", response_class=HTMLResponse)
async def admin_agent_chat(
    request: Request,
    chat_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Render the admin agent chat interface.
    """
    # In a real application, you would check authentication here
    
    # If no chat_id is provided, create a new one
    if not chat_id:
        # Create a new chat via the API
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{request.base_url}api/v1/admin/agent/new-chat")
            if response.status_code == 200:
                new_chat = response.json()
                chat_id = new_chat["id"]
                return RedirectResponse(url=f"/admin/agent-chat?chat_id={chat_id}", status_code=303)
    
    # Get chat history
    chat_history = []
    messages = []
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Get chat history via the API
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{request.base_url}api/v1/admin/agent/chats")
            if response.status_code == 200:
                chat_history = response.json().get("chats", [])
            
            # If chat_id is provided, get the messages for that chat
            if chat_id:
                response = await client.get(f"{request.base_url}api/v1/admin/agent/chat/{chat_id}")
                if response.status_code == 200:
                    chat_data = response.json()
                    messages = chat_data.get("messages", [])
    except Exception as e:
        logger.error(f"Error getting chat data: {str(e)}")
    
    # Log the website usage
    try:
        website_usage = WebsiteUsage(
            page="admin_agent_chat",
            user_agent=request.headers.get("user-agent", ""),
            ip_address=request.client.host,
            referrer=request.headers.get("referer", ""),
            query_params=str(request.query_params)
        )
        db.add(website_usage)
        db.commit()
    except Exception as e:
        logger.error(f"Error logging website usage: {str(e)}")
    
    return templates.TemplateResponse(
        "admin/agent_chat.html",
        {
            "request": request, 
            "active_page": "agent-chat", 
            "chat_id": chat_id,
            "chat_history": chat_history,
            "messages": messages,
            "current_time": current_time
        }
    )

@router.get("/admin/rag-database", response_class=HTMLResponse)
async def admin_rag_database(request: Request, db: Session = Depends(get_db)):
    """
    Render the admin RAG database page.
    """
    # In a real application, you would check authentication here
    
    # Get RAG database statistics
    rag_service = RAGService(db)
    stats = rag_service.get_usage_statistics()
    
    # Get document types
    document_types = db.query(Document.document_type).distinct().all()
    document_types = [doc_type[0] for doc_type in document_types]
    
    return templates.TemplateResponse(
        "admin/rag_database.html",
        {
            "request": request,
            "active_page": "rag-database",
            "stats": stats,
            "document_types": document_types
        }
    )

@router.get("/admin/analytics", response_class=HTMLResponse)
async def admin_analytics(request: Request, db: Session = Depends(get_db)):
    """
    Render the admin analytics page.
    """
    try:
        # Import the necessary models
        from app.models.client import Client
        from app.models.property import Property
        from app.models.project import Project, ProjectStatus
        from sqlalchemy import func, extract, cast, Integer
        import datetime
        import random
        
        # Get analytics data with error handling
        try:
            total_appraisals = db.query(Project).count()
        except Exception as e:
            logger.error(f"Error getting appraisal count: {e}")
            total_appraisals = 0
            
        try:
            total_clients = db.query(Client).count()
        except Exception as e:
            logger.error(f"Error getting client count: {e}")
            total_clients = 0
            
        try:
            total_properties = db.query(Property).count()
        except Exception as e:
            logger.error(f"Error getting property count: {e}")
            total_properties = 0
        
        # Get real monthly data for the past 12 months
        current_date = datetime.datetime.now()
        start_date = current_date - datetime.timedelta(days=365)
        
        # Initialize data arrays with zeros
        months = []
        appraisal_data = [0] * 12
        revenue_data = [0] * 12
        client_data = [0] * 12
        
        # Generate month labels
        for i in range(12):
            month_date = current_date - datetime.timedelta(days=30 * (11 - i))
            months.append(month_date.strftime("%b"))
        
        try:
            # Get monthly appraisal counts with safer query
            try:
                monthly_appraisals = db.query(
                    extract('month', Project.created_at).label('month'),
                    extract('year', Project.created_at).label('year'),
                    func.count(Project.id).label('count')
                ).filter(
                    Project.created_at >= start_date
                ).group_by(
                    extract('year', Project.created_at),
                    extract('month', Project.created_at)
                ).all()
                
                # Map the results to our data array
                for month_num, year, count in monthly_appraisals:
                    # Convert to integers to avoid type issues
                    try:
                        month_num = int(month_num)
                        current_month = int(current_date.month)
                        month_index = (month_num - current_month) % 12
                        if month_index < 12:  # Only include last 12 months
                            appraisal_data[month_index] = int(count)
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error processing month data: {e}")
            except Exception as e:
                logger.error(f"Error in monthly appraisal query: {e}")
        except Exception as e:
            logger.error(f"Error getting monthly appraisal data: {e}")
        
        try:
            # Get monthly revenue (sum of estimated values) with safer query
            try:
                monthly_revenue = db.query(
                    extract('month', Project.created_at).label('month'),
                    extract('year', Project.created_at).label('year'),
                    func.sum(Project.estimated_value).label('revenue')
                ).filter(
                    Project.created_at >= start_date
                ).group_by(
                    extract('year', Project.created_at),
                    extract('month', Project.created_at)
                ).all()
                
                # Map the results to our data array
                for month_num, year, revenue in monthly_revenue:
                    try:
                        month_num = int(month_num)
                        current_month = int(current_date.month)
                        month_index = (month_num - current_month) % 12
                        if month_index < 12:  # Only include last 12 months
                            revenue_data[month_index] = int(revenue or 0)
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error processing revenue data: {e}")
            except Exception as e:
                logger.error(f"Error in monthly revenue query: {e}")
        except Exception as e:
            logger.error(f"Error getting monthly revenue data: {e}")
        
        try:
            # Get monthly new client counts with safer query
            try:
                monthly_clients = db.query(
                    extract('month', Client.created_at).label('month'),
                    extract('year', Client.created_at).label('year'),
                    func.count(Client.id).label('count')
                ).filter(
                    Client.created_at >= start_date
                ).group_by(
                    extract('year', Client.created_at),
                    extract('month', Client.created_at)
                ).all()
                
                # Map the results to our data array
                for month_num, year, count in monthly_clients:
                    try:
                        month_num = int(month_num)
                        current_month = int(current_date.month)
                        month_index = (month_num - current_month) % 12
                        if month_index < 12:  # Only include last 12 months
                            client_data[month_index] = int(count)
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error processing client data: {e}")
            except Exception as e:
                logger.error(f"Error in monthly client query: {e}")
        except Exception as e:
            logger.error(f"Error getting monthly client data: {e}")
            
        # If we have no data, generate some mock data to show the charts
        if sum(appraisal_data) == 0:
            appraisal_data = [random.randint(5, 30) for _ in range(12)]
        
        if sum(revenue_data) == 0:
            revenue_data = [random.randint(5000, 20000) for _ in range(12)]
            
        if sum(client_data) == 0:
            client_data = [random.randint(1, 10) for _ in range(12)]
        
        # Prepare the data for the template
        analytics = {
            "total_appraisals": total_appraisals,
            "total_clients": total_clients,
            "total_properties": total_properties,
            "chart_data": {
                "months": months,
                "appraisals": appraisal_data,
                "revenue": revenue_data,
                "clients": client_data
            }
        }
        
        return templates.TemplateResponse(
            "admin/analytics.html",
            {
                "request": request,
                "analytics": analytics,
                "active_page": "analytics"
            }
        )
    except Exception as e:
        logger.error(f"Error rendering analytics page: {e}")
        # Return a simplified analytics page with error message
        return templates.TemplateResponse(
            "admin/analytics.html",
            {
                "request": request,
                "error": f"Error loading analytics data: {str(e)}",
                "analytics": {
                    "total_appraisals": 0,
                    "total_clients": 0,
                    "total_properties": 0,
                    "chart_data": {
                        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                        "appraisals": [0] * 12,
                        "revenue": [0] * 12,
                        "clients": [0] * 12
                    }
                },
                "active_page": "analytics"
            }
        )

@router.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, db: Session = Depends(get_db)):
    """
    Render the admin settings page.
    """
    # In a real application, you would check authentication here
    
    return templates.TemplateResponse(
        "admin/settings.html",
        {"request": request, "active_page": "settings"}
    )

@router.get("/admin/logout", response_class=HTMLResponse)
async def admin_logout(request: Request):
    """
    Log out the admin user and redirect to the login page.
    """
    # In a real application, you would handle logout logic here
    return RedirectResponse(url="/admin/login")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Render the login page.
    """
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request}
    )

@router.post("/login", response_class=RedirectResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Process login form submission.
    """
    # Default admin credentials for initial setup
    default_admin_email = "admin@appraisalai.com"
    default_admin_password = "Admin123!"
    
    # Check if using default admin credentials
    if username == default_admin_email and password == default_admin_password:
        # Set session cookie or token (simplified for now)
        response = RedirectResponse(url="/admin", status_code=303)
        return response
    
    # Try database login only if default credentials don't match
    try:
        # Check if the user exists
        user = db.query(User).filter(User.email == username).first()
        
        # Check password if user exists
        if user and verify_password(password, user.hashed_password):
            response = RedirectResponse(url="/admin", status_code=303)
            return response
    except Exception as e:
        logger.error(f"Error during database login: {e}")
    
    # If authentication fails, redirect back to login with error
    return templates.TemplateResponse(
        "admin/login.html", 
        {"request": request, "error": "Invalid username or password"}
    )

@router.get("/admin/api/clients", response_class=JSONResponse)
async def api_get_clients(request: Request, db: Session = Depends(get_db)):
    """
    API endpoint to get all clients for dropdown menus.
    """
    # Import necessary models
    from app.models.client import Client
    
    # Get all clients from the database
    clients = db.query(Client).all()
    
    # Format client data for the API response
    client_data = []
    for client in clients:
        client_data.append({
            "id": client.id,
            "name": client.name,
            "company": client.company or ""
        })
    
    return client_data

@router.get("/services/{service_name}", response_class=HTMLResponse)
async def service_page(request: Request, service_name: str, db: Session = Depends(get_db)):
    """
    Render a service page.
    """
    # Log website visit
    usage = WebsiteUsage(
        page_visited=f"service_{service_name}",
        session_id=request.cookies.get("session_id", "unknown"),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "unknown")
    )
    
    db.add(usage)
    db.commit()
    
    # Map service_name to template
    service_templates = {
        "residential": "services/residential.html",
        "commercial": "services/commercial.html",
        "consultation": "services/consultation.html",
        "valuation": "services/valuation.html"
    }
    
    if service_name not in service_templates:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return templates.TemplateResponse(
        service_templates[service_name],
        {"request": request, "service_name": service_name}
    )

@router.get("/about", response_class=HTMLResponse)
async def about_page(request: Request, db: Session = Depends(get_db)):
    """
    Render the about page.
    """
    # Log website visit
    usage = WebsiteUsage(
        page_visited="about",
        session_id=request.cookies.get("session_id", "unknown"),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "unknown")
    )
    
    db.add(usage)
    db.commit()
    
    return templates.TemplateResponse(
        "about.html",
        {"request": request}
    )

@router.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request, db: Session = Depends(get_db)):
    """
    Render the contact page.
    """
    # Log website visit
    usage = WebsiteUsage(
        page_visited="contact",
        session_id=request.cookies.get("session_id", "unknown"),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", "unknown")
    )
    
    db.add(usage)
    db.commit()
    
    return templates.TemplateResponse(
        "contact.html",
        {"request": request}
    )

"""
Web controllers for the Apeko website.
"""
from fastapi import APIRouter, Request, Depends, HTTPException, Form, File, UploadFile, Query, Path
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
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
    # In a real application, you would check authentication here
    
    try:
        # Get real stats from the database
        client_count = db.query(User).filter(User.role == UserRole.CLIENT).count()
        
        # Import the necessary models
        from app.models.client import Client
        from app.models.property import Property
        from app.models.project import Project, ProjectStatus
        
        # Get actual counts from database with error handling
        try:
            total_clients = db.query(Client).count()
        except Exception as e:
            logger.error(f"Error getting client count: {e}")
            total_clients = 0
            
        try:
            total_appraisals = db.query(Project).count()
        except Exception as e:
            logger.error(f"Error getting project count: {e}")
            total_appraisals = 0
            
        try:
            active_projects = db.query(Project).filter(Project.status == ProjectStatus.IN_PROGRESS).count()
        except Exception as e:
            logger.error(f"Error getting active projects count: {e}")
            active_projects = 0
            
        try:
            pending_requests = db.query(Project).filter(Project.status == ProjectStatus.DRAFT).count()
        except Exception as e:
            logger.error(f"Error getting pending requests count: {e}")
            pending_requests = 0
        
        # Prepare stats dictionary for the template
        stats = {
            "total_clients": total_clients,
            "total_clients_change": 5,  # Mock change percentage
            "total_appraisals": total_appraisals,
            "active_projects": active_projects,
            "pending_requests": pending_requests,
            "website_visits": 1250,  # Mock value
            "website_visits_change": 8,  # Mock change percentage
            "total_reports": total_appraisals,
            "total_reports_change": 5,  # Mock change percentage
            "monthly_revenue": 15000,  # Mock value
            "monthly_revenue_change": 15,  # Mock change percentage
        }
        
        # Use mock data for recent activities if database query fails
        try:
            # Get recent activities
            recent_projects = db.query(Project).order_by(Project.created_at.desc()).limit(4).all()
            
            recent_activities = []
            for project in recent_projects:
                client = db.query(Client).filter(Client.id == project.client_id).first()
                client_name = client.name if client else "Unknown Client"
                
                recent_activities.append({
                    "id": project.id,
                    "title": getattr(project, "title", "Untitled Project"),
                    "client": client_name,
                    "date": project.created_at.strftime("%Y-%m-%d"),
                    "status": project.status.value if hasattr(project.status, "value") else str(project.status)
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
        
        # Get RAG statistics
        try:
            # Get document counts by type
            document_counts = db.query(
                Document.document_type, 
                db.func.count(Document.id).label('count')
            ).group_by(Document.document_type).all()
            
            rag_stats = {doc_type: count for doc_type, count in document_counts}
            
            # Get total documents
            total_documents = db.query(Document).count()
            
            # Get website usage stats
            website_stats = db.query(WebsiteUsage).order_by(WebsiteUsage.timestamp.desc()).limit(30).all()
            
            # Format data for charts
            website_data = {
                "labels": [stat.timestamp.strftime("%m-%d") for stat in website_stats],
                "visits": [stat.visit_count for stat in website_stats]
            }
            
            document_data = {
                "labels": list(rag_stats.keys()),
                "counts": list(rag_stats.values())
            }
        except Exception as e:
            logger.error(f"Error getting RAG statistics: {e}")
            # Mock data for RAG statistics
            total_documents = 120
            rag_stats = {
                "appraisal_report": 45,
                "market_analysis": 30,
                "property_listing": 25,
                "legal_document": 20
            }
            
            website_data = {
                "labels": [f"03-{day:02d}" for day in range(1, 31)],
                "visits": [random.randint(10, 50) for _ in range(30)]
            }
            
            document_data = {
                "labels": list(rag_stats.keys()),
                "counts": list(rag_stats.values())
            }
        
        # Add RAG stats to the template context
        rag_stats_data = {
            "total_documents": total_documents,
            "total_chunks": 450,  # Mock value
            "total_queries": 250,  # Mock value
            "document_type_distribution": rag_stats
        }
        
        # Render the dashboard template with all the data
        return templates.TemplateResponse(
            "admin/dashboard.html",
            {
                "request": request,
                "stats": stats,
                "rag_stats": rag_stats_data,
                "website_data": website_data,
                "document_data": document_data,
                "active_page": "dashboard"
            }
        )
    except Exception as e:
        logger.error(f"Error rendering admin dashboard: {e}")
        # Return a simplified dashboard with error message
        return templates.TemplateResponse(
            "admin/dashboard.html",
            {
                "request": request,
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
                    "recent_activities": []
                },
                "rag_stats": {
                    "total_documents": 0,
                    "total_chunks": 0,
                    "total_queries": 0,
                    "document_type_distribution": {}
                },
                "website_data": {"labels": [], "visits": []},
                "document_data": {"labels": [], "counts": []},
                "active_page": "dashboard"
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
    # In a real application, you would check authentication here
    
    # Import necessary models
    from app.models.project import Project, ProjectStatus
    from app.models.client import Client
    from app.models.property import Property
    
    # Get all projects with client and property information
    projects = db.query(Project).join(Client).join(Property).all()
    
    # Format project data for the template
    project_data = []
    for project in projects:
        project_data.append({
            "id": project.id,
            "title": project.title,
            "property_address": f"{project.property.address}, {project.property.city}",
            "client_name": project.client.name,
            "property_type": project.property.property_type,
            "status": project.status,
            "created_date": project.created_at.strftime("%b %d, %Y") if project.created_at else "Not set",
            "due_date": "Not set"  # The Project model doesn't have a due_date field
        })
    
    return templates.TemplateResponse(
        "admin/appraisals.html",
        {"request": request, "active_page": "appraisals", "projects": project_data, "ProjectStatus": ProjectStatus}
    )

@router.get("/admin/appraisals/{project_id}", response_class=HTMLResponse)
async def view_project(request: Request, project_id: int, db: Session = Depends(get_db)):
    """
    View a specific project/appraisal.
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
    
    # Format project data for the template
    project_data = {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "created_at": project.created_at.strftime("%b %d, %Y") if project.created_at else "Not set",
        "client": {
            "id": project.client.id,
            "name": project.client.name,
            "email": project.client.email,
            "phone": project.client.phone
        },
        "property": {
            "id": project.property.id,
            "address": project.property.address,
            "city": project.property.city,
            "state": project.property.state,
            "zip_code": project.property.zip_code,
            "property_type": project.property.property_type
        },
        "estimated_value": project.estimated_value
    }
    
    return templates.TemplateResponse(
        "admin/project_detail.html",
        {"request": request, "active_page": "appraisals", "project": project_data}
    )

@router.get("/admin/appraisals/{project_id}/edit", response_class=HTMLResponse)
async def edit_project_form(request: Request, project_id: int, db: Session = Depends(get_db)):
    """
    Render the edit project form.
    """
    # In a real application, you would check authentication here
    
    # Import necessary models
    from app.models.project import Project, ProjectStatus
    from app.models.client import Client
    from app.models.property import Property
    
    # Get the project with client and property information
    project = db.query(Project).filter(Project.id == project_id).join(Client).join(Property).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all clients for the dropdown
    clients = db.query(Client).all()
    
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
    # In a real application, you would check authentication here
    
    # Import necessary models
    from app.models.project import Project, ProjectStatus
    
    # Get the project
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update project fields
    project.title = title
    project.description = description
    project.status = ProjectStatus[status]
    project.client_id = client_id
    project.estimated_value = estimated_value
    
    # Save changes
    db.commit()
    
    # Redirect to project detail page
    return RedirectResponse(url=f"/admin/appraisals/{project_id}", status_code=303)

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
    # In a real application, you would check authentication here
    
    # Import necessary models
    from app.models.client import Client
    from app.models.property import Property
    from app.models.project import Project, ProjectStatus
    from app.models.report import Report
    from sqlalchemy import func
    import datetime
    
    # Get real analytics data
    # Total appraisals
    total_appraisals = db.query(Project).count()
    
    # Total property value
    total_property_value = db.query(func.sum(Project.estimated_value)).scalar() or 0
    
    # Average days to complete
    completed_projects = db.query(Project).filter(Project.status == ProjectStatus.COMPLETED).all()
    if completed_projects:
        total_days = 0
        for project in completed_projects:
            if project.created_at and project.updated_at:
                days = (project.updated_at - project.created_at).days
                total_days += days
        avg_days = total_days / len(completed_projects) if len(completed_projects) > 0 else 0
    else:
        avg_days = 0
    
    # Get property types distribution
    property_types = db.query(
        Property.property_type, 
        func.count(Property.id)
    ).group_by(Property.property_type).all()
    
    property_type_distribution = {}
    for prop_type, count in property_types:
        property_type_distribution[prop_type] = count
    
    # Get monthly appraisal requests (last 6 months)
    today = datetime.datetime.now()
    six_months_ago = today - datetime.timedelta(days=180)
    
    monthly_requests = db.query(
        func.strftime('%Y-%m', Project.created_at).label('month'),
        func.count(Project.id)
    ).filter(Project.created_at >= six_months_ago).group_by('month').all()
    
    monthly_data = {}
    for month, count in monthly_requests:
        if month:
            monthly_data[month] = count
    
    # Get average property value by location
    property_values_by_location = db.query(
        Property.city,
        func.avg(Project.estimated_value)
    ).join(Project, Project.property_id == Property.id).group_by(Property.city).all()
    
    location_values = {}
    for city, avg_value in property_values_by_location:
        if city and avg_value:
            location_values[city] = avg_value
    
    # Completion time trends
    completion_time_trend = db.query(
        func.strftime('%Y-%m', Project.created_at).label('month'),
        func.avg(func.julianday(Project.updated_at) - func.julianday(Project.created_at))
    ).filter(
        Project.status == ProjectStatus.COMPLETED,
        Project.created_at >= six_months_ago
    ).group_by('month').all()
    
    completion_trend = {}
    for month, avg_days in completion_time_trend:
        if month and avg_days:
            completion_trend[month] = avg_days
    
    analytics_data = {
        "total_appraisals": total_appraisals,
        "total_property_value": total_property_value,
        "avg_days_to_complete": avg_days,
        "client_satisfaction": 0,  # This would need a real survey/feedback system
        "property_type_distribution": property_type_distribution,
        "monthly_requests": monthly_data,
        "location_values": location_values,
        "completion_trend": completion_trend
    }
    
    return templates.TemplateResponse(
        "admin/analytics.html",
        {
            "request": request, 
            "active_page": "analytics",
            "analytics": analytics_data
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

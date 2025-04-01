"""
Website API endpoints for the Apeko website.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime

from app.db.session import get_db
from app.models.rag import WebsiteUsage
from app.models.user import User
from app.models.client import Client
from app.models.project import Project
from app.models.property import Property

router = APIRouter()

@router.post("/contact")
async def submit_contact_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    service: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Submit a contact form from the website.
    
    This endpoint processes contact form submissions from the website
    and creates a new client lead in the database.
    """
    try:
        # Create a new client lead
        client = Client(
            name=name,
            email=email,
            phone=phone,
            source="website_contact",
            status="lead",
            notes=f"Service Interest: {service}\nMessage: {message}"
        )
        
        db.add(client)
        db.commit()
        
        # Log website usage
        usage = WebsiteUsage(
            page_visited="contact_form",
            session_id=request.cookies.get("session_id", "unknown"),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown"),
            time_spent=None
        )
        
        db.add(usage)
        db.commit()
        
        return {"success": True, "message": "Thank you for your message. We will get back to you soon."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting contact form: {str(e)}")

@router.post("/subscribe")
async def subscribe_to_newsletter(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Subscribe to the newsletter.
    
    This endpoint processes newsletter subscription requests from the website.
    """
    try:
        # Check if email already exists
        existing_client = db.query(Client).filter(Client.email == email).first()
        
        if existing_client:
            # Update existing client
            existing_client.newsletter_subscription = True
            db.add(existing_client)
        else:
            # Create a new client
            client = Client(
                email=email,
                newsletter_subscription=True,
                source="website_newsletter",
                status="lead"
            )
            db.add(client)
        
        db.commit()
        
        # Log website usage
        usage = WebsiteUsage(
            page_visited="newsletter_subscription",
            session_id=request.cookies.get("session_id", "unknown"),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown"),
            time_spent=None
        )
        
        db.add(usage)
        db.commit()
        
        return {"success": True, "message": "Thank you for subscribing to our newsletter."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error subscribing to newsletter: {str(e)}")

@router.get("/stats")
async def get_website_stats(
    db: Session = Depends(get_db)
):
    """
    Get website statistics for the admin dashboard.
    
    This endpoint returns statistics about website usage, clients, and projects.
    """
    try:
        # Get total clients
        total_clients = db.query(Client).count()
        
        # Get website visits
        website_visits = db.query(WebsiteUsage).count()
        
        # Get total reports/projects
        total_reports = db.query(Project).count()
        
        # Get monthly revenue (placeholder for demo)
        monthly_revenue = 25000
        
        # Get recent activity
        recent_activity = []
        
        # Get website usage by page
        page_visits = db.query(
            WebsiteUsage.page_visited,
            db.func.count(WebsiteUsage.id).label("count")
        ).group_by(WebsiteUsage.page_visited).all()
        
        page_visit_data = {page: count for page, count in page_visits}
        
        # Get client acquisition by source
        client_sources = db.query(
            Client.source,
            db.func.count(Client.id).label("count")
        ).group_by(Client.source).all()
        
        client_source_data = {source: count for source, count in client_sources}
        
        # Get property types distribution
        property_types = db.query(
            Property.property_type,
            db.func.count(Property.id).label("count")
        ).group_by(Property.property_type).all()
        
        property_type_data = {prop_type: count for prop_type, count in property_types}
        
        return {
            "total_clients": total_clients,
            "website_visits": website_visits,
            "total_reports": total_reports,
            "monthly_revenue": monthly_revenue,
            "page_visits": page_visit_data,
            "client_sources": client_source_data,
            "property_types": property_type_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting website stats: {str(e)}")

@router.post("/track")
async def track_website_usage(
    request: Request,
    data: Dict[str, Any]
):
    """
    Track website usage.
    
    This endpoint tracks user behavior on the website for analytics.
    """
    try:
        db = next(get_db())
        
        # Create usage record
        usage = WebsiteUsage(
            page_visited=data.get("page", "unknown"),
            session_id=data.get("session_id", request.cookies.get("session_id", "unknown")),
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown"),
            time_spent=data.get("time_spent")
        )
        
        # If user is logged in, associate with user
        if "user_id" in data and data["user_id"]:
            usage.user_id = data["user_id"]
        
        db.add(usage)
        db.commit()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking website usage: {str(e)}")

"""
Client management endpoints for the Appraisal AI Agent.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uuid

router = APIRouter()

# Mock database for clients (in a real app, this would be a database)
CLIENTS_DB = {}

class ClientBase(BaseModel):
    """Base model for client data."""
    name: str
    type: str  # individual, bank, insurance, government, etc.
    contact_info: Dict[str, Any]
    notes: Optional[str] = None

class ClientCreate(ClientBase):
    """Model for creating a new client."""
    pass

class ClientUpdate(BaseModel):
    """Model for updating a client."""
    name: Optional[str] = None
    type: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class Client(ClientBase):
    """Full client model with ID and timestamps."""
    id: str
    created_at: datetime
    updated_at: datetime
    projects: Optional[List[str]] = []
    properties: Optional[List[str]] = []

@router.post("", response_model=Client)
async def create_client(client: ClientCreate):
    """
    Create a new client.
    """
    client_id = str(uuid.uuid4())
    now = datetime.now()
    
    new_client = {
        **client.dict(),
        "id": client_id,
        "created_at": now,
        "updated_at": now,
        "projects": [],
        "properties": []
    }
    
    CLIENTS_DB[client_id] = new_client
    return new_client

@router.get("", response_model=List[Client])
async def list_clients(
    client_type: Optional[str] = None,
    search: Optional[str] = None
):
    """
    List all clients with optional filtering.
    """
    clients = list(CLIENTS_DB.values())
    
    # Apply filters
    if client_type:
        clients = [c for c in clients if c["type"] == client_type]
    
    if search:
        search = search.lower()
        clients = [c for c in clients if search in c["name"].lower()]
    
    return clients

@router.get("/{client_id}", response_model=Client)
async def get_client(client_id: str):
    """
    Get a specific client by ID.
    """
    if client_id not in CLIENTS_DB:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return CLIENTS_DB[client_id]

@router.put("/{client_id}", response_model=Client)
async def update_client(client_id: str, client_update: ClientUpdate):
    """
    Update a client.
    """
    if client_id not in CLIENTS_DB:
        raise HTTPException(status_code=404, detail="Client not found")
    
    current_client = CLIENTS_DB[client_id]
    
    # Update fields that are provided
    update_data = client_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "contact_info" and isinstance(value, dict) and "contact_info" in current_client:
            # Merge contact info
            current_client["contact_info"].update(value)
        else:
            current_client[field] = value
    
    # Update the updated_at timestamp
    current_client["updated_at"] = datetime.now()
    
    CLIENTS_DB[client_id] = current_client
    return current_client

@router.delete("/{client_id}")
async def delete_client(client_id: str):
    """
    Delete a client.
    """
    if client_id not in CLIENTS_DB:
        raise HTTPException(status_code=404, detail="Client not found")
    
    del CLIENTS_DB[client_id]
    return {"message": "Client deleted successfully"}

@router.get("/{client_id}/projects")
async def get_client_projects(client_id: str):
    """
    Get all projects for a client.
    """
    if client_id not in CLIENTS_DB:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # In a real implementation, this would query the projects database
    # For demo purposes, we'll return projects from the mock projects database
    from app.api.v1.projects import PROJECTS_DB
    
    client_projects = [
        project for project in PROJECTS_DB.values()
        if project.get("client_id") == client_id
    ]
    
    # Update client's projects list
    CLIENTS_DB[client_id]["projects"] = [project["id"] for project in client_projects]
    
    return client_projects

@router.get("/{client_id}/properties")
async def get_client_properties(client_id: str):
    """
    Get all properties associated with a client.
    """
    if client_id not in CLIENTS_DB:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # In a real implementation, this would query the properties database
    # For demo purposes, we'll return properties from the mock properties database
    from app.api.v1.properties import PROPERTIES_DB
    
    # Get client's projects
    from app.api.v1.projects import PROJECTS_DB
    
    client_projects = [
        project for project in PROJECTS_DB.values()
        if project.get("client_id") == client_id
    ]
    
    # Get properties from client's projects
    client_properties = []
    for project in client_projects:
        for property_id in project.get("property_ids", []):
            if property_id in PROPERTIES_DB:
                client_properties.append(PROPERTIES_DB[property_id])
    
    # Update client's properties list
    CLIENTS_DB[client_id]["properties"] = [prop["id"] for prop in client_properties]
    
    return client_properties

@router.post("/{client_id}/reminders")
async def create_client_reminder(
    client_id: str,
    title: str,
    due_date: date,
    description: Optional[str] = None,
    priority: Optional[str] = "medium"
):
    """
    Create a reminder for a client.
    """
    if client_id not in CLIENTS_DB:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # In a real implementation, this would add to a reminders database
    # For demo purposes, we'll add to the client record
    
    reminder_id = str(uuid.uuid4())
    now = datetime.now()
    
    reminder = {
        "id": reminder_id,
        "client_id": client_id,
        "title": title,
        "description": description,
        "due_date": due_date.isoformat(),
        "priority": priority,
        "created_at": now.isoformat(),
        "status": "pending"
    }
    
    # Add reminders list if it doesn't exist
    if "reminders" not in CLIENTS_DB[client_id]:
        CLIENTS_DB[client_id]["reminders"] = []
    
    CLIENTS_DB[client_id]["reminders"].append(reminder)
    
    return reminder

@router.get("/{client_id}/reminders")
async def get_client_reminders(
    client_id: str,
    status: Optional[str] = None
):
    """
    Get reminders for a client.
    """
    if client_id not in CLIENTS_DB:
        raise HTTPException(status_code=404, detail="Client not found")
    
    reminders = CLIENTS_DB[client_id].get("reminders", [])
    
    # Apply filters
    if status:
        reminders = [r for r in reminders if r["status"] == status]
    
    return reminders

@router.get("/{client_id}/history")
async def get_client_history(client_id: str):
    """
    Get interaction history for a client.
    """
    if client_id not in CLIENTS_DB:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # In a real implementation, this would query an interaction history database
    # For demo purposes, we'll generate mock history data
    
    now = datetime.now()
    
    # Generate mock history entries
    history = [
        {
            "id": str(uuid.uuid4()),
            "client_id": client_id,
            "type": "project_created",
            "description": "Created new appraisal project",
            "timestamp": (now.replace(day=now.day-5)).isoformat(),
            "user_id": "user123",
            "details": {
                "project_id": "proj_001",
                "project_name": "Commercial Building Appraisal"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "client_id": client_id,
            "type": "property_added",
            "description": "Added property to project",
            "timestamp": (now.replace(day=now.day-4)).isoformat(),
            "user_id": "user123",
            "details": {
                "project_id": "proj_001",
                "property_id": "prop_001",
                "address": "123 Main St, Metropolis"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "client_id": client_id,
            "type": "report_submitted",
            "description": "Submitted appraisal report",
            "timestamp": (now.replace(day=now.day-2)).isoformat(),
            "user_id": "user456",
            "details": {
                "project_id": "proj_001",
                "report_id": "rep_001",
                "report_type": "full"
            }
        },
        {
            "id": str(uuid.uuid4()),
            "client_id": client_id,
            "type": "email_sent",
            "description": "Sent report to client",
            "timestamp": (now.replace(day=now.day-1)).isoformat(),
            "user_id": "user456",
            "details": {
                "email_subject": "Completed Appraisal Report",
                "recipient": "client@example.com"
            }
        }
    ]
    
    return history

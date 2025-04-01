"""
Project management endpoints for the Appraisal AI Agent.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import uuid

router = APIRouter()

# Mock database for projects (in a real app, this would be a database)
PROJECTS_DB = {}

class ProjectBase(BaseModel):
    """Base model for project data."""
    name: str
    client_id: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    priority: Optional[str] = "medium"
    property_ids: Optional[List[str]] = []
    appraiser_ids: Optional[List[str]] = []
    status: Optional[str] = "pending"

class ProjectCreate(ProjectBase):
    """Model for creating a new project."""
    pass

class ProjectUpdate(BaseModel):
    """Model for updating a project."""
    name: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[date] = None
    priority: Optional[str] = None
    property_ids: Optional[List[str]] = None
    appraiser_ids: Optional[List[str]] = None
    status: Optional[str] = None

class Project(ProjectBase):
    """Full project model with ID and timestamps."""
    id: str
    created_at: datetime
    updated_at: datetime

@router.post("", response_model=Project)
async def create_project(project: ProjectCreate):
    """
    Create a new appraisal project.
    """
    project_id = str(uuid.uuid4())
    now = datetime.now()
    
    new_project = {
        **project.dict(),
        "id": project_id,
        "created_at": now,
        "updated_at": now
    }
    
    PROJECTS_DB[project_id] = new_project
    return new_project

@router.get("", response_model=List[Project])
async def list_projects(
    client_id: Optional[str] = None,
    status: Optional[str] = None,
    appraiser_id: Optional[str] = None
):
    """
    List all projects with optional filtering.
    """
    projects = list(PROJECTS_DB.values())
    
    # Apply filters
    if client_id:
        projects = [p for p in projects if p["client_id"] == client_id]
    
    if status:
        projects = [p for p in projects if p["status"] == status]
    
    if appraiser_id:
        projects = [p for p in projects if appraiser_id in p.get("appraiser_ids", [])]
    
    return projects

@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """
    Get a specific project by ID.
    """
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return PROJECTS_DB[project_id]

@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, project_update: ProjectUpdate):
    """
    Update a project.
    """
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    
    current_project = PROJECTS_DB[project_id]
    
    # Update fields that are provided
    update_data = project_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        current_project[field] = value
    
    # Update the updated_at timestamp
    current_project["updated_at"] = datetime.now()
    
    PROJECTS_DB[project_id] = current_project
    return current_project

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """
    Delete a project.
    """
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    
    del PROJECTS_DB[project_id]
    return {"message": "Project deleted successfully"}

@router.post("/{project_id}/assign")
async def assign_appraisers(project_id: str, appraiser_ids: List[str]):
    """
    Assign appraisers to a project.
    """
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    
    current_project = PROJECTS_DB[project_id]
    current_project["appraiser_ids"] = appraiser_ids
    current_project["updated_at"] = datetime.now()
    
    return {"message": "Appraisers assigned successfully", "project": current_project}

@router.post("/{project_id}/properties")
async def add_properties(project_id: str, property_ids: List[str]):
    """
    Add properties to a project.
    """
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    
    current_project = PROJECTS_DB[project_id]
    current_properties = current_project.get("property_ids", [])
    
    # Add new properties without duplicates
    current_project["property_ids"] = list(set(current_properties + property_ids))
    current_project["updated_at"] = datetime.now()
    
    return {"message": "Properties added successfully", "project": current_project}

@router.get("/{project_id}/timeline")
async def get_project_timeline(project_id: str):
    """
    Get the timeline and milestones for a project.
    """
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = PROJECTS_DB[project_id]
    
    # In a real implementation, this would fetch actual timeline data
    # For demo purposes, we'll generate mock timeline data
    
    # Calculate milestone dates based on deadline
    deadline = project.get("deadline")
    if not deadline:
        raise HTTPException(status_code=400, detail="Project has no deadline set")
    
    created_at = project.get("created_at")
    
    # Generate timeline
    timeline = {
        "project_id": project_id,
        "project_name": project.get("name"),
        "start_date": created_at,
        "end_date": deadline,
        "milestones": [
            {
                "name": "Project Initiation",
                "date": created_at,
                "status": "completed"
            },
            {
                "name": "Data Collection",
                "date": created_at + (deadline - created_at) * 0.25,
                "status": "in_progress" if datetime.now().date() < deadline else "completed"
            },
            {
                "name": "Property Inspection",
                "date": created_at + (deadline - created_at) * 0.5,
                "status": "pending" if datetime.now().date() < created_at + (deadline - created_at) * 0.5 else "in_progress"
            },
            {
                "name": "Valuation Analysis",
                "date": created_at + (deadline - created_at) * 0.75,
                "status": "pending"
            },
            {
                "name": "Report Generation",
                "date": deadline,
                "status": "pending"
            }
        ],
        "progress": 25  # percentage
    }
    
    return timeline

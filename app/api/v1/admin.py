"""
Admin API endpoints for the Apeko website.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import shutil
import json
import uuid
from sqlalchemy import func

from app.db.session import get_db
from app.models.rag import Document, DocumentChunk, RAGQuery, WebsiteUsage
from app.models.user import User
from app.models.client import Client
from app.models.project import Project, ProjectStatus
from app.models.property import Property
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.services.dependencies import get_llm_service

router = APIRouter()

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db)
):
    """
    Get statistics for the admin dashboard.
    
    This endpoint returns statistics about clients, website usage, projects, and RAG database.
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
        
        # Get RAG database stats
        rag_service = RAGService(db)
        rag_stats = rag_service.get_usage_statistics()
        
        # Get recent activity
        recent_activity = []
        
        # Get recent website usage
        recent_visits = db.query(WebsiteUsage).order_by(WebsiteUsage.visit_time.desc()).limit(10).all()
        
        for visit in recent_visits:
            user = None
            if visit.user_id:
                user = db.query(User).filter(User.id == visit.user_id).first()
            
            recent_activity.append({
                "user": user.name if user else "Anonymous",
                "action": f"Visited {visit.page_visited}",
                "time": visit.visit_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Completed",
                "status_class": "success"
            })
        
        # Get recent projects
        recent_projects = db.query(Project).order_by(Project.created_at.desc()).limit(5).all()
        
        for project in recent_projects:
            client = db.query(Client).filter(Client.id == project.client_id).first()
            
            recent_activity.append({
                "user": client.name if client else "Unknown Client",
                "action": f"Created project: {project.name}",
                "time": project.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": project.status,
                "status_class": "success" if project.status == "completed" else "pending"
            })
        
        # Sort by time
        recent_activity.sort(key=lambda x: x["time"], reverse=True)
        
        return {
            "stats": {
                "total_clients": total_clients,
                "website_visits": website_visits,
                "total_reports": total_reports,
                "monthly_revenue": monthly_revenue
            },
            "rag_stats": rag_stats,
            "recent_activity": recent_activity[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboard stats: {str(e)}")

@router.get("/files")
async def list_files(
    path: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List files in the specified directory.
    
    This endpoint returns a list of files and directories in the specified path.
    """
    try:
        # Set base directory for file storage
        base_dir = os.path.join(os.getcwd(), "app", "data", "files")
        
        # Create base directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)
        
        # Determine current directory
        current_dir = base_dir
        if path:
            # Validate path to prevent directory traversal
            requested_path = os.path.normpath(os.path.join(base_dir, path))
            if not requested_path.startswith(base_dir):
                raise HTTPException(status_code=403, detail="Access denied")
            
            current_dir = requested_path
        
        # Get relative path for display
        relative_path = os.path.relpath(current_dir, base_dir)
        if relative_path == ".":
            relative_path = ""
        
        # List files and directories
        files = []
        
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            is_dir = os.path.isdir(item_path)
            
            # Get file stats
            stats = os.stat(item_path)
            
            # Determine icon
            icon = "fa-folder" if is_dir else "fa-file"
            icon_class = "folder" if is_dir else "document"
            
            # For files, determine more specific icon based on extension
            if not is_dir:
                ext = os.path.splitext(item)[1].lower()
                if ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
                    icon = "fa-image"
                    icon_class = "image"
                elif ext in [".pdf"]:
                    icon = "fa-file-pdf"
                elif ext in [".doc", ".docx"]:
                    icon = "fa-file-word"
                elif ext in [".xls", ".xlsx"]:
                    icon = "fa-file-excel"
                elif ext in [".ppt", ".pptx"]:
                    icon = "fa-file-powerpoint"
                elif ext in [".txt", ".md"]:
                    icon = "fa-file-alt"
            
            # Format size
            size = stats.st_size
            if is_dir:
                size_str = ""
            elif size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            else:
                size_str = f"{size / (1024 * 1024 * 1024):.1f} GB"
            
            # Format modified time
            modified = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if file can be added to RAG
            can_add_to_rag = False
            if not is_dir:
                ext = os.path.splitext(item)[1].lower()
                if ext in [".txt", ".md", ".pdf", ".doc", ".docx"]:
                    can_add_to_rag = True
            
            # Add to list
            files.append({
                "name": item,
                "path": os.path.join(relative_path, item),
                "type": "folder" if is_dir else "file",
                "size": size_str,
                "modified": modified,
                "icon": icon,
                "icon_class": icon_class,
                "can_add_to_rag": can_add_to_rag
            })
        
        # Sort: directories first, then files, both alphabetically
        files.sort(key=lambda x: (0 if x["type"] == "folder" else 1, x["name"].lower()))
        
        return {
            "current_path": relative_path,
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.post("/files/upload")
async def upload_files(
    current_path: str = Form(...),
    files: List[UploadFile] = File(...),
    add_to_rag: bool = Form(False),
    document_type: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Upload files to the specified directory.
    
    This endpoint handles file uploads to the specified directory.
    """
    try:
        # Set base directory for file storage
        base_dir = os.path.join(os.getcwd(), "app", "data", "files")
        
        # Create base directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)
        
        # Determine target directory
        target_dir = base_dir
        if current_path:
            # Validate path to prevent directory traversal
            requested_path = os.path.normpath(os.path.join(base_dir, current_path))
            if not requested_path.startswith(base_dir):
                raise HTTPException(status_code=403, detail="Access denied")
            
            target_dir = requested_path
        
        # Create target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Upload files
        uploaded_files = []
        
        for file in files:
            # Save file
            file_path = os.path.join(target_dir, file.filename)
            
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            uploaded_files.append(file.filename)
            
            # Add to RAG if requested
            if add_to_rag and document_type:
                # Check if file type is supported
                ext = os.path.splitext(file.filename)[1].lower()
                if ext in [".txt", ".md", ".pdf", ".doc", ".docx"]:
                    # Read file content
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    # Add to RAG database
                    rag_service = RAGService(db, llm_service)
                    await rag_service.add_document(
                        title=file.filename,
                        content=content,
                        document_type=document_type,
                        source=f"uploaded_file:{current_path}/{file.filename}"
                    )
        
        return {
            "success": True,
            "uploaded_files": uploaded_files,
            "added_to_rag": add_to_rag
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading files: {str(e)}")

@router.post("/files/new-folder")
async def create_folder(
    current_path: str = Form(...),
    folder_name: str = Form(...)
):
    """
    Create a new folder in the specified directory.
    
    This endpoint creates a new folder in the specified directory.
    """
    try:
        # Set base directory for file storage
        base_dir = os.path.join(os.getcwd(), "app", "data", "files")
        
        # Create base directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)
        
        # Determine target directory
        target_dir = base_dir
        if current_path:
            # Validate path to prevent directory traversal
            requested_path = os.path.normpath(os.path.join(base_dir, current_path))
            if not requested_path.startswith(base_dir):
                raise HTTPException(status_code=403, detail="Access denied")
            
            target_dir = requested_path
        
        # Create new folder
        new_folder_path = os.path.join(target_dir, folder_name)
        
        if os.path.exists(new_folder_path):
            raise HTTPException(status_code=400, detail="Folder already exists")
        
        os.makedirs(new_folder_path)
        
        return {
            "success": True,
            "folder_name": folder_name,
            "path": os.path.join(current_path, folder_name)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating folder: {str(e)}")

@router.get("/files/download")
async def download_file(
    path: str
):
    """
    Download a file.
    
    This endpoint allows downloading a file from the specified path.
    """
    try:
        # Set base directory for file storage
        base_dir = os.path.join(os.getcwd(), "app", "data", "files")
        
        # Validate path to prevent directory traversal
        requested_path = os.path.normpath(os.path.join(base_dir, path))
        if not requested_path.startswith(base_dir) or not os.path.isfile(requested_path):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return FileResponse(
            path=requested_path,
            filename=os.path.basename(requested_path),
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@router.get("/files/view")
async def view_file(
    path: str
):
    """
    View a file.
    
    This endpoint returns the content of a file for viewing.
    """
    try:
        # Set base directory for file storage
        base_dir = os.path.join(os.getcwd(), "app", "data", "files")
        
        # Validate path to prevent directory traversal
        requested_path = os.path.normpath(os.path.join(base_dir, path))
        if not requested_path.startswith(base_dir) or not os.path.isfile(requested_path):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Read file content
        with open(requested_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Get file info
        stats = os.stat(requested_path)
        size = stats.st_size
        
        # Format size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{size / (1024 * 1024 * 1024):.1f} GB"
        
        # Format modified time
        modified = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "name": os.path.basename(requested_path),
            "path": path,
            "content": content,
            "size": size_str,
            "modified": modified
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error viewing file: {str(e)}")

@router.get("/files/rename")
async def rename_file(
    path: str,
    new_name: str
):
    """
    Rename a file or folder.
    
    This endpoint renames a file or folder at the specified path.
    """
    try:
        # Set base directory for file storage
        base_dir = os.path.join(os.getcwd(), "app", "data", "files")
        
        # Validate path to prevent directory traversal
        requested_path = os.path.normpath(os.path.join(base_dir, path))
        if not requested_path.startswith(base_dir) or not os.path.exists(requested_path):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get directory and old name
        directory = os.path.dirname(requested_path)
        
        # Create new path
        new_path = os.path.join(directory, new_name)
        
        # Check if new path already exists
        if os.path.exists(new_path):
            raise HTTPException(status_code=400, detail="A file or folder with that name already exists")
        
        # Rename
        os.rename(requested_path, new_path)
        
        return {
            "success": True,
            "old_path": path,
            "new_path": os.path.join(os.path.dirname(path), new_name)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error renaming file: {str(e)}")

@router.get("/files/delete")
async def delete_file(
    path: str
):
    """
    Delete a file or folder.
    
    This endpoint deletes a file or folder at the specified path.
    """
    try:
        # Set base directory for file storage
        base_dir = os.path.join(os.getcwd(), "app", "data", "files")
        
        # Validate path to prevent directory traversal
        requested_path = os.path.normpath(os.path.join(base_dir, path))
        if not requested_path.startswith(base_dir) or not os.path.exists(requested_path):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete
        if os.path.isdir(requested_path):
            shutil.rmtree(requested_path)
        else:
            os.remove(requested_path)
        
        return {
            "success": True,
            "deleted_path": path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@router.get("/files/add-to-rag")
async def add_file_to_rag(
    path: str,
    document_type: str,
    db: Session = Depends(get_db),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Add a file to the RAG database.
    
    This endpoint adds a file to the RAG database for retrieval.
    """
    try:
        # Set base directory for file storage
        base_dir = os.path.join(os.getcwd(), "app", "data", "files")
        
        # Validate path to prevent directory traversal
        requested_path = os.path.normpath(os.path.join(base_dir, path))
        if not requested_path.startswith(base_dir) or not os.path.isfile(requested_path):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if file type is supported
        ext = os.path.splitext(requested_path)[1].lower()
        if ext not in [".txt", ".md", ".pdf", ".doc", ".docx"]:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Read file content
        with open(requested_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Add to RAG database
        rag_service = RAGService(db, llm_service)
        document = await rag_service.add_document(
            title=os.path.basename(requested_path),
            content=content,
            document_type=document_type,
            source=f"uploaded_file:{path}"
        )
        
        return {
            "success": True,
            "document_id": document.id,
            "title": document.title,
            "document_type": document.document_type
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding file to RAG database: {str(e)}")

@router.get("/agent/chats")
async def get_agent_chats(
    user_id: Optional[int] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get agent chat history.
    
    This endpoint returns a list of agent chat sessions.
    """
    try:
        # This is a placeholder - in a real implementation, you would have a Chat model
        # For now, we'll return mock data
        return {
            "chats": [
                {
                    "id": "chat1",
                    "title": "Residential Property Appraisal",
                    "time": "2025-03-29 14:30:45",
                    "user_id": 1,
                    "message_count": 12
                },
                {
                    "id": "chat2",
                    "title": "Commercial Market Analysis",
                    "time": "2025-03-28 09:15:22",
                    "user_id": 1,
                    "message_count": 8
                },
                {
                    "id": "chat3",
                    "title": "Property Regulations in New York",
                    "time": "2025-03-27 16:45:10",
                    "user_id": 2,
                    "message_count": 15
                }
            ],
            "total": 3
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent chats: {str(e)}")

@router.get("/agent/chat/{chat_id}")
async def get_agent_chat(
    chat_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific agent chat.
    
    This endpoint returns the messages in a specific agent chat session.
    """
    try:
        # This is a placeholder - in a real implementation, you would fetch from database
        # For now, we'll return mock data
        return {
            "id": chat_id,
            "title": "Residential Property Appraisal",
            "created_at": "2025-03-29 14:30:45",
            "user_id": 1,
            "messages": [
                {
                    "id": "msg1",
                    "role": "user",
                    "content": "I need help appraising a residential property in Metropolis.",
                    "time": "2025-03-29 14:30:45"
                },
                {
                    "id": "msg2",
                    "role": "agent",
                    "content": "I'd be happy to help with your residential property appraisal in Metropolis. To provide an accurate appraisal, I'll need some details about the property. Could you please provide the following information:\n\n1. Property address or neighborhood\n2. Square footage\n3. Number of bedrooms and bathrooms\n4. Year built\n5. Any recent renovations or special features\n6. Lot size (if known)",
                    "time": "2025-03-29 14:30:50"
                },
                {
                    "id": "msg3",
                    "role": "user",
                    "content": "It's a 3-bedroom, 2-bathroom house at 123 Main Street, Metropolis. About 2,000 square feet, built in 2010. The lot is 0.25 acres. The kitchen was renovated last year.",
                    "time": "2025-03-29 14:31:30"
                },
                {
                    "id": "msg4",
                    "role": "agent",
                    "content": "Thank you for providing those details about the property at 123 Main Street in Metropolis. I'll use our property data service to find comparable properties and analyze the current market conditions.\n\nBased on the information you've provided and our database of recent sales in Metropolis, here's my preliminary appraisal analysis:\n\n**Property Details:**\n- 3 bedrooms, 2 bathrooms\n- 2,000 square feet\n- 0.25 acre lot\n- Built in 2010\n- Recent kitchen renovation\n\n**Comparable Properties:**\n1. 145 Oak Ave: 3bd/2ba, 1,950 sq ft, built 2012, sold for $425,000 (3 months ago)\n2. 78 Elm St: 3bd/2.5ba, 2,100 sq ft, built 2008, sold for $445,000 (1 month ago)\n3. 210 Pine Rd: 3bd/2ba, 1,850 sq ft, built 2011, sold for $410,000 (2 months ago)\n\n**Market Analysis:**\n- The Metropolis residential market has shown a 5.2% appreciation over the past year\n- Properties with recent kitchen renovations typically see a 3-5% increase in value\n- The average price per square foot in this neighborhood is approximately $215\n\n**Estimated Value Range:**\n$430,000 - $460,000\n\nThis estimate takes into account the property's size, age, location, and the recent kitchen renovation. The higher end of the range reflects the value added by the renovation and the property's slightly larger size compared to some of the comparable sales.\n\nWould you like more detailed information about any aspect of this appraisal?",
                    "time": "2025-03-29 14:32:15",
                    "sources": [
                        {
                            "document_id": 12,
                            "document_title": "Metropolis Housing Market Report 2025",
                            "document_type": "market_analysis",
                            "similarity": 0.92
                        },
                        {
                            "document_id": 8,
                            "document_title": "Residential Property Valuation Guidelines",
                            "document_type": "appraisal_report",
                            "similarity": 0.85
                        }
                    ]
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent chat: {str(e)}")

@router.get("/agent/new-chat")
async def create_new_chat(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Create a new agent chat session.
    
    This endpoint creates a new agent chat session.
    """
    try:
        # This is a placeholder - in a real implementation, you would create in database
        # For now, we'll return mock data
        return {
            "id": "new_chat_id",
            "title": "New Chat",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating new chat: {str(e)}")

@router.post("/agent/chat/{chat_id}/message")
async def send_agent_message(
    chat_id: str,
    message: dict,
    db: Session = Depends(get_db),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Send a message to the agent and get a response.
    
    This endpoint processes a user message and returns the agent's response.
    """
    try:
        # Extract the message content
        user_message = message.get("content", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message content is required")
        
        # Get data from the database based on the message content
        # This is where we connect the agent to the website's data
        
        # Check if the message is asking about client count
        if "cuantos clientes" in user_message.lower() or "¿cuántos clientes" in user_message.lower():
            # Count clients in the database
            from app.models.client import Client
            client_count = db.query(Client).count()
            
            return {
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "role": "agent",
                "content": f"Actualmente tenemos {client_count} clientes registrados en Apeko.",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Check if the message is asking about projects/appraisals
        elif "proyectos" in user_message.lower() or "tasaciones" in user_message.lower() or "appraisals" in user_message.lower():
            # Count projects in the database
            from app.models.project import Project, ProjectStatus
            total_projects = db.query(Project).count()
            completed_projects = db.query(Project).filter(Project.status == ProjectStatus.COMPLETED).count()
            in_progress_projects = db.query(Project).filter(Project.status == ProjectStatus.IN_PROGRESS).count()
            
            return {
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "role": "agent",
                "content": f"Tenemos un total de {total_projects} proyectos de tasación en el sistema. De estos, {completed_projects} están completados y {in_progress_projects} están en progreso.",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Check if the message is asking about properties
        elif "propiedades" in user_message.lower() or "properties" in user_message.lower():
            # Count properties in the database
            from app.models.property import Property
            property_count = db.query(Property).count()
            
            # Get property types distribution
            property_types = db.query(Property.property_type, func.count(Property.id)).group_by(Property.property_type).all()
            property_type_info = "\n".join([f"- {p_type}: {count} propiedades" for p_type, count in property_types])
            
            return {
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "role": "agent",
                "content": f"Tenemos {property_count} propiedades registradas en el sistema. La distribución por tipo es:\n\n{property_type_info}",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # For other types of questions, use the LLM service with RAG
        else:
            # Get relevant documents from the RAG database
            rag_service = RAGService(db)
            relevant_docs = rag_service.search_documents(user_message, limit=3)
            
            # Format context from relevant documents
            context = ""
            if relevant_docs:
                context = "Information from our database:\n\n"
                for doc in relevant_docs:
                    context += f"- {doc.title}: {doc.content[:200]}...\n\n"
            
            # Generate response using the LLM service
            prompt = f"""You are an AI assistant for Apeko, a real estate appraisal company. 
            Answer the following question using the provided context if relevant.
            
            Context: {context}
            
            Question: {user_message}
            
            Answer in the same language as the question:"""
            
            response = await llm_service.generate_text(prompt)
            
            return {
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "role": "agent",
                "content": response,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sources": [
                    {
                        "document_id": doc.id,
                        "document_title": doc.title,
                        "document_type": doc.document_type,
                        "similarity": 0.85  # Placeholder similarity score
                    } for doc in relevant_docs
                ] if relevant_docs else []
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing agent message: {str(e)}")

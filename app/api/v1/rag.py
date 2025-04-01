"""
RAG (Retrieval-Augmented Generation) API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.services.rag_service import RAGService
from app.services.dependencies import get_llm_service
from app.models.rag import Document

router = APIRouter()

class DocumentCreate(BaseModel):
    """Request model for document creation."""
    title: str
    content: str
    document_type: str
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DocumentResponse(BaseModel):
    """Response model for documents."""
    id: int
    title: str
    document_type: str
    source: Optional[str] = None
    created_at: str
    updated_at: str

class SearchQuery(BaseModel):
    """Request model for search queries."""
    query: str
    document_type: Optional[str] = None
    top_k: int = 5
    user_id: Optional[int] = None

class SearchResult(BaseModel):
    """Response model for search results."""
    chunk_id: int
    document_id: int
    document_title: str
    document_type: str
    chunk_index: int
    content: str
    similarity: float

class RAGResponse(BaseModel):
    """Response model for RAG-generated responses."""
    response: str
    sources: List[Dict[str, Any]]

class UsageStatistics(BaseModel):
    """Response model for usage statistics."""
    total_documents: int
    total_chunks: int
    total_queries: int
    document_type_distribution: Dict[str, int]
    recent_queries: List[Dict[str, Any]]

@router.post("/documents", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    llm_service = Depends(get_llm_service)
):
    """
    Create a new document for RAG.
    
    This endpoint adds a document to the RAG database, processes it into chunks,
    and generates embeddings for each chunk.
    """
    rag_service = RAGService(db, llm_service)
    
    try:
        doc = await rag_service.add_document(
            title=document.title,
            content=document.content,
            document_type=document.document_type,
            source=document.source,
            metadata=document.metadata
        )
        
        return {
            "id": doc.id,
            "title": doc.title,
            "document_type": doc.document_type,
            "source": doc.source,
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating document: {str(e)}")

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(...),
    source: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    llm_service = Depends(get_llm_service)
):
    """
    Upload a document file for RAG.
    
    This endpoint accepts a file upload, extracts the text content,
    and adds it to the RAG database.
    """
    rag_service = RAGService(db, llm_service)
    
    try:
        # Read file content
        content = await file.read()
        
        # Convert bytes to string
        text_content = content.decode("utf-8")
        
        # Create document
        doc = await rag_service.add_document(
            title=title,
            content=text_content,
            document_type=document_type,
            source=source or file.filename
        )
        
        return {
            "id": doc.id,
            "title": doc.title,
            "document_type": doc.document_type,
            "source": doc.source,
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@router.get("/documents", response_model=List[DocumentResponse])
async def get_documents(
    document_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get all documents with optional filtering by type.
    
    This endpoint returns a list of documents in the RAG database,
    with optional filtering by document type.
    """
    rag_service = RAGService(db)
    
    try:
        if document_type:
            documents = rag_service.get_documents_by_type(document_type)
        else:
            documents = rag_service.get_all_documents(limit, offset)
        
        return [
            {
                "id": doc.id,
                "title": doc.title,
                "document_type": doc.document_type,
                "source": doc.source,
                "created_at": doc.created_at.isoformat(),
                "updated_at": doc.updated_at.isoformat()
            }
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a document by ID.
    
    This endpoint returns a specific document from the RAG database.
    """
    rag_service = RAGService(db)
    
    try:
        doc = rag_service.get_document_by_id(document_id)
        
        if not doc:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
        
        return {
            "id": doc.id,
            "title": doc.title,
            "document_type": doc.document_type,
            "source": doc.source,
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a document by ID.
    
    This endpoint deletes a document and its chunks from the RAG database.
    """
    rag_service = RAGService(db)
    
    try:
        success = rag_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
        
        return {"message": f"Document with ID {document_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.post("/search", response_model=List[SearchResult])
async def search_documents(
    query: SearchQuery,
    db: Session = Depends(get_db),
    llm_service = Depends(get_llm_service)
):
    """
    Search for relevant document chunks.
    
    This endpoint searches the RAG database for chunks relevant to the query.
    """
    rag_service = RAGService(db, llm_service)
    
    try:
        results = await rag_service.search_documents(
            query=query.query,
            document_type=query.document_type,
            top_k=query.top_k,
            user_id=query.user_id
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

@router.post("/generate", response_model=RAGResponse)
async def generate_response(
    query: SearchQuery,
    db: Session = Depends(get_db),
    llm_service = Depends(get_llm_service)
):
    """
    Generate a response using RAG.
    
    This endpoint generates a response to the query using RAG,
    retrieving relevant document chunks and using them as context for the LLM.
    """
    rag_service = RAGService(db, llm_service)
    
    try:
        response = await rag_service.generate_response_with_context(
            query=query.query,
            user_id=query.user_id,
            document_type=query.document_type,
            top_k=query.top_k
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@router.get("/statistics", response_model=UsageStatistics)
async def get_statistics(
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for the RAG system.
    
    This endpoint returns statistics about the RAG system,
    including document counts, query counts, and more.
    """
    rag_service = RAGService(db)
    
    try:
        stats = rag_service.get_usage_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

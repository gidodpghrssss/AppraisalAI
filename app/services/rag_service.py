"""
RAG (Retrieval-Augmented Generation) service for the Appraisal AI Agent.
This service handles document processing, embedding, and retrieval for the agent.
"""
import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.rag import Document, DocumentChunk, RAGQuery, RAGQueryChunk
from app.services.llm_service import LLMService
from app.core.config import settings

class RAGService:
    """Service for handling RAG operations."""
    
    def __init__(self, db: Session, llm_service: Optional[LLMService] = None):
        """Initialize the RAG service."""
        self.db = db
        self.llm_service = llm_service
        self.embedding_dimension = 1536  # Default for most embedding models
        
        # Create directories for storing embeddings if they don't exist
        os.makedirs("app/data/embeddings", exist_ok=True)
    
    async def add_document(
        self, 
        title: str, 
        content: str, 
        document_type: str, 
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> Document:
        """
        Add a document to the RAG database.
        
        Args:
            title: Document title
            content: Document content
            document_type: Type of document (e.g., 'appraisal_report', 'market_analysis')
            source: Source of the document
            metadata: Additional metadata for the document
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
            
        Returns:
            The created document
        """
        # Create the document
        document = Document(
            title=title,
            content=content,
            document_type=document_type,
            source=source,
            document_metadata=json.dumps(metadata) if metadata else None
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        # Chunk the document
        chunks = self._chunk_text(content, chunk_size, chunk_overlap)
        
        # Create document chunks
        for i, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_text,
                embedding=None  # Will be computed later
            )
            self.db.add(chunk)
        
        self.db.commit()
        
        # Generate embeddings for the chunks (async)
        await self._generate_embeddings_for_document(document.id)
        
        return document
    
    async def search_documents(
        self, 
        query: str, 
        document_type: Optional[str] = None,
        top_k: int = 5,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks based on a query.
        
        Args:
            query: The search query
            document_type: Optional filter for document type
            top_k: Number of results to return
            user_id: Optional user ID for tracking
            
        Returns:
            List of relevant document chunks with metadata
        """
        # Generate embedding for the query
        query_embedding = await self._generate_embedding(query)
        
        if not query_embedding:
            # Fallback to keyword search if embedding generation fails
            return self._keyword_search(query, document_type, top_k)
        
        # Find chunks with similar embeddings
        results = []
        chunks = self.db.query(DocumentChunk).all()
        
        for chunk in chunks:
            if chunk.embedding:
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, chunk.embedding)
                
                # Get document metadata
                document = self.db.query(Document).filter(Document.id == chunk.document_id).first()
                
                # Filter by document type if specified
                if document_type and document.document_type != document_type:
                    continue
                
                results.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_title": document.title,
                    "document_type": document.document_type,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "similarity": float(similarity)
                })
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Take top k results
        top_results = results[:top_k]
        
        # Log the query for analytics
        self._log_query(query, query_embedding, top_results, user_id)
        
        return top_results
    
    async def generate_response_with_context(
        self, 
        query: str, 
        user_id: Optional[int] = None,
        document_type: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Generate a response to a query using RAG.
        
        Args:
            query: The user query
            user_id: Optional user ID for tracking
            document_type: Optional filter for document type
            top_k: Number of results to use for context
            
        Returns:
            Generated response with metadata
        """
        # Search for relevant documents
        search_results = await self.search_documents(
            query=query,
            document_type=document_type,
            top_k=top_k,
            user_id=user_id
        )
        
        if not search_results:
            return {
                "response": "I couldn't find any relevant information to answer your question.",
                "sources": []
            }
        
        # Prepare context from search results
        context = "\n\n".join([f"Document: {result['document_title']}\n{result['content']}" for result in search_results])
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert real estate appraiser AI assistant. Use the following information to answer the user's question.
        If you don't know the answer based on the provided information, say so.
        
        Context information:
        {context}
        
        User question: {query}
        """
        
        # Generate response using LLM
        if self.llm_service:
            from app.services.llm_service import Message
            
            messages = [
                Message(role="system", content=prompt),
                Message(role="user", content=query)
            ]
            
            try:
                llm_response = await self.llm_service.generate_completion(messages=messages)
                
                # Extract response content
                response_content = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not response_content:
                    response_content = "I apologize, but I couldn't generate a proper response based on the available information."
            except Exception as e:
                response_content = f"I apologize, but I encountered an error while generating a response: {str(e)}"
        else:
            response_content = "LLM service is not available. I can only provide the relevant documents."
        
        # Prepare sources for citation
        sources = []
        for result in search_results:
            sources.append({
                "document_id": result["document_id"],
                "document_title": result["document_title"],
                "document_type": result["document_type"],
                "similarity": result["similarity"]
            })
        
        return {
            "response": response_content,
            "sources": sources
        }
    
    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get a document by ID."""
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_documents_by_type(self, document_type: str) -> List[Document]:
        """Get all documents of a specific type."""
        return self.db.query(Document).filter(Document.document_type == document_type).all()
    
    def get_all_documents(self, limit: int = 100, offset: int = 0) -> List[Document]:
        """Get all documents with pagination."""
        return self.db.query(Document).order_by(Document.created_at.desc()).offset(offset).limit(limit).all()
    
    def delete_document(self, document_id: int) -> bool:
        """Delete a document and its chunks."""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False
        
        self.db.delete(document)
        self.db.commit()
        return True
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for the RAG system."""
        try:
            # Get document statistics
            total_documents = self.db.query(func.count(Document.id)).scalar() or 0
            
            # Get chunk statistics
            total_chunks = self.db.query(func.count(DocumentChunk.id)).scalar() or 0
            
            # Get query statistics
            total_queries = self.db.query(func.count(RAGQuery.id)).scalar() or 0
            
            # Get average relevance score (if available)
            avg_relevance = self.db.query(func.avg(RAGQuery.relevance_score)).scalar() or 0.0
            
            # Get document type distribution
            document_type_distribution = {}
            doc_type_counts = self.db.query(
                Document.document_type, 
                func.count(Document.id)
            ).group_by(Document.document_type).all()
            
            for doc_type, count in doc_type_counts:
                document_type_distribution[doc_type] = count
                
            # Get recent queries
            recent_queries = self.db.query(RAGQuery).order_by(
                desc(RAGQuery.created_at)
            ).limit(10).all()
            
            recent_query_data = []
            for query in recent_queries:
                # Get number of chunks retrieved for this query
                chunk_count = self.db.query(func.count(RAGQueryChunk.id)).filter(
                    RAGQueryChunk.query_id == query.id
                ).scalar() or 0
                
                recent_query_data.append({
                    "id": query.id,
                    "query_text": query.query_text,
                    "user_id": query.user_id,
                    "created_at": query.created_at,
                    "relevance_score": query.relevance_score or 0.0,
                    "chunk_count": chunk_count
                })
            
            return {
                "total_documents": total_documents,
                "total_chunks": total_chunks,
                "total_queries": total_queries,
                "average_relevance": avg_relevance,
                "document_type_distribution": document_type_distribution,
                "recent_queries": recent_query_data
            }
        except Exception as e:
            print(f"Error getting usage statistics: {str(e)}")
            # Return default values in case of error
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "total_queries": 0,
                "average_relevance": 0.0,
                "document_type_distribution": {},
                "recent_queries": []
            }
    
    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Split text into overlapping chunks."""
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to find a good breaking point (end of sentence or paragraph)
            if end < len(text):
                # Look for paragraph break
                paragraph_break = text.rfind("\n\n", start, end)
                if paragraph_break != -1 and paragraph_break > start + chunk_size // 2:
                    end = paragraph_break + 2
                else:
                    # Look for sentence break
                    sentence_break = max(
                        text.rfind(". ", start, end),
                        text.rfind("! ", start, end),
                        text.rfind("? ", start, end)
                    )
                    if sentence_break != -1 and sentence_break > start + chunk_size // 2:
                        end = sentence_break + 2
            
            chunks.append(text[start:end])
            start = end - chunk_overlap
        
        return chunks
    
    async def _generate_embeddings_for_document(self, document_id: int) -> None:
        """Generate embeddings for all chunks of a document."""
        chunks = self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
        
        for chunk in chunks:
            embedding = await self._generate_embedding(chunk.content)
            if embedding:
                chunk.embedding = embedding
                self.db.add(chunk)
        
        self.db.commit()
    
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate an embedding for a text using the LLM service.
        
        In a production environment, this would use a dedicated embedding model.
        For simplicity, we're using a mock implementation.
        """
        # Mock implementation - in a real system, use a proper embedding model
        try:
            # Simple hash-based embedding for demo purposes
            import hashlib
            
            # Create a deterministic but unique embedding based on text hash
            hash_obj = hashlib.md5(text.encode())
            hash_bytes = hash_obj.digest()
            
            # Convert hash to a list of floats
            embedding = []
            for i in range(self.embedding_dimension):
                # Use modulo to cycle through the hash bytes
                byte_val = hash_bytes[i % len(hash_bytes)]
                # Normalize to [-1, 1]
                embedding.append((byte_val / 128.0) - 1.0)
            
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm_vec1 = np.linalg.norm(vec1)
            norm_vec2 = np.linalg.norm(vec2)
            
            if norm_vec1 == 0 or norm_vec2 == 0:
                return 0.0
            
            return dot_product / (norm_vec1 * norm_vec2)
        except Exception as e:
            print(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
    
    def _keyword_search(
        self, 
        query: str, 
        document_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fallback keyword-based search when embeddings are not available.
        
        Args:
            query: The search query
            document_type: Optional filter for document type
            top_k: Number of results to return
            
        Returns:
            List of relevant document chunks
        """
        # Simple keyword matching for demo purposes
        query_terms = query.lower().split()
        
        chunks_query = self.db.query(DocumentChunk, Document).join(
            Document, DocumentChunk.document_id == Document.id
        )
        
        if document_type:
            chunks_query = chunks_query.filter(Document.document_type == document_type)
        
        chunks = chunks_query.all()
        
        results = []
        for chunk, document in chunks:
            # Calculate a simple relevance score based on term frequency
            content_lower = chunk.content.lower()
            term_matches = sum(1 for term in query_terms if term in content_lower)
            relevance = term_matches / len(query_terms) if query_terms else 0
            
            if relevance > 0:
                results.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_title": document.title,
                    "document_type": document.document_type,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "similarity": relevance
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return results[:top_k]
    
    def _log_query(
        self, 
        query: str, 
        query_embedding: Optional[List[float]], 
        results: List[Dict[str, Any]],
        user_id: Optional[int] = None
    ) -> None:
        """Log a query for analytics."""
        try:
            # Create query record
            rag_query = RAGQuery(
                user_id=user_id,
                query_text=query,
                query_embedding=query_embedding,
                result_text=None,  # Will be updated when response is generated
                relevance_score=None  # Will be updated with user feedback
            )
            
            self.db.add(rag_query)
            self.db.commit()
            self.db.refresh(rag_query)
            
            # Log retrieved chunks
            for rank, result in enumerate(results):
                query_chunk = RAGQueryChunk(
                    query_id=rag_query.id,
                    chunk_id=result["chunk_id"],
                    similarity_score=result["similarity"],
                    rank=rank
                )
                
                self.db.add(query_chunk)
            
            self.db.commit()
        except Exception as e:
            print(f"Error logging query: {str(e)}")
            # Don't raise the exception - this is a non-critical operation

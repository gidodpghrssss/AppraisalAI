"""RAG (Retrieval-Augmented Generation) models for the application."""
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Index, DateTime, func, JSON
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

class Document(Base, TimestampMixin):
    """Document model for storing text documents for RAG."""
    __tablename__ = "rag_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    document_type = Column(String(50), nullable=False)  # e.g., 'appraisal_report', 'market_analysis', 'regulation'
    document_metadata = Column(Text, nullable=True)  # JSON string for additional metadata
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', type='{self.document_type}')>"


class DocumentChunk(Base, TimestampMixin):
    """Document chunk model for storing text chunks with embeddings for RAG."""
    __tablename__ = "rag_document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("rag_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # Vector embedding for semantic search stored as JSON
    
    # Relationships
    document = relationship("Document", back_populates="chunks")

    # Create an index on document_id and chunk_index
    __table_args__ = (
        Index("ix_rag_document_chunks_document_id_chunk_index", "document_id", "chunk_index"),
    )

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"


class RAGQuery(Base, TimestampMixin):
    """Model for storing user queries and their results for analytics and improvement."""
    __tablename__ = "rag_queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    query_text = Column(Text, nullable=False)
    query_embedding = Column(JSON, nullable=True)  # Stored as JSON
    result_text = Column(Text, nullable=True)
    relevance_score = Column(Float, nullable=True)  # User feedback or system evaluation
    query_time = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    retrieved_chunks = relationship("RAGQueryChunk", back_populates="query", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RAGQuery(id={self.id}, query_text='{self.query_text[:30]}...')>"


class RAGQueryChunk(Base, TimestampMixin):
    """Model for storing which chunks were retrieved for a query."""
    __tablename__ = "rag_query_chunks"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("rag_queries.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(Integer, ForeignKey("rag_document_chunks.id", ondelete="CASCADE"), nullable=False)
    similarity_score = Column(Float, nullable=False)  # Cosine similarity or other relevance metric
    rank = Column(Integer, nullable=False)  # Rank in the retrieval results
    
    # Relationships
    query = relationship("RAGQuery", back_populates="retrieved_chunks")
    chunk = relationship("DocumentChunk")

    # Create an index on query_id and rank
    __table_args__ = (
        Index("ix_rag_query_chunks_query_id_rank", "query_id", "rank"),
    )

    def __repr__(self):
        return f"<RAGQueryChunk(query_id={self.query_id}, chunk_id={self.chunk_id}, rank={self.rank})>"


class WebsiteUsage(Base, TimestampMixin):
    """Model for tracking website usage for the admin dashboard."""
    __tablename__ = "website_usage"

    id = Column(Integer, primary_key=True, index=True)
    page_visited = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(String(255), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    visit_time = Column(DateTime, default=func.now(), nullable=False)
    time_spent = Column(Integer, nullable=True)  # Time spent on page in seconds
    
    def __repr__(self):
        return f"<WebsiteUsage(id={self.id}, page='{self.page_visited}', time='{self.visit_time}')>"

"""
Models package initialization.
This file ensures proper model loading order to avoid circular dependencies.
"""
# Import base models first
from .base import Base, TimestampMixin

# Import user models
from .user import User, UserRole

# Import property models
from .property import Property, PropertyImage

# Import client models
from .client import Client

# Import project models
from .project import Project, ProjectStatus

# Import report models
from .report import Report, ReportStatus

# Import RAG models
from .rag import (
    Document,
    DocumentChunk,
    RAGQuery,
    RAGQueryChunk,
    WebsiteUsage
)

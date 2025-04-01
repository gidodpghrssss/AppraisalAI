"""
Service dependencies for FastAPI dependency injection.
"""
from app.services.llm_service import LLMService
from app.services.property_data_service import PropertyDataService
from app.services.web_search_service import WebSearchService

# Singleton instances
_llm_service = None
_property_data_service = None
_web_search_service = None

def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

def get_property_data_service() -> PropertyDataService:
    """Get or create property data service instance."""
    global _property_data_service, _web_search_service
    if _property_data_service is None:
        if _web_search_service is None:
            _web_search_service = WebSearchService()
        _property_data_service = PropertyDataService(web_search_service=_web_search_service)
    return _property_data_service

def get_web_search_service() -> WebSearchService:
    """Get or create web search service instance."""
    global _web_search_service
    if _web_search_service is None:
        _web_search_service = WebSearchService()
    return _web_search_service

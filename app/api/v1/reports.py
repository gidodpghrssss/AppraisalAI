"""
Report generation endpoints for the Appraisal AI Agent.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from app.services.dependencies import get_property_data_service

router = APIRouter()

# Mock database for reports (in a real app, this would be a database)
REPORTS_DB = {}

class ReportBase(BaseModel):
    """Base model for report data."""
    property_id: str
    report_type: str = "summary"
    include_sections: Optional[List[str]] = None

class ReportCreate(ReportBase):
    """Model for creating a new report."""
    pass

class ReportUpdate(BaseModel):
    """Model for updating a report."""
    report_type: Optional[str] = None
    include_sections: Optional[List[str]] = None
    sections: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class Report(ReportBase):
    """Full report model with ID and timestamps."""
    id: str
    created_at: datetime
    updated_at: datetime
    sections: Dict[str, Any]
    status: str = "draft"
    appraiser_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    compliance_results: Optional[Dict[str, Any]] = None

@router.post("", response_model=Report)
async def create_report(
    report_data: ReportCreate,
    property_service = Depends(get_property_data_service)
):
    """
    Create a new appraisal report.
    """
    # Check if property exists
    try:
        property_data = await property_service.get_property_details(report_data.property_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Property not found: {str(e)}")
    
    # Generate report using tool
    from app.tools.tool_executor import _execute_report_generator
    
    try:
        report_result = await _execute_report_generator({
            "property_id": report_data.property_id,
            "report_type": report_data.report_type,
            "include_sections": report_data.include_sections or [
                "property_description",
                "valuation",
                "reconciliation",
                "certification"
            ]
        })
        
        report_id = report_result["report_id"]
        now = datetime.now()
        
        new_report = {
            "id": report_id,
            "property_id": report_data.property_id,
            "report_type": report_data.report_type,
            "include_sections": report_data.include_sections,
            "sections": report_result["sections"],
            "status": "draft",
            "created_at": now,
            "updated_at": now
        }
        
        REPORTS_DB[report_id] = new_report
        return new_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@router.get("", response_model=List[Report])
async def list_reports(
    property_id: Optional[str] = None,
    status: Optional[str] = None,
    appraiser_id: Optional[str] = None
):
    """
    List all reports with optional filtering.
    """
    reports = list(REPORTS_DB.values())
    
    # Apply filters
    if property_id:
        reports = [r for r in reports if r["property_id"] == property_id]
    
    if status:
        reports = [r for r in reports if r["status"] == status]
    
    if appraiser_id:
        reports = [r for r in reports if r.get("appraiser_id") == appraiser_id]
    
    return reports

@router.get("/{report_id}", response_model=Report)
async def get_report(report_id: str):
    """
    Get a specific report by ID.
    """
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return REPORTS_DB[report_id]

@router.put("/{report_id}", response_model=Report)
async def update_report(report_id: str, report_update: ReportUpdate):
    """
    Update a report.
    """
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report not found")
    
    current_report = REPORTS_DB[report_id]
    
    # Update fields that are provided
    update_data = report_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "sections" and isinstance(value, dict) and "sections" in current_report:
            # Merge sections
            for section_key, section_data in value.items():
                current_report["sections"][section_key] = section_data
        else:
            current_report[field] = value
    
    # Update the updated_at timestamp
    current_report["updated_at"] = datetime.now()
    
    REPORTS_DB[report_id] = current_report
    return current_report

@router.delete("/{report_id}")
async def delete_report(report_id: str):
    """
    Delete a report.
    """
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report not found")
    
    del REPORTS_DB[report_id]
    return {"message": "Report deleted successfully"}

@router.post("/{report_id}/submit")
async def submit_report(report_id: str):
    """
    Submit a report for review.
    """
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report not found")
    
    current_report = REPORTS_DB[report_id]
    
    # Check if report is in draft status
    if current_report["status"] != "draft":
        raise HTTPException(status_code=400, detail="Only draft reports can be submitted")
    
    # Update status
    current_report["status"] = "submitted"
    current_report["updated_at"] = datetime.now()
    
    return {"message": "Report submitted successfully", "report": current_report}

@router.post("/{report_id}/review")
async def review_report(
    report_id: str,
    reviewer_id: str,
    approved: bool,
    comments: Optional[str] = None
):
    """
    Review a submitted report.
    """
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report not found")
    
    current_report = REPORTS_DB[report_id]
    
    # Check if report is in submitted status
    if current_report["status"] != "submitted":
        raise HTTPException(status_code=400, detail="Only submitted reports can be reviewed")
    
    # Update report with review information
    current_report["reviewer_id"] = reviewer_id
    current_report["status"] = "approved" if approved else "rejected"
    current_report["review_comments"] = comments
    current_report["review_date"] = datetime.now()
    current_report["updated_at"] = datetime.now()
    
    return {
        "message": f"Report {current_report['status']}",
        "report": current_report
    }

@router.post("/{report_id}/finalize")
async def finalize_report(report_id: str):
    """
    Finalize an approved report.
    """
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report not found")
    
    current_report = REPORTS_DB[report_id]
    
    # Check if report is in approved status
    if current_report["status"] != "approved":
        raise HTTPException(status_code=400, detail="Only approved reports can be finalized")
    
    # Update status
    current_report["status"] = "final"
    current_report["finalized_at"] = datetime.now()
    current_report["updated_at"] = datetime.now()
    
    return {"message": "Report finalized successfully", "report": current_report}

@router.post("/{report_id}/check-compliance")
async def check_report_compliance(
    report_id: str,
    standards: Optional[List[str]] = None
):
    """
    Check if a report complies with specified standards.
    """
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Use compliance checker tool
    from app.tools.tool_executor import _execute_compliance_checker
    
    try:
        compliance_results = await _execute_compliance_checker({
            "report_id": report_id,
            "standards": standards or ["USPAP"]
        })
        
        # Update report with compliance results
        current_report = REPORTS_DB[report_id]
        current_report["compliance_results"] = compliance_results
        current_report["updated_at"] = datetime.now()
        
        return compliance_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking compliance: {str(e)}")

@router.get("/{report_id}/export")
async def export_report(
    report_id: str,
    format: str = "pdf"
):
    """
    Export a report in the specified format.
    """
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # In a real implementation, this would generate the report in the specified format
    # For demo purposes, we'll return a mock response
    
    formats = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xml": "application/xml",
        "json": "application/json"
    }
    
    if format not in formats:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
    
    report = REPORTS_DB[report_id]
    
    return {
        "report_id": report_id,
        "format": format,
        "content_type": formats[format],
        "filename": f"appraisal_report_{report_id}.{format}",
        "download_url": f"/api/v1/reports/{report_id}/download?format={format}",
        "generated_at": datetime.now().isoformat()
    }

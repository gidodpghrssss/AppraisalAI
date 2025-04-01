"""
Agent endpoints for the Appraisal AI Agent.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json

from app.services.llm_service import Message
from app.services.dependencies import get_llm_service, get_property_data_service
from app.tools.tool_registry import get_available_tools
from app.tools.tool_executor import execute_tool
from app.core.config import settings

router = APIRouter()

class AgentRequest(BaseModel):
    """Request model for agent interactions."""
    messages: List[Message]
    property_id: Optional[str] = None
    project_id: Optional[str] = None
    tools_to_use: Optional[List[str]] = None

class AgentResponse(BaseModel):
    """Response model for agent interactions."""
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    property_data: Optional[Dict[str, Any]] = None

@router.post("", response_model=AgentResponse)
async def query_agent(
    request: AgentRequest,
    llm_service = Depends(get_llm_service),
    property_service = Depends(get_property_data_service)
):
    """
    Query the appraisal AI agent.
    
    This endpoint processes user messages and returns AI-generated responses
    with optional tool calls for appraisal-related tasks.
    """
    # Prepare messages with system prompt
    system_message = Message(role="system", content=settings.SYSTEM_PROMPT)
    all_messages = [system_message] + request.messages
    
    # Get available tools based on request
    tools = get_available_tools(request.tools_to_use or settings.TOOLS_ENABLED)
    
    # Get property data if property_id is provided
    property_data = None
    if request.property_id:
        try:
            property_data = await property_service.get_property_details(request.property_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Property not found: {str(e)}")
    
    # Generate response with tools
    try:
        llm_response = await llm_service.generate_with_tools(
            messages=all_messages,
            tools=tools
        )
        
        # Extract response and tool calls
        choices = llm_response.get("choices", [{}])
        if not choices:
            raise ValueError("No choices in LLM response")
            
        message = choices[0].get("message", {})
        response_content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])
        
        # Handle tool calls if present and content is None
        if tool_calls and response_content is None:
            # Execute tool calls and get results
            tool_results = []
            for tool_call in tool_calls:
                if tool_call.get("type") == "function":
                    function_data = tool_call.get("function", {})
                    tool_name = function_data.get("name", "")
                    tool_args = function_data.get("arguments", "{}")
                    
                    try:
                        # Parse arguments
                        if isinstance(tool_args, str):
                            tool_args = json.loads(tool_args)
                        
                        # Execute the tool
                        result = await execute_tool(tool_name, tool_args)
                        
                        # Add result to tool results
                        tool_results.append({
                            "tool_call_id": tool_call.get("id", ""),
                            "role": "tool",
                            "name": tool_name,
                            "content": json.dumps(result)
                        })
                    except Exception as e:
                        tool_results.append({
                            "tool_call_id": tool_call.get("id", ""),
                            "role": "tool",
                            "name": tool_name,
                            "content": json.dumps({"error": str(e)})
                        })
            
            # If we have tool results, add them to messages and call LLM again
            if tool_results:
                # Add the assistant's message with tool calls
                all_messages.append(Message(
                    role="assistant",
                    content=""  # Content is empty for tool calls
                ))
                
                # Add tool results as messages
                for result in tool_results:
                    all_messages.append(Message(
                        role="tool",
                        content=result["content"],
                        name=result["name"],
                        tool_call_id=result["tool_call_id"]
                    ))
                
                # Call LLM again to get a response based on tool results
                try:
                    second_response = await llm_service.generate_completion(
                        messages=all_messages,
                        tools=[]  # No tools for the second call
                    )
                    
                    # Extract the final response
                    second_choices = second_response.get("choices", [{}])
                    if second_choices:
                        second_message = second_choices[0].get("message", {})
                        response_content = second_message.get("content", "")
                except Exception as e:
                    print(f"Error in second LLM call: {str(e)}")
                    response_content = f"I've analyzed your request and gathered the following information:\n\n"
                    
                    # Create a simple response based on tool results
                    for result in tool_results:
                        try:
                            result_data = json.loads(result["content"])
                            response_content += f"**{result['name']} results:**\n"
                            
                            # Format based on tool type
                            if result["name"] == "property_search":
                                properties = result_data.get("results", [])
                                response_content += f"Found {len(properties)} properties in {result_data.get('query', {}).get('location', 'the specified location')}.\n\n"
                            elif result["name"] == "market_analysis":
                                trends = result_data.get("trends", {})
                                if trends:
                                    response_content += f"Market in {trends.get('location', 'the specified location')} shows "
                                    price_change = trends.get("price_trends", {}).get("last_year", 0)
                                    response_content += f"{price_change}% price change over the last year.\n\n"
                            elif result["name"] == "valuation_calculator":
                                valuation = result_data.get("valuation", {})
                                if valuation:
                                    response_content += f"Estimated value: ${valuation.get('estimated_value', 0):,.2f}\n\n"
                            else:
                                response_content += f"{json.dumps(result_data, indent=2)}\n\n"
                        except:
                            response_content += f"Error parsing result for {result['name']}\n\n"
        
        # Ensure response_content is a string (not None)
        if response_content is None:
            response_content = "I apologize, but I couldn't generate a proper response. Please try again or rephrase your question."
            print(f"Warning: Received None response from LLM API. Full response: {llm_response}")
        
        return AgentResponse(
            response=response_content,
            tool_calls=tool_calls,
            property_data=property_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@router.post("/execute-tool")
async def execute_tool_endpoint(
    tool_call: Dict[str, Any],
    llm_service = Depends(get_llm_service)
):
    """
    Execute a tool call from the agent.
    
    This endpoint receives a tool call from the frontend and executes it,
    returning the result.
    """
    # Implementation for tool execution
    tool_id = tool_call.get("id")
    tool_name = tool_call.get("function", {}).get("name")
    tool_args = tool_call.get("function", {}).get("arguments", {})
    
    try:
        result = await execute_tool(tool_name, tool_args)
        return {"tool_id": tool_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing tool {tool_name}: {str(e)}")

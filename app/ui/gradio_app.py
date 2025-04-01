"""
Gradio UI for the Appraisal AI Agent.
"""
import gradio as gr
import httpx
import os
import json
from typing import List, Dict, Any
import asyncio

# Import services
from app.services.llm_service import LLMService, Message
from app.core.config import settings

# Initialize services
llm_service = LLMService()

class AppraisalAIUI:
    """Gradio UI for the Appraisal AI Agent."""
    
    def __init__(self):
        """Initialize the UI."""
        # Use environment variables or fallback to localhost
        api_host = os.getenv("API_HOST", "localhost")
        api_port = int(os.getenv("PORT", "8001"))
        self.api_url = f"http://{api_host}:{api_port}{settings.API_V1_STR}"
        self.conversation_history = []
        self.current_property_id = None
        self.current_project_id = None
        print(f"UI initialized with API URL: {self.api_url}")
    
    async def chat_with_agent(self, message: str, history: List[List[str]]) -> List[List[str]]:
        """
        Chat with the AI agent.
        
        Args:
            message: User message
            history: Chat history
            
        Returns:
            Updated chat history
        """
        if not message.strip():
            return history
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Prepare messages for the agent
        messages = [Message(role=msg["role"], content=msg["content"]) for msg in self.conversation_history]
        
        try:
            # Call the agent API
            async with httpx.AsyncClient(timeout=60.0) as client:
                print(f"Sending request to {self.api_url}/agent")
                response = await client.post(
                    f"{self.api_url}/agent",
                    json={
                        "messages": [msg.dict() for msg in messages],
                        "property_id": self.current_property_id,
                        "project_id": self.current_project_id
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    agent_response = result.get("response", "Sorry, I couldn't generate a response.")
                    
                    # Add agent response to conversation history
                    self.conversation_history.append({"role": "assistant", "content": agent_response})
                    
                    # Update history for Gradio (using traditional format)
                    history.append([message, agent_response])
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    print(f"API Error: {error_msg}")
                    history.append([message, error_msg])
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"Exception: {error_msg}")
            history.append([message, error_msg])
        
        return history
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
        return [], ""
    
    def search_properties(
        self,
        location: str,
        property_type: str,
        min_price: float,
        max_price: float,
        min_size: float,
        max_size: float
    ) -> str:
        """
        Search for properties based on criteria.
        
        Args:
            property_type: Type of property
            min_price: Minimum price
            max_price: Maximum price
            min_size: Minimum size
            max_size: Maximum size
            
        Returns:
            Search results as formatted string
        """
        try:
            # Call the property search tool
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.api_url}/properties/search",
                    json={
                        "tool_call": {
                            "name": "search_properties",
                            "arguments": json.dumps({
                                "location": location,
                                "property_type": property_type,
                                "min_price": min_price if min_price > 0 else None,
                                "max_price": max_price if max_price > 0 else None,
                                "min_size": min_size if min_size > 0 else None,
                                "max_size": max_size if max_size > 0 else None
                            })
                        }
                    }
                )
                
                if response.status_code != 200:
                    return f"Error searching properties: {response.text}"
                
                result = response.json().get("result", {})
                properties = result.get("results", [])
                
                if not properties:
                    return "No properties found matching the criteria."
                
                # Format results
                formatted_results = f"Found {len(properties)} properties matching your criteria:\n\n"
                
                for i, prop in enumerate(properties, 1):
                    formatted_results += f"**Property {i}:**\n"
                    formatted_results += f"- Address: {prop.get('address')}\n"
                    formatted_results += f"- Type: {prop.get('type')}\n"
                    formatted_results += f"- Size: {prop.get('size')} sq ft\n"
                    formatted_results += f"- Price: ${prop.get('price'):,}\n"
                    formatted_results += f"- Price per sq ft: ${prop.get('price_per_sqft'):,}\n"
                    formatted_results += f"- Year built: {prop.get('year_built')}\n"
                    
                    if property_type == "residential":
                        formatted_results += f"- Bedrooms: {prop.get('bedrooms')}\n"
                        formatted_results += f"- Bathrooms: {prop.get('bathrooms')}\n"
                    
                    formatted_results += "\n"
                
                return formatted_results
        except Exception as e:
            return f"Error searching properties: {str(e)}"
    
    async def get_market_analysis(self, location: str, property_type: str) -> str:
        """
        Get market analysis for a location and property type.
        
        Args:
            location: Location to analyze
            property_type: Type of property
            
        Returns:
            Market analysis as formatted string
        """
        try:
            # Call the market analysis tool
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/market-analysis",
                    json={
                        "location": location,
                        "property_type": property_type
                    }
                )
                
                if response.status_code != 200:
                    return f"Error getting market analysis: {response.text}"
                
                result = response.json()
                analysis = result.get("analysis", "No analysis available.")
                return analysis
        except Exception as e:
            return f"Error getting market analysis: {str(e)}"
    
    def create_ui(self) -> gr.Blocks:
        """
        Create the Gradio UI.
        
        Returns:
            Gradio Blocks interface
        """
        # Create Gradio app WITHOUT queue
        app = gr.Blocks(
            title="Appraisal AI Agent",
            css="footer {visibility: hidden}"
        )
        
        with app:
            gr.Markdown("# Appraisal AI Agent")
            gr.Markdown(f"""
            An AI-powered assistant for real estate appraisers using {settings.MODEL_NAME}
            
            **Key Features:**
            - Property search and valuation
            - Market analysis and trends
            - Appraisal report generation
            - Regulatory compliance checking
            - Project management and CRM
            
            Powered by {settings.MODEL_NAME} through Nebius inference API.
            """)
            
            with gr.Tabs():
                with gr.TabItem("Chat with AI Agent"):
                    chatbot = gr.Chatbot(
                        label="Chatbot",
                        bubble_full_width=False,
                        show_copy_button=True
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            show_label=False,
                            placeholder="Ask me anything about property appraisal...",
                            container=False
                        )
                        submit = gr.Button("Send")
                    
                    # Set up event handlers without queue
                    submit_event = msg.submit(
                        self.chat_with_agent,
                        inputs=[msg, chatbot],
                        outputs=chatbot,
                        queue=False
                    )
                    submit_click = submit.click(
                        self.chat_with_agent,
                        inputs=[msg, chatbot],
                        outputs=chatbot,
                        queue=False
                    )
                    
                    # Clear message box after sending
                    submit_event.then(lambda: "", None, msg, queue=False)
                    submit_click.then(lambda: "", None, msg, queue=False)
                    
                    # Clear button
                    clear = gr.Button("Clear")
                    clear.click(
                        self.clear_conversation,
                        None,
                        [chatbot, msg],
                        queue=False
                    )
                
                with gr.TabItem("Property Search"):
                    with gr.Row():
                        with gr.Column():
                            location = gr.Textbox(label="Location", placeholder="e.g., New York, NY")
                            property_type = gr.Dropdown(
                                label="Property Type",
                                choices=["Residential", "Commercial", "Industrial", "Land"],
                                value="Residential"
                            )
                            min_price = gr.Number(label="Min Price ($)", value=0)
                            max_price = gr.Number(label="Max Price ($)", value=0)
                            min_size = gr.Number(label="Min Size (sq ft)", value=0)
                            max_size = gr.Number(label="Max Size (sq ft)", value=0)
                            search_btn = gr.Button("Search Properties")
                        
                        with gr.Column():
                            property_results = gr.Markdown(label="Search Results")
                    
                    search_btn.click(
                        self.search_properties,
                        inputs=[location, property_type, min_price, max_price, min_size, max_size],
                        outputs=property_results,
                        api_name="property_search",
                        queue=False
                    )
                
                with gr.TabItem("Market Analysis"):
                    with gr.Row():
                        with gr.Column():
                            market_location = gr.Textbox(label="Location", placeholder="e.g., New York, NY")
                            market_property_type = gr.Dropdown(
                                label="Property Type",
                                choices=["Residential", "Commercial", "Industrial", "Land"],
                                value="Residential"
                            )
                            market_analysis_btn = gr.Button("Get Market Analysis")
                        
                        with gr.Column():
                            market_results = gr.Markdown(label="Market Analysis")
                    
                    market_analysis_btn.click(
                        self.get_market_analysis,
                        inputs=[market_location, market_property_type],
                        outputs=market_results,
                        api_name="market_analysis",
                        queue=False
                    )
            
            gr.Markdown("## About Appraisal AI Agent")
            gr.Markdown(f"""
            The Appraisal AI Agent is a powerful tool for real estate appraisers, combining AI with industry expertise to streamline the appraisal process.
            
            **Key Features:**
            - Property search and valuation
            - Market analysis and trends
            - Appraisal report generation
            - Regulatory compliance checking
            - Project management and CRM
            
            Powered by {settings.MODEL_NAME} through Nebius inference API.
            """)
        
        return app

# Create UI instance
ui = AppraisalAIUI()

# Get Gradio app
app = ui.create_ui()

if __name__ == "__main__":
    # Launch with share=True to avoid localhost access issues
    app.launch(server_name="0.0.0.0", server_port=7860, share=True)

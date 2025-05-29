from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
import os
import sys
from io import StringIO
import re
from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

def create_travel_agent():
    """Create and return a travel planning agent"""
    return Agent(
        model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
        description="""You are an expert travel planner and local guide. Your role is to:
        1. Help users plan their trips step by step:
           - First, suggest specific streets, markets, or areas to stay in (like Mall Road in Manali, Colaba Causeway in Mumbai)
           - Then, recommend specific hotels and restaurants in the chosen area
           - Finally, create a detailed day-by-day itinerary
        2. For each specific location suggestion, provide:
           - Exact location and landmarks
           - Safety information
           - Walking distance to major attractions
           - Transportation options
           - Local atmosphere and vibe
           - Price range for accommodations
        3. For hotels, include:
           - Exact address
           - Price range
           - Amenities
           - Reviews
           - Location benefits
           - Booking links when available
        4. For restaurants, provide:
           - Exact location
           - Cuisine type
           - Price range
           - Popular dishes
           - Opening hours
           - Reservation information
        5. For itineraries:
           - Create a balanced schedule
           - Include walking/travel times between locations
           - Suggest optimal visiting hours
           - Include backup options for bad weather
           - Allow for customization
        6. Always consider:
           - User's budget
           - Travel preferences
           - Time of year
           - Local events
           - Transportation options
        7. Provide helpful links and resources for:
           - Booking accommodations
           - Restaurant reservations
           - Attraction tickets
           - Local transportation
           - Weather forecasts
        8. IMPORTANT: Format all responses in clear, readable markdown with appropriate headings, bullet points, and sections.""",
        tools=[DuckDuckGoTools()],
        markdown=True
    )

def capture_agent_response(agent, prompt):
    """Capture the agent's response as a string"""
    # Redirect stdout to capture the response
    old_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output
    
    # Get the response
    agent.print_response(prompt)
    
    # Restore stdout
    sys.stdout = old_stdout
    
    # Get the captured output and clean it
    response = captured_output.getvalue().strip()
    
    # Remove ANSI color codes and box-drawing characters
    # Remove ANSI escape sequences
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    response = ansi_escape.sub('', response)
    
    # Remove any remaining non-printable characters
    response = ''.join(char for char in response if char.isprintable() or char.isspace())
    
    # Remove the "Message" part and clean up extra spaces
    response = re.sub(r'^\s*Message\s*', '', response)
    response = re.sub(r'\n\s*\n\s*\n', '\n\n', response)  # Remove extra blank lines
    response = response.strip()
    
    return response

def get_location_suggestions(agent, destination, days):
    """Get location suggestions for the destination"""
    prompt = f"""Please suggest 3-4 specific streets, markets, or areas to stay in {destination} for a {days}-day trip. 
    For each area, include:
    - Name and exact location (format as **Location Name**)
    - Nearby landmarks
    - Pros and cons
    - Safety information
    - Walking distances to major attractions
    - Transportation options
    - Local atmosphere and vibe
    - Price range for accommodations
    
    Format your response in clear markdown with headings and bullet points. Make sure to use **bold** for location names."""
    return capture_agent_response(agent, prompt)

def get_hotel_suggestions(agent, chosen_area, destination):
    """Get hotel suggestions for the chosen area"""
    prompt = f"""Please suggest 3-4 specific hotels in {chosen_area}, {destination}.
    For each hotel, include:
    - Name and exact address (format as **Hotel Name**)
    - Price range
    - Amenities
    - Location benefits
    - Booking information
    
    Format your response in clear markdown with separate sections for each hotel."""
    return capture_agent_response(agent, prompt)

def get_restaurant_suggestions(agent, chosen_area, destination):
    """Get restaurant suggestions for the chosen area"""
    prompt = f"""Please suggest 3-4 specific restaurants in {chosen_area}, {destination}.
    For each restaurant, include:
    - Name and exact location (format as **Restaurant Name**)
    - Cuisine type
    - Price range
    - Popular dishes
    - Opening hours
    - Reservation information
    
    Format your response in clear markdown with separate sections for each restaurant."""
    return capture_agent_response(agent, prompt)

def get_itinerary(agent, destination, chosen_area, days):
    """Get detailed itinerary for the trip"""
    prompt = f"""Please create a detailed {days}-day itinerary for {destination}, staying in {chosen_area}.
    For each day, include:
    - A balanced schedule with time slots
    - Activities and their locations
    - Duration of each activity
    - Estimated costs
    - Transportation details
    - Restaurant recommendations for each meal
    - Backup plans for bad weather
    
    Format your response in clear markdown with daily sections and bullet points.
    Make sure to use **bold** for important locations and activities."""
    return capture_agent_response(agent, prompt) 
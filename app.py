import streamlit as st
from travel_agent import (
    create_travel_agent,
    get_location_suggestions,
    get_hotel_suggestions,
    get_restaurant_suggestions,
    get_itinerary
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

def generate_pdf(destination, chosen_area, days, hotel_suggestions, restaurant_suggestions, itinerary):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1E88E5')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=12,
        textColor=colors.HexColor('#2E7D32')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
        leading=14
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=12,
        leftIndent=20,
        spaceAfter=6,
        leading=14
    )

    story = []

    # Title
    story.append(Paragraph(f"Your Trip to {destination}", title_style))
    story.append(Spacer(1, 20))

    # Trip Details
    story.append(Paragraph("Trip Details", heading_style))
    story.append(Paragraph(f"Destination: {destination}", normal_style))
    story.append(Paragraph(f"Area: {chosen_area}", normal_style))
    story.append(Paragraph(f"Duration: {days} days", normal_style))
    story.append(Spacer(1, 20))

    # Hotels
    story.append(Paragraph("Accommodation Options", heading_style))
    
    # Process hotel suggestions
    hotel_lines = hotel_suggestions.split('\n')
    for line in hotel_lines:
        if line.strip():
            if line.strip().startswith('•'):
                story.append(Paragraph(line.strip(), bullet_style))
            elif line.strip().startswith('**'):
                # Handle bold text
                text = line.strip().replace('**', '')
                story.append(Paragraph(f"<b>{text}</b>", normal_style))
            else:
                story.append(Paragraph(line.strip(), normal_style))
    
    story.append(Spacer(1, 20))

    # Restaurants
    story.append(Paragraph("Dining Options", heading_style))
    
    # Process restaurant suggestions
    restaurant_lines = restaurant_suggestions.split('\n')
    for line in restaurant_lines:
        if line.strip():
            if line.strip().startswith('•'):
                story.append(Paragraph(line.strip(), bullet_style))
            elif line.strip().startswith('**'):
                # Handle bold text
                text = line.strip().replace('**', '')
                story.append(Paragraph(f"<b>{text}</b>", normal_style))
            else:
                story.append(Paragraph(line.strip(), normal_style))
    
    story.append(Spacer(1, 20))

    # Itinerary
    story.append(Paragraph("Your Itinerary", heading_style))
    
    # Process itinerary
    itinerary_lines = itinerary.split('\n')
    for line in itinerary_lines:
        if line.strip():
            if line.strip().startswith('•'):
                story.append(Paragraph(line.strip(), bullet_style))
            elif line.strip().startswith('**'):
                # Handle bold text
                text = line.strip().replace('**', '')
                story.append(Paragraph(f"<b>{text}</b>", normal_style))
            else:
                story.append(Paragraph(line.strip(), normal_style))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def main():
    # Configure Streamlit page
    st.set_page_config(layout="wide")
    
    # Add custom CSS to improve text wrapping and readability
    st.markdown("""
        <style>
        .stCodeBlock {
            max-width: 100%;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .stMarkdown {
            max-width: 100%;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        /* Make important text elements bold and bigger */
        .stMarkdown strong {
            font-size: 1.2em;
            font-weight: 700;
        }
        /* Style for location names and important headings */
        .location-name {
            font-size: 1.3em;
            font-weight: 700;
            color: #1E88E5;
        }
        /* Style for hotel and restaurant names */
        .venue-name {
            font-size: 1.2em;
            font-weight: 600;
            color: #2E7D32;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🌍 Go Trip - AI Trip Companion")
    st.write("Let's plan your perfect trip! I'll help you with location selection, accommodations, dining, and a detailed itinerary.")
    
    # Initialize the travel agent
    if 'agent' not in st.session_state:
        st.session_state.agent = create_travel_agent()
    
    # Initialize session state variables
    if 'show_plan' not in st.session_state:
        st.session_state.show_plan = False
    if 'location_suggestions' not in st.session_state:
        st.session_state.location_suggestions = None
    if 'chosen_area' not in st.session_state:
        st.session_state.chosen_area = None
    if 'destination' not in st.session_state:
        st.session_state.destination = None
    if 'days' not in st.session_state:
        st.session_state.days = None
    if 'hotel_suggestions' not in st.session_state:
        st.session_state.hotel_suggestions = None
    if 'restaurant_suggestions' not in st.session_state:
        st.session_state.restaurant_suggestions = None
    if 'itinerary' not in st.session_state:
        st.session_state.itinerary = None
    
    # Get destination and duration
    destination = st.text_input("📍 Where would you like to go?")
    days = st.number_input("📅 How many days will you be staying?", min_value=1, step=1)
    
    # Get overall budget
    st.subheader("💰 Budget Planning")
    daily_budget = st.text_input("What's your daily budget per person (in local currency)?")
    
    if st.button("Start Planning"):
        if destination and days and daily_budget:
            # Store destination and days in session state
            st.session_state.destination = destination
            st.session_state.days = days
            # Get initial location suggestions
            location_suggestions = get_location_suggestions(st.session_state.agent, destination, days)
            st.session_state.location_suggestions = location_suggestions
        else:
            st.warning("Please fill in all the required information to start planning.")

    # Show location suggestions if they exist
    if st.session_state.location_suggestions:
        st.subheader(f"🔍 Suggested areas to stay in {st.session_state.destination}")
        st.code(st.session_state.location_suggestions, language="markdown")

        # Area selection
        chosen_area = st.text_input("🏨 Which specific area would you like to stay in?")
        if chosen_area:
            st.session_state.chosen_area = chosen_area
        
        # Always show the plan button if we have location suggestions
        if st.button("🔍 Show Accommodations & Plan"):
            if st.session_state.chosen_area:
                st.session_state.show_plan = True
            else:
                st.warning("Please select an area first!")

    # Show the plan section if the button was clicked
    if st.session_state.show_plan and st.session_state.chosen_area:
        chosen_area = st.session_state.chosen_area
        # Create tabs for better organization
        tab1, tab2, tab3 = st.tabs(["🏨 Accommodations", "🍽️ Dining", "📅 Complete Itinerary"])
        
        with tab1:
            st.subheader(f"🏨 Hotels in {chosen_area}")
            hotel_suggestions = get_hotel_suggestions(st.session_state.agent, chosen_area, st.session_state.destination)
            st.session_state.hotel_suggestions = hotel_suggestions
            st.code(hotel_suggestions, language="markdown")
            
            # Add hotel selection
            # selected_hotel = st.text_input("Which hotel would you like to stay at?")
        
        with tab2:
            st.subheader(f"🍽️ Restaurants in {chosen_area}")
            restaurant_suggestions = get_restaurant_suggestions(st.session_state.agent, chosen_area, st.session_state.destination)
            st.session_state.restaurant_suggestions = restaurant_suggestions
            st.code(restaurant_suggestions, language="markdown")
        
        with tab3:
            st.subheader(f"📅 Your Complete {st.session_state.days}-Day Itinerary")
            
            # Add date selection
            start_date = st.date_input("When would you like to start your trip?")
            
            if start_date:
                itinerary = get_itinerary(st.session_state.agent, st.session_state.destination, chosen_area, st.session_state.days)
                st.session_state.itinerary = itinerary
                st.code(itinerary, language="markdown")
                
                # Add customization options
                st.subheader("✨ Customize Your Plan")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("📝 Adjust Schedule")
                    st.write("- Change activity timings")
                    st.write("- Add or remove attractions")
                    st.write("- Modify transportation plans")
                
                with col2:
                    st.write("💰 Budget Adjustments")
                    st.write("- Modify daily budget")
                    st.write("- Change accommodation preferences")
                    st.write("- Adjust dining options")
                
                # Add export option
                if st.button("📥 Export Plan"):
                    if all([st.session_state.hotel_suggestions, st.session_state.restaurant_suggestions, st.session_state.itinerary]):
                        pdf_data = generate_pdf(
                            st.session_state.destination,
                            st.session_state.chosen_area,
                            st.session_state.days,
                            st.session_state.hotel_suggestions,
                            st.session_state.restaurant_suggestions,
                            st.session_state.itinerary
                        )
                        st.download_button(
                            label="Download PDF",
                            data=pdf_data,
                            file_name="travel_plan.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.warning("Please wait for all sections to load before exporting the plan.")

if __name__ == "__main__":
    main() 
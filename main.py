import streamlit as st
from serpapi import GoogleSearch
import google.generativeai as genai
from langchain_core.prompts import ChatPromptTemplate
import os
import dotenv

# Load environment variables
dotenv.load_dotenv()

# System prompt for filtering Google scraped data
system_prompt = """
You are a helpful assistant. Your role is to filter the Google scraped data and provide the best result to the user.

Rules:
1. You are a helpful assistant.
2. You must filter the data and give the best result to the user.
3. Do not provide any irrelevant information or suggestions except event-related information from the data.
4. Provide a to-the-point and clear response.
"""

# Prompt template for the agent
agent_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", """
    User Input: {user_input}
    Scraped Data: {scraped_data}
    
    ---
    Generate a response that:
    1. Is relevant to the user input
    2. Is concise and to the point
    3. Does not include any irrelevant information or suggestions
    4. Uses only the provided scraped data for event-related information
    """)
])

def get_data(location):
    """Get upcoming events for a specific location using SerpApi."""
    try:
        # Try to get API key from secrets first, then from environment variables
        serpapi_key = os.getenv("SERPAPI_KEY") or st.secrets.get("SERPAPI_KEY")
        
        if not serpapi_key:
            st.error("SERPAPI_KEY not found. Please configure your API keys.")
            return None

        params = {
            "api_key": serpapi_key,
            "engine": "google",
            "q": f"upcoming events in {location}",
            "google_domain": "google.co.in",
            "gl": "in",
            "hl": "en",
            "tbs": "events",
            "tbm": "nws",
            "safe": "off"
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        if 'news_results' not in results or not results['news_results']:
            return None
        
        return [{
            'title': item.get('title', 'No title'),
            'link': item.get('link', '#'),
            'source': item.get('source', 'Unknown source'),
            'date': item.get('date', 'Date not available'),
            'snippet': item.get('snippet', 'No description')
        } for item in results['news_results'][:5]]  # Get first 5 results
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def ai_filtering(user_input, scraped_data):
    """Filter scraped data using Gemini AI to provide a relevant response."""
    try:
        # Try to get API key from secrets first, then from environment variables
        google_api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

        
        if not google_api_key:
            st.error("GOOGLE_API_KEY not found. Please configure your API keys.")
            return None

        genai.configure(api_key=google_api_key)
        
        generation_config = {
            "temperature": 0.4,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 500,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config
        )
        
        prompt = agent_template.format(
            user_input=user_input,
            scraped_data=str(scraped_data) if scraped_data else "No event data available."
        )
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error in AI filtering: {e}"

def main():
    st.set_page_config(page_title="Event Finder", page_icon="🎪")
    st.title("Local Event Finder")
    st.write("Discover upcoming events in your area!")
    
    location = st.text_input("Enter a location:", placeholder="e.g., Mumbai, New York, London...")
    
    if st.button("Find Events"):
        if location:
            with st.spinner("Searching for events..."):
                scraped_data = get_data(location)
                
            if not scraped_data:
                st.warning("No events found for this location.")
                return
                
            st.subheader("📅 Upcoming Events Summary")
            with st.expander("View Raw Event Data", expanded=False):
                for idx, event in enumerate(scraped_data, 1):
                    st.markdown(f"""
                    **Event {idx}**
                    - **Title**: {event['title']}
                    - **Source**: {event['source']}
                    - **Date**: {event['date']}
                    - **Description**: {event['snippet']}
                    - **Link**: {event['link']}
                    """)
            
            with st.spinner("Analyzing events..."):
                user_input = f"upcoming events in {location}"
                filtered_response = ai_filtering(user_input, scraped_data)
                
            st.subheader("✨ Curated Event Suggestions")
            st.markdown(filtered_response)
            
        else:
            st.warning("Please enter a location to search for events.")

if __name__ == "__main__":
    main()
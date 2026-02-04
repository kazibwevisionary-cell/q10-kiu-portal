import streamlit as st
import pandas as pd
from supabase import create_client
import re

# 1. UI CONFIGURATION (Must be the very first line)
st.set_page_config(page_title="KIU Portal", layout="wide")

# 2. DATABASE CONNECTION (Hardcoded for simplicity)
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" 

@st.cache_resource
def get_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

supabase = get_supabase()

# 3. HELPER FUNCTIONS
def convert_drive_url(url):
    """Converts Google Drive 'Share' links to direct images"""
    if url and isinstance(url, str) and "drive.google.com" in url:
        match = re.search(r'[-\w]{25,}', url)
        if match:
            return f"https://drive.google.com/uc?id={match.group()}"
    return url

# 4. CUSTOM STYLING
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&display=swap');
    .main-title {
        font-family: 'Comic Neue', cursive;
        font-size: 3rem;
        color: #FF4B4B;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">KIU Learning Portal</h1>', unsafe_allow_html=True)

# 5. MAIN APP LOGIC
if supabase:
    search_query = st.text_input("🔍 Search for a course program", placeholder="e.g. Computer Science")

    try:
        if not search_query:
            st.subheader("Explore Courses")
            # Fetch data - we only ask for course_program for the main grid
            response = supabase.table("materials").select("*").execute()
            
            if response.data:
                # Use a set to get unique programs and handle missing keys safely
                unique_programs = list(set([item.get('course_program') for item in response.data if item.get('course_program')]))
                
                # Setup 4 columns for a cleaner mobile look
                cols = st.columns(min(len(unique_programs), 4) if unique_programs else 1)
                for i, program in enumerate(unique_programs):
                    with cols[i % 4]:
                        # Use an info box instead of st.image for maximum stability
                        st.info(f"📚 {program}")
            else:
                st.write("No data found in the materials table.")
        
        else:
            # Search Results
            st.subheader(f"Results for '{search_query}'")
            results = supabase.table("materials").select("*").ilike("course_program", f"%{search_query}%").execute()
            
            if results.data:
                # width='stretch' is the new standard instead of use_container_width
                st.dataframe(pd.DataFrame(results.data), width='stretch')
            else:
                st.warning("No matches found.")

    except Exception as e:
        # This catch-all prevents the app from showing a red traceback to users
        st.error("Database is syncing. Please refresh the page in a moment.")
        print(f"Error details: {e}")

else:
    st.error("Could not verify database credentials.")

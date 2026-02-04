import streamlit as st
import pandas as pd
from supabase import create_client
import re

# 1. UI CONFIGURATION (Must be the very first command)
st.set_page_config(page_title="KIU Portal", layout="wide")

# 2. DATABASE CONNECTION
# Using your provided credentials
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" 

@st.cache_resource
def get_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

supabase = get_supabase()

# 3. HELPER FUNCTIONS
def convert_drive_url(url):
    """Converts Google Drive 'Share' links to 'Direct Image' links"""
    if url and "drive.google.com" in url:
        match = re.search(r'[-\w]{25,}', url)
        if match:
            return f"https://drive.google.com/uc?id={match.group()}"
    return url

# 4. STYLING
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&display=swap');
    .main-title {
        font-family: 'Comic Neue', cursive;
        font-size: 3rem;
        color: #FF4B4B;
        text-align: center;
    }
    .stInfo {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">KIU Learning Portal</h1>', unsafe_allow_html=True)

# 5. MAIN APP LOGIC
if supabase:
    search_query = st.text_input("🔍 Search for your course program (e.g., Computer Science)", placeholder="Type here...")

    try:
        if not search_query:
            st.subheader("Explore Programs")
            
            # We fetch 'course_program' and 'image_url'. 
            # If image_url is missing in your DB, .get() will handle it safely.
            response = supabase.table("materials").select("course_program, image_url").execute()
            
            if response.data:
                # Get unique courses to avoid duplicates
                unique_data = {}
                for item in response.data:
                    course = item.get('course_program')
                    if course and course not in unique_data:
                        unique_data[course] = item.get('image_url')

                # Display in a 4-column grid
                courses = list(unique_data.keys())
                cols = st.columns(4)
                for i, course in enumerate(courses):
                    with cols[i % 4]:
                        img = convert_drive_url(unique_data[course])
                        if img:
                            st.image(img, use_container_width=True)
                        else:
                            st.info(f"📚 {course}")
            else:
                st.write("No courses found in database yet.")
        
        else:
            # Search Results Logic
            st.subheader(f"Results for '{search_query}'")
            results = supabase.table("materials").select("*").ilike("course_program", f"%{search_query}%").execute()
            
            if results.data:
                df = pd.DataFrame(results.data)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No matches found. Try a different keyword.")

    except Exception as e:
        st.warning("The database is still updating. Please refresh in a moment.")
        # Logging the exact error for your debug console
        print(f"DEBUG: {e}")

else:
    st.error("Authentication Failed. Check your Supabase Keys.")

# NO GRADIO .launch() CALLS HERE

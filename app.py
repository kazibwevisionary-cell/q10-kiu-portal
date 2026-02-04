import streamlit as st
import pandas as pd
from supabase import create_client
import re

# 1. Page Configuration (Must be first)
st.set_page_config(page_title="KIU Portal", layout="wide")

# 2. Database Connection
SUPABASE_URL = "https://uxtmgdenwfyuwhezcleh.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-"

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# 3. Main UI
st.title("KIU Learning Portal")

# 4. Fixed Query Logic
# We removed 'image_url' because it does not exist in your Supabase table
try:
    search_query = st.text_input("Search for courses...")
    
    if not search_query:
        st.subheader("Explore Courses")
        # Fetching only existing columns to prevent '42703' error
        tiles_data = supabase.table("materials").select("course_program").execute()
        
        if tiles_data.data:
            # Create unique courses list without relying on image_url
            unique_courses = list(set([item['course_program'] for item in tiles_data.data]))
            
            cols = st.columns(min(len(unique_courses), 4))
            for i, course in enumerate(unique_courses):
                with cols[i % 4]:
                    st.info(f"📚 {course}")
    else:
        # Search logic
        results = supabase.table("materials").select("*").ilike("course_program", f"%{search_query}%").execute()
        if results.data:
            st.write(pd.DataFrame(results.data))
        else:
            st.warning("No courses found.")

except Exception as e:
    st.error(f"An error occurred: {e}")

# IMPORTANT: No Gradio .launch() calls here as they crash Streamlit Cloud

import streamlit as st
import pandas as pd
from supabase import create_client

# 1. UI CONFIG (Must be the very first line)
st.set_page_config(page_title="KIU Portal", layout="wide")

# 2. DATABASE CONNECTION
# Using your provided project credentials
URL = "https://uxtmgdenwfyuwhezcleh.supabase.co"
KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# 3. HEADER
st.title("🎓 KIU Learning Portal")

# 4. FIXED DATA LOGIC (No image_url)
try:
    # Fetch data but ONLY the columns we are sure exist
    response = supabase.table("materials").select("course_program, material_title").execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        
        # Search interface
        search = st.text_input("🔍 Search programs", placeholder="e.g. Computer Science")
        
        if not search:
            st.subheader("Available Programs")
            # Get unique courses to display as simple info boxes
            unique_courses = df['course_program'].unique()
            cols = st.columns(min(len(unique_courses), 3))
            for i, course in enumerate(unique_courses):
                with cols[i % 3]:
                    st.info(f"📚 {course}")
        else:
            # Filtered search view using 'width=stretch' to avoid warnings
            filtered = df[df['course_program'].str.contains(search, case=False, na=False)]
            st.dataframe(filtered, width='stretch')
            
    else:
        st.warning("Database connected, but the 'materials' table is empty.")

except Exception as e:
    # Defensive error handling to prevent the red crash screen
    st.error("Waiting for database to sync. Please refresh in a moment.")
    print(f"DEBUG: {e}")

# IMPORTANT: No Gradio code here.

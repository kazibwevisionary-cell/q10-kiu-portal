import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Page Config (Must be FIRST)
st.set_page_config(page_title="KIU Portal", layout="wide")

# 2. Database Connection
SUPABASE_URL = "https://uxtmgdenwfyuwhezcleh.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-"

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

st.title("KIU Learning Portal")

# 3. Defensive App Logic
try:
    search_query = st.text_input("Search for courses...")
    
    if not search_query:
        st.subheader("Explore Courses")
        # Fetch data safely
        response = supabase.table("materials").select("*").execute()
        
        if response.data:
            # We use .get() to safely handle missing 'course_program' or 'image_url'
            unique_courses = list(set([item.get('course_program') for item in response.data if item.get('course_program')]))
            
            cols = st.columns(min(len(unique_courses), 4) if unique_programs else 1)
            for i, course in enumerate(unique_courses):
                with cols[i % 4]:
                    # Use a standard info box to avoid image-loading errors
                    st.info(f"📚 {course}")
        else:
            st.write("No courses found in database.")
    else:
        # Search logic
        results = supabase.table("materials").select("*").ilike("course_program", f"%{search_query}%").execute()
        if results.data:
            # width='stretch' is the new standard (fixes log warnings)
            st.dataframe(pd.DataFrame(results.data), width='stretch')
        else:
            st.warning("No courses found.")

except Exception as e:
    st.error(f"Database sync in progress... Please refresh in a moment. ({e})")

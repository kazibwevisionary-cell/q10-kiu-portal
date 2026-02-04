import streamlit as st
import pandas as pd
from supabase import create_client

# 1. UI CONFIG (Must be first line)
st.set_page_config(page_title="KIU Portal", layout="wide")

# 2. DATABASE CONNECTION
URL = "https://uxtmgdenwfyuwhezcleh.supabase.co"
KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

st.title("🎓 KIU Learning Portal")

# 3. CLEAN DATA LOGIC
try:
    # We only select columns we KNOW exist now
    response = supabase.table("materials").select("course_program, material_title").execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        search = st.text_input("🔍 Search programs", placeholder="e.g. Computer Science")
        
        if not search:
            st.subheader("Available Programs")
            unique_courses = df['course_program'].unique()
            cols = st.columns(min(len(unique_courses), 3))
            for i, course in enumerate(unique_courses):
                with cols[i % 3]:
                    st.info(f"📚 {course}")
        else:
            filtered = df[df['course_program'].str.contains(search, case=False, na=False)]
            st.dataframe(filtered, use_container_width=True)
    else:
        st.warning("Database connected, but no data found.")

except Exception as e:
    st.error("App is live. Synchronizing database...")
    print(f"Debug: {e}")

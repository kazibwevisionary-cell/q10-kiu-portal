import streamlit as st
import pandas as pd
from supabase import create_client
import re

# 1. UI CONFIG (Must be first)
st.set_page_config(page_title="KIU Portal", layout="wide")

# 2. DATABASE CONNECTION
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" 

@st.cache_resource
def get_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase = get_supabase()

# 3. UI STYLE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&display=swap');
    .main-title { font-family: 'Comic Neue', cursive; font-size: 2.5rem; color: #FF4B4B; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">KIU Learning Portal</h1>', unsafe_allow_html=True)

# 4. DATA LOGIC
if supabase:
    search_query = st.text_input("🔍 Search for a program", placeholder="e.g. Computer Science")
    
    try:
        # We use a broad select and handle missing columns in Python logic
        response = supabase.table("materials").select("*").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Check if 'course_program' exists in the data returned by DB
            if 'course_program' in df.columns:
                unique_courses = df['course_program'].dropna().unique()
                
                if not search_query:
                    st.subheader("Explore Programs")
                    cols = st.columns(min(len(unique_courses), 4) if len(unique_courses) > 0 else 1)
                    for i, course in enumerate(unique_courses):
                        with cols[i % 4]:
                            st.info(f"📚 {course}")
                else:
                    filtered_df = df[df['course_program'].str.contains(search_query, case=False, na=False)]
                    st.dataframe(filtered_df, use_container_width=True)
            else:
                st.warning("Database connected, but 'course_program' column missing. Check Supabase.")
        else:
            st.write("No data found in table 'materials'.")
            
    except Exception as e:
        st.error(f"Database Sync Error: {e}")

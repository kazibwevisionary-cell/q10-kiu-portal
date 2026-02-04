import streamlit as st
import pandas as pd
from supabase import create_client

# 1. UI CONFIG (CRITICAL: MUST BE LINE 1)
st.set_page_config(page_title="KIU Portal", layout="wide")

# 2. DATABASE CONNECTION
URL = "https://uxtmgdenwfyuwhezcleh.supabase.co"
KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# 3. SIMPLE HEADER
st.title("🎓 KIU Learning Portal")

# 4. SAFETY-FIRST DATA LOGIC
try:
    # We fetch everything, but we handle missing columns in Python so the app NEVER crashes
    response = supabase.table("materials").select("*").execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        
        # SEARCH BAR
        search = st.text_input("🔍 Search programs", placeholder="e.g. Computer Science")
        
        # SAFE COLUMN CHECK: This is the fix for error 42703
        main_col = 'course_program' if 'course_program' in df.columns else df.columns[0]
        
        if not search:
            st.subheader("Available Programs")
            unique_items = df[main_col].unique()
            cols = st.columns(min(len(unique_items), 3))
            for i, item in enumerate(unique_items):
                with cols[i % 3]:
                    st.info(f"📁 {item}")
        else:
            # Filtered search view
            filtered = df[df[main_col].str.contains(search, case=False, na=False)]
            st.dataframe(filtered, use_container_width=True)
            
    else:
        st.warning("Database connected, but the 'materials' table is empty.")
        st.info("Add data in your Supabase dashboard to see it here.")

except Exception as e:
    st.error("The app is live, but we are still syncing with your database.")
    st.write("Technical detail for you:", str(e))

# NO .launch() or Gradio code allowed here.

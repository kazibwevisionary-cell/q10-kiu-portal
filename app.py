import streamlit as st
import pandas as pd
from supabase import create_client
import re

# 1. UI CONFIGURATION (CRITICAL: MUST BE LINE 1)
st.set_page_config(page_title="Flux", layout="wide")

# 2. DATABASE CONNECTION (HARDCODED)
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" 

@st.cache_resource
def get_supabase():
    try:
        # We use a timeout or basic check to prevent the app from hanging
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Database Connection Failed: {e}")
        return None

supabase = get_supabase()

# 3. HELPER: Converts Google Drive "Share" links to "Direct Image" links
def convert_drive_url(url):
    if "drive.google.com" in url:
        match = re.search(r'[-\w]{25,}', url)
        if match:
            return f"https://drive.google.com/uc?id={match.group()}"
    return url

# 4. UI STYLE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&display=swap');
    
    .main-title {
        font-family: 'Comic Neue', cursive;
        color: #FF4B4B;
        text-align: center;
        font-size: 3rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Flux</h1>', unsafe_allow_html=True)

# 5. DATA TEST
if supabase:
    st.success("⚡ Connected to Supabase")
    # You can now add your supabase queries here
else:
    st.error("❌ Could not connect to database.")

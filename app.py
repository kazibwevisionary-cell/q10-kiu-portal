import streamlit as st
import pandas as pd
from supabase import create_client
import re

# 1. DATABASE CONNECTION
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" 

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# HELPER: Converts "Share" link to "Direct" link
def convert_drive_url(url):
    if "drive.google.com" in url:
        # Extracts the file ID from the URL
        match = re.search(r'[-\w]{25,}', url)
        if match:
            return f"https://drive.google.com/uc?id={match.group()}"
    return url

# 2. UI STYLE
st.set_page_config(page_title="Flux", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&display=swap');
    .main-title { font-family: 'Comic Neue', cursive; font-size: 32px !important; text-align: center; color: #333; }
    
    /* Tiles that show the Drive Image as background */
    .course-tile {
        position: relative; height: 200px; border-radius: 12px; overflow: hidden;
        margin-bottom: 10px; border: 1px solid #ddd; background-color: #f8f9fa;
    }
    .tile-img { width: 100%; height: 100%; object-fit: cover; }
    .tile-label {
        position: absolute; bottom: 0; width: 100%; background: rgba(0,0,0,0.7);
        color: white; padding: 10px; text-align: center; font-family: 'Comic Neue', cursive;
    }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #666; font-size: 14px; background: white; border-top: 1px solid #eee; z-index: 999; }
    </style>
    """, unsafe_allow_html=True)

# 3. AUTHENTICATION
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>Flux</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container(border=True):
            st.text_input("Username")
            st.text_input("Password", type="password")
            if st.button("Enter Portal", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# 4. NAVIGATION
role = st.sidebar.radio("Navigation", ["Student Portal", "Admin Dashboard"])

# --- ADMIN DASHBOARD ---
if role == "Admin Dashboard":
    st.write("### Course Creator")
    if st.text_input("Password", type="password") == "flux":
        with st.container(border=True):
            c_name = st.text_input("Course Program Name")
            drive_url = st.text_input("Google Drive Image URL (Shared Link)")
            f_content = st.file_uploader("Upload Excel Module List", type=['xlsx','csv'])
            
            if st.button("Deploy Course"):
                if c_name and drive_url and f_content:
                    # Fix the drive URL immediately
                    direct_url = convert_drive_url(drive_url)
                    
                    df = pd.read_excel(f_content) if "xlsx" in f_content.name else pd.read_csv(f_content)
                    for idx, row in df.iterrows():
                        supabase.table("materials").insert({
                            "course_program": c_name,
                            "course_name": str(row.get('Topic Covered', f'Module {idx+1}')),
                            "week": idx + 1,
                            "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                            "notes_url": str(row.get('link to Google docs Document', '')),
                            "image_url": direct_url, # Stored as a clean URL
                        }).execute()
                    st.success(f"Course '{c_name}' deployed using Drive images!")

# --- STUDENT PORTAL ---
elif role == "Student Portal":
    st.markdown("<div class='main-title'>Flux</div>", unsafe_allow_html=True)
    query = st.text_input("Search...").strip()
    
    if not query:
        st.subheader("Explore Courses")
        res = supabase.table("materials").select("course_program, image_url").execute()
        if res.data:
            unique_courses = {}
            for i in res.data:
                if i['course_program'] not in unique_courses:
                    unique_courses[i['course_program']] = i.get('image_url')
            
            cols = st.columns(4)
            for idx, (name, img) in enumerate(unique_courses.items()):
                with cols[idx % 4]:
                    st.markdown(f"""
                        <div class="course-tile">
                            <img src="{img if img else 'https://via.placeholder.com/300'}" class="tile-img">
                            <div class="tile-label">{name}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Open", key=f"b_{idx}", use_container_width=True):
                        st.session_state.search_trigger = name
                        st.rerun()

    # (Search logic remains consistent with previous version)

st.markdown('<div class="footer">Built by KMT Dynamics | Flux</div>', unsafe_allow_html=True)

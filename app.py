import streamlit as st
import pandas as pd
from supabase import create_client
import re

# 1. DATABASE CONNECTION
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" 

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    st.error("Connection error.")
    st.stop()

# 2. UI CONFIG (Keeping your exact original styling)
st.set_page_config(page_title="KIU Q10 Portal", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 8px; color: #888; font-size: 12px; background: white; border-top: 1px solid #eee; z-index: 1000; }
    .video-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 8px; margin-bottom: 10px;}
    .video-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKGROUND HELPER: THE LINK FIXER ---
def fix_youtube_link(url):
    """Automatically converts any YouTube link to a working embed format."""
    if not url or not isinstance(url, str):
        return url
    # Regex to find the 11-character Video ID
    match = re.search(r"(?:v=|\/|be\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})", url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    return url

# 3. LOGIN GATE
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🎓 KIU Q10 Portal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        with st.container(border=True):
            st.subheader("Student & Staff Login")
            st.text_input("Username")
            st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True) or st.button("⏭️ Skip & Browse Courses", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
    st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True)
    st.stop()

# 4. NAVIGATION
st.sidebar.title("🎓 KIU Portal")
role = st.sidebar.radio("Navigation:", ["Student Portal", "Admin Dashboard", "President Board"])

# --- ADMIN DASHBOARD ---
if role == "Admin Dashboard":
    st.header("🛠 Admin Management")
    t1, t2, t3 = st.tabs(["➕ Add Single", "📊 Bulk Upload", "🗑️ Manage Content"])
    
    with t1:
        with st.form("manual"):
            p = st.text_input("Course Name")
            t = st.text_input("Topic")
            w = st.number_input("Week", 1, 15)
            y = st.text_input("Video/Slide Link")
            n = st.text_input("Notes Link")
            if st.form_submit_button("Save Entry"):
                supabase.table("materials").insert({"course_program": p, "course_name": t, "week": w, "video_url": y, "notes_url": n}).execute()
                st.success("Saved!")

    with t2:
        target = st.text_input("Assign to Course (e.g., Petroleum Engineering)")
        wipe = st.checkbox("Wipe existing data for this course name first?")
        f = st.file

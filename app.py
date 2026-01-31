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

# 2. UI CONFIG
st.set_page_config(page_title="KIU Q10 Portal", layout="wide", page_icon="🎓")

# Background Player CSS
st.markdown("""
    <style>
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #888; font-size: 13px; background: white; border-top: 1px solid #eee; z-index: 1000; }
    .video-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 12px; }
    .video-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
    </style>
    """, unsafe_allow_html=True)

# 3. BACKGROUND LINK TRANSFORMER FUNCTION
def get_embed_url(raw_url):
    """Converts any YouTube link to a working embed format."""
    if not raw_url or pd.isna(raw_url):
        return None
    
    # Extract ID from various YouTube formats
    # Handles: youtu.be/ID, youtube.com/watch?v=ID, youtube.com/embed/ID, etc.
    youtube_id_match = re.search(r'(?:v=|\/|be\/|embed\/)([0-9A-Za-z_-]{11})', raw_url)
    if youtube_id_match:
        video_id = youtube_id_match.group(1)
        return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
    
    # Handle Google Slides
    if "docs.google.com/presentation" in raw_url:
        return raw_url.replace("/edit", "/embed")
    
    return raw_url

# 4. LOGIN GATE (Simplified for brevity)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🎓 KIU Q10 Portal</h1>", unsafe_allow_html=True)
    if st.button("Enter Portal", use_container_width=True):
        st.session_state.logged_in = True
        st.rerun()
    st.stop()

# 5. NAVIGATION
role = st.sidebar.radio("Navigation:", ["Student Portal", "Admin Dashboard"])

# --- ADMIN DASHBOARD ---
if role == "Admin Dashboard":
    st.header("🛠 Admin Management")
    f = st.file_uploader("Upload Petroleum Excel", type=["xlsx", "csv"])
    target = st.text_input("Course Name", value="Petroleum Engineering")
    
    if f and st.button("🚀 Process & Upload"):
        df = pd.read_excel(f) if "xlsx" in f.name else pd.read_csv(f)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Clean existing data for this course
        supabase.table("materials").delete().eq("course_program", target).execute()
        
        for _, row in df.iterrows():
            supabase.table("materials").insert({
                "course_program": target,
                "course_name": str(row.get('Topic Covered', 'Untitled')),
                "week": _ + 1, # Auto-assigning week based on row order
                "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                "notes_url": str(row.get('link to Google docs Document', ''))
            }).execute()
        st.success("Database Updated!")

# --- STUDENT PORTAL ---
elif role == "Student Portal":
    st.title("📖 Course Materials")
    search = st.text_input("🔍 Search Course").strip()
    
    if search:
        res = supabase.table("materials").select("*").ilike("course_program", f"%{search}%").order("week").execute()
        if res.data:
            for item in res.data:
                with st.expander(f"📚 Module {item['week']} - {item['course_name']}"):
                    # RUN BACKGROUND TRANSFORMER
                    clean_url = get_embed_url(item['video_url'])
                    
                    if clean_url:
                        st.markdown(f'<div class="video-container"><iframe src="{clean_url}" allowfullscreen></iframe></div>', unsafe_allow_html=True)
                        # Add a direct backup button just in case the creator disabled embedding
                        st.link_button("📺 Watch on YouTube", item['video_url'])
                    
                    if item.get('notes_url'):
                        st.divider()
                        st.link_button("📝 Open Lecture Notes", item['notes_url'])
        else:
            st.info("Course not found.")

st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True)

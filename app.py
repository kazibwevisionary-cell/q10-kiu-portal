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
    st.error("Database Connection Failed.")
    st.stop()

# HELPER: Convert Google Drive Link to Direct Image Link
def fix_drive_url(url):
    if "drive.google.com" in url:
        # Extract the ID from the URL
        match = re.search(r'[-\w]{25,}', url)
        if match:
            return f"https://drive.google.com/uc?id={match.group()}"
    return url

# 2. UI CONFIG & FOOTER
st.set_page_config(page_title="Flux", layout="wide")

st.markdown("""
    <style>
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #666; font-size: 14px; background: white; border-top: 1px solid #eee; z-index: 999; }
    .video-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 8px; margin-bottom: 10px; }
    .video-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
    .course-tile { border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin-bottom: 20px; text-align: center; background: white; }
    .main-title { font-size: 42px !important; font-weight: 800; text-align: center; margin-top: 20px; margin-bottom: 20px; }
    h1 { font-size: 28px !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN PAGE
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>Flux</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        with st.container(border=True):
            st.subheader("Login Access")
            st.text_input("Username")
            st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True) or st.button("⏭️ Skip & Browse", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# 4. SIDEBAR
role = st.sidebar.radio("Navigation", ["Student Portal", "Course Creator (Admin)", "President Board"])

# --- COURSE CREATOR (ADMIN) ---
if role == "Course Creator (Admin)":
    st.header("Course Creation Console")
    admin_pw = st.text_input("Enter Admin Password", type="password")
    
    if admin_pw == "flux":
        st.success("Access Granted")
        
        with st.container(border=True):
            st.subheader("Create New Course")
            c_name = st.text_input("Course Name (e.g., Civil Engineering)")
            c_img_raw = st.text_input("Google Drive Image URL (Course Tile)")
            c_img = fix_drive_url(c_img_raw)
            
            st.write("---")
            st.write("📂 **Upload Module Content**")
            st.caption("Upload your Excel file. Modules will be numbered automatically (1, 2, 3...) based on the row order.")
            f = st.file_uploader("Upload Excel/CSV", type=["xlsx", "csv"])
            
            if st.button("🚀 Create Course & Generate Modules", use_container_width=True):
                if not c_name or not f:
                    st.error("Please provide both a Course Name and a file.")
                else:
                    # Load data
                    df = pd.read_excel(f) if "xlsx" in f.name else pd.read_csv(f)
                    df.columns = [str(c).strip() for c in df.columns]
                    
                    progress_bar = st.progress(0)
                    total_rows = len(df)
                    
                    for index, row in df.iterrows():
                        # Sequential module number based on row index (starting at 1)
                        mod_num = index + 1
                        
                        supabase.table("materials").insert({
                            "course_program": c_name,
                            "course_name": str(row.get('Topic Covered', f"Module {mod_num} Content")),
                            "week": mod_num, # Using sequential number
                            "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                            "notes_url": str(row.get('link to Google docs Document', '')),
                            "image_url": c_img
                        }).execute()
                        
                        progress_bar.progress((index + 1) / total_rows)
                    
                    st.success(f"Course '{c_name}' created with {total_rows} sequential modules!")

# --- STUDENT PORTAL ---
elif role == "Student Portal":
    st.markdown("<div class='main-title'>Flux</div>", unsafe_allow_html=True)
    
    search_query = st.text_input("Search for your Course or Topic").strip()
    
    if not search_query:
        st.subheader("Explore Courses")
        try:
            tiles_data = supabase.table("materials").select("course_program, image_url").execute()
            if tiles_data.data:
                # Group by course name to only show one tile per course
                unique_courses = {item['course_program']: item.get('image_url') for item in tiles_data.data}
                
                cols = st.columns(4)
                for idx, (c_name, c_img) in enumerate(unique_courses.items()):
                    with cols[idx % 4]:
                        with st.container(border=True):
                            # Display fixed Drive image or placeholder
                            if c_img:
                                st.image(c_img, use_container_width=True)
                            else:
                                st.image("https://via.placeholder.com/300x200?text=Flux+Course", use_container_width=True)
                            
                            st.write(f"**{c_name}**")
                            if st.button("Open Course", key=f"tile_{idx}"):
                                st.session_state.search_trigger = c_name
                                st.rerun()
        except Exception as e:
            st.info("No courses found. Use the Admin Dashboard to add content.")

    final_query = st.session_state.get('search_trigger', search_query)

    if final_query:
        if 'search_trigger' in st.session_state: del st.session_state.search_trigger
        res = supabase.table("materials").select("*").or_(f"course_program.ilike.%{final_query}%,course_name.ilike.%{final_query}%").order("week").execute()
        
        if res.data:
            st.divider()
            st.subheader(f"Modules for {final_query}")
            for item in res.data:
                with st.expander(f"Module {item['week']} - {item['course_name']}"):
                    raw_url = str(item.get('video_url', ''))
                    if "youtube" in raw_url or "youtu.be" in raw_url:
                        v_id = raw_url.split("v=")[1].split("&")[0] if "v=" in raw_url else raw_url.split("/")[-1]
                        st.markdown(f'<div class="video-container"><iframe src="https://www.youtube.com/embed/{v_id}" allowfullscreen></iframe></div>', unsafe_allow_html=True)
                    
                    if item.get('notes_url'):
                        # Allowing multiple links if comma separated, otherwise single button
                        notes = item['notes_url'].split(",")
                        for i, link in enumerate(notes):
                            label = f"📝 Read Class Notes {i+1}" if len(notes) > 1 else "📝 Read Class Notes"
                            st.link_button(label, link.strip())
        else:
            st.warning("No modules found.")

# --- PRESIDENT BOARD ---
elif role == "President Board":
    st.header("Post Announcements")
    pres_pw = st.text_input("Enter Board Password", type="password")
    if pres_pw == "flux":
        with st.form("notice"):
            tt = st.text_input("Title")
            mm = st.text_area("Message")
            if st.form_submit_button("Publish"):
                supabase.table("notices").insert({"title": tt, "content": mm}).execute()
                st.success("Published!")
    elif pres_pw != "":
        st.error("Access Denied")

# 5. FOOTER
st.markdown('<div class="footer">Built by KMT Dynamics | Flux</div>', unsafe_allow_html=True)

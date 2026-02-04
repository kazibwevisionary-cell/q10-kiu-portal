import streamlit as st
import pandas as pd
from supabase import create_client
import base64
from io import BytesIO

# 1. DATABASE CONNECTION
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" 

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    st.error("Database Connection Failed.")
    st.stop()

# HELPER: Convert Image to Base64
def img_to_base64(image_file):
    if image_file is not None:
        return base64.b64encode(image_file.getvalue()).decode()
    return None

# 2. UI CONFIG & STYLE
st.set_page_config(page_title="Flux", layout="wide")

# Persistent Background Check
bg_img = st.session_state.get("login_bg", "")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&display=swap');
    
    .stApp {{
        background: {f"url(data:image/png;base64,{bg_img})" if bg_img else "#ffffff"};
        background-size: cover;
        background-attachment: fixed;
    }}

    .main-title {{
        font-family: 'Comic Neue', 'Comic Sans MS', cursive;
        font-size: 32px !important;
        color: #333;
        text-align: center;
        margin-bottom: 20px;
    }}
    
    .admin-header {{ font-size: 16px !important; font-weight: bold; color: #666; }}

    /* Course Tile with Full Cover Image */
    .course-tile {{
        position: relative;
        height: 220px;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 10px;
        border: 1px solid #eee;
    }}
    .tile-img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}
    .tile-label {{
        position: absolute;
        bottom: 0;
        width: 100%;
        background: rgba(0,0,0,0.65);
        color: white;
        padding: 8px;
        text-align: center;
        font-family: 'Comic Neue', cursive;
    }}
    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #666; font-size: 14px; background: rgba(255,255,255,0.8); z-index: 999; }}
    </style>
    """, unsafe_allow_html=True)

# 3. AUTH & REGISTRATION
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>Flux</div>", unsafe_allow_html=True)
    t_log, t_reg = st.tabs(["Login", "Sign Up"])
    
    with t_log:
        with st.container(border=True):
            st.text_input("Username")
            st.text_input("Password", type="password")
            if st.button("Enter Flux", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()

    with t_reg:
        with st.container(border=True):
            st.text_input("Full Name")
            st.text_input("Major/Course")
            st.text_area("What are your interests? (Keywords)")
            if st.button("Create Account", use_container_width=True):
                st.success("Registration complete!")
    st.stop()

# 4. SIDEBAR
role = st.sidebar.radio("Navigation", ["Student Portal", "Admin Dashboard", "President Board"])

# --- ADMIN DASHBOARD ---
if role == "Admin Dashboard":
    st.markdown("<p class='admin-header'>Course Creation Console</p>", unsafe_allow_html=True)
    if st.text_input("Admin Password", type="password") == "flux":
        tabs = st.tabs(["🚀 New Course", "🗑️ Delete Content", "🎨 Portal Branding"])
        
        with tabs[0]:
            c_name = st.text_input("Course Name")
            tags = st.text_input("Keywords (for search)")
            c_img = st.file_uploader("Upload Tile Cover", type=['jpg','png'])
            f_content = st.file_uploader("Upload Content (Excel)", type=['xlsx','csv'])
            
            if st.button("Create Course"):
                if c_name and f_content:
                    b64_img = img_to_base64(c_img) if c_img else ""
                    df = pd.read_excel(f_content) if "xlsx" in f_content.name else pd.read_csv(f_content)
                    
                    for idx, row in df.iterrows():
                        try:
                            supabase.table("materials").insert({
                                "course_program": c_name,
                                "course_name": str(row.get('Topic Covered', f'Module {idx+1}')),
                                "week": idx + 1,
                                "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                                "notes_url": str(row.get('link to Google docs Document', '')),
                                "image_url": f"data:image/png;base64,{b64_img}" if b64_img else None,
                                "keywords": tags
                            }).execute()
                        except Exception as e:
                            st.error(f"Error at row {idx}: Column 'keywords' or 'image_url' might be missing in Supabase.")
                            break
                    st.success("Course Created!")

        with tabs[1]:
            # Old delete functionality preserved
            data = supabase.table("materials").select("*").execute()
            if data.data:
                for item in data.data:
                    c1, c2 = st.columns([5,1])
                    c1.write(f"{item['course_program']} - {item['course_name']}")
                    if c2.button("Delete", key=item['id']):
                        supabase.table("materials").delete().eq("id", item['id']).execute()
                        st.rerun()

        with tabs[2]:
            st.write("### Change Login Background")
            bg_file = st.file_uploader("Choose Background Image", type=['jpg','png'])
            if st.button("Apply Background"):
                st.session_state.login_bg = img_to_base64(bg_file)
                st.rerun()

# --- STUDENT PORTAL ---
elif role == "Student Portal":
    st.markdown("<div class='main-title'>Flux</div>", unsafe_allow_html=True)
    query = st.text_input("Search for courses or topics").strip()
    
    if not query:
        st.subheader("Explore Courses")
        res = supabase.table("materials").select("course_program, image_url").execute()
        if res.data:
            unique_courses = {i['course_program']: i.get('image_url') for i in res.data}
            cols = st.columns(4)
            for idx, (name, img) in enumerate(unique_courses.items()):
                with cols[idx % 4]:
                    st.markdown(f"""
                        <div class="course-tile">
                            <img src="{img if img else 'https://via.placeholder.com/300'}" class="tile-img">
                            <div class="tile-label">{name}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Open", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.search_trigger = name
                        st.rerun()

    final_q = st.session_state.get('search_trigger', query)
    if final_q:
        if 'search_trigger' in st.session_state: del st.session_state.search_trigger
        # Enhanced search looks at program, topic, and keywords
        res = supabase.table("materials").select("*").or_(
            f"course_program.ilike.%{final_q}%,keywords.ilike.%{final_q}%,course_name.ilike.%{final_q}%"
        ).order("week").execute()
        
        for item in res.data:
            with st.expander(f"Module {item['week']} - {item['course_name']}"):
                if item.get('video_url'): st.video(item['video_url'])
                if item.get('notes_url'): st.link_button("Notes", item['notes_url'])

st.markdown('<div class="footer">Built by KMT Dynamics | Flux</div>', unsafe_allow_html=True)

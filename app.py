import streamlit as st
import pandas as pd
from supabase import create_client
import base64

# 1. DATABASE CONNECTION
# Ensure your Supabase table has columns: course_program, course_name, week, video_url, notes_url, image_url, keywords
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" 

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    st.error("Database Connection Failed.")
    st.stop()

# HELPER: Convert Image to Base64 for Direct Display/Storage
def img_to_base64(image_file):
    if image_file is not None:
        return base64.b64encode(image_file.getvalue()).decode()
    return None

# 2. UI CONFIG & STYLE (Comic Sans & Custom Branding)
st.set_page_config(page_title="Flux", layout="wide")

# Check for custom background in session
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

    /* Course Tile Styling - Image covers the whole tile */
    .course-tile {{
        position: relative;
        height: 220px;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 10px;
        border: 1px solid #eee;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 8px;
        text-align: center;
        font-family: 'Comic Neue', cursive;
    }}
    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #666; font-size: 14px; background: rgba(255,255,255,0.8); z-index: 999; }}
    </style>
    """, unsafe_allow_html=True)

# 3. AUTHENTICATION
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'>Flux</div>", unsafe_allow_html=True)
    t_log, t_reg = st.tabs(["Login", "Sign Up"])
    
    with t_log:
        with st.container(border=True):
            st.text_input("Username", key="l_user")
            st.text_input("Password", type="password", key="l_pass")
            if st.button("Enter Flux", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()

    with t_reg:
        with st.container(border=True):
            st.text_input("Full Name")
            st.text_input("Major/Course")
            st.text_area("Keywords for Interests")
            if st.button("Create Account", use_container_width=True):
                st.success("Account Ready!")
    st.stop()

# 4. SIDEBAR NAVIGATION
role = st.sidebar.radio("Navigation", ["Student Portal", "Admin Dashboard", "President Board"])

# --- ADMIN DASHBOARD ---
if role == "Admin Dashboard":
    st.markdown("<p class='admin-header'>Course Creation Console</p>", unsafe_allow_html=True)
    if st.text_input("Admin Password", type="password") == "flux":
        tabs = st.tabs(["🚀 Create Course", "🗑️ Manage Data", "🎨 Portal Branding"])
        
        with tabs[0]:
            c_name = st.text_input("Course Name")
            tags = st.text_input("Search Keywords")
            c_img = st.file_uploader("Upload Course Tile Image", type=['jpg','png','jpeg'])
            f_content = st.file_uploader("Upload Excel Module List", type=['xlsx','csv'])
            
            if st.button("Deploy Course"):
                if c_name and f_content:
                    b64_img = img_to_base64(c_img) if c_img else ""
                    df = pd.read_excel(f_content) if "xlsx" in f_content.name else pd.read_csv(f_content)
                    
                    for idx, row in df.iterrows():
                        supabase.table("materials").insert({
                            "course_program": c_name,
                            "course_name": str(row.get('Topic Covered', f'Module {idx+1}')),
                            "week": idx + 1,
                            "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                            "notes_url": str(row.get('link to Google docs Document', '')),
                            "image_url": f"data:image/png;base64,{b64_img}" if b64_img else None,
                            "keywords": tags
                        }).execute()
                    st.success(f"Deployed {c_name} with {len(df)} modules!")

        with tabs[1]:
            data = supabase.table("materials").select("id, course_program, course_name").execute()
            if data.data:
                for item in data.data:
                    c1, c2 = st.columns([5,1])
                    c1.write(f"**{item['course_program']}**: {item['course_name']}")
                    if c2.button("Delete", key=f"del_{item['id']}"):
                        supabase.table("materials").delete().eq("id", item['id']).execute()
                        st.rerun()

        with tabs[2]:
            st.write("### Branding")
            bg_file = st.file_uploader("Update Login/Signup Background", type=['jpg','png','jpeg'])
            if st.button("Apply Background"):
                st.session_state.login_bg = img_to_base64(bg_file)
                st.rerun()

# --- STUDENT PORTAL ---
elif role == "Student Portal":
    st.markdown("<div class='main-title'>Flux</div>", unsafe_allow_html=True)
    query = st.text_input("Search (e.g., Engineering, Math, Logic)").strip()
    
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
                    if st.button("Open Course", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.search_trigger = name
                        st.rerun()

    final_q = st.session_state.get('search_trigger', query)
    if final_q:
        if 'search_trigger' in st.session_state: del st.session_state.search_trigger
        res = supabase.table("materials").select("*").or_(
            f"course_program.ilike.%{final_q}%,keywords.ilike.%{final_q}%,course_name.ilike.%{final_q}%"
        ).order("week").execute()
        
        if res.data:
            st.divider()
            for item in res.data:
                with st.expander(f"Module {item['week']} - {item['course_name']}"):
                    if item.get('video_url'): st.video(item['video_url'])
                    if item.get('notes_url'): 
                        for link in item['notes_url'].split(","):
                            st.link_button("📝 Read Notes", link.strip())
        else:
            st.warning("Nothing found.")

# --- PRESIDENT BOARD ---
elif role == "President Board":
    st.header("Board Announcements")
    if st.text_input("Board Password", type="password") == "flux":
        with st.form("notice"):
            t = st.text_input("Title")
            m = st.text_area("Content")
            if st.form_submit_button("Post"):
                supabase.table("notices").insert({"title":t, "content":m}).execute()
                st.success("Notice Posted")

st.markdown('<div class="footer">Built by KMT Dynamics | Flux</div>', unsafe_allow_html=True)

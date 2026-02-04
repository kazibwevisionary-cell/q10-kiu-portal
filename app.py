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

# HELPER: Convert Uploaded Image to Base64 for CSS/Database
def img_to_base64(image_file):
    if image_file is not None:
        buffered = BytesIO(image_file.read())
        return base64.b64encode(buffered.getvalue()).decode()
    return None

# 2. UI CONFIG & DYNAMIC STYLING
# We check if a custom background exists in the session or DB (simplified here to session)
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
        font-size: 36px !important;
        color: #333;
        text-align: center;
        margin: 10px 0;
        background: rgba(255,255,255,0.7);
        border-radius: 10px;
        display: inline-block;
        padding: 0 20px;
    }}
    
    /* Full-cover Course Tiles */
    .course-tile-container {{
        position: relative;
        width: 100%;
        height: 200px;
        border-radius: 15px;
        overflow: hidden;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    .tile-image {{
        width: 100%;
        height: 100%;
        object-fit: cover;
    }}
    .tile-overlay {{
        position: absolute;
        bottom: 0;
        width: 100%;
        background: rgba(0,0,0,0.6);
        color: white;
        padding: 10px;
        text-align: center;
        font-family: 'Comic Neue', cursive;
    }}

    .admin-header {{ font-size: 18px !important; font-weight: bold; color: #555; }}
    .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #666; font-size: 14px; background: rgba(255,255,255,0.8); border-top: 1px solid #eee; z-index: 999; }}
    </style>
    """, unsafe_allow_html=True)

# 3. AUTHENTICATION (SIGN UP & LOGIN)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<center><div class='main-title'>Flux</div></center>", unsafe_allow_html=True)
    tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab_login:
        col1, col2, col3 = st.columns([1,1.5,1])
        with col2:
            with st.container(border=True):
                st.text_input("Username", key="l_u")
                st.text_input("Password", type="password", key="l_p")
                if st.button("Login", use_container_width=True):
                    st.session_state.logged_in = True
                    st.rerun()
                st.button("Skip to Browse", on_click=lambda: st.session_state.update({"logged_in": True}))

    with tab_signup:
        col1, col2, col3 = st.columns([1,1.5,1])
        with col2:
            with st.container(border=True):
                st.subheader("New Student Registration")
                st.text_input("Full Name")
                st.text_input("Email")
                st.text_input("Major")
                st.text_area("Interests (Keywords)")
                if st.button("Register Account", use_container_width=True):
                    st.success("Registered!")
    st.stop()

# 4. SIDEBAR
role = st.sidebar.radio("Navigation", ["Student Portal", "Admin Dashboard", "President Board"])

# --- ADMIN DASHBOARD ---
if role == "Admin Dashboard":
    st.markdown("<p class='admin-header'>Course Creation Console</p>", unsafe_allow_html=True)
    if st.text_input("Admin Password", type="password") == "flux":
        t1, t2, t3, t4 = st.tabs(["🚀 New Course Creator", "➕ Manual Entry", "🗑️ Manage Content", "🎨 Portal Branding"])
        
        with t1:
            st.write("### Structured Course Upload")
            c_name = st.text_input("Course Program Name")
            tags = st.text_input("Search Keywords")
            # Uploading directly from device
            c_img_file = st.file_uploader("Upload Course Cover Image", type=['png', 'jpg', 'jpeg'])
            f = st.file_uploader("Upload Excel Content", type=["xlsx", "csv"])
            
            if st.button("Generate Course"):
                if c_name and f and c_img_file:
                    b64_img = img_to_base64(c_img_file)
                    df = pd.read_excel(f) if "xlsx" in f.name else pd.read_csv(f)
                    for idx, row in df.iterrows():
                        supabase.table("materials").insert({
                            "course_program": c_name,
                            "course_name": str(row.get('Topic Covered', f"Module {idx+1}")),
                            "week": idx + 1,
                            "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                            "notes_url": str(row.get('link to Google docs Document', '')),
                            "image_url": f"data:image/png;base64,{b64_img}",
                            "keywords": tags
                        }).execute()
                    st.success("Course Created with Custom Cover!")

        with t4:
            st.write("### Adjust Portal Background")
            bg_file = st.file_uploader("Upload Login/Signup Background Image", type=['png', 'jpg', 'jpeg'])
            if st.button("Apply New Background"):
                if bg_file:
                    st.session_state.login_bg = img_to_base64(bg_file)
                    st.success("Background Updated!")
                    st.rerun()

        # ... (Manual Entry and Manage Content Tabs remain as before)

# --- STUDENT PORTAL ---
elif role == "Student Portal":
    st.markdown("<div class='main-title'>Flux</div>", unsafe_allow_html=True)
    query = st.text_input("Search by Course, Keyword, or Topic").strip()
    
    if not query:
        st.subheader("Explore Courses")
        tiles_data = supabase.table("materials").select("course_program, image_url").execute()
        if tiles_data.data:
            unique_courses = {item['course_program']: item.get('image_url') for item in tiles_data.data}
            cols = st.columns(3)
            for idx, (c_name, c_img) in enumerate(unique_courses.items()):
                with cols[idx % 3]:
                    # Full cover tile styling
                    st.markdown(f"""
                        <div class="course-tile-container">
                            <img src="{c_img if c_img else 'https://via.placeholder.com/400'}" class="tile-image">
                            <div class="tile-overlay">{c_name}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Open {c_name}", key=f"v_{idx}", use_container_width=True):
                        st.session_state.search_trigger = c_name
                        st.rerun()

    # ... (Search Results logic remains as before)

st.markdown('<div class="footer">Built by KMT Dynamics | Flux</div>', unsafe_allow_html=True)

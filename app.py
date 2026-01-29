import streamlit as st
from supabase import create_client, Client
import pandas as pd

# ==============================================================================
# /// A.I Architect: MUGABI KIZITO LENNY ///
# PROJECT: Q10 KIU REPOSITORY (PRODUCTION BUILD 1.1)
# ==============================================================================

# --- PAGE CONFIG ---
st.set_page_config(page_title="Q10 | KIU Repository", page_icon="🎓", layout="wide")

# --- SECURE DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    try:
        # These pull from the "Secrets" tab in your Streamlit Cloud dashboard
        # This keeps your credentials hidden from the public on GitHub
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("Database Connection Failed. Please check Streamlit Secrets.")
        return None

supabase = init_connection()

# --- CSS & ARCHITECT SIGNATURE ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .footer { 
        position: fixed; 
        bottom: 10px; 
        right: 25px; 
        color: #d1d1d1; 
        font-family: monospace; 
        font-size: 11px;
    }
    </style>
    <div class='footer'>A.I Architect: MUGABI KIZITO LENNY</div>
    """, unsafe_allow_html=True)

# --- SESSION HANDLING ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None

# --- MAIN INTERFACE ---
if not st.session_state.logged_in:
    st.title("🎓 Q10 | KIU Repository")
    st.caption("The Unified Academic Cloud Platform")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛠 Admin Login", use_container_width=True):
            st.session_state.role = "Admin"; st.session_state.logged_in = True; st.rerun()
    with col2:
        if st.button("👑 President Login", use_container_width=True):
            st.session_state.role = "President"; st.session_state.logged_in = True; st.rerun()
    with col3:
        if st.button("📖 Student Login", use_container_width=True):
            st.session_state.role = "Student"; st.session_state.logged_in = True; st.rerun()

else:
    role = st.session_state.role
    st.sidebar.title(f"Q10 | {role}")
    st.sidebar.divider()
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

    if role == "Admin":
        st.header("🛠 Global Admin Dashboard")
        st.write(f"Access Level: **System Architect**")
        with st.form("admin_upload"):
            c_name = st.text_input("Course Name")
            week = st.number_input("Week No.", 1, 15)
            v_url = st.text_input("Video URL (YouTube)")
            if st.form_submit_button("Save to Cloud"):
                if c_name:
                    supabase.table("materials").insert({"course_name": c_name, "week": week, "video_url": v_url}).execute()
                    st.success(f"Material for {c_name} is now live!")
                else:
                    st.warning("Please enter a course name.")

    elif role == "President":
        st.header("👑 Class Notice Board")
        with st.form("notice_form"):
            t = st.text_input("Notice Title")
            c = st.text_area("Announcement Details")
            if st.form_submit_button("Post Announcement"):
                supabase.table("notices").insert({"title": t, "content": c, "posted_by": "President"}).execute()
                st.success("Broadcast successful!")

    elif role == "Student":
        st.header("🚀 Student Portal")
        t1, t2 = st.tabs(["📚 Materials", "🔔 Notices"])
        with t1:
            try:
                res = supabase.table("materials").select("*").execute()
                if res.data:
                    df = pd.DataFrame(res.data)
                    st.dataframe(df[['course_name', 'week', 'video_url']], use_container_width=True)
                else:
                    st.info("The library is currently being updated.")
            except:
                st.error("Could not reach cloud database.")
        with t2:
            try:
                notices = supabase.table("notices").select("*").order('created_at', desc=True).execute()
                if notices.data:
                    for n in notices.data:
                        with st.expander(f"📌 {n['title']}"):
                            st.write(n['content'])
                else:
                    st.info("No active notices.")
            except:
                st.write("Notice board unavailable.")

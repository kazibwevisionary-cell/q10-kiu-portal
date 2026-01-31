import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONNECTION SETUP
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" 

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Connection error. Check your network.")
    st.stop()

# 2. UI THEME & BRANDING
st.set_page_config(page_title="KIU Q10 Portal", layout="wide", page_icon="🎓")

# Custom CSS for the footer and styling
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        color: #6c757d;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN PAGE (Skipable)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🎓 KIU Q10 Portal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container(border=True):
            st.subheader("Portal Login")
            st.text_input("Username")
            st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
            if st.button("⏭️ Skip & Browse Courses", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
    st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True)
    st.stop()

# 4. SIDEBAR NAVIGATION
st.sidebar.title("🎓 KIU Portal")
role = st.sidebar.radio("Role Selection:", ["Student Portal", "Admin Dashboard", "President Board"])

# --- ADMIN DASHBOARD ---
if role == "Admin Dashboard":
    st.header("🛠 Global Admin Control")
    tab_single, tab_bulk, tab_manage = st.tabs(["➕ Add Single", "📊 Bulk Upload", "🗑️ Manage Content"])
    
    with tab_single:
        with st.form("admin_form"):
            prog = st.text_input("Course Name (e.g., Mechanical Engineering)")
            topic = st.text_input("Topic Covered")
            wk = st.number_input("Week", 1, 15)
            yt = st.text_input("YouTube Embed Link")
            nt = st.text_input("Notes Link")
            if st.form_submit_button("Save Entry"):
                supabase.table("materials").insert({
                    "course_program": prog, "course_name": topic, "week": wk, "video_url": yt, "notes_url": nt
                }).execute()
                st.success("Entry Saved!")

    with tab_bulk:
        st.subheader("📊 Bulk Upload")
        prog_target = st.text_input("Target Course Name")
        replace_mode = st.checkbox("🔥 Wipe existing data for this course before uploading?")
        uploaded_file = st.file_uploader("Choose File", type=["xlsx", "csv"])
        
        if uploaded_file and prog_target and st.button("🚀 Process Upload"):
            if replace_mode:
                supabase.table("materials").delete().eq("course_program", prog_target).execute()
            
            df = pd.read_excel(uploaded_file) if "xlsx" in uploaded_file.name else pd.read_csv(uploaded_file)
            df.columns = [str(c).strip() for c in df.columns]
            for _, row in df.iterrows():
                supabase.table("materials").insert({
                    "course_program": prog_target,
                    "course_name": str(row.get('Topic Covered', '')),
                    "week": int(row.get('Week', 1)) if 'Week' in df.columns else 1,
                    "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                    "notes_url": str(row.get('link to Google docs Document', ''))
                }).execute()
            st.success(f"Uploaded to {prog_target}!")

    with tab_manage:
        st.subheader("🗑️ Delete Course Materials")
        all_data = supabase.table("materials").select("*").execute()
        if all_data.data:
            for item in all_data.data:
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{item['course_program']}** - Wk {item['week']}: {item['course_name']}")
                if col2.button("🗑️ Delete", key=f"del_{item['id']}"):
                    supabase.table("materials").delete().eq("id", item['id']).execute()
                    st.rerun()
        else:
            st.info("No materials found to manage.")

# --- PRESIDENT BOARD ---
elif role == "President Board":
    st.header("📢 Post Announcement")
    with st.form("p_form"):
        title = st.text_input("Title")
        msg = st.text_area("Message")
        if st.form_submit_button("Post"):
            supabase.table("notices").insert({"title": title, "content": msg}).execute()
            st.success("Announcement live!")

# --- STUDENT PORTAL ---
elif role == "Student Portal":
    st.markdown("<h1>🎓 Student Learning Portal</h1>", unsafe_allow_html=True)
    search = st.text_input("🔍 Search for your Course (e.g. 'Mechanical Engineering')", "").strip()
    
    if search:
        res = supabase.table("materials").select("*").ilike("course_program", f"%{search}%").order("week").execute()
        if res.data:
            for item in res.data:
                with st.expander(f"📖 Week {item['week']} - {item['course_name']}"):
                    if item.get('video_url'):
                        st.video(item['video_url'])
                    if item.get('notes_url'):
                        st.link_button("📝 Open Notes", item['notes_url'])
        else:
            st.warning("No content found. Please check spelling or contact Admin.")
    else:
        st.info("Please enter your course name above to view modules.")

# 5. FOOTER
st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True)

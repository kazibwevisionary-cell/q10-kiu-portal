import streamlit as st
import pandas as pd
from supabase import create_client

# 1. HARD-WIRED CONNECTION (No Secrets Required)
# ---------------------------------------------------------
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" 

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()
# ---------------------------------------------------------

# 2. UI BRANDING & LAYOUT
st.set_page_config(page_title="KIU Q10 Portal", layout="wide", page_icon="🎓")

# Custom CSS for a cleaner look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("🎓 KIU Q10 Portal")
role = st.sidebar.radio("Identify Your Role:", ["Student", "President", "Admin"])

# --- ADMIN VIEW (The Tabbed UI you liked) ---
if role == "Admin":
    st.header("🛠 Global Admin Dashboard")
    st.info("Manage course content and bulk uploads here.")
    
    tab_single, tab_bulk = st.tabs(["➕ Single Entry", "📊 Bulk Excel Upload"])
    
    with tab_single:
        with st.form("admin_upload"):
            st.subheader("Add Single Course Module")
            c_name = st.text_input("Topic Covered (e.g., Atomic Structure)")
            week = st.number_input("Week Number", 1, 15, value=1)
            v_url = st.text_input("YouTube Video URL")
            n_url = st.text_input("Google Docs / Notes URL")
            
            if st.form_submit_button("🚀 Save to Database"):
                if c_name:
                    try:
                        supabase.table("materials").insert({
                            "course_name": c_name, "week": week, 
                            "video_url": v_url, "notes_url": n_url
                        }).execute()
                        st.success(f"✅ Successfully added: {c_name}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab_bulk:
        st.subheader("📊 Bulk Import from Excel")
        st.write("I will map your columns automatically.")
        uploaded_file = st.file_uploader("Upload Course Excel", type=["xlsx"])
        
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).strip() for c in df.columns] # Clean hidden spaces
            st.dataframe(df.head(3)) # Preview
            
            if st.button("🔥 Push All Data to Cloud"):
                with st.spinner("Processing rows..."):
                    success_count = 0
                    for _, row in df.iterrows():
                        try:
                            # Mapping based on your specific spreadsheet columns
                            payload = {
                                "course_name": str(row.get('Topic Covered', row.get('title', 'Unnamed'))),
                                "week": int(row.get('Week', 1)) if pd.notna(row.get('Week')) else 1,
                                "video_url": str(row.get('Embeddable YouTube Video Link', row.get('YouTube link', ''))),
                                "notes_url": str(row.get('link to Google docs Document', row.get('link', '')))
                            }
                            supabase.table("materials").insert(payload).execute()
                            success_count += 1
                        except:
                            continue
                st.success(f"✅ Uploaded {success_count} rows successfully!")

# --- PRESIDENT VIEW ---
elif role == "President":
    st.header("📢 President's Notice Board")
    with st.form("post_notice"):
        title = st.text_input("Notice Title")
        content = st.text_area("Announcement Details")
        if st.form_submit_button("📢 Post to Student Portal"):
            try:
                supabase.table("notices").insert({"title": title, "content": content}).execute()
                st.success("Announcement is now live!")
            except Exception as e:
                st.error(f"Check if 'notices' table exists: {e}")

# --- STUDENT VIEW (The Expander UI you liked) ---
elif role == "Student":
    st.title("📚 KIU Student Portal")
    
    # 1. Announcements Section
    try:
        notices = supabase.table("notices").select("*").order("created_at", desc=True).execute()
        if notices.data:
            with st.container():
                st.subheader("🔔 Latest Notices")
                for n in notices.data[:2]: # Show last 2 notices
                    st.info(f"**{n['title']}**: {n['content']}")
                st.divider()
    except:
        pass

    # 2. Materials Section
    try:
        res = supabase.table("materials").select("*").order("week").execute()
        if res.data:
            st.subheader("📖 Course Modules")
            for item in res.data:
                # Grouped by Week in Expanders
                with st.expander(f"Week {item['week']} - {item['course_name']}"):
                    c1, c2 = st.columns(2)
                    if item.get('video_url'): 
                        c1.link_button("📺 Watch Lecture", item['video_url'])
                    if item.get('notes_url'): 
                        c2.link_button("📝 Read Notes", item['notes_url'])
        else:
            st.info("No materials available yet. Please check back later.")
    except Exception as e:
        st.error(f"Database Error: {e}")

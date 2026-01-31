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

# 2. UI BRANDING & NAVIGATION
st.set_page_config(page_title="KIU Q10 Portal", layout="wide")

st.sidebar.title("🎓 Q10 KIU Portal")
role = st.sidebar.radio("Select Your Role:", ["Student", "President", "Admin"])

# --- ADMIN VIEW ---
if role == "Admin":
    st.header("🛠 Global Admin Dashboard")
    tab_single, tab_bulk = st.tabs(["➕ Single Entry", "📊 Bulk Excel Upload"])
    
    with tab_single:
        with st.form("admin_upload"):
            c_name = st.text_input("Course Name (e.g., Atomic Structure)")
            week = st.number_input("Week", 1, 15)
            v_url = st.text_input("YouTube Link")
            n_url = st.text_input("Notes Link")
            
            if st.form_submit_button("Save Single Course"):
                if c_name:
                    supabase.table("materials").insert({
                        "course_name": c_name, "week": week, 
                        "video_url": v_url, "notes_url": n_url
                    }).execute()
                    st.success(f"✅ Successfully added: {c_name}")

    with tab_bulk:
        st.subheader("📊 Bulk Import from Excel")
        st.info("Ensure your Excel columns are named: 'Topic Covered', 'Week', 'Embeddable YouTube Video Link', 'link to Google docs Document'")
        uploaded_file = st.file_uploader("Upload your Excel sheet", type=["xlsx"])
        
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).strip() for c in df.columns] # Clean hidden spaces
            
            if st.button("🚀 Push All Data to Cloud"):
                with st.spinner("Uploading to KIU Database..."):
                    for _, row in df.iterrows():
                        supabase.table("materials").insert({
                            "course_name": str(row.get('Topic Covered', 'Unnamed')),
                            "week": int(row.get('Week', 1)) if pd.notna(row.get('Week')) else 1,
                            "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                            "notes_url": str(row.get('link to Google docs Document', ''))
                        }).execute()
                st.success("🔥 Success! All records are now live.")

# --- PRESIDENT VIEW ---
elif role == "President":
    st.header("📢 President's Notice Board")
    with st.form("post_notice"):
        title = st.text_input("Notice Title")
        content = st.text_area("Content")
        if st.form_submit_button("Post Notice"):
            supabase.table("notices").insert({"title": title, "content": content}).execute()
            st.success("Notice Posted Successfully!")

# --- STUDENT VIEW ---
elif role == "Student":
    st.title("📚 Student Learning Portal")
    
    # Show Notices First
    try:
        notices = supabase.table("notices").select("*").order("created_at", desc=True).execute()
        if notices.data:
            st.subheader("Latest Announcements")
            for n in notices.data:
                st.warning(f"🔔 **{n['title']}**: {n['content']}")
    except:
        pass # Skip if notices table isn't set up yet

    # Show Course Materials
    try:
        res = supabase.table("materials").select("*").order("week").execute()
        if res.data:
            st.subheader("Learning Modules")
            for item in res.data:
                with st.expander(f"📖 Week {item['week']}: {item['course_name']}"):
                    col1, col2 = st.columns(2)
                    if item.get('video_url'): 
                        col1.link_button("📺 Watch Video", item['video_url'])
                    if item.get('notes_url'): 
                        col2.link_button("📝 View Notes", item['notes_url'])
        else:
            st.info("No materials available yet. Admin needs to upload the Excel sheet.")
    except Exception as e:
        st.error(f"⚠️ Database Connection Error: {e}")
        st.info("Did you run the SQL commands in Supabase to create the tables?")

import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Setup Connection to Supabase
# Ensure these keys are set in your Streamlit Cloud Secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 2. Sidebar Navigation - Defining 'role' first to prevent NameError
st.sidebar.title("🔐 KIU Portal Access")
role = st.sidebar.radio("Select Your Role:", ["Home", "Student", "President", "Admin"])

# 3. Application Logic
if role == "Home":
    st.title("🎓 Q10 KIU Learning Portal")
    st.write("Welcome to the official repository for course materials and notices.")
    st.info("Please select your role in the sidebar to view content or manage data.")

elif role == "Admin":
    st.header("🛠 Global Admin Dashboard")
    tab_single, tab_bulk = st.tabs(["Single Entry", "Bulk Excel Upload"])
    
    with tab_single:
        with st.form("admin_upload"):
            c_name = st.text_input("Course Name")
            week = st.number_input("Week", 1, 15)
            v_url = st.text_input("YouTube Video URL")
            n_url = st.text_input("Google Drive Notes URL")
            q_url = st.text_input("Questions URL (Short Answers)")
            
            if st.form_submit_button("Save Single Course"):
                if c_name:
                    supabase.table("materials").insert({
                        "course_name": c_name, "week": week, 
                        "video_url": v_url, "notes_url": n_url, "questions_url": q_url
                    }).execute()
                    st.success(f"✅ Successfully added: {c_name}")
                else:
                    st.error("Please provide a Course Name.")

    with tab_bulk:
        st.subheader("📊 Bulk Import from Excel")
        st.info("The uploader matches: 'Course Name', 'Week', 'Video URL', 'Notes URL', 'Questions URL'")
        uploaded_file = st.file_uploader("Upload your Excel sheet", type=["xlsx"])
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                # Clean column names to remove trailing spaces that cause KeyErrors
                df.columns = df.columns.str.strip()
                
                st.write("Columns Detected:", list(df.columns))
                st.write("Preview of your data:", df.head())
                
                if st.button("🚀 Push All Data to Cloud"):
                    with st.spinner("Uploading to KIU Database..."):
                        for _, row in df.iterrows():
                            # Using .get() ensures the app won't crash if a column is missing
                            supabase.table("materials").insert({
                                "course_name": str(row.get('Course Name', 'Unnamed Course')),
                                "week": int(row.get('Week', 0)),
                                "video_url": str(row.get('Video URL', '')),
                                "notes_url": str(row.get('Notes URL', '')),
                                "questions_url": str(row.get('Questions URL', ''))
                            }).execute()
                    st.success(f"🔥 Success! {len(df)} records are now live.")
            except Exception as e:
                st.error(f"❌ Error processing file: {e}")

elif role == "President":
    st.header("📢 President's Notice Board")
    with st.form("post_notice"):
        title = st.text_input("Notice Title")
        content = st.text_area("Content")
        if st.form_submit_button("Post Notice"):
            supabase.table("notices").insert({"title": title, "content": content, "posted_by": "President"}).execute()
            st.success("Notice Posted Successfully!")

elif role == "Student":
    st.header("📚 Student Portal")
    
    # 1. Display Notices
    res_n = supabase.table("notices").select("*").order("created_at", desc=True).execute()
    if res_n.data:
        st.subheader("Latest Announcements")
        for n in res_n.data:
            with st.expander(f"📌 {n['title']}"):
                st.write(n['content'])
    
    # 2. Display Course Materials
    res_m = supabase.table("materials").select("*").order("week").execute()
    if res_m.data:
        st.subheader("Learning Materials")
        for item in res_m.data:
            st.write(f"### Week {item['week']}: {item['course_name']}")
            c1, c2, c3 = st.columns(3)
            if item.get('video_url'): c1.link_button("📺 Watch Video", item['video_url'])
            if item.get('notes_url'): c2.link_button("📝 View Notes", item['notes_url'])
            if item.get('questions_url'): c3.link_button("❓ Questions", item['questions_url'])
            st.divider()

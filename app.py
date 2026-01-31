import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Setup Connection
# Make sure these match your Streamlit Secrets exactly
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 2. Define the User Role FIRST
# This fixes the NameError because 'role' is now defined before the 'if' statements
st.sidebar.title("🔐 KIU Portal Access")
role = st.sidebar.radio("Select Your Role:", ["Student", "President", "Admin"])

# 3. App Logic
if role == "Admin":
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
                        "course_name": c_name, 
                        "week": week, 
                        "video_url": v_url, 
                        "notes_url": n_url, 
                        "questions_url": q_url
                    }).execute()
                    st.success(f"✅ Successfully added: {c_name}")
                else:
                    st.error("Please provide a Course Name.")

    with tab_bulk:
        st.subheader("📊 Excel Bulk Import")
        st.info("Required columns: 'Course Name', 'Week', 'Video URL', 'Notes URL', 'Questions URL'")
        uploaded_file = st.file_uploader("Upload your Excel sheet", type=["xlsx"])
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.write("Preview of your data:", df.head())
                
                if st.button("🚀 Push All Data to Cloud"):
                    with st.spinner("Uploading to KIU Database..."):
                        for index, row in df.iterrows():
                            data_to_insert = {
                                "course_name": str(row['Course Name']),
                                "week": int(row['Week']),
                                "video_url": str(row['Video URL']) if pd.notna(row['Video URL']) else "",
                                "notes_url": str(row['Notes URL']) if pd.notna(row['Notes URL']) else "",
                                "questions_url": str(row['Questions URL']) if pd.notna(row['Questions URL']) else ""
                            }
                            supabase.table("materials").insert(data_to_insert).execute()
                    st.success(f"🔥 Success! {len(df)} records are now live.")
            except Exception as e:
                st.error(f"❌ Error: {e}. Check if column names match exactly.")

elif role == "President":
    st.header("📢 President's Notice Board")
    with st.form("post_notice"):
        title = st.text_input("Notice Title")
        content = st.text_area("Notice Content")
        if st.form_submit_button("Broadcast to Class"):
            supabase.table("notices").insert({
                "title": title, "content": content, "posted_by": "President"
            }).execute()
            st.success("Notice Posted!")

elif role == "Student":
    st.header("📚 Student Learning Portal")
    
    # Show Notices
    notices = supabase.table("notices").select("*").order("created_at", desc=True).execute()
    if notices.data:
        st.subheader("Latest Announcements")
        for n in notices.data:
            with st.expander(f"📌 {n['title']}"):
                st.write(n['content'])
    
    # Show Materials
    data = supabase.table("materials").select("*").order("week").execute()
    if data.data:
        st.subheader("Course Materials")
        for item in data.data:
            with st.container():
                st.write(f"### Week {item['week']}: {item['course_name']}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if item['video_url']:
                        st.link_button("📺 Watch Video", item['video_url'])
                with col2:
                    if item['notes_url']:
                        st.link_button("📝 View Notes", item['notes_url'])
                with col3:
                    if item['questions_url']:
                        st.link_button("❓ Questions", item['questions_url'])
                st.divider()

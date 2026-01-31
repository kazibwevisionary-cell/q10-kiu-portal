import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Setup Connection
# These must match your Streamlit Secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 2. Sidebar Navigation
st.sidebar.title("🔐 KIU Portal Access")
role = st.sidebar.radio("Select Your Role:", ["Home", "Student", "President", "Admin"])

# 3. App Logic
if role == "Home":
    st.title("🎓 Q10 KIU Learning Portal")
    st.write("Welcome to the official repository for course materials and notices.")
    st.info("Select your role in the sidebar to get started.")

elif role == "Admin":
    st.header("🛠 Global Admin Dashboard")
    tab_single, tab_bulk = st.tabs(["Single Entry", "Bulk Excel Upload"])
    
    with tab_single:
        with st.form("admin_upload"):
            c_name = st.text_input("Course Name")
            week = st.number_input("Week", 1, 15)
            v_url = st.text_input("YouTube Video URL")
            n_url = st.text_input("Google Drive Notes URL")
            q_url = st.text_input("Questions URL")
            if st.form_submit_button("Save Single Course"):
                supabase.table("materials").insert({
                    "course_name": c_name, "week": week, 
                    "video_url": v_url, "notes_url": n_url, "questions_url": q_url
                }).execute()
                st.success("✅ Added successfully!")

    with tab_bulk:
        st.subheader("📊 Bulk Import")
        uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            if st.button("🚀 Push All to Cloud"):
                for _, row in df.iterrows():
                    supabase.table("materials").insert({
                        "course_name": str(row['Course Name']),
                        "week": int(row['Week']),
                        "video_url": str(row['Video URL']) if pd.notna(row['Video URL']) else "",
                        "notes_url": str(row['Notes URL']) if pd.notna(row['Notes URL']) else "",
                        "questions_url": str(row['Questions URL']) if pd.notna(row['Questions URL']) else ""
                    }).execute()
                st.success("🔥 Bulk Upload Complete!")

elif role == "President":
    st.header("📢 President's Notice Board")
    with st.form("post_notice"):
        title = st.text_input("Notice Title")
        content = st.text_area("Content")
        if st.form_submit_button("Post Notice"):
            supabase.table("notices").insert({"title": title, "content": content, "posted_by": "President"}).execute()
            st.success("Notice Posted!")

elif role == "Student":
    st.header("📚 Student Portal")
    
    # Show Notices
    res_n = supabase.table("notices").select("*").order("created_at", desc=True).execute()
    if res_n.data:
        st.subheader("Announcements")
        for n in res_n.data:
            with st.expander(f"📌 {n['title']}"):
                st.write(n['content'])
    
    # Show Materials
    res_m = supabase.table("materials").select("*").order("week").execute()
    if res_m.data:
        st.subheader("Course Materials")
        for item in res_m.data:
            st.write(f"### Week {item['week']}: {item['course_name']}")
            c1, c2, c3 = st.columns(3)
            if item['video_url']: c1.link_button("📺 Video", item['video_url'])
            if item['notes_url']: c2.link_button("📝 Notes", item['notes_url'])
            if item['questions_url']: c3.link_button("❓ Questions", item['questions_url'])
            st.divider()

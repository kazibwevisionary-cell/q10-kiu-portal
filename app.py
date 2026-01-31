import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Connection with Debugger
try:
    # Clean the secrets to remove hidden spaces/newlines
    raw_url = st.secrets["SUPABASE_URL"].strip()
    raw_key = st.secrets["SUPABASE_KEY"].strip()
    
    # Remove a trailing slash if it exists
    if raw_url.endswith("/"):
        raw_url = raw_url[:-1]

    supabase = create_client(raw_url, raw_key)
except Exception as e:
    st.error(f"❌ Connection Setup Failed!")
    st.info(f"The app is trying to connect to: {st.secrets.get('SUPABASE_URL', 'NOT FOUND')}")
    st.write(f"Error Details: {e}")
    st.stop()

# 2. Navigation
role = st.sidebar.radio("Identify Role:", ["Student", "Admin"])

if role == "Admin":
    st.header("🛠 Bulk Upload (KIU Portal)")
    file = st.file_uploader("Upload Excel", type=["xlsx"])
    
    if file:
        df = pd.read_excel(file)
        df.columns = [str(c).strip() for c in df.columns] # Clean spaces in headers
        
        if st.button("🚀 Push to Database"):
            with st.spinner("Uploading..."):
                for _, row in df.iterrows():
                    # This matches your spreadsheet: title, link, YouTube link
                    supabase.table("materials").insert({
                        "course_name": str(row.get('title', 'No Title')),
                        "week": int(row.get('Week', 1)) if 'Week' in df.columns else 1,
                        "video_url": str(row.get('YouTube link', '')),
                        "notes_url": str(row.get('link', '')),
                        "questions_url": str(row.get('Short Answer On link', ''))
                    }).execute()
            st.success("Success! Data is live.")

elif role == "Student":
    st.title("📚 Course Materials")
    try:
        data = supabase.table("materials").select("*").order("week").execute()
        for item in data.data:
            with st.expander(f"Week {item['week']}: {item['course_name']}"):
                c1, c2, c3 = st.columns(3)
                if item['video_url']: c1.link_button("📺 Video", item['video_url'])
                if item['notes_url']: c2.link_button("📝 Notes", item['notes_url'])
                if item['questions_url']: c3.link_button("❓ Quiz", item['questions_url'])
    except Exception as e:
        st.error(f"Database Error: {e}")

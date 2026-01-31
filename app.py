import streamlit as st
import pandas as pd
from supabase import create_client, Client

# 1. Connection with Pre-Check
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    
    # Validation: Ensure URL is formatted correctly
    if not url.startswith("https://"):
        st.error("❌ SUPABASE_URL must start with 'https://'")
        st.stop()
        
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"⚠️ Connection Setup Error: {e}")
    st.info("Please check your Streamlit Secrets for typos.")
    st.stop()

# 2. Sidebar Navigation
st.sidebar.title("🔐 KIU Portal")
role = st.sidebar.radio("Role:", ["Student", "Admin"])

if role == "Admin":
    st.header("🛠 Bulk Content Uploader")
    uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).strip() for c in df.columns] # Clean headers
            
            if st.button("🚀 Push to Cloud"):
                with st.spinner("Connecting to database..."):
                    for _, row in df.iterrows():
                        # Maps data from your spreadsheet: Title, link, and YouTube Link [cite: 1, 2]
                        payload = {
                            "course_name": str(row.get('title', 'Unknown')),
                            "week": int(row.get('Week', 1)) if 'Week' in df.columns else 1,
                            "video_url": str(row.get('YouTube link', '')),
                            "notes_url": str(row.get('link', '')),
                            "questions_url": str(row.get('Short Answer On link', ''))
                        }
                        supabase.table("materials").insert(payload).execute()
                st.success("✅ Uploaded successfully!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

elif role == "Student":
    st.title("📚 Course Materials")
    try:
        # Fetching data for topics like Atomic Structure and Crystal Geometry [cite: 2]
        res = supabase.table("materials").select("*").order("week").execute()
        for item in res.data:
            with st.expander(f"Week {item['week']}: {item['course_name']}"):
                c1, c2, c3 = st.columns(3)
                if item.get('video_url'): c1.link_button("📺 Video", item['video_url'])
                if item.get('notes_url'): c2.link_button("📝 Notes", item['notes_url'])
                if item.get('questions_url'): c3.link_button("❓ Questions", item['questions_url'])
    except Exception as e:
        st.error(f"Database error: {e}")

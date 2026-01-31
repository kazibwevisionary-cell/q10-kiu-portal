import streamlit as st
import pandas as pd
from supabase import create_client

# 1. Setup Connection
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Credential Error: Check your Streamlit Secrets.")
    st.stop()

# 2. Sidebar Navigation
st.sidebar.title("🔐 KIU Portal Access")
role = st.sidebar.radio("Select Your Role:", ["Home", "Student", "President", "Admin"])

# 3. Application Logic
if role == "Home":
    st.title("🎓 Q10 KIU Learning Portal")
    st.write("Welcome to the official repository for KIU course materials.")
    st.info("👈 Use the sidebar to log in as a Student, President, or Admin.")

elif role == "Admin":
    st.header("🛠 Global Admin Dashboard")
    tab1, tab2 = st.tabs(["Single Entry", "Bulk Excel Upload"])
    
    with tab1:
        with st.form("single_upload"):
            c_name = st.text_input("Course Name")
            week = st.number_input("Week", 1, 15)
            v_url = st.text_input("YouTube Link")
            n_url = st.text_input("Notes Link")
            q_url = st.text_input("Questions Link")
            if st.form_submit_button("Save"):
                supabase.table("materials").insert({
                    "course_name": c_name, "week": week, "video_url": v_url, 
                    "notes_url": n_url, "questions_url": q_url
                }).execute()
                st.success("Uploaded!")

    with tab2:
        st.subheader("📊 Bulk Excel Upload")
        uploaded_file = st.file_uploader("Choose Excel File", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).strip() for c in df.columns] # Remove hidden spaces
            st.write("Columns found:", list(df.columns))
            
            if st.button("🚀 Push to Cloud"):
                for _, row in df.iterrows():
                    # This .get() method prevents "KeyError" if columns are missing
                    payload = {
                        "course_name": str(row.get('Course Name', row.get('title', 'Unknown'))),
                        "week": int(row.get('Week', 0)),
                        "video_url": str(row.get('Video URL', row.get('YouTube link', ''))),
                        "notes_url": str(row.get('Notes URL', row.get('link', ''))),
                        "questions_url": str(row.get('Questions URL', ''))
                    }
                    supabase.table("materials").insert(payload).execute()
                st.success("Done!")

elif role == "President":
    st.header("📢 Post a Notice")
    title = st.text_input("Title")
    msg = st.text_area("Message")
    if st.button("Post"):
        supabase.table("notices").insert({"title": title, "content": msg}).execute()
        st.success("Posted!")

elif role == "Student":
    st.header("📚 Materials")
    res = supabase.table("materials").select("*").order("week").execute()
    for item in res.data:
        with st.expander(f"Week {item['week']}: {item['course_name']}"):
            c1, c2, c3 = st.columns(3)
            if item['video_url']: c1.link_button("📺 Video", item['video_url'])
            if item['notes_url']: c2.link_button("📝 Notes", item['notes_url'])
            if item['questions_url']: c3.link_button("❓ Questions", item['questions_url'])

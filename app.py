import streamlit as st
import pandas as pd
from supabase import create_client
import re

# 1. DATABASE CONNECTION
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" 

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    st.error("Connection error.")
    st.stop()

# 2. UI CONFIG
st.set_page_config(page_title="KIU Q10 Portal", layout="wide", page_icon="🎓")

# Custom CSS for Professional Footer and Video Embedding
st.markdown("""
    <style>
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 8px; color: #888; font-size: 12px; background: white; border-top: 1px solid #eee; z-index: 1000; }
    .video-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 8px; margin-bottom: 10px;}
    .video-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN GATE
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🎓 KIU Q10 Portal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        with st.container(border=True):
            st.subheader("Student & Staff Login")
            st.text_input("Username")
            st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True) or st.button("⏭️ Skip & Browse Courses", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
    st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True)
    st.stop()

# 4. NAVIGATION
st.sidebar.title("🎓 KIU Portal")
role = st.sidebar.radio("Navigation:", ["Student Portal", "Admin Dashboard", "President Board"])

# --- ADMIN DASHBOARD ---
if role == "Admin Dashboard":
    st.header("🛠 Admin Management")
    t1, t2, t3 = st.tabs(["➕ Add Single", "📊 Bulk Upload", "🗑️ Manage Content"])
    
    with t1:
        with st.form("manual"):
            p = st.text_input("Course Name")
            t = st.text_input("Topic")
            w = st.number_input("Week", 1, 15)
            y = st.text_input("Video/Slide Link")
            n = st.text_input("Notes Link")
            if st.form_submit_button("Save Entry"):
                supabase.table("materials").insert({"course_program": p, "course_name": t, "week": w, "video_url": y, "notes_url": n}).execute()
                st.success("Saved!")

    with t2:
        target = st.text_input("Assign to Course (e.g., Petroleum Engineering)")
        wipe = st.checkbox("Wipe existing data for this course name first?")
        f = st.file_uploader("Upload Excel/CSV", type=["xlsx", "csv"])
        if f and target and st.button("🚀 Push to Database"):
            if wipe: supabase.table("materials").delete().eq("course_program", target).execute()
            df = pd.read_excel(f) if "xlsx" in f.name else pd.read_csv(f)
            df.columns = [str(c).strip() for c in df.columns]
            for _, row in df.iterrows():
                supabase.table("materials").insert({
                    "course_program": target,
                    "course_name": str(row.get('Topic Covered', '')),
                    "week": int(row.get('Week', 1)) if 'Week' in df.columns else 1,
                    "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                    "notes_url": str(row.get('link to Google docs Document', ''))
                }).execute()
            st.success("Bulk Upload Complete!")

    with t3:
        st.subheader("🗑️ Delete Course Materials")
        data = supabase.table("materials").select("*").execute()
        if data.data:
            for item in data.data:
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{item['course_program']}** | Wk {item['week']}: {item['course_name']}")
                if c2.button("🗑️ Delete", key=f"del_{item['id']}"):
                    supabase.table("materials").delete().eq("id", item['id']).execute()
                    st.rerun()

# --- PRESIDENT BOARD ---
elif role == "President Board":
    st.header("📢 Announcements")
    with st.form("p"):
        tt = st.text_input("Title")
        mm = st.text_area("Message")
        if st.form_submit_button("Post Notice"):
            supabase.table("notices").insert({"title": tt, "content": mm}).execute()
            st.success("Posted!")

# --- STUDENT PORTAL ---
elif role == "Student Portal":
    st.title("📖 Course Materials")
    search = st.text_input("🔍 Search your Course (e.g. 'Petroleum Engineering')").strip()
    
    if search:
        res = supabase.table("materials").select("*").ilike("course_program", f"%{search}%").order("week").execute()
        if res.data:
            for item in res.data:
                with st.expander(f"📚 Week {item['week']} - {item['course_name']}"):
                    url = str(item.get('video_url', ''))
                    
                    # 1. SMART EMBED LOGIC
                    if "youtube.com" in url or "youtu.be" in url:
                        # Convert standard link to embed link
                        video_id = ""
                        if "v=" in url: video_id = url.split("v=")[1].split("&")[0]
                        elif "be/" in url: video_id = url.split("be/")[1]
                        elif "embed/" in url: video_id = url.split("embed/")[1]
                        
                        embed_url = f"https://www.youtube.com/embed/{video_id}"
                        st.markdown(f'<div class="video-container"><iframe src="{embed_url}" allowfullscreen></iframe></div>', unsafe_allow_html=True)
                    
                    elif "docs.google.com/presentation" in url:
                        # If it's a slide deck instead of a video
                        st.info("No video lecture: Displaying Presentation Slides")
                        slide_url = url.replace("/edit", "/embed")
                        st.markdown(f'<div class="video-container"><iframe src="{slide_url}"></iframe></div>', unsafe_allow_html=True)
                    
                    else:
                        st.warning("No video or slide link detected for this module.")
                    
                    if item.get('notes_url'):
                        st.link_button("📝 Read Full Notes", item['notes_url'])
        else:
            st.info("No materials found. Check spelling or contact your Admin.")

# 5. FOOTER
st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True)

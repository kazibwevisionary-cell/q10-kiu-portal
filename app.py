import streamlit as st
import pandas as pd
from supabase import create_client

# 1. DATABASE CONNECTION
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" 

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    st.error("Connection error. Check database status.")
    st.stop()

# 2. UI CONFIG & FOOTER STYLING
st.set_page_config(page_title="KIU Q10 Portal", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #666; font-size: 14px; background: white; border-top: 1px solid #eee; z-index: 999; }
    .video-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 8px; margin-bottom: 10px; }
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
            st.subheader("Login")
            st.text_input("Username")
            st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True) or st.button("⏭️ Skip & Browse", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
    st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True)
    st.stop()

# 4. NAVIGATION
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
        target = st.text_input("Course Name (e.g., Petroleum Engineering)")
        wipe = st.checkbox("Wipe existing data for this course name first?")
        f = st.file_uploader("Upload File", type=["xlsx", "csv"])
        if f and target and st.button("🚀 Push to Cloud"):
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
            st.success("Upload Successful!")

    with t3:
        data = supabase.table("materials").select("*").execute()
        for item in data.data:
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{item['course_program']}** | Week {item['week']}: {item['course_name']}")
            if c2.button("🗑️ Delete", key=f"del_{item['id']}"):
                supabase.table("materials").delete().eq("id", item['id']).execute()
                st.rerun()

# --- PRESIDENT BOARD ---
elif role == "President Board":
    st.header("📢 Post Notice")
    with st.form("p"):
        tt = st.text_input("Title")
        mm = st.text_area("Message")
        if st.form_submit_button("Post"):
            supabase.table("notices").insert({"title": tt, "content": mm}).execute()
            st.success("Posted!")

# --- STUDENT PORTAL ---
elif role == "Student Portal":
    st.title("📖 Course Materials")
    search = st.text_input("🔍 Search Course (e.g. 'Petroleum Engineering')").strip()
    
    if search:
        res = supabase.table("materials").select("*").ilike("course_program", f"%{search}%").order("week").execute()
        if res.data:
            for item in res.data:
                with st.expander(f"📚 Week {item['week']} - {item['course_name']}"):
                    raw_url = str(item.get('video_url', ''))
                    
                    # 📽️ YOUTUBE HANDLING
                    if "youtube.com" in raw_url or "youtu.be" in raw_url:
                        # Extract Video ID and force Embed format
                        if "v=" in raw_url:
                            v_id = raw_url.split("v=")[1].split("&")[0]
                        else:
                            v_id = raw_url.split("/")[-1]
                        
                        embed_url = f"https://www.youtube.com/embed/{v_id}"
                        
                        st.markdown(f'<div class="video-container"><iframe src="{embed_url}" allowfullscreen></iframe></div>', unsafe_allow_html=True)
                        st.link_button("📺 Watch on YouTube (If embed shows error)", f"https://www.youtube.com/watch?v={v_id}")
                    
                    # 📊 GOOGLE SLIDES HANDLING
                    elif "docs.google.com" in raw_url:
                        st.info("No video available. Loading Presentation Slides...")
                        slide_url = raw_url.replace("/edit", "/embed")
                        st.markdown(f'<div class="video-container"><iframe src="{slide_url}"></iframe></div>', unsafe_allow_html=True)
                        st.link_button("📂 Open Original Slides", raw_url)

                    if item.get('notes_url'):
                        st.write("---")
                        st

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
    st.error("Database Connection Failed.")
    st.stop()

# 2. UI CONFIG & FOOTER
st.set_page_config(page_title="Flux Portal", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #666; font-size: 14px; background: white; border-top: 1px solid #eee; z-index: 999; }
    .video-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 8px; margin-bottom: 10px; }
    .video-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
    .course-tile { border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin-bottom: 20px; transition: 0.3s; }
    .course-tile:hover { border-color: #ff4b4b; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN PAGE
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>⚡ Flux Portal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        with st.container(border=True):
            st.subheader("Login Access")
            st.text_input("Username")
            st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True) or st.button("⏭️ Skip & Browse", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
    st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True)
    st.stop()

# 4. SIDEBAR
role = st.sidebar.radio("Navigation", ["Student Portal", "Admin Dashboard", "President Board"])

# --- ADMIN DASHBOARD ---
if role == "Admin Dashboard":
    st.header("🛠 Flux Management Console")
    t1, t2, t3 = st.tabs(["➕ Add Entry", "📊 Bulk Upload", "🗑️ Delete Content"])
    
    with t1:
        with st.form("manual"):
            p = st.text_input("Course Name (Program)")
            t = st.text_input("Module Topic")
            w = st.number_input("Week Number", 1, 15)
            y = st.text_input("YouTube/Slide Link")
            n = st.text_input("Notes Link")
            img = st.text_input("Course Image URL (for tiles)")
            if st.form_submit_button("Save to Flux"):
                supabase.table("materials").insert({
                    "course_program": p, 
                    "course_name": t, 
                    "week": w, 
                    "video_url": y, 
                    "notes_url": n,
                    "image_url": img
                }).execute()
                st.success("Module saved successfully!")

    with t2:
        target = st.text_input("Target Course Name (e.g. Petroleum Engineering)")
        target_img = st.text_input("Default Image URL for this batch")
        wipe = st.checkbox("Wipe current data for this course before upload?")
        f = st.file_uploader("Upload CSV/Excel", type=["xlsx", "csv"])
        if f and target and st.button("🚀 Start Bulk Upload"):
            if wipe: supabase.table("materials").delete().eq("course_program", target).execute()
            df = pd.read_excel(f) if "xlsx" in f.name else pd.read_csv(f)
            df.columns = [str(c).strip() for c in df.columns]
            for _, row in df.iterrows():
                supabase.table("materials").insert({
                    "course_program": target,
                    "course_name": str(row.get('Topic Covered', '')),
                    "week": int(row.get('Week', 1)) if 'Week' in df.columns else 1,
                    "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                    "notes_url": str(row.get('link to Google docs Document', '')),
                    "image_url": target_img
                }).execute()
            st.success("Bulk Upload Finished!")

    with t3:
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
    st.header("📢 Post Announcements")
    with st.form("notice"):
        tt = st.text_input("Notice Title")
        mm = st.text_area("Detailed Message")
        if st.form_submit_button("Publish Now"):
            supabase.table("notices").insert({"title": tt, "content": mm}).execute()
            st.success("Notice published to all students!")

# --- STUDENT PORTAL ---
elif role == "Student Portal":
    st.title("📖 Flux Learning Modules")
    
    # Keyword search bar
    search_query = st.text_input("🔍 Search for your Course or Topic (Keyword)")
    search_btn = st.button("Enter", use_container_width=True)
    
    # 1. Show Visual Tiles (Course Thumbnails) when not searching
    if not search_query:
        st.subheader("Explore Courses")
        # Fetch unique courses to show as tiles
        tiles_data = supabase.table("materials").select("course_program, image_url").execute()
        if tiles_data.data:
            unique_courses = {item['course_program']: item['image_url'] for item in tiles_data.data}
            cols = st.columns(4)
            for idx, (c_name, c_img) in enumerate(unique_courses.items()):
                with cols[idx % 4]:
                    st.markdown(f'<div class="course-tile">', unsafe_allow_html=True)
                    if c_img:
                        st.image(c_img, use_column_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x200?text=No+Image", use_column_width=True)
                    st.markdown(f"**{c_name}**", unsafe_allow_html=True)
                    if st.button(f"View {c_name}", key=f"btn_{idx}"):
                        search_query = c_name
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Search Logic (Allows keyword search across program and topic)
    if search_query or search_btn:
        # Search by keyword in course_program OR course_name
        res = supabase.table("materials").select("*").or_(f"course_program.ilike.%{search_query}%,course_name.ilike.%{search_query}%").order("week").execute()
        
        if res.data:
            st.divider()
            st.subheader(f"Results for: {search_query}")
            for item in res.data:
                with st.expander(f"📚 {item['course_program']} | Week {item['week']} - {item['course_name']}"):
                    raw_url = str(item.get('video_url', ''))
                    
                    if "youtube.com" in raw_url or "youtu.be" in raw_url:
                        v_id = raw_url.split("v=")[1].split("&")[0] if "v=" in raw_url else raw_url.split("/")[-1]
                        embed_url = f"https://www.youtube.com/embed/{v_id}"
                        st.markdown(f'<div class="video-container"><iframe src="{embed_url}" allowfullscreen></iframe></div>', unsafe_allow_html=True)
                        st.link_button("📺 Watch on YouTube", f"https://www.youtube.com/watch?v={v_id}")
                    
                    elif "docs.google.com" in raw_url:
                        st.info("Presentation Slides Available")
                        slide_url = raw_url.replace("/edit", "/embed")
                        st.markdown(f'<div class="video-container"><iframe src="{slide_url}"></iframe></div>', unsafe_allow_html=True)
                        st.link_button("📂 View Full Slides", raw_url)

                    if item.get('notes_url'):
                        st.write("---")
                        st.link_button("📝 Read Lecture Notes", item['notes_url'])
        else:
            st.warning("No modules found matching that keyword.")

# 5. FIXED FOOTER
st.markdown('<div class="footer">Built by KMT Dynamics | Flux Portal</div>', unsafe_allow_html=True)

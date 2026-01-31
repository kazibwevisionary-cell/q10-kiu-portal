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
                        st.success(f"Successfully added: {c_name}")
                    else:
                        st.error("Please provide a Course Name.")

        with tab_bulk:
            st.subheader("Excel Bulk Import")
            st.info("Template columns required: 'Course Name', 'Week', 'Video URL', 'Notes URL', 'Questions URL'")
            uploaded_file = st.file_uploader("Upload your Excel sheet", type=["xlsx"])
            
            if uploaded_file:
                try:
                    df = pd.read_excel(uploaded_file)
                    st.write("Preview of your data:", df.head())
                    
                    if st.button("🚀 Push All Data to Cloud"):
                        with st.spinner("Uploading to KIU Database..."):
                            for index, row in df.iterrows():
                                # This maps your Excel columns directly to the Database
                                data_to_insert = {
                                    "course_name": str(row['Course Name']),
                                    "week": int(row['Week']),
                                    "video_url": str(row['Video URL']) if pd.notna(row['Video URL']) else "",
                                    "notes_url": str(row['Notes URL']) if pd.notna(row['Notes URL']) else "",
                                    "questions_url": str(row['Questions URL']) if pd.notna(row['Questions URL']) else ""
                                }
                                supabase.table("materials").insert(data_to_insert).execute()
                        st.success(f"Success! {len(df)} records are now live.")
                except Exception as e:
                    st.error(f"Error processing file: {e}. Check if column names match exactly.")

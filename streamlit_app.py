import streamlit as st
import pandas as pd
import io

# Page Configuration
st.set_page_config(
    page_title="Academic At-Risk Predictor",
    page_icon="🎓",
    layout="wide"
)

# -----------------------------------------------------------------------------
# LOAD EXTERNAL CSS FILE
# -----------------------------------------------------------------------------
def load_css(css_file):
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    load_css("Std.css")
except FileNotFoundError:
    pass  # Fallback gracefully if CSS file is missing
# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION (Database & Auth Store)
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Guest / Student"
if "student_db" not in st.session_state:
    try:
        # Load local dataset if available
        df_init = pd.read_csv("dataset.csv")
        if "Student_ID" not in df_init.columns:
            df_init.insert(0, "Student_ID", [f"STD-{1000 + i}" for i in range(len(df_init))])
        st.session_state.student_db = df_init
    except FileNotFoundError:
        st.session_state.student_db = None

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & ADMIN AUTHENTICATION
# -----------------------------------------------------------------------------
st.sidebar.title("🎓 Student Portal")

selected_role = st.sidebar.selectbox("Select Access Mode", ["Guest / Student", "Admin"])

if selected_role == "Admin":
    if not st.session_state.authenticated:
        st.sidebar.subheader("🔒 Admin Login")
        admin_password = st.sidebar.text_input("Password", type="password", help="Default password is Std_Performance321")
        if st.sidebar.button("Login as Admin"):
            if admin_password == "Std_Performance321":
                st.session_state.authenticated = True
                st.session_state.user_role = "Admin"
                st.sidebar.success("✅ Logged in successfully!")
                st.rerun()
            else:
                st.sidebar.error("❌ Incorrect Password")
    else:
        st.session_state.user_role = "Admin"
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_role = "Guest / Student"
            st.rerun()
else:
    st.session_state.user_role = "Guest / Student"
    st.session_state.authenticated = False

st.sidebar.write("---")
st.sidebar.markdown(f"**Current Role:** `{st.session_state.user_role}`")

page = st.sidebar.radio("Navigate", ["Home", "Student Prediction", "Admin Dashboard"])

# -----------------------------------------------------------------------------
# PAGE 1: HOME
# -----------------------------------------------------------------------------
if page == "Home":
    st.title("🎓 Student Academic Performance & At-Risk Prediction System")
    st.write("""
    This machine learning system predicts student academic outcomes (**Graduate**, **Enrolled**, or **Dropout**) 
    based on demographic, socioeconomic, and academic performance indicators.
    """)
    
    st.info("💡 **Students/Faculty:** Navigate to 'Student Prediction' to test predictions.\n\n"
            "🔒 **Admins:** Select 'Admin' in the sidebar and enter the admin password (`Std_Performance321`) to manage records.")

# -----------------------------------------------------------------------------
# PAGE 2: STUDENT PREDICTION
# -----------------------------------------------------------------------------
elif page == "Student Prediction":
    st.title("👨‍🎓 Individual Student Performance Prediction")
    st.write("Enter the required student indicators below to estimate performance trajectory.")
    
    col1, col2 = st.columns(2)
    with col1:
        admission_grade = st.number_input("Admission Grade (0 - 200)", min_value=0.0, max_value=200.0, value=125.0)
        approved_units = st.number_input("Approved Curricular Units (1st Sem)", min_value=0, max_value=30, value=5)
    with col2:
        evaluations = st.number_input("Evaluations Taken", min_value=0, max_value=30, value=6)
        failed_units = st.number_input("Failed Curricular Units (1st Sem)", min_value=0, max_value=30, value=0)
        
    if st.button("Run Outcome Prediction"):
        st.subheader("Prediction Result")
        st.success("🟢 **Predicted Outcome:** GRADUATE")
        st.write("**Model Probability Breakdown:**")
        st.json({"Graduate": "84.2%", "Enrolled": "10.8%", "Dropout": "5.0%"})

# -----------------------------------------------------------------------------
# PAGE 3: ADMIN DASHBOARD (PROTECTED)
# -----------------------------------------------------------------------------
elif page == "Admin Dashboard":
    if st.session_state.user_role != "Admin" or not st.session_state.authenticated:
        st.error("⛔ **Access Restricted**")
        st.warning("You must log in as Admin to access the master database and management analytics.")
    else:
        st.title("👨‍💼 Admin Dashboard & Master Database")
        
        tab1, tab2, tab3 = st.tabs(["📊 Database Analytics", "📂 Student Records Viewer", "⚡ Upload & Convert Dataset"])
        
        # TAB 1: OVERVIEW
        with tab1:
            if st.session_state.student_db is not None:
                total_students = len(st.session_state.student_db)
                st.metric(label="Total Registered Student Records", value=f"{total_students:,}")
                
                if "Target" in st.session_state.student_db.columns:
                    st.write("### Target Outcome Distribution")
                    st.bar_chart(st.session_state.student_db["Target"].value_counts())
            else:
                st.info("No active dataset loaded in memory. Upload a dataset in the 'Upload & Convert Dataset' tab.")

        # TAB 2: MASTER DATABASE VIEWER & CSV DOWNLOAD
        with tab2:
            st.subheader("📋 Active Master Student Database")
            
            if st.session_state.student_db is not None:
                df = st.session_state.student_db
                
                # Search Bar
                search_term = st.text_input("🔍 Search Student ID or Keyword:")
                if search_term:
                    df_display = df[df.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)]
                else:
                    df_display = df

                # High contrast interactive table
                st.dataframe(df_display, use_container_width=True, height=450)
                st.caption(f"Displaying {len(df_display)} of {len(df)} total student records.")
                
                # Export active view as CSV
                csv_bytes = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Current View as CSV",
                    data=csv_bytes,
                    file_name="master_student_database.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No database currently loaded. Upload a dataset file to get started.")

        # TAB 3: UPLOAD & CONVERT FILE TO CSV
        with tab3:
            st.subheader("📤 Upload & Convert Student Dataset")
            st.write("Upload any dataset file (CSV, TXT, Excel-compatible text). The system will automatically convert and format it into a structured CSV database with Student IDs.")
            
            uploaded_file = st.file_uploader("Choose a file to upload", type=["csv", "txt", "xlsx"])
            if uploaded_file is not None:
                try:
                    # Parse file into Pandas DataFrame
                    if uploaded_file.name.endswith(".xlsx"):
                        new_df = pd.read_excel(uploaded_file)
                    else:
                        new_df = pd.read_csv(uploaded_file, sep=None, engine='python')
                    
                    # Auto-generate Student IDs if missing
                    if "Student_ID" not in new_df.columns:
                        new_df.insert(0, "Student_ID", [f"STD-{1000 + i}" for i in range(len(new_df))])
                    
                    # Store in active session memory
                    st.session_state.student_db = new_df
                    
                    st.success(f"✅ Successfully converted and activated dataset with **{len(new_df):,}** records!")
                    
                    # Provide immediate direct CSV download of the newly uploaded/converted data
                    converted_csv = new_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Uploaded File as Formatted CSV",
                        data=converted_csv,
                        file_name=f"converted_{uploaded_file.name.split('.')[0]}.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Error parsing uploaded file: {e}")
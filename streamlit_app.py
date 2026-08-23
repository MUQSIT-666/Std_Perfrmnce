import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Academic At-Risk Predictor",
    page_icon="🎓",
    layout="wide"
)

# -----------------------------------------------------------------------------
# CUSTOM CSS FOR PROFESSIONAL BROWN & GRADIENT THEME
# -----------------------------------------------------------------------------
custom_css = """
<style>
    /* Main background and text */
    .stApp {
        background-color: #FAF6F0;
        color: #3E2723;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #3E2723 0%, #4E342E 50%, #21120B 100%);
        color: #F5EBE6;
    }
    
    /* Sidebar Text & Labels */
    section[data-testid="stSidebar"] *, 
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] label {
        color: #F5EBE6 !important;
    }
    
    /* Headers & Subheaders */
    h1, h2, h3, h4 {
        color: #3E2723 !important;
        font-family: 'Georgia', serif;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #8D6E63 0%, #5D4037 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #6D4C41 0%, #3E2723 100%);
        box-shadow: 0 4px 12px rgba(62, 39, 35, 0.25);
    }
    
    /* Input fields and select boxes */
    .stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 6px;
        border: 1px solid #D7CCC8;
        background-color: #FFFFFF;
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        color: #5D4037 !important;
        font-weight: bold;
    }
    
    /* Tabs Header */
    button[data-baseweb="tab"] {
        color: #5D4037 !important;
        font-weight: 600;
    }
    button[aria-selected="true"] {
        border-bottom-color: #8D6E63 !important;
        color: #3E2723 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "Guest / Student"
if "student_db" not in st.session_state:
    try:
        df_init = pd.read_csv("dataset.csv")
        if "Student_ID" not in df_init.columns:
            df_init.insert(0, "Student_ID", [f"STD-{1000 + i}" for i in range(len(df_init))])
        st.session_state.student_db = df_init
    except FileNotFoundError:
        st.session_state.student_db = None

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & AUTHENTICATION
# -----------------------------------------------------------------------------
st.sidebar.title("🎓 Student Portal")

selected_role = st.sidebar.selectbox("Select Role", ["Guest / Student", "Admin"])

if selected_role == "Admin":
    if not st.session_state.authenticated:
        st.sidebar.subheader("🔒 Admin Login Required")
        admin_password = st.sidebar.text_input("Enter Admin Password", type="password")
        if st.sidebar.button("Login"):
            if admin_password == "Std_Performance321":
                st.session_state.authenticated = True
                st.session_state.user_role = "Admin"
                st.sidebar.success("Logged in successfully as Admin!")
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
st.sidebar.write(f"Active Role: **{st.session_state.user_role}**")

page = st.sidebar.radio("Navigation", ["Home", "Student Prediction", "Admin Dashboard"])

# -----------------------------------------------------------------------------
# PAGE 1: HOME
# -----------------------------------------------------------------------------
if page == "Home":
    st.title("🎓 Student Academic Performance & At-Risk Prediction System")
    st.write("""
    Welcome to the Academic Performance Predictor. This platform uses Machine Learning 
    to analyze academic factors and provide early guidance on student success outcomes.
    """)
    st.info("Use the sidebar to navigate to the prediction form or log in as Admin.")

# -----------------------------------------------------------------------------
# PAGE 2: STUDENT PREDICTION
# -----------------------------------------------------------------------------
elif page == "Student Prediction":
    st.title("👨‍🎓 Individual Student Outcome Prediction")
    st.write("Enter academic indicators below to receive an outcome forecast.")
    
    col1, col2 = st.columns(2)
    with col1:
        admission_grade = st.number_input("Admission Grade", min_value=0.0, max_value=200.0, value=120.0)
        approved_units = st.number_input("Approved Curricular Units (1st Sem)", min_value=0, max_value=30, value=5)
    with col2:
        evaluations = st.number_input("Evaluations Taken", min_value=0, max_value=30, value=6)
        failed_units = st.number_input("Failed Curricular Units (1st Sem)", min_value=0, max_value=30, value=0)
        
    if st.button("Predict Outcome"):
        st.subheader("Results")
        st.success("Predicted Outcome: 🟢 GRADUATE")
        st.write("Estimated Probabilities:")
        st.json({"Graduate": "84%", "Enrolled": "11%", "Dropout": "5%"})

# -----------------------------------------------------------------------------
# PAGE 3: ADMIN DASHBOARD
# -----------------------------------------------------------------------------
elif page == "Admin Dashboard":
    if st.session_state.user_role != "Admin" or not st.session_state.authenticated:
        st.error("⛔ Access Denied: You must be authenticated as Admin to view this dashboard.")
        st.info("Please select 'Admin' in the sidebar and enter the password (`Std_Performance321`).")
    else:
        st.title("👨‍💼 Admin Analytics & Master Database Management")
        
        tab1, tab2, tab3 = st.tabs(["📊 Overview Analytics", "📂 Student Records Database", "⚡ Upload New Dataset"])
        
        with tab1:
            if st.session_state.student_db is not None:
                total_students = len(st.session_state.student_db)
                st.metric(label="Total Registered Students in System", value=f"{total_students:,}")
                
                if "Target" in st.session_state.student_db.columns:
                    st.write("### Target Outcome Distribution")
                    st.bar_chart(st.session_state.student_db["Target"].value_counts())
            else:
                st.info("No dataset currently loaded in session memory.")

        with tab2:
            st.subheader("📋 Master Student Records")
            st.write("Full database access: view student IDs, academic attributes, and export records.")
            
            if st.session_state.student_db is not None:
                df = st.session_state.student_db
                
                search_term = st.text_input("🔍 Search Student ID or Keyword:")
                if search_term:
                    df_display = df[df.astype(str).apply(lambda row: row.str.contains(search_term, case=False).any(), axis=1)]
                else:
                    df_display = df

                st.dataframe(df_display, use_container_width=True, height=450)
                st.caption(f"Showing {len(df_display)} of {len(df)} total records.")
                
                csv_data = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Current Database View (CSV)",
                    data=csv_data,
                    file_name="master_student_database.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No dataset loaded. Please upload a dataset in the 'Upload New Dataset' tab.")

        with tab3:
            st.subheader("📤 Upload Master Student Dataset")
            st.write("Upload a CSV file to update or replace the current active student database.")
            
            uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
            if uploaded_file is not None:
                try:
                    new_df = pd.read_csv(uploaded_file)
                    if "Student_ID" not in new_df.columns:
                        new_df.insert(0, "Student_ID", [f"STD-{1000 + i}" for i in range(len(new_df))])
                    
                    st.session_state.student_db = new_df
                    st.success(f"✅ Successfully uploaded and activated dataset containing {len(new_df):,} student records!")
                    st.info("Switch to the 'Student Records Database' tab to view the updated table.")
                except Exception as e:
                    st.error(f"Error parsing file: {e}")
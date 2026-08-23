import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Academic At-Risk Predictor",
    page_icon="🎓",
    layout="wide"
)

# Role & Session Initialization
if "user_role" not in st.session_state:
    st.session_state.user_role = "Guest"

# Sidebar Navigation
st.sidebar.title("🎓 Student Portal")
st.sidebar.write(f"Logged in as: **{st.session_state.user_role}**")

# Role Switcher (For Development Testing)
role = st.sidebar.selectbox("Select Role Mode", ["Guest / Student", "Admin"])
st.session_state.user_role = role

page = st.sidebar.radio("Navigation", ["Home", "Student Prediction", "Admin Dashboard"])

# 1. HOME PAGE
if page == "Home":
    st.title("🎓 Student Academic Performance & At-Risk Prediction System")
    st.write("""
    Welcome to the Academic Performance Predictor. This platform uses Machine Learning 
    to analyze academic factors and provide early guidance on student success outcomes.
    """)
    st.info("Use the sidebar to navigate to the prediction form or access admin features.")

# 2. STUDENT PREDICTION PAGE
elif page == "Student Prediction":
    st.title("👨‍🎓 Individual Student Outcome Prediction")
    st.write("Enter academic indicators below to receive an outcome forecast.")
    
    col1, col2 = st.columns(2)
    with col1:
        admission_grade = st.number_input("Admission Grade", min_value=0.0, max_value=200.0, value=120.0)
        approved_units = st.number_input("Approved Curricular Units", min_value=0, max_value=30, value=5)
    with col2:
        evaluations = st.number_input("Evaluations Taken", min_value=0, max_value=30, value=6)
        failed_units = st.number_input("Failed Curricular Units", min_value=0, max_value=30, value=0)
        
    if st.button("Predict Outcome", type="primary"):
        # Placeholder logic until ML model pickle file is loaded
        st.subheader("Results")
        st.success("Predicted Outcome: 🟢 GRADUATE")
        st.write("Estimated Probabilities:")
        st.json({"Graduate": "84%", "Enrolled": "11%", "Dropout": "5%"})

# 3. ADMIN DASHBOARD PAGE
elif page == "Admin Dashboard":
    if st.session_state.user_role != "Admin":
        st.warning("⚠️ Access Restricted. Please switch to 'Admin' mode in the sidebar to view this dashboard.")
    else:
        st.title("👨‍💼 Admin Analytics & Management")
        
        tab1, tab2 = st.tabs(["Overview Analytics", "Batch CSV Prediction"])
        
        with tab1:
            st.metric(label="Total Dataset Students", value="4,424")
            st.write("Outcome Summary:")
            st.bar_chart({"Graduate": 2209, "Enrolled": 794, "Dropout": 1421})
            
        with tab2:
            st.write("Upload a CSV dataset for batch prediction:")
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            if uploaded_file is not None:
                st.success("File uploaded successfully. Ready for batch inference.")
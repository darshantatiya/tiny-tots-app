import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Tiny Tots Dashboard",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Welcome Dashboard ---
st.title("🏫 Tiny Tots Preschool Management")
st.markdown("---")

st.subheader("Welcome to your digital hub!")
st.write("Use the sidebar menu on the left to navigate through the system. Your database is securely connected to the cloud.")

# Create clean, visual info cards for the staff
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.info("#### 📝 Admissions\nRegister new students, set up their fee plans, and manage academic batches.")

with col2:
    st.success("#### 💰 Fee Desk\nCollect payments, generate smart PDF invoices, and track installments.")

with col3:
    st.warning("#### 📊 Profiles & Ledger\nSearch complete student records and view their 360° financial ledger.")

st.markdown("---")
st.caption("System Status: Online 🟢 | Database Connected")

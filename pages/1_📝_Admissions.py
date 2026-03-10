import streamlit as st
from datetime import datetime
import sys
import os

# Add the root directory to path so it can find the utils folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.database import init_connection

st.set_page_config(page_title="Admissions | Tiny Tots", page_icon="📝", layout="wide")

st.title("📝 New Student Admission")
st.markdown("Fill out the details below. Mandatory fields are marked with an asterisk (*).")

# Connect to database
try:
    settings_sheet, admissions_sheet, fees_sheet = init_connection()
except Exception as e:
    st.error("Database connection failed. Please check your utils/database.py file.")
    st.stop()

# Build the beautiful UI using Tabs
tab1, tab2, tab3 = st.tabs(["👦 Student Info", "👪 Family Details", "💰 Fee Setup & Submit"])

with st.form("admission_form"):
    
    with tab1:
        st.subheader("Student Details")
        col1, col2, col3 = st.columns(3)
        form_no = col1.text_input("Form No *")
        adm_date = col2.date_input("Admission Date")
        # For now, we will hardcode a few classes until we build the Settings page
        class_name = col3.selectbox("Class *", ["Playgroup", "Nursery", "LKG", "UKG", "Prep Batch"])
        
        col4, col5, col6 = st.columns(3)
        child_name = col4.text_input("Child's Full Name *").title()
        nickname = col5.text_input("Nickname").title()
        dob = col6.date_input("Date of Birth *", min_value=datetime(2015, 1, 1))
        
        col7, col8, col9 = st.columns(3)
        gender = col7.selectbox("Gender", ["Male", "Female", "Other"])
        nationality = col8.text_input("Nationality", value="Indian")
        pob = col9.text_input("Place of Birth")
        
        lang1 = st.text_input("First Language")
        lang2 = st.text_input("Other Languages")
        allergies = st.text_input("Allergies / Medical Conditions (Type 'None' if blank)", value="None")
        address = st.text_area("Full Residential Address *")

    with tab2:
        st.subheader("Parents & Guardians")
        col10, col11 = st.columns(2)
        
        with col10:
            st.markdown("**Father's Details**")
            f_name = st.text_input("Father's Name").title()
            f_contact = st.text_input("Father's Contact Number *", max_chars=10)
            f_email = st.text_input("Father's Email")
            f_qual = st.text_input("Father's Qualification")
            f_prof = st.text_input("Father's Profession")
            f_desig = st.text_input("Father's Designation")
            
            st.markdown("**Guardian 1 (Optional)**")
            g1_name = st.text_input("Guardian 1 Name")
            g1_contact = st.text_input("Guardian 1 Contact", max_chars=10)
            g1_rel = st.text_input("Guardian 1 Relation")
            
            st.markdown("**Emergency Contacts**")
            em1 = st.text_input("Emergency Contact 1 Name & No.")
            em2 = st.text_input("Emergency Contact 2 Name & No.")
            
        with col11:
            st.markdown("**Mother's Details**")
            m_name = st.text_input("Mother's Name").title()
            m_contact = st.text_input("Mother's Contact Number *", max_chars=10)
            m_email = st.text_input("Mother's Email")
            m_qual = st.text_input("Mother's Qualification")
            m_prof = st.text_input("Mother's Profession")
            m_desig = st.text_input("Mother's Designation")
            
            st.markdown("**Guardian 2 (Optional)**")
            g2_name = st.text_input("Guardian 2 Name")
            g2_contact = st.text_input("Guardian 2 Contact", max_chars=10)
            g2_rel = st.text_input("Guardian 2 Relation")
            
            st.markdown("**Siblings & Extra Emergency**")
            sib_name = st.text_input("Sibling Name (if any)")
            sib_details = st.text_input("Sibling School/Class")
            em3 = st.text_input("Emergency Contact 3 Name & No.")

    with tab3:
        st.subheader("Financial Setup")
        st.info("💡 Enter the fee amounts below. The system will automatically calculate the total.")
        
        col12, col13 = st.columns(2)
        ac_year = col12.selectbox("Academic Year *", ["2026-2027", "2027-2028", "2028-2029"])
        fee_plan = col13.selectbox("Fee Plan Selected *", ["Annual Single Payment", "Two Installments (+₹2000)"])
        
        col14, col15 = st.columns(2)
        base_tuition = col14.number_input("Base Tuition Fee (₹)", min_value=0, value=0, step=500)
        book_fees = col15.number_input("Books & Stationery (₹)", min_value=0, value=0, step=100)
        
        col16, col17 = st.columns(2)
        activity_fees = col16.number_input("Activity Charges (₹)", min_value=0, value=0, step=100)
        uniform_fees = col17.number_input("Uniform Fees (₹) (Type 0 if reusing old)", min_value=0, value=0, step=100)
        
        status = st.selectbox("Current Status", ["Active", "Dropped", "Promoted"])
        
        # Form Submit Button
        st.markdown("---")
        submitted = st.form_submit_button("💾 Save Admission Record", type="primary")

# --- Form Logic & Validation ---
if submitted:
    # 1. Validation Checks
    if not form_no or not child_name or not address:
        st.error("⚠️ Please fill in all mandatory fields (Form No, Child Name, Address).")
    elif len(f_contact) > 0 and (len(f_contact) != 10 or not f_contact.isdigit()):
        st.error("⚠️ Father's contact must be exactly 10 digits.")
    elif len(m_contact) > 0 and (len(m_contact) != 10 or not m_contact.isdigit()):
        st.error("⚠️ Mother's contact must be exactly 10 digits.")
    elif len(f_contact) == 0 and len(m_contact) == 0:
        st.error("⚠️ Please provide at least one parent's contact number.")
    else:
        with st.spinner("Encrypting and saving to database..."):
            
            # 2. Auto-Math: Calculate Total Payable Fees
            total_payable = base_tuition + book_fees + activity_fees + uniform_fees
            if fee_plan == "Two Installments (+₹2000)":
                total_payable += 2000
                actual_tuition_saved = base_tuition + 2000
            else:
                actual_tuition_saved = base_tuition
            
            # 3. Compile the exact 44 columns for Google Sheets
            row_data = [
                form_no, str(adm_date), class_name, child_name, nickname, str(dob), gender, nationality, pob, 
                lang1, lang2, allergies, address, f_name, f_contact, f_email, f_qual, f_prof, f_desig, 
                m_name, m_contact, m_email, m_qual, m_prof, m_desig, g1_name, g1_contact, g1_rel, 
                g2_name, g2_contact, g2_rel, sib_name, sib_details, em1, em2, em3, ac_year, fee_plan, 
                actual_tuition_saved, book_fees, activity_fees, uniform_fees, total_payable, status
            ]
            
            # 4. Push to Google Sheets
            try:
                admissions_sheet.append_row(row_data)
                st.success(f"✅ Successfully registered {child_name}! Total Fees Locked at ₹{total_payable}.")
                st.balloons()
            except Exception as e:
                st.error(f"⚠️ Error saving to database: {e}")

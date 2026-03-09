import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import gspread
from google.oauth2.service_account import Credentials
import os

# --- Google Sheets Setup (Cloud-Ready) ---
def init_connection():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # This clever block checks if we are on the cloud or on your local computer
    if "gcp_service_account" in st.secrets:
     import json
     creds_dict = json.loads(st.secrets["gcp_service_account"])
     creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    else:
        # We are on your local computer
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        
    client = gspread.authorize(creds)
    sheet = client.open("Tiny Tots Database")
    return sheet

# --- PDF Invoice Generation ---
def generate_pdf(receipt_no, name, amount, date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(200, 10, txt="TINY TOTS PRE PRIMARY SCHOOL", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt="Igatpuri", ln=True, align='C')
    pdf.cell(200, 10, txt="Fee Invoice / Official Receipt", ln=True, align='C')
    pdf.line(10, 40, 200, 40)
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, txt=f"Receipt No: {receipt_no:04d}")
    pdf.cell(90, 10, txt=f"Date: {date}", align='R', ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Student Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Amount Paid: INR {amount:,.2f}", ln=True)
    pdf.ln(30)
    pdf.line(10, 110, 200, 110)
    pdf.cell(190, 10, txt="Authorized Signatory", align='R')
    filename = f"Receipt_{receipt_no:04d}_{name.replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename

# --- Main Web Application ---
st.set_page_config(page_title="Tiny Tots Manager", page_icon="🏫", layout="wide")
st.title("🏫 Tiny Tots Preschool Management Dashboard")

# Connect to Database
try:
    db = init_connection()
    admissions_sheet = db.worksheet("Admissions")
    fees_sheet = db.worksheet("Fees")
except Exception as e:
    st.error("⚠️ Could not connect to Google Sheets. Check your credentials.")
    st.stop()

menu = ["Add New Student", "Collect Fees & Invoice", "View Database Records"]
choice = st.sidebar.selectbox("Menu Navigation", menu)

# --- 1. Add Student Screen ---
if choice == "Add New Student":
    st.header("Comprehensive Admission Form")
    
    with st.form("admission_form", clear_on_submit=True):
        
        # General Info
        col1, col2, col3 = st.columns(3)
        with col1: form_no = st.text_input("Form No.")
        with col2: admission_date = st.date_input("Date of Admission")
        with col3: admission_class = st.selectbox("Admission Seeking In", ["Playgroup", "Nursery", "Junior KG", "Senior KG"])
        
        # Creating Tabs for Organization
        tab1, tab2, tab3, tab4 = st.tabs(["👦 Child Details", "👨‍👩‍👦 Parents", "🛡️ Guardians & Emergencies", "👧 Siblings"])
        
        with tab1:
            c1, c2 = st.columns(2)
            with c1:
                full_name = st.text_input("Child's Full Name")
                dob = st.date_input("Date of Birth")
                nationality = st.text_input("Nationality", value="Indian")
                place_of_birth = st.text_input("Place of Birth")
            with c2:
                nickname = st.text_input("Nickname")
                gender = st.radio("Gender", ["Girl", "Boy"])
                first_language = st.text_input("First Language")
                other_languages = st.text_input("Other Languages Known")
            allergies = st.text_area("Allergies / Medical Conditions (Specify 'No' if none)")
            address = st.text_area("Full Residential Address")
            
        with tab2:
            c3, c4 = st.columns(2)
            with c3:
                st.markdown("**Father's Details**")
                father_name = st.text_input("Father's Name")
                father_contact = st.text_input("Father Contact No.")
                father_email = st.text_input("Father E-mail")
                father_qual = st.text_input("Father Qualification")
                father_prof = st.text_input("Father Profession")
                father_desig = st.text_input("Father Designation")
            with c4:
                st.markdown("**Mother's Details**")
                mother_name = st.text_input("Mother's Name")
                mother_contact = st.text_input("Mother Contact No.")
                mother_email = st.text_input("Mother E-mail")
                mother_qual = st.text_input("Mother Qualification")
                mother_prof = st.text_input("Mother Profession")
                mother_desig = st.text_input("Mother Designation")

        with tab3:
            st.markdown("**Guardians (Optional)**")
            c5, c6 = st.columns(2)
            with c5:
                g1_name = st.text_input("1st Guardian Name")
                g1_contact = st.text_input("1st Guardian Contact No.")
                g1_relation = st.text_input("1st Guardian Relation")
            with c6:
                g2_name = st.text_input("2nd Guardian Name")
                g2_contact = st.text_input("2nd Guardian Contact No.")
                g2_relation = st.text_input("2nd Guardian Relation")
            
            st.markdown("---")
            st.markdown("**Emergency Contacts (Order of Priority)**")
            e1 = st.text_input("1st Priority (Relation & Contact No)")
            e2 = st.text_input("2nd Priority (Relation & Contact No)")
            e3 = st.text_input("3rd Priority (Relation & Contact No)")
            
        with tab4:
            st.markdown("**Sibling Information (Optional)**")
            sibling_name = st.text_input("Sibling Name")
            sibling_details = st.text_input("Sibling School & Class")
            
        st.markdown("---")
        submit = st.form_submit_button("💾 Save Full Admission Record")
        
        if submit and full_name:
            # This order perfectly matches the 36 columns you created in Google Sheets
            new_row = [
                form_no, str(admission_date), admission_class, full_name, nickname, 
                str(dob), gender, nationality, place_of_birth, first_language, other_languages, 
                allergies, address, father_name, father_contact, father_email, father_qual, 
                father_prof, father_desig, mother_name, mother_contact, mother_email, mother_qual, 
                mother_prof, mother_desig, g1_name, g1_contact, g1_relation, g2_name, g2_contact, 
                g2_relation, sibling_name, sibling_details, e1, e2, e3
            ]
            admissions_sheet.append_row(new_row)
            st.success(f"✅ Successfully saved comprehensive record for {full_name}!")

# --- 2. Fee Collection Screen ---
elif choice == "Collect Fees & Invoice":
    st.header("Record Payment & Generate Invoice")
    records = admissions_sheet.get_all_records()
    df_students = pd.DataFrame(records)
    
    if df_students.empty or 'Child Full Name' not in df_students.columns:
        st.warning("⚠️ No students found. Please add an admission first.")
    else:
        student_list = df_students['Child Full Name'] + " (" + df_students['Class'] + ")"
        selected_student = st.selectbox("Select Student", options=student_list)
        amount = st.number_input("Fee Amount Received (INR)", min_value=100.0, step=100.0)
        
        if st.button("Process Payment & Generate PDF"):
            date_today = datetime.now().strftime("%Y-%m-%d")
            total_fee_rows = len(fees_sheet.get_all_values())
            receipt_no = total_fee_rows
            student_name_only = selected_student.split(" (")[0]
            
            fees_sheet.append_row([receipt_no, student_name_only, amount, date_today])
            pdf_file = generate_pdf(receipt_no, student_name_only, amount, date_today)
            
            st.success("✅ Payment Recorded Successfully in Google Sheets!")
            with open(pdf_file, "rb") as file:
                st.download_button(label="📄 Download PDF Invoice", data=file, file_name=pdf_file, mime="application/pdf")

# --- 3. View Records Screen ---
elif choice == "View Database Records":
    st.header("Database Overview")
    st.subheader("Enrolled Students")
    student_records = admissions_sheet.get_all_records()
    if student_records:
        df_students = pd.DataFrame(student_records)
        cols_to_show = ['Form No', 'Child Full Name', 'Class', 'Father Contact']
        existing_cols = [col for col in cols_to_show if col in df_students.columns]
        st.dataframe(df_students[existing_cols] if existing_cols else df_students, use_container_width=True, hide_index=True)
    else:
        st.info("No students enrolled yet.")
    
    st.subheader("Fee Collection History")
    fee_records = fees_sheet.get_all_records()
    if fee_records:
        st.dataframe(pd.DataFrame(fee_records), use_container_width=True, hide_index=True)
    else:
        st.info("No fees collected yet.")

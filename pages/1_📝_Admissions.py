import streamlit as st
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.database import init_connection

st.set_page_config(page_title="Admissions | Tiny Tots", page_icon="📝", layout="wide")

st.title("📝 New Student Admission")
st.markdown("Fill out the details below. Mandatory fields are marked with an asterisk (*).")

try:
    settings_sheet, admissions_sheet, fees_sheet = init_connection()
except Exception as e:
    st.error("Database connection failed. Please check your utils/database.py file.")
    st.stop()

# --- AUTO-GENERATE UNIQUE ID LOGIC ---
existing_forms = admissions_sheet.col_values(1)[1:]

valid_numbers = [int(num) for num in existing_forms if num.isdigit()]
if valid_numbers:
    next_form_no = str(max(valid_numbers) + 1)
else:
    next_form_no = "101"

with st.form("admission_form"):
    
    tab1, tab2, tab3 = st.tabs(["1️⃣ Student Info", "2️⃣ Family Details", "3️⃣ Fee Setup & Submit"])
    
    with tab1:
        st.subheader("Student Details")
        
        col1, col2, col3 = st.columns(3)
        form_no = col1.text_input("Form No (Auto-Generated) 🔒", value=next_form_no, disabled=True)
        adm_date = col2.date_input("Admission Date")
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

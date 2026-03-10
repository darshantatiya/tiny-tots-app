import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add the root directory to path so it can find the utils folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.database import init_connection

st.set_page_config(page_title="Fee Desk | Tiny Tots", page_icon="💰", layout="wide")

st.title("💰 Smart Fee Desk")
st.markdown("Select a student to view their current balance and collect payments.")

# Connect to database
try:
    settings_sheet, admissions_sheet, fees_sheet = init_connection()
except Exception as e:
    st.error("Database connection failed. Please check your utils/database.py file.")
    st.stop()

# Fetch all data and convert to Pandas DataFrames for easy math
adm_values = admissions_sheet.get_all_values()
fees_values = fees_sheet.get_all_values()

# Check if we have any students admitted yet
if len(adm_values) <= 1:
    st.info("ℹ️ No students found in the database. Please admit a student first.")
    st.stop()

# Convert to DataFrames
df_adm = pd.DataFrame(adm_values[1:], columns=adm_values[0])
df_fees = pd.DataFrame(fees_values[1:], columns=fees_values[0]) if len(fees_values) > 1 else pd.DataFrame(columns=fees_values[0])

# 1. Search & Select Student
st.subheader("🔍 Find Student")
# Create a searchable list: "FormNo - StudentName"
student_list = df_adm['Form No'].astype(str) + " - " + df_adm['Child Full Name']
selected_student = st.selectbox("Search by Form No or Name", options=["Select a Student..."] + list(student_list))

if selected_student != "Select a Student...":
    # Extract just the Form No from the selection
    target_form_no = selected_student.split(" - ")[0]
    
    # Get the specific student's data
    student_data = df_adm[df_adm['Form No'] == target_form_no].iloc[0]
    student_name = student_data['Child Full Name']
    academic_year = student_data['Academic Year']
    fee_plan = student_data['Fee Plan Selected']
    
    # Do the Math: Total Payable vs Total Paid
    try:
        total_payable = float(student_data['Total Payable Fees'])
    except:
        total_payable = 0.0
        
    # Calculate how much they have already paid from the Fees sheet
    if not df_fees.empty:
        # Filter fees for this specific student
        student_payments = df_fees[df_fees['Form No'] == target_form_no]
        # Convert the 'Amount Paid' column to numbers and sum it up
        total_paid_so_far = pd.to_numeric(student_payments['Amount Paid'], errors='coerce').sum()
    else:
        total_paid_so_far = 0.0
        
    pending_balance = total_payable - total_paid_so_far
    
    # 2. Financial Dashboard UI
    st.markdown("---")
    st.subheader(f"Financial Overview: {student_name}")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Fee Plan", fee_plan)
    col2.metric("Total Payable", f"₹{total_payable:,.2f}")
    col3.metric("Total Paid So Far", f"₹{total_paid_so_far:,.2f}")
    
    # Highlight pending balance in red if they owe money, green if fully paid
    if pending_balance > 0:
        col4.metric("Pending Balance", f"₹{pending_balance:,.2f}", delta="-Owes Money", delta_color="inverse")
    else:
        col4.metric("Pending Balance", f"₹{pending_balance:,.2f}", delta="Fully Paid", delta_color="normal")

    st.markdown("---")
    
    # 3. Collect New Payment Form
    if pending_balance > 0:
        st.subheader("💵 Collect New Payment")
        with st.form("payment_form"):
            pay_col1, pay_col2, pay_col3 = st.columns(3)
            
            # Auto-generate a Receipt Number based on the current date and time
            new_receipt_no = datetime.now().strftime("REC-%Y%m%d-%H%M%S")
            payment_date = datetime.now().strftime("%Y-%m-%d")
            
            pay_col1.text_input("Receipt No (Auto-Generated)", value=new_receipt_no, disabled=True)
            amount_to_pay = pay_col2.number_input("Amount Paying Today (₹)", min_value=1.0, max_value=float(pending_balance), step=100.0)
            payment_mode = pay_col3.selectbox("Payment Mode", ["Cash", "UPI", "Bank Transfer", "Cheque"])
            
            fee_type = st.selectbox("Fee Type Paid", ["Term 1 Installment", "Term 2 Installment", "Full Annual Payment", "Partial Payment"])
            remarks = st.text_input("Remarks (Optional)")
            
            submit_payment = st.form_submit_button("💳 Process Payment & Save", type="primary")
            
            if submit_payment:
                with st.spinner("Recording payment..."):
                    # Prepare the row for the Fees Google Sheet
                    new_fee_record = [
                        new_receipt_no, payment_date, academic_year, target_form_no, 
                        student_name, amount_to_pay, payment_mode, fee_type, remarks
                    ]
                    
                    try:
                        fees_sheet.append_row(new_fee_record)
                        st.success(f"✅ Payment of ₹{amount_to_pay} successfully recorded for {student_name}!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"⚠️ Could not save payment: {e}")
    else:
        st.success("🎉 This student has fully paid their fees for the academic year!")

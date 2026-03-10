import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json

@st.cache_resource
def init_connection():
    # The permissions Google needs
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        # Load the secure digital key we hid in Streamlit Cloud
        creds_dict = json.loads(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Open your master database
        db = client.open("Tiny Tots Database")
        
        # Grab the exact 3 tabs you just created
        settings_sheet = db.worksheet("Settings")
        admissions_sheet = db.worksheet("Admissions")
        fees_sheet = db.worksheet("Fees")
        
        return settings_sheet, admissions_sheet, fees_sheet
        
    except Exception as e:
        st.error(f"⚠️ Could not connect to the database. Error: {e}")
        st.stop()

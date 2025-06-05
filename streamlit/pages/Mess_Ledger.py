import streamlit as st
import pandas as pd
from functions import *
from datetime import datetime
st.set_page_config(layout="wide")

st.subheader("Mess Ledger Management")   

col1, col2 = st.columns(2)

with col1:
    with st.form("mess_entry_form"):
        mess_type = st.selectbox(
            "Charge Type",
            options=["Normal", "Daily Messing", "Extra Messing"],
            key="mess_type"
        )
        
        mess_desc = st.text_input(
            "Description",
            max_chars=100,
            key="mess_desc"
        )
        
        mess_remarks = st.text_input(
            "Remarks",
            max_chars=200,
            key="mess_remarks"
        )
        
        mess_amt = st.number_input(
            "Amount (₹)",
            min_value=0.01,
            value=0.01,
            step=0.01,
            key="mess_amt",
            format="%.2f"
        )
        
        officer_uid = None
        if mess_type != "Normal":
            officers = get_name_uid_mess_member()
            if officers:
                officer_options = [f"{uid}: {name}" for uid, name in officers]
                selected_officer = st.selectbox(
                    "Officer Associated",
                    options=officer_options,
                    key="mess_officer"
                )
                officer_uid = selected_officer.split(":")[0].strip()
            else:
                st.warning("No mess members found")
        
        charge_date = st.date_input(
            "Date",
            value=datetime.now(),
            key="mess_date"
        )
        
        if st.form_submit_button("Add Entry"):
            try:
                result = add_mess_entry(
                    charge_type=mess_type,
                    description=mess_desc,
                    remarks=mess_remarks,
                    amount=mess_amt,
                    officer=officer_uid,
                    date=charge_date
                )
                st.success(result)
                st.rerun()  # Updated to current Streamlit API
            except Exception as e:
                st.error(f"Error adding entry: {str(e)}")
with col2:
    try:
        entries = get_mess_entry()
        if entries:
            # Create DataFrame from the results
            df = pd.DataFrame(entries)
            
            # Format amount column properly
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            df['Amount'] = df['Amount'].apply(lambda x: f"₹{x:,.2f}" if pd.notnull(x) else "₹0.00")
            
            # Display only relevant columns
            st.dataframe(
                df[['Charge Type', 'Description', 'Amount']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No entries found in the mess ledger")
    except Exception as e:
        st.error(f"Error loading entries: {str(e)}")
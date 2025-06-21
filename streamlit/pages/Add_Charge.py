import streamlit as st
import pandas as pd
from create_db import set_database
from functions import *
st.set_page_config(layout="wide")

st.subheader("Add New Charge")   

col1, col2 = st.columns(2)  




with col1:
    officers_split = []
    officer_uid=""
    charge_type = st.selectbox(label="",options=["Split","Individual"])
    if charge_type != "Split":    
        uid_options = [f"{uid}: {name}" for uid, name in get_name_uid()]
        officer_uid = st.selectbox("Officer UID", options=uid_options)
    charge_desc = st.text_input(label="Charge Description")
    
    if charge_type == "Split":
        officers_split = get_current_split()
        print(officers_split)
        if not officers_split:
            st.text("Add Officers to split")
        else:
            colp, colq, colr = st.columns(3)
            with colq:
                st.text("Current Split")       
            st.dataframe(pd.DataFrame(officers_split, columns=["UID", "Name", "Share"]), use_container_width=True)

        cola, colb  = st.columns(2)
        with cola:
            officer_split_option = st.selectbox(label="Officer", options=get_name_uid())
            officer_split_id = officer_split_option[0]  # Extract UID

        with colb:
            officer_split_amt = st.number_input("Share", min_value=0.0, step=10.0)
        colaa,colbb,colcc = st.columns(3)
        with colaa:
            with st.form("Add Officer to Split"):
              submitted = st.form_submit_button("Add Officer")
              if submitted:
               st.success(addto_current_split(officer_split_id, officer_split_amt))
               st.rerun()

        with colbb:
            if st.button(label="Clear Split"):
                st.text(empty_current_split())
                st.rerun()
           
    
            
    charge_amt = st.number_input("Total Amount", min_value=0.0, step=10.0)
    charge_date = st.date_input(label="Date")
    charge_remarks = st.text_input(label="Remarks")
    col_a, col_b, col_c = st.columns(3)
    with col_b:
      if st.button("Add Charge"):
        if not charge_desc:
           st.warning("Please enter a charge description.")
        elif charge_type == "Individual" and not officer_uid:
           st.warning("Please select an officer.")
        elif charge_amt <= 0:
           st.warning("Amount must be greater than zero.")
        elif charge_type == "Split" and not officers_split:
           st.warning("Split charge must have at least one officer.")
        else:
         result = add_charge(
            charge_type=charge_type,
            uid=officer_uid.split(":")[0].strip() if charge_type == "Individual" else "",
            description=charge_desc,
            amount=charge_amt,
            charge_date=charge_date,
            officers_split=officers_split if charge_type == "Split" else None
        )
        if result.lower().startswith("error") or "must" in result.lower():
         st.error(result)
        else:
          st.success(result)
        st.rerun()

        

with col2:
    charge_list = get_charges()
    st.dataframe(pd.DataFrame(charge_list,columns=["UID","Description", "Amount","Date"]),use_container_width=True)
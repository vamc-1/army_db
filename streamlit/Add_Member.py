import streamlit as st
import pandas as pd
from create_db import set_database
from functions import *  # Make sure get_name_rank exists in functions.py

# Configure page
st.set_page_config(layout="wide")
set_database()

# Constants
RANK_OPTIONS = ["Rank 1", "Rank 2", "Rank 3", "Rank 4"]

def validate_member_input(name, uid, is_guest):
    """Validate member input fields"""
    if not name:
        return "Name is required"
    if not is_guest and not uid:
        return "UID is required for non-guests"
    return None

def display_member_form():
    """Display the member addition form"""
    st.subheader("Add New Member")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Form inputs
        guest = st.toggle('Guest')
        name = st.text_input("Name")
        
        if not guest:
            uid = st.text_input("UID")
            rank = st.selectbox("Rank", options=RANK_OPTIONS)
            unit = st.text_input("Unit")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                married = st.checkbox("Married")
            with col_b:
                accomodation = st.checkbox("Accomodation")
            with col_c:
                mess_member = st.checkbox("Mess Member")
        else:
            uid = rank = unit = ""
            married = accomodation = mess_member = False
        
        # Submit button
        if st.button("Add Member"):
            error = validate_member_input(name, uid, guest)
            if error:
                st.error(error)
            else:
                result = add_officer(
                    uid=uid,
                    officer_name=name,
                    officer_rank=rank,
                    officer_unit=unit,
                    married=married,
                    accomodation=accomodation,
                    mess_member=mess_member,
                    guest=guest
                )
                st.success(result)
                st.rerun()
    
    with col2:
        # Display existing members (with error handling)
        try:
            # First try get_name_rank
            members = get_name_rank() if 'get_name_rank' in globals() else []
            
            # Fallback to alternative if needed
            if not members:
                all_officers = get_all_officer_data()
                if all_officers:
                    members = [[o['NAME'], o['OFFICER_RANK']] for o in all_officers]
            
            if members:
                st.dataframe(
                    pd.DataFrame(members, columns=["Name", "Rank"]),
                    use_container_width=True,
                    height=400
                )
            else:
                st.info("No members found in the database")
        except Exception as e:
            st.error(f"Error loading members: {str(e)}")

def main():
    display_member_form()

if __name__ == "__main__":
    main()
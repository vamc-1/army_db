import streamlit as st
from functions import get_name_uid
from pdf import generate_bill
from datetime import datetime
from calendar import month_abbr
import os

st.set_page_config(layout="wide")
st.subheader("Billing")   

col1, col2 = st.columns(2)

with col1:
    # Officer selection
    officers = get_name_uid()  # This should return list of [uid, name] pairs
    officer_index = st.selectbox(
        "Officer",
        range(len(officers)),
        format_func=lambda x: f"{officers[x][0]}: {officers[x][1]}"
    )
    selected_officer = officers[officer_index]
    
    # Month/Year selection
    with st.expander('Billing Month'):
        this_year = datetime.now().year
        this_month = datetime.now().month
        report_year = st.selectbox(
            "Year",
            range(this_year, this_year - 5, -1),
            index=0,
            key="year_select"
        )
        month_names = month_abbr[1:]
        report_month_str = st.radio(
            "Month",
            month_names,
            index=this_month - 1,
            horizontal=True,
            key="month_select"
        )
    
    arrears = st.number_input("Arrears", min_value=0.0, value=0.0, step=100.0)
    
    if st.button("Generate Bill"):
        try:
            # Generate the bill and get the result
            result = generate_bill(selected_officer, arrears, report_month_str, report_year)
            
            # Show success message
            st.success(result[0])
            
            # Read the generated PDF
            with open(result[1], "rb") as pdf_file:
                PDFbyte = pdf_file.read()
            
            # Create download button
            st.download_button(
                label="Export Bill",
                data=PDFbyte,
                file_name=os.path.basename(result[1]),
                mime='application/pdf'
            )
            
            # Clean up the temporary file
            os.remove(result[1])
            
        except Exception as e:
            st.error(f"Error generating bill: {str(e)}")
            if 'result' in locals() and os.path.exists(result[1]):
                os.remove(result[1])
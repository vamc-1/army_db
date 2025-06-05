from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from functions import *
import random
import os
from functions import get_total_bill
from datetime import datetime
from reportlab.lib.units import inch

def generate_bill(officer, arrears, month, year):
    """
    Generate a PDF bill for an officer
    Args:
        officer: Either a string in "UID: Name" format or a list [uid, name]
        arrears: Arrears information
        month: Month as string (e.g., "Jan")
        year: Year as string (e.g., "2023")
    Returns:
        List: [message, pdf_filename]
    """
    # Handle both string and list inputs for officer
    if isinstance(officer, list):
        if len(officer) >= 2:
            uid = str(officer[0])
            name = str(officer[1])
        else:
            raise ValueError("Officer list must contain at least [uid, name]")
    else:
        try:
            # Handle string input "UID: Name"
            parts = officer.split(':')
            if len(parts) < 2:
                raise ValueError("Officer string must be in 'UID: Name' format")
            uid = parts[0].strip()
            name = parts[1].strip()
        except AttributeError:
            raise TypeError("Officer must be string 'UID: Name' or list [uid, name]")

    # Process name for filename
    name_tmp = name.replace(" ", "_")
    
    # PDF setup
    pdf_filename = os.path.join(os.getcwd(), f'mess_bill_{name_tmp}.pdf')
    pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)

    # Current date
    current_date = datetime.now()
    current_month = str(current_date.month)
    current_year = str(current_date.year)
    formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S")

    # Month mappings
    month_dict_inv = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }
    
    month_dict = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    # Table 1: Header information
    data1 = [
        ["", "", "OFFICERS MESS : 621 EME BN", ""],
        ["Name: ", name, "Bill Month: ", f"{month} {current_year}", "Bill Date:", formatted_date],
        ["Unit: ", get_unit(uid), "Bill no.:", random.randint(100, 1000)],
        [],
        [],
    ]

    table_style1 = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ])

    table1 = Table(data1, style=table_style1)

    # Table 2: Bill items
    month_num = month_dict_inv[month]
    total_bill = get_total_bill(uid, arrears, month_num, year)
    
    data2 = [["Sr", "Description", "Amount", "Remarks"]]
    data2.extend(total_bill)
    data2.extend([[], []])

    table_style2 = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 18),
    ])

    table2 = Table(data2, style=table_style2)

    # Table 3: Payment information
    data3 = [
        ["Payment be made through POS machine/ Bank Acct / QR Code :-"],
        ["A/c Name - OFFRS MESS ACCT 621 EME BN"],
        ["A/c No - 34328506911"],
        ["IFSC: SBIN0016944"],
        ["Branch - SBI, CHANGSARI"],
    ]

    table3 = Table(data3)
    
    # QR Code function
    def add_qr_code(canvas, doc):
        image_path = os.path.join(os.getcwd(), 'qr_image.png')
        if os.path.exists(image_path):
            canvas.drawImage(image_path, 
                           letter[0] - 2.5*inch, 0.5*inch,
                           width=2*inch, height=2*inch)

    # Build PDF
    elements = [table1, table2, table3]
    pdf.build(elements, onFirstPage=add_qr_code, onLaterPages=add_qr_code)

    return [f"PDF generated at: {pdf_filename}", f'mess_bill_{name_tmp}.pdf']
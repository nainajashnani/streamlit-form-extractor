import streamlit as st 
import pytesseract
import pandas as pd
import re
from pdf2image import convert_from_bytes
from PIL import Image

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.title("📄 Form Extractor App")
st.write("Upload multiple PDFs to extract Form Name, Form Number, and Edition Date.")

# File uploader
uploaded_files = st.file_uploader("Upload PDF Files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    results = []
    
    for uploaded_file in uploaded_files:
        st.write(f"📂 Processing: {uploaded_file.name}")

        # Convert only the first page to an image
        images = convert_from_bytes(uploaded_file.getvalue(), dpi=300, first_page=1, last_page=1)
        image = images[0]

        # Extract text using Tesseract
        extracted_text = pytesseract.image_to_string(image)

        # Debugging: Display extracted text
        st.text_area(f"Extracted Text from {uploaded_file.name}", extracted_text, height=150)

        # Split text into sections for better accuracy
        lines = extracted_text.split("\n")
        first_half = "\n".join(lines[:len(lines)//2])  # Top/Middle of the page
        last_half = "\n".join(lines[len(lines)//2:])   # Bottom of the page

        # Extract Form Name (Find the first uppercase block of text)
        form_name_match = re.search(r"\n([A-Z][A-Z\s\-]+)\n", first_half, re.DOTALL)
        form_name = form_name_match.group(1).strip() if form_name_match else "Not Found"
   
        # Extract Form Number (Look in the last few lines)
        form_number_match = re.search(r"\b([A-Z]+\s?\d{4,6}[A-Z]*)\b", last_half)
        form_number = form_number_match.group(1) if form_number_match else "Not Found"

        # Extract Edition Date (Look in the last few lines)
        edition_date_match = re.search(r"\b(\d{2}[\/\-]\d{2,4}|\d{2} \d{2,4})\b", last_half)
        edition_date = edition_date_match.group(1) if edition_date_match else "Not Found"

        # Store extracted data
        results.append({
            "File Name": uploaded_file.name,
            "Form Name": form_name,
            "Form Number": form_number,
            "Edition Date": edition_date
        })

    # Convert results to DataFrame and display
    df = pd.DataFrame(results)
    st.dataframe(df)

    # Download results as CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Extracted Data", csv, "extracted_forms.csv", "text/csv")

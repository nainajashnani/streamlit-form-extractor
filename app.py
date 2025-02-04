import streamlit as st
import os
import re
import pytesseract
import pandas as pd
from pdf2image import convert_from_path
from PIL import Image

st.title("📄 Form Extractor App")
st.write("Upload PDFs to extract Form Name, Form Number, and Edition Date.")

# File uploader
uploaded_files = st.file_uploader("Upload PDF Files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    results = []

    for uploaded_file in uploaded_files:
        st.write(f"Processing: {uploaded_file.name}")

        # Save uploaded file
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Convert PDF to images
        images = convert_from_path(uploaded_file.name, dpi=300)

        for i, image in enumerate(images):
            extracted_text = pytesseract.image_to_string(image)

            # Extract Form Name
            form_name_match = re.search(r"PEST CONTROL PROPERTY DAMAGE BROADENING\s*COVERAGE FOR TREATMENT RENEWAL", extracted_text, re.DOTALL)
            form_name = form_name_match.group(0).strip() if form_name_match else "Not Found"

            # Extract Form Number (e.g., PCPGL 0009)
            form_number_match = re.search(r"([A-Z]+ \d{4})", extracted_text)
            form_number = form_number_match.group(1) if form_number_match else "Not Found"

            # Extract Edition Date (e.g., 06 24)
            edition_date_match = re.search(r"(\d{2} \d{2})", extracted_text)
            edition_date = edition_date_match.group(1) if edition_date_match else "Not Found"

            # Store results
            results.append({
                "File Name": uploaded_file.name,
                "Page": i + 1,
                "Form Name": form_name,
                "Form Number": form_number,
                "Edition Date": edition_date
            })

    # Convert results to DataFrame
    df = pd.DataFrame(results)
    st.dataframe(df)

    # Download CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Results", csv, "extracted_forms.csv", "text/csv")

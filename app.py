import streamlit as st
from dotenv import load_dotenv
from utils import *
import io


def main():
    load_dotenv()

    st.set_page_config(page_title="Academic Paper Analysis Tool")
    st.title("Academic Paper Analysis Tool 💼")
    st.subheader("Assisting you in analyzing academic papers")

    # Upload the academic papers (pdf files)
    pdf = st.file_uploader(
        "Upload academic papers here, only PDF files allowed",
        type=["pdf"],
        accept_multiple_files=True,
    )

    submit = st.button("Analyze Papers")
    if submit:
        with st.spinner("Analyzing..."):
            df = create_paper_review_df(pdf)
            st.write(df.head())

            # Convert DataFrame to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Sheet1")
                # No need to call writer.save()

            data_as_excel = output.getvalue()

            # Download button for Excel
            st.download_button(
                label="Download analysis as Excel",
                data=data_as_excel,
                file_name="academic-papers-analysis.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download-analysis-excel",
            )
        st.success("Your academic paper analysis is ready!")


# Invoking main function
if __name__ == "__main__":
    main()

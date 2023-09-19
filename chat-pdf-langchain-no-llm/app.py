from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import PyPDFLoader
from langchain import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os
import tempfile

# api_key=os.environ["OPENAI_API_KEY"]  

def summarize_pdfs_from_folder(pdfs_folder):
    summaries = []
    for pdf_file in pdfs_folder:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(pdf_file.read())
        
        loader = PyPDFLoader(temp_path)
        docs = loader.load_and_split()
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        summary = chain.run(docs)
        summaries.append(summary)

        # Delete the temporary file
        os.remove(temp_path)
    
    return summaries


if __name__ == "__main__":
    # Load OpenAI API key
    load_dotenv()
    api_key=os.environ.get("openai_api_key")
    # print(api_key)
    llm = OpenAI(temperature=0)


    # Streamlit App
    st.title("Multiple PDF Summarizer")

    # Allow user to upload PDF files
    pdf_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    if pdf_files:
        # Generate summaries when the "Generate Summary" button is clicked
        if st.button("Generate Summary"):
            st.write("Summaries:")
            summaries = summarize_pdfs_from_folder(pdf_files)
            for i, summary in enumerate(summaries):
                st.write(f"Summary for PDF {i+1}:")
                st.write(summary)

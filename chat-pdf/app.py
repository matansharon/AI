import os
import streamlit as st
from functions import *
import openai
import dotenv
dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    st.title("Chat PDF")
    uploadfile=st.file_uploader("Upload a PDF file", type=["pdf",'txt'])
    if uploadfile is not None:
        save_uploaded(uploadfile)
        st.write("Please wait while we process your file...")
        



if __name__ == "__main__":
    main()
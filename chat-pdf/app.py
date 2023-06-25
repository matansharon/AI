import os
import streamlit as st
from functions import *
import openai
import dotenv
dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def main():
    st.title("Chat PDF")



if __name__ == "__main__":
    main()
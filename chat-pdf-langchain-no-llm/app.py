import streamlit as st
import os
import openai
import pickle
import langchain
from dotenv import load_dotenv


def main():
    st.header("Chat with PDF 💬")
    st.sidebar.title('🤗💬 LLM Chat App')
    st.sidebar.markdown('''
    ## About
    This app is an LLM-powered chatbot built using:
    - [Streamlit](https://streamlit.io/)
    - [LangChain](https://python.langchain.com/)
    - [OpenAI](https://platform.openai.com/docs/models) LLM model
    
        ''')



if __name__ == '__main__':
    main()
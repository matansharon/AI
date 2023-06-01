import streamlit as st
import openai
import os
from dotenv import load_dotenv


def get_response(message):
    load_dotenv()
    openai.api_key = os.getenv("openai_key")
    # os.environ['openai_key']
    # key = os.getenv("openai_key")
    response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        temperature = 1,
        messages = [
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0]["message"]["content"]

def main():
    #create a header that will as for a question. and a button to submit the question
    st.title("Ask a question")
    question = st.text_input("What is your question?")
    submit = st.button("Submit")

    #when the button is clicked, the question will be sent to the model and the answer will be returned
    if submit:
        st.write("The answer to your question is: ")
        q=get_response(question)
        st.write(q)
        
        #get an answer from openai api gpt3 and display it
        
if __name__ == "__main__":
    main()
    # print('hello')
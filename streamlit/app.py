import streamlit as st
import openai
import os
from dotenv import load_dotenv


import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")




def get_query(question):
    load_dotenv()
    key = os.getenv("openai_key")
    openai.api_key = key
    response = openai.Completion.create(
  model="text-davinci-003",
  prompt=question,
  temperature=0,
  max_tokens=100,
  top_p=1,
  frequency_penalty=0.0,
  presence_penalty=0.0,
  stop=["\n", "Q:"]
)
    return response.choices[0].text
    
#create a header that will as for a question. and a button to submit the question
st.title("Ask a question")
question = st.text_input("What is your question?")
submit = st.button("Submit")

#when the button is clicked, the question will be sent to the model and the answer will be returned
if submit:
    st.write("The answer to your question is: ")
    q=get_query(question)
    st.write(q)
    print(q)
    #get an answer from openai api gpt3 and display it
    
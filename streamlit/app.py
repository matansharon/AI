import streamlit as st
import openai
import os
import base64
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
client = OpenAI()
def get_response(question):
    """
    This function takes a question as input and returns the answer from the OpenAI API.
    """
    # Set up the OpenAI API client
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Call the OpenAI API to get the answer
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. you job is to improve the user given text grammatically and semantically. you will be given a text and you will improve it. you will not add any new information to the text. you will not change the meaning of the text. you will not add any new information to the text. you will not change the meaning of the text. you will not add any new information to the text. you will not change the meaning of the text."
            },
            {
                "role": "user",
                "content": question
            }
            
        ]
    )
    
    # Extract and return the answer from the response
    return response.choices[0].message.content
def get_audio_response(question):
    """
    This function takes a question as input and returns the answer from the OpenAI API.
    """
    # Set up the OpenAI API client

    
    # Call the OpenAI API to get the answer
    completion = client.chat.completions.create(
        model="gpt-4o-audio-preview",
        modalities=["text", "audio"],
        audio={"voice": "alloy", "format": "wav"},
        messages=[
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return completion.choices[0].message.audio.data

def main():
    #create a header that will as for a question. and a button to submit the question
    st.title("Add some text to convert to audio")
    question = st.chat_input("What is your question?")
    

    #when the button is clicked, the question will be sent to the model and the answer will be returned
    if question:
        
        q=get_response(question)
        st.write(q)
        audio=base64.b64decode(get_audio_response(q))
        st.audio(audio)
        
        
if __name__ == "__main__":
    main()
    
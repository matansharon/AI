import streamlit as st
st.write("Hello world!")
#create an input line and show the input
user_input = st.text_input("Please enter your name")
st.write(user_input)
#show the input in a header
st.header(user_input)
#show the input in a markdown
st.markdown(user_input)
#show the input in a code block
st.code(user_input)
#show the input in a json
st.json(user_input)
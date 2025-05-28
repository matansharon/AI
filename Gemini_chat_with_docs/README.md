# Chat with Documents - Gemini AI

A Streamlit web application that lets you upload documents and have intelligent conversations about their content using Google Gemini AI.

## Features

- **Document Upload**: Support for PDF, TXT, DOCX, and MD files
- **Smart DOCX Processing**: Automatically extracts text from DOCX files (including tables)
- **Intelligent Chat**: Ask questions about your uploaded documents
- **Context Awareness**: AI maintains context of all uploaded documents throughout the conversation
- **Multiple Documents**: Upload and discuss multiple documents simultaneously
- **Conversation History**: Keep track of your chat history

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

3. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

4. Your API key will be auto-loaded from the `.env` file!

## Usage

1. **Upload Documents**: Use the sidebar to upload PDF, TXT, DOCX, or MD files
2. **Start Chat**: Click "Start Chat with Documents" to process your files
3. **Ask Questions**: Use the chat interface to ask questions about your documents
4. **View History**: See your conversation history and document context

## Example Questions

- "What are the main topics discussed in these documents?"
- "Can you summarize the key points?"
- "What conclusions can you draw from this content?"
- "Are there any important dates or numbers mentioned?"
- "Compare the different viewpoints presented in these documents"
# Chat with Documents - Claude AI

A Streamlit web application that lets you upload documents and have intelligent conversations about their content using Anthropic's Claude AI.

## Features

- **Document Upload**: Support for PDF, TXT, DOCX, and MD files
- **Native PDF Processing**: Claude natively processes PDFs including images, charts, and tables
- **Smart DOCX Processing**: Automatically extracts text from DOCX files (including tables)
- **Intelligent Chat**: Ask questions about your uploaded documents with streaming responses
- **Context Awareness**: Claude maintains context of all uploaded documents throughout the conversation
- **Multiple Documents**: Upload and discuss multiple documents simultaneously
- **Conversation History**: Keep track of your chat history

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Get your Anthropic API key from [Anthropic Console](https://console.anthropic.com/)

3. Update the `.env` file with your API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

4. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

## Usage

1. **Upload Documents**: Use the sidebar to upload PDF, TXT, DOCX, or MD files
2. **Start Chat**: Click "Start Chat with Documents" to process your files with Claude
3. **Ask Questions**: Use the chat interface to ask questions about your documents
4. **View History**: See your conversation history and document context

## Document Types

- **PDF**: Native processing with Claude's vision capabilities (charts, images, tables)
- **TXT/MD**: Direct text analysis
- **DOCX**: Text extraction then analysis

## Example Questions

- "What are the main topics discussed in these documents?"
- "Can you summarize the key points?"
- "What conclusions can you draw from this content?"
- "Are there any important dates or numbers mentioned?"
- "Compare the different viewpoints presented in these documents"
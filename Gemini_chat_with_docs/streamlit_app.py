import streamlit as st
import os
from google import genai
import tempfile
from dotenv import load_dotenv
from docx import Document
import io

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Chat with Documents - Gemini AI",
    page_icon="📄",
    layout="wide"
)

def initialize_client(api_key):
    """Initialize the Gemini client with provided API key."""
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize client: {e}")
        return None

def extract_text_from_docx(file_bytes):
    """Extract text content from DOCX file bytes."""
    try:
        # Create a Document object from file bytes
        doc = Document(io.BytesIO(file_bytes))
        
        # Extract text from all paragraphs
        full_text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():  # Only add non-empty paragraphs
                full_text.append(paragraph.text)
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        full_text.append(cell.text)
        
        return '\n\n'.join(full_text)
    except Exception as e:
        raise Exception(f"Error extracting text from DOCX: {e}")

def main():
    """Main function for chat with documents."""
    st.title("📄 Chat with Documents - Gemini AI")
    st.markdown("Upload documents and have a conversation with AI about their content")
    st.markdown("---")
    
    # Sidebar for API key and document upload
    with st.sidebar:
        st.header("🔑 Configuration")
        
        # Try to get API key from environment first
        env_api_key = os.getenv("GOOGLE_API_KEY")
        
        api_key = st.text_input(
            "Enter your Gemini API Key:", 
            value=env_api_key if env_api_key else "",
            type="password",
            help="Get your API key from Google AI Studio (auto-loaded from .env if available)"
        )
        
        if not api_key:
            st.warning("Please enter your API key to continue")
            return
            
        client = initialize_client(api_key)
        if not client:
            st.error("❌ Failed to initialize client")
            return
        
        st.success("✅ Client initialized successfully!")
        st.markdown("---")
        
        # Document Upload Section
        st.header("📁 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose documents to chat about:",
            type=['pdf', 'txt', 'docx', 'md'],
            accept_multiple_files=True,
            help="Upload documents you want to discuss with AI. DOCX files will have their text extracted, while PDF/TXT/MD files are uploaded directly."
        )
        
        # Document management
        if uploaded_files:
            st.markdown("### 📂 Uploaded Documents:")
            for i, file in enumerate(uploaded_files, 1):
                file_extension = file.name.split('.')[-1].lower()
                if file_extension == 'docx':
                    st.markdown(f"**{i}.** {file.name} 📝 (Text will be extracted)")
                else:
                    st.markdown(f"**{i}.** {file.name} 📄")
            
            if st.button("🚀 Start Chat with Documents", type="primary"):
                with st.spinner("Processing documents..."):
                    try:
                        # Initialize session state for document chat
                        st.session_state.document_files = []
                        st.session_state.document_texts = []
                        st.session_state.temp_files = []
                        
                        # Process all documents
                        for file in uploaded_files:
                            file_extension = file.name.split('.')[-1].lower()
                            
                            if file_extension == 'docx':
                                # Extract text from DOCX file
                                text_content = extract_text_from_docx(file.getvalue())
                                st.session_state.document_texts.append({
                                    'name': file.name,
                                    'content': text_content,
                                    'type': 'text'
                                })
                            else:
                                # Handle other file types (PDF, TXT, MD) - upload to Gemini
                                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
                                    tmp_file.write(file.getvalue())
                                    st.session_state.temp_files.append(tmp_file.name)
                                
                                # Upload to Gemini
                                uploaded_gemini_file = client.files.upload(file=tmp_file.name)
                                st.session_state.document_files.append({
                                    'name': file.name,
                                    'file': uploaded_gemini_file,
                                    'type': 'file'
                                })
                        
                        # Initialize document context for streaming
                        st.session_state.chat_history = []
                        st.session_state.documents_loaded = True
                        
                        # Create comprehensive context message
                        context_parts = [f"I have uploaded {len(uploaded_files)} documents: {', '.join([f.name for f in uploaded_files])}. Please analyze these documents and let me know you're ready to answer questions about them."]
                        
                        # Add text content from DOCX files
                        for doc_text in st.session_state.document_texts:
                            context_parts.append(f"\n\n--- Content from {doc_text['name']} ---\n{doc_text['content']}")
                        
                        # Add file uploads for other formats
                        file_objects = [doc['file'] for doc in st.session_state.document_files]
                        
                        # Send initial context message with streaming
                        contents = context_parts + file_objects
                        
                        # Create container for streaming response
                        response_container = st.empty()
                        full_response = ""
                        
                        # Start with processing indicator
                        response_container.markdown("**🤖 AI:** 📄 _Analyzing documents..._")
                        
                        response_stream = client.models.generate_content_stream(
                            model="gemini-2.5-pro-preview-05-06",
                            contents=contents
                        )
                        
                        for chunk in response_stream:
                            if hasattr(chunk, 'text') and chunk.text:
                                full_response += chunk.text
                                response_container.markdown(f"**🤖 AI:** {full_response}▋")
                        
                        # Remove cursor when done
                        response_container.markdown(f"**🤖 AI:** {full_response}")
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": full_response
                        })
                        
                        st.success(f"✅ {len(uploaded_files)} documents processed successfully!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error processing documents: {e}")
    
    # Main Chat Interface
    if 'documents_loaded' in st.session_state and st.session_state.documents_loaded:
        st.header("💬 Chat with Your Documents")
        
        # Display document context
        with st.expander("📋 Loaded Documents", expanded=False):
            # Show uploaded files
            for doc in st.session_state.document_files:
                st.markdown(f"• **{doc['name']}** (File Upload)")
            # Show text content from DOCX files
            for doc in st.session_state.document_texts:
                st.markdown(f"• **{doc['name']}** (Text Extracted)")
        
        # Document previews (separate from the main expander)
        if st.session_state.document_texts:
            for doc in st.session_state.document_texts:
                with st.expander(f"📄 Preview: {doc['name']}", expanded=False):
                    preview = doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content']
                    st.text(preview)
        
        # Chat controls
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
        
        # Chat input
        user_question = st.text_input(
            "Ask a question about your documents:",
            placeholder="What is the main topic of these documents?",
            key="doc_chat_input"
        )
        
        # Add hint
        st.caption("💡 Tip: Type your question and press Enter or click Send")
        
        if st.button("📤 Send Question", type="primary") and user_question.strip():
            try:
                # Add user message to history first
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_question
                })
                
                # Build conversation context for streaming
                conversation_context = []
                
                # Add document context
                doc_context = f"Document Context - I have access to these documents: {', '.join([doc['name'] for doc in st.session_state.document_files] + [doc['name'] for doc in st.session_state.document_texts])}"
                conversation_context.append(doc_context)
                
                # Add text content from DOCX files
                for doc_text in st.session_state.document_texts:
                    conversation_context.append(f"\n--- Content from {doc_text['name']} ---\n{doc_text['content']}")
                
                # Add conversation history
                for msg in st.session_state.chat_history[:-1]:  # Exclude the just-added user message
                    if msg["role"] == "user":
                        conversation_context.append(f"User: {msg['content']}")
                    else:
                        conversation_context.append(f"Assistant: {msg['content']}")
                
                # Add current user question
                conversation_context.append(f"User: {user_question}")
                conversation_context.append("Assistant:")
                
                # Add file objects for non-DOCX files
                file_objects = [doc['file'] for doc in st.session_state.document_files]
                
                # Prepare contents for streaming
                contents = ["\n\n".join(conversation_context)] + file_objects
                
                # Show user message immediately
                st.markdown(f"**👤 You:** {user_question}")
                
                # Create placeholder for streaming response
                response_placeholder = st.empty()
                full_response = ""
                
                # Start with typing indicator
                response_placeholder.markdown("**🤖 AI:** ✨ _Thinking..._")
                
                try:
                    response_stream = client.models.generate_content_stream(
                        model="gemini-2.5-pro-preview-05-06",
                        contents=contents
                    )
                    
                    for chunk in response_stream:
                        if hasattr(chunk, 'text') and chunk.text:
                            full_response += chunk.text
                            # Show streaming response with cursor
                            response_placeholder.markdown(f"**🤖 AI:** {full_response}▋")
                    
                    # Remove cursor when done
                    response_placeholder.markdown(f"**🤖 AI:** {full_response}")
                    
                except Exception as stream_error:
                    response_placeholder.markdown(f"**🤖 AI:** ❌ Error: {stream_error}")
                    full_response = f"Error: {stream_error}"
                
                # Add assistant response to history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": full_response
                })
                
                # Clear the placeholder and rerun to show full chat history
                response_placeholder.empty()
                st.rerun()
                    
            except Exception as e:
                st.error(f"Error sending message: {e}")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### 💬 Conversation")
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"**👤 You:** {message['content']}")
                else:
                    st.markdown(f"**🤖 AI:** {message['content']}")
                st.markdown("---")
    
    else:
        # Welcome message when no documents are loaded
        st.markdown("""
        ## Welcome! 👋
        
        To get started:
        1. **Upload documents** in the sidebar (PDF, TXT, DOCX, MD)
        2. **Click "Start Chat"** to process your documents
        3. **Ask questions** about your documents in the chat interface
        
        ### Example Questions:
        - "What are the main topics discussed in these documents?"
        - "Can you summarize the key points?"
        - "What conclusions can you draw from this content?"
        - "Are there any important dates or numbers mentioned?"
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Made with ❤️ using [Streamlit](https://streamlit.io) and [Google Gemini API](https://ai.google.dev/)"
    )

if __name__ == "__main__":
    main()
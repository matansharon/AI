import streamlit as st
import os
from google import genai
import tempfile
from dotenv import load_dotenv

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

def main():
    st.title("🤖 Google Gemini API Tester")
    st.markdown("---")
    
    # Sidebar for API key
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
        
        if api_key:
            client = initialize_client(api_key)
            if client:
                st.success("✅ Client initialized successfully!")
            else:
                st.error("❌ Failed to initialize client")
                return
        else:
            st.warning("Please enter your API key to continue")
            return
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["💬 Content Generation", "🗨️ Chat Conversation", "📁 File Analysis"])
    
    # Tab 1: Streaming Content Generation
    with tab1:
        st.header("📝 Streaming Content Generation")
        st.markdown("Generate content with real-time streaming responses")
        
        prompt = st.text_area(
            "Enter your prompt:",
            value="Explain how AI works",
            height=100,
            placeholder="Type your question or prompt here..."
        )
        
        if st.button("🚀 Generate Content", type="primary"):
            if prompt.strip():
                with st.spinner("Generating response..."):
                    try:
                        response_container = st.empty()
                        full_response = ""
                        
                        response = client.models.generate_content_stream(
                            model="gemini-2.0-flash",
                            contents=[prompt]
                        )
                        
                        for chunk in response:
                            full_response += chunk.text
                            response_container.markdown(full_response)
                        
                        st.success("✅ Content generated successfully!")
                        
                    except Exception as e:
                        st.error(f"Error generating content: {e}")
            else:
                st.warning("Please enter a prompt")
    
    # Tab 2: Chat Conversation
    with tab2:
        st.header("💬 Chat Conversation")
        st.markdown("Have a multi-turn conversation with Gemini")
        
        # Initialize chat session in session state
        if 'chat_session' not in st.session_state:
            st.session_state.chat_session = None
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🆕 Start New Chat"):
                try:
                    st.session_state.chat_session = client.chats.create(model="gemini-2.0-flash")
                    st.session_state.chat_history = []
                    st.success("New chat session started!")
                except Exception as e:
                    st.error(f"Error starting chat: {e}")
        
        with col2:
            if st.button("🗑️ Clear History"):
                st.session_state.chat_history = []
                st.success("History cleared!")
        
        # Chat interface
        if st.session_state.chat_session:
            user_message = st.text_input(
                "Your message:",
                placeholder="Type your message here...",
                key="chat_input"
            )
            
            if st.button("📤 Send Message") and user_message.strip():
                try:
                    with st.spinner("Sending message..."):
                        response = st.session_state.chat_session.send_message(user_message)
                        
                        # Add to history
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": user_message
                        })
                        st.session_state.chat_history.append({
                            "role": "assistant", 
                            "content": response.text
                        })
                        
                        # Clear input
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error sending message: {e}")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### 📜 Chat History")
            for i, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    st.markdown(f"**👤 You:** {message['content']}")
                else:
                    st.markdown(f"**🤖 Gemini:** {message['content']}")
                st.markdown("---")
        else:
            st.info("Start a new chat to begin conversation")
    
    # Tab 3: File Analysis
    with tab3:
        st.header("📁 File Upload & Analysis")
        st.markdown("Upload multiple files for AI analysis")
        
        uploaded_files = st.file_uploader(
            "Choose files to analyze",
            type=['mp3', 'wav', 'ogg', 'm4a','pdf', 'txt', 'docx', 'jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            help="Upload audio, document, or image files for analysis"
        )
        
        analysis_prompt = st.text_area(
            "Analysis prompt:",
            value="Analyze and describe these files",
            height=80,
            placeholder="What would you like to know about these files?"
        )
        
        # Show uploaded files
        if uploaded_files:
            st.markdown("### 📂 Uploaded Files:")
            for i, file in enumerate(uploaded_files, 1):
                st.markdown(f"**{i}.** {file.name} ({file.size:,} bytes)")
        
        if uploaded_files and analysis_prompt:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                analyze_together = st.button("🔍 Analyze All Together", type="primary")
            with col2:
                analyze_separately = st.button("📝 Analyze Each File Separately")
            
            if analyze_together:
                try:
                    with st.spinner(f"Uploading and analyzing {len(uploaded_files)} files together..."):
                        gemini_files = []
                        temp_files = []
                        
                        # Upload all files to Gemini
                        for file in uploaded_files:
                            # Save uploaded file temporarily
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp_file:
                                tmp_file.write(file.getvalue())
                                temp_files.append(tmp_file.name)
                            
                            # Upload to Gemini
                            uploaded_gemini_file = client.files.upload(file=tmp_file.name)
                            gemini_files.append(uploaded_gemini_file)
                        
                        # Generate analysis for all files together
                        contents = [analysis_prompt] + gemini_files
                        response = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=contents
                        )
                        
                        st.success(f"✅ {len(uploaded_files)} files analyzed together successfully!")
                        st.markdown("### 📊 Combined Analysis Result:")
                        st.markdown(response.text)
                        
                        # Clean up temp files
                        for temp_file in temp_files:
                            os.unlink(temp_file)
                        
                except Exception as e:
                    st.error(f"Error analyzing files: {e}")
                    # Clean up temp files on error
                    for temp_file in temp_files:
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
            
            elif analyze_separately:
                try:
                    with st.spinner(f"Analyzing {len(uploaded_files)} files separately..."):
                        for i, file in enumerate(uploaded_files, 1):
                            st.markdown(f"### 📄 Analysis of File {i}: {file.name}")
                            
                            # Save uploaded file temporarily
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp_file:
                                tmp_file.write(file.getvalue())
                                tmp_file_path = tmp_file.name
                            
                            # Upload to Gemini
                            uploaded_gemini_file = client.files.upload(file=tmp_file_path)
                            
                            # Generate analysis
                            response = client.models.generate_content(
                                model="gemini-2.0-flash",
                                contents=[f"{analysis_prompt} (File: {file.name})", uploaded_gemini_file]
                            )
                            
                            st.markdown(response.text)
                            st.markdown("---")
                            
                            # Clean up temp file
                            os.unlink(tmp_file_path)
                        
                        st.success(f"✅ All {len(uploaded_files)} files analyzed separately!")
                        
                except Exception as e:
                    st.error(f"Error analyzing files: {e}")
                    try:
                        os.unlink(tmp_file_path)
                    except:
                        pass
        
        elif uploaded_files:
            st.info("Enter an analysis prompt to proceed")
        else:
            st.info("Upload files to begin analysis")

    # Footer
    st.markdown("---")
    st.markdown(
        "Made with ❤️ using [Streamlit](https://streamlit.io) and [Google Gemini API](https://ai.google.dev/)"
    )

if __name__ == "__main__":
    main()
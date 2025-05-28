import os
from google import genai

def setup_client():
    """Initialize the Gemini client with API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    return genai.Client(api_key=api_key)

def generate_content_stream(client, prompt):
    """Generate content with streaming response."""
    print(f"Generating response for: {prompt}")
    print("-" * 50)
    
    response = client.models.generate_content_stream(
        model="gemini-2.0-flash",
        contents=[prompt]
    )
    
    for chunk in response:
        print(chunk.text, end="")
    print("\n" + "=" * 50)

def chat_conversation(client):
    """Demonstrate chat functionality with conversation history."""
    print("Starting chat conversation...")
    print("-" * 50)
    
    chat = client.chats.create(model="gemini-2.0-flash")
    
    # First message
    response = chat.send_message("I have 2 dogs in my house.")
    print(f"User: I have 2 dogs in my house.")
    print(f"AI: {response.text}")
    
    # Follow-up message
    response = chat.send_message("How many paws are in my house?")
    print(f"User: How many paws are in my house?")
    print(f"AI: {response.text}")
    
    print("\nConversation History:")
    print("-" * 30)
    for message in chat.get_history():
        print(f'{message.role}: {message.parts[0].text}')
    
    print("=" * 50)

def upload_and_analyze_file(client, file_path):
    """Upload and analyze an audio file."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    print(f"Uploading and analyzing file: {file_path}")
    print("-" * 50)
    
    try:
        myfile = client.files.upload(file=file_path)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=["Describe this audio clip", myfile]
        )
        
        print(response.text)
    except Exception as e:
        print(f"Error processing file: {e}")
    
    print("=" * 50)

def main():
    """Main function to demonstrate Gemini API capabilities."""
    try:
        client = setup_client()
        
        # Demo 1: Content generation with streaming
        generate_content_stream(client, "Explain how AI works")
        
        # Demo 2: Chat conversation
        chat_conversation(client)
        
        # Demo 3: File upload (uncomment and provide a valid audio file path)
        # upload_and_analyze_file(client, "path/to/sample.mp3")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set your GEMINI_API_KEY environment variable")

if __name__ == "__main__":
    main()
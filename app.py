import streamlit as st
import requests
import re
from datetime import datetime

# Page configuration and styling
st.set_page_config(
    page_title="NUST Bank Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
  .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
    }
   
    .stButton button {
        background-color: #3B82F6;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #1E3A8A;
    }
   
    .footer {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.8rem;
        color: #6B7280;
    }
   
    .warning-box {
        background-color: #FEF3C7;
        padding: 0.75rem;
        border-left: 4px solid #F59E0B;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 0.75rem;
        border-left: 4px solid #10B981;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>🏦 NUST Bank Assistant</h1>", unsafe_allow_html=True)

# Initialize session state variables
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

if "api_key_submitted" not in st.session_state:
    st.session_state["api_key_submitted"] = False

if "document_uploaded" not in st.session_state:
    st.session_state["document_uploaded"] = False

if "documents" not in st.session_state:
    st.session_state["documents"] = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "sidebar_state" not in st.session_state:
    st.session_state["sidebar_state"] = "expanded"

# Backend URL
backend_url = "https://wasifis-backend.hf.space"

# Sidebar
with st.sidebar:
    st.markdown("<h2 class='subheader'>Settings</h2>", unsafe_allow_html=True)
    
    # API Key section
    st.markdown("### API Key Configuration")
    if not st.session_state["api_key_submitted"]:
        st.session_state["api_key"] = st.text_input("Enter your OpenAI API key", type="password")
        if st.button("Submit API Key", key="submit_api_key") and st.session_state["api_key"]:
            with st.spinner("Validating API key..."):
                response = requests.post(f"{backend_url}/set_openai_api_key/", json={"api_key": st.session_state["api_key"]})
                if response.status_code == 200:
                    st.session_state["api_key_submitted"] = True
                    st.markdown("<div class='success-box'>API key set successfully!</div>", unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown("<div class='warning-box'>Failed to set API key. Please check if it's valid.</div>", unsafe_allow_html=True)
    else:
        st.markdown("✅ API key configured")
        if st.button("Change API Key", key="change_api_key"):
            st.session_state["api_key_submitted"] = False
            st.rerun()
    
    # About section
    st.markdown("### About")
    st.markdown("""
    This assistant helps with:
    - Banking policy questions
    - Account information
    - Financial services
    - General banking queries
    
    Upload documents to enhance responses with specific information.
    """)

# Only show the rest of the interface if API key is submitted
if st.session_state["api_key_submitted"]:
    # Main content with two columns
    col1, col2 = st.columns([1, 2])
    
    # Upload document section in the first column
    with col1:
        st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
        st.markdown("<h2 class='subheader'>Upload Documents</h2>", unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload banking documents (PDF, Word, Excel, CSV)",
            type=["pdf", "docx", "doc", "xlsx", "xls", "csv"],
            help="Upload documents to get more accurate and context-specific answers"
        )
        
        if uploaded_file is not None:
            if st.button("Process Document", key="process_doc"):
                with st.spinner("Processing document..."):
                    # Upload the file to the backend
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{backend_url}/upload_document/", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "message" in data:
                            st.markdown("<div class='success-box'>Document processed successfully!</div>", unsafe_allow_html=True)
                            st.session_state["document_uploaded"] = True
                            # Add document to the list
                            st.session_state["documents"].append({
                                "name": uploaded_file.name,
                                "type": uploaded_file.type,
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                            })
                        elif "error" in data:
                            st.markdown(f"<div class='warning-box'>Error: {data['error']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='warning-box'>Error uploading document: {response.status_code}</div>", unsafe_allow_html=True)
        
        # Display uploaded documents
        if len(st.session_state["documents"]) > 0:
            st.markdown("### Uploaded Documents")
            for i, doc in enumerate(st.session_state["documents"]):
                st.markdown(f"**{i+1}. {doc['name']}**")
                st.markdown(f"Type: {doc['type']} | Uploaded: {doc['date']}")
                st.divider()
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Chat interface in the second column
    with col2:
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        st.markdown("<h2 class='subheader'>Chat with NUST Bank Assistant</h2>", unsafe_allow_html=True)
        
        # Show a warning if no document is uploaded, but don't block chat
        if not st.session_state["document_uploaded"]:
            st.markdown("<div class='warning-box'>⚠️ No documents uploaded yet. Answers will be limited to general knowledge.</div>", unsafe_allow_html=True)
        
        # Display chat history
        if not st.session_state.messages:
            st.markdown("👋 Hello! I'm your NUST Bank Assistant. How can I help you today?")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask your banking question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = requests.post(f"{backend_url}/process_input_message/", json={"message": prompt})
                
                if response.status_code == 200:
                    response_data = response.json()
                    response_text = response_data.get("message", "No response received.")
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    error_text = f"Error: Could not process your request (Status code: {response.status_code})"
                    st.markdown(error_text)
                    st.session_state.messages.append({"role": "assistant", "content": error_text})
        
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>© 2025 NUST Bank Assistant | Powered by OpenAI</div>", unsafe_allow_html=True)
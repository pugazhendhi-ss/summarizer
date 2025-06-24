import streamlit as st
import requests
import time
import json

st.set_page_config(
    page_title="PDF Analyzer",
    page_icon="📊",
    layout="wide"
)


def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_mode' not in st.session_state:
        st.session_state.chat_mode = False
    if 'summary_result' not in st.session_state:
        st.session_state.summary_result = None
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'chat_setup_complete' not in st.session_state:
        st.session_state.chat_setup_complete = False


def main():
    # Initialize session state first
    initialize_session_state()

    st.title("📊 PDF Analysis Tool")
    st.markdown("Upload a WASDE PDF to analyze commodity data or start a chat session")

    # Main interface logic
    if not st.session_state.chat_mode and st.session_state.summary_result is None:
        show_upload_interface()
    elif st.session_state.summary_result is not None:
        show_summary_result()
    elif st.session_state.chat_mode:
        show_chat_interface()


def show_upload_interface():
    st.markdown("### Upload PDF File")

    # File upload
    uploaded_file = st.file_uploader(
        "Choose a WASDE PDF file",
        type=['pdf'],
        help="Upload a WASDE (World Agricultural Supply and Demand Estimates) PDF file"
    )

    if uploaded_file is not None:
        # Display file info
        st.success(f"File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")

        # Create two columns for buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📋 Summarize PDF", use_container_width=True, type="primary"):
                handle_summarize_pdf(uploaded_file)

        with col2:
            if st.button("💬 Setup Chat", use_container_width=True, type="secondary"):
                handle_setup_chat(uploaded_file)
    else:
        st.info("Please upload a PDF file to continue")


def handle_summarize_pdf(uploaded_file):
    """Handle PDF summarization request"""
    with st.spinner("🔄 Processing PDF and generating summary... This may take a few minutes."):
        try:
            # Prepare the file for upload
            files = {
                'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')
            }

            # Prepare form data with operation parameter
            data = {
                'operation': 'summarize'
            }

            # Make request to unified endpoint with operation parameter
            response = requests.post(
                'http://127.0.0.1:7000/upload-pdf',
                files=files,
                data=data,  # Add the operation parameter
                timeout=300  # 5 minutes timeout
            )

            if response.status_code == 200:
                result = response.json()
                st.session_state.summary_result = result
                st.rerun()
            else:
                st.error(f"Error: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            st.error("Request timed out. The PDF processing is taking longer than expected.")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the server. Please ensure the API is running.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


def handle_setup_chat(uploaded_file):
    """Handle chat setup request"""
    with st.spinner("🔄 Setting up chat (ingesting into vector DB)... Please wait."):
        try:
            # Prepare the file for upload
            files = {
                'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')
            }

            # Prepare form data with operation parameter
            data = {
                'operation': 'chat'
            }

            # Make request to unified endpoint with operation parameter
            response = requests.post(
                'http://127.0.0.1:7000/upload-pdf',
                files=files,
                data=data,  # Add the operation parameter
                timeout=300  # 5 minutes timeout
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    st.session_state.pdf_filename = result.get('pdf_filename', uploaded_file.name)
                    st.session_state.chat_mode = True
                    st.session_state.chat_setup_complete = True
                    st.success("Chat session setup successfully!")
                    time.sleep(1)  # Brief pause to show success message
                    st.rerun()
                else:
                    st.error(f"Chat setup failed: {result.get('message', 'Unknown error')}")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            st.error("Request timed out. The chat setup is taking longer than expected.")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the server. Please ensure the API is running.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


def show_summary_result():
    """Display the PDF summary result"""
    st.markdown("### 📋 PDF Summary Result")

    # Back button
    if st.button("← Back to Upload", type="secondary"):
        st.session_state.summary_result = None
        st.rerun()

    st.markdown("---")

    # Display the summary
    if st.session_state.summary_result:
        try:
            # Assuming the API returns a JSON with summary content
            summary_content = st.session_state.summary_result.get('summary', 'No summary available')

            # Display summary in a nice format
            st.markdown("#### Complete WASDE Analysis")
            st.markdown(summary_content)

            # Download button for the summary
            st.download_button(
                label="📥 Download Summary",
                data=summary_content,
                file_name=f"wasde_summary_{int(time.time())}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Error displaying summary: {str(e)}")
            st.json(st.session_state.summary_result)  # Fallback to raw JSON


def show_chat_interface():
    """Display the chat interface"""
    pdf_name = st.session_state.get('pdf_filename', 'Document')
    st.markdown(f"### 💬 You are now chatting with **{pdf_name}**")
    # st.markdown("### 💬 Chat with WASDE Document")

    # Back button
    if st.button("← Back to Upload", type="secondary"):
        st.session_state.chat_mode = False
        st.session_state.chat_setup_complete = False
        st.session_state.chat_messages = []
        st.rerun()

    st.markdown("---")

    if st.session_state.chat_setup_complete:
        # Display chat messages
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask questions about the WASDE document..."):
            # Add user message to chat history
            st.session_state.chat_messages.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = handle_chat_message(prompt)
                    st.markdown(response)

            # Add assistant response to chat history
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
    else:
        st.error("Chat session not properly set up. Please go back and try again.")


def handle_chat_message(user_message):
    """Handle chat message and get response from chat API"""
    try:
        # Get PDF filename from session state
        pdf_name = st.session_state.get('pdf_filename', 'Document')
        pdf_name = pdf_name.split('.')[0]

        # Prepare chat payload according to ChatPayload model
        chat_payload = {
            "file_name": pdf_name,
            "query": user_message
        }

        # Make request to chat endpoint
        response = requests.post(
            'http://127.0.0.1:7000/chat',
            json=chat_payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()

            # Check if the response was successful
            if result.get('status') == 'success':
                # Return the LLM reply from ChatResponse
                return result.get('llm_reply', 'No response received from the AI.')
            else:
                # Handle case where status is not success
                error_message = result.get('message', 'Unknown error occurred')
                return f"Sorry, I encountered an issue: {error_message}"

        else:
            # Handle HTTP error responses
            return f"Sorry, I couldn't process your request. Server returned status code: {response.status_code}"

    except requests.exceptions.Timeout:
        return "Sorry, the request took too long to process. Please try again with a shorter question."

    except requests.exceptions.ConnectionError:
        return "Sorry, I couldn't connect to the chat service. Please ensure the API server is running."

    except requests.exceptions.RequestException as e:
        return f"Sorry, there was a network error: {str(e)}"

    except json.JSONDecodeError:
        return "Sorry, I received an invalid response from the server. Please try again."

    except Exception as e:
        return f"Sorry, I encountered an unexpected error: {str(e)}"


def add_sidebar_info():
    """Add information sidebar"""
    with st.sidebar:
        st.markdown("### ℹ️ About")
        st.markdown("""
        This tool helps you analyze WASDE (World Agricultural Supply and Demand Estimates) PDF documents.

        **Features:**
        - 📋 **Summarize**: Get a comprehensive analysis of commodity data
        - 💬 **Chat**: Ask specific questions about the document

        **Supported formats:** PDF files only
        """)

        st.markdown("### Server status")
        try:
            health_response = requests.get('http://127.0.0.1:7000/health', timeout=5)
            if health_response.status_code == 200:
                st.success("✅ API Server Connected")
            else:
                st.error("❌ API Server Issues")
        except:
            st.error("❌ API Server Offline")

add_sidebar_info()
main()

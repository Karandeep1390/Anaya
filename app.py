import streamlit as st
from aiAgents.loan_reengagement import LoanReengagementAgent
from util.utils import logger
from config.config import LOG_FILE_PATH
from auth.auth import initialize_session, login_form, logout

# Initialize session state
initialize_session()

# Page config with custom CSS
st.set_page_config(
    page_title="Anaya",
    page_icon="💰",
    layout="wide"
)

# Dark Black Theme CSS
st.markdown("""
<style>
    /* Dark background gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #000000 100%);
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Main container styling */
    .main-container {
        background: linear-gradient(145deg, #111111, #1e1e1e);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.8),
            0 0 0 1px rgba(255, 255, 255, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }

    /* Chat message styling */
    .stChatMessage {
        background: rgba(25, 25, 25, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(5px);
    }

    /* User message styling */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #1a2332 0%, #2d3748 100%);
        border-left: 3px solid #4a9eff;
    }

    /* Assistant message styling */
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-left: 3px solid #48bb78;
    }

    /* Welcome message styling */
    .welcome-message {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
        color: #ffffff;
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.6),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    .welcome-message h1 {
        background: linear-gradient(135deg, #ffffff 0%, #b3b3b3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    .welcome-message p {
        color: #cccccc;
        font-size: 1.1rem;
        margin: 0.5rem 0;
    }

    /* Sidebar styling */
    .css-1d391kg, .css-1cypcdb {
        background: linear-gradient(145deg, #0f0f0f, #1a1a1a);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    .css-1d391kg .element-container, .css-1cypcdb .element-container {
        color: #ffffff;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #333333 0%, #4a4a4a 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
        border-color: rgba(255, 255, 255, 0.3);
    }

    /* Chat input styling */
    .stChatInputContainer {
        background: rgba(20, 20, 20, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }

    .stChatInput > div > div > input {
        background: transparent;
        color: #ffffff;
        border: none;
        font-size: 1rem;
    }

    .stChatInput > div > div > input::placeholder {
        color: #666666;
    }

    /* Text area styling for logs */
    .stTextArea > div > div > textarea {
        background: rgba(15, 15, 15, 0.9);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        font-family: 'Courier New', monospace;
    }

    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #4a9eff;
    }

    /* Markdown text styling */
    .stMarkdown, .stText, p, div, h1, h2, h3, h4, h5, h6 {
        color: inherit;
    }

    /* Conversation header styling */
    .conversation-header {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }

    /* Empty state styling */
    .empty-chat {
        text-align: center;
        padding: 3rem 2rem;
        color: #888888;
        background: rgba(25, 25, 25, 0.5);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .empty-chat h3 {
        color: #cccccc;
        margin-bottom: 1rem;
    }

    /* Footer styling */
    .app-footer {
        text-align: center;
        padding: 1.5rem;
        color: #666666;
        font-size: 0.9rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 2rem;
        background: rgba(10, 10, 10, 0.5);
        border-radius: 10px;
    }

    /* Sidebar section headers */
    .sidebar-header {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }

    ::-webkit-scrollbar-thumb {
        background: #333333;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #555555;
    }

    /* Error message styling */
    .stAlert > div {
        background: rgba(116, 42, 42, 0.3);
        color: #f87171;
        border: 1px solid rgba(248, 113, 113, 0.3);
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }

    /* Success message styling */
    .stSuccess > div {
        background: rgba(34, 84, 61, 0.3);
        color: #4ade80;
        border: 1px solid rgba(74, 222, 128, 0.3);
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }

    /* Chat message content */
    .stChatMessage div {
        color: #ffffff;
    }

    /* Make sure all text is visible */
    * {
        color: inherit;
    }
</style>
""", unsafe_allow_html=True)

# Authentication check
if not st.session_state.authenticated:
    if login_form():
        st.rerun()
    st.stop()

# Initialize agent with customer ID
if 'agent' not in st.session_state:
    try:
        st.session_state.agent = LoanReengagementAgent(customer_id=st.session_state.customer_id)
        logger.info(f"Agent initialized successfully for customer {st.session_state.customer_id}")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        st.error("Failed to initialize the chat assistant. Please try again later.")
        st.stop()

# Initialize messages if not exists
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Main container
with st.container():
    # Title and welcome message
    st.markdown(f"""
    <div class="welcome-message">
        <h1>💰 Loan Re-engagement Assistant</h1>
        <p>Welcome, <strong>{st.session_state.username}</strong>! 👋</p>
        <p>I'm here to help you understand your pre-approved loan offer and answer any questions you might have about your loan amount, EMI, interest rate, or any other details! 😊</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar with minimal options
with st.sidebar:
    st.markdown('<div class="sidebar-header">Account</div>', unsafe_allow_html=True)

    # Only show logout button to customers
    if st.button("🚪 Logout", key="logout_btn"):
        logout()
        st.rerun()

    # Admin-only features (hidden from regular customers)
    if hasattr(st.session_state, 'user_role') and st.session_state.user_role == 'admin':
        st.markdown("---")
        st.markdown('<div class="sidebar-header">Admin Options</div>', unsafe_allow_html=True)

        if st.button("🗑️ Clear Chat", key="admin_clear"):
            st.session_state.messages = []
            st.rerun()

        if st.button("📋 View Logs", key="admin_logs"):
            try:
                with open(LOG_FILE_PATH, 'r') as f:
                    logs = f.read()
                    st.text_area("Application Logs", logs, height=300)
            except Exception as e:
                st.error("Could not load logs")

# Chat interface
# st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Display chat messages with improved styling
if st.session_state.messages:
    # st.markdown('<div class="conversation-header">💬 Conversation</div>', unsafe_allow_html=True)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
else:
    st.markdown("""
    <div class="empty-chat">
        <h3>👋 Start the conversation!</h3>
        <p>Ask me anything about your loan offer. I'm here to help!</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask me about your loan offer..."):
    try:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.agent.process_message(
                    prompt,
                    st.session_state.messages
                )
                st.write(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        st.error("Sorry, I encountered an error. Please try again.")

st.markdown("""
<div class="app-footer">
    🔒 Need help? Contact our support team for assistance with your loan application.
</div>
""", unsafe_allow_html=True)
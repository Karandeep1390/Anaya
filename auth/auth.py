import streamlit as st
import pandas as pd
from typing import Dict, Optional
from util.utils import logger
from config.config import CUSTOMER_DATA_PATH, USER_CREDENTIALS_PATH


def load_user_credentials() -> pd.DataFrame:
    """Load user credentials from CSV file."""
    try:
        return pd.read_csv(USER_CREDENTIALS_PATH)
    except Exception as e:
        logger.error(f"Error loading user credentials: {str(e)}")
        raise


def load_customer_data() -> pd.DataFrame:
    """Load customer data from CSV file."""
    try:
        return pd.read_csv(CUSTOMER_DATA_PATH)
    except Exception as e:
        logger.error(f"Error loading customer data: {str(e)}")
        raise


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user and return user data if successful.

    Args:
        username: User's username/email
        password: User's password

    Returns:
        Dictionary with user data if authentication successful, None otherwise
    """
    try:
        df = load_user_credentials()
        user = df[(df['username'] == username) & (df['password'] == password)]

        if not user.empty:
            user_data = user.iloc[0].to_dict()
            # Add role if not present (default to customer)
            if 'role' not in user_data:
                user_data['role'] = 'customer'
            return user_data
        return None
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return None


def get_customer_details(customer_id: str) -> Optional[Dict]:
    """
    Get customer details by customer_id.

    Args:
        customer_id: Customer ID

    Returns:
        Dictionary with customer details if found, None otherwise
    """
    try:
        df = load_customer_data()
        customer = df[df['customer_id'] == customer_id]

        if not customer.empty:
            return customer.iloc[0].to_dict()
        return None
    except Exception as e:
        logger.error(f"Error getting customer details: {str(e)}")
        return None


def initialize_session():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'customer_id' not in st.session_state:
        st.session_state.customer_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'customer_data' not in st.session_state:
        st.session_state.customer_data = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = 'customer'


def login_form() -> bool:
    """
    Display clean and aesthetic dark black login form.

    Returns:
        True if login successful, False otherwise
    """

    # Dark Black Theme CSS styling
    st.markdown("""
    <style>
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}

        /* Dark background */
        .stApp {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #000000 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #ffffff;
        }

        /* Main container */
        .login-card {
            background: linear-gradient(145deg, #111111, #1e1e1e);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.8),
                0 0 0 1px rgba(255, 255, 255, 0.05),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            max-width: 400px;
            margin: 3rem auto;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }

        /* Header */
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .app-title {
            font-size: 1.75rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #b3b3b3 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
            letter-spacing: -0.025em;
        }

        .app-subtitle {
            font-size: 0.95rem;
            color: #888888;
            margin-top: 0.5rem;
            font-weight: 400;
        }

        /* Input styling */
        .stTextInput > div > div > input {
            background: rgba(20, 20, 20, 0.8);
            border: 1.5px solid rgba(255, 255, 255, 0.15);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            color: #ffffff;
            backdrop-filter: blur(5px);
        }

        .stTextInput > div > div > input:focus {
            border-color: #4a9eff;
            box-shadow: 
                0 0 0 3px rgba(74, 158, 255, 0.2),
                0 0 20px rgba(74, 158, 255, 0.1);
            background: rgba(25, 25, 25, 0.9);
            outline: none;
        }

        .stTextInput > div > div > input::placeholder {
            color: #666666;
        }

        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            font-size: 0.95rem;
            font-weight: 600;
            width: 100%;
            margin-top: 1rem;
            transition: all 0.3s ease;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #333333 0%, #4a4a4a 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
            border-color: rgba(255, 255, 255, 0.3);
        }

        .stButton > button:active {
            transform: translateY(0);
        }

        /* Form container */
        .stForm {
            background: transparent;
            border: none;
            padding: 0;
        }

        /* Input labels */
        .input-label {
            color: #cccccc;
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            display: block;
        }

        /* Hide default streamlit labels */
        .stTextInput label {
            display: none;
        }

        /* Alert styling */
        .stAlert {
            border-radius: 10px;
            border: none;
            font-size: 0.875rem;
            backdrop-filter: blur(10px);
        }

        /* Success message */
        .stSuccess {
            background: rgba(34, 84, 61, 0.3);
            color: #4ade80;
            border: 1px solid rgba(74, 222, 128, 0.3);
            box-shadow: 0 4px 15px rgba(34, 84, 61, 0.2);
        }

        /* Error message */
        .stError {
            background: rgba(116, 42, 42, 0.3);
            color: #f87171;
            border: 1px solid rgba(248, 113, 113, 0.3);
            box-shadow: 0 4px 15px rgba(116, 42, 42, 0.2);
        }

        /* Footer */
        .login-footer {
            text-align: center;
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: #666666;
            font-size: 0.8rem;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .login-card {
                margin: 1rem;
                padding: 2rem 1.5rem;
            }
        }

        /* Sidebar styling (if needed) */
        .css-1d391kg {
            background-color: #111111;
        }

        /* Make sure text is visible in dark theme */
        .stMarkdown, .stText, p, div {
            color: inherit;
        }

        /* Custom scrollbar for dark theme */
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
    </style>
    """, unsafe_allow_html=True)

    # Center the login form
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="login-header">
                <h1 class="app-title">Loan Portal</h1>
                <p class="app-subtitle">Sign in to your account</p>
            </div>
        """, unsafe_allow_html=True)

        # Login form
        with st.form("login_form", clear_on_submit=False):
            st.markdown('<label class="input-label">Email or Username</label>', unsafe_allow_html=True)
            username = st.text_input("Email or Username", placeholder="Enter your email", key="login_username",
                                     label_visibility="collapsed")

            st.markdown('<label class="input-label">Password</label>', unsafe_allow_html=True)
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password",
                                     label_visibility="collapsed")

            submit = st.form_submit_button("Sign In")

        # Handle form submission outside the form context
        if submit:
            if not username or not password:
                st.error("Please fill in all fields")
                return False

            user_data = authenticate_user(username, password)
            if not user_data:
                st.error("Invalid credentials")
                logger.warning(f"Failed login attempt for username: {username}")
                return False
            else:
                # Extract customer_id from user_data
                customer_id = user_data.get('customer_id')

                # Load customer data
                customer_data = get_customer_details(customer_id) if customer_id else None

                st.session_state.authenticated = True
                st.session_state.customer_id = customer_id
                st.session_state.username = username
                st.session_state.customer_data = customer_data
                st.session_state.user_role = user_data.get('role', 'customer')

                logger.info(f"User {username} (Customer: {customer_id}) logged in successfully")

                # Show welcome message
                welcome_name = customer_data.get('name', username) if customer_data else username
                st.success(f"Welcome back, {welcome_name}!")

                # Small delay to show success message
                import time
                time.sleep(1)
                st.rerun()
                return True

        st.markdown("""
            <div class="login-footer">
                <p>🔒 Secure & encrypted connection</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return False


def logout():
    """Handle user logout."""
    username = st.session_state.get('username', 'Unknown')

    # Clear all session state
    st.session_state.authenticated = False
    st.session_state.customer_id = None
    st.session_state.username = None
    st.session_state.customer_data = None
    st.session_state.user_role = 'customer'

    # Clear messages if they exist
    if 'messages' in st.session_state:
        st.session_state.messages = []

    logger.info(f"User {username} logged out")
    st.rerun()


def display_user_info():
    """Display current user information in sidebar."""
    if st.session_state.authenticated and st.session_state.customer_data:
        with st.sidebar:
            st.markdown("### User Profile")
            customer = st.session_state.customer_data
            st.write(f"**{customer.get('name', 'N/A')}**")
            st.write(f"ID: {customer.get('customer_id', 'N/A')}")

            # Show role if admin
            if st.session_state.user_role == 'admin':
                st.write(f"**Role:** Admin")

            if st.button("Sign Out", use_container_width=True):
                logout()


def require_authentication():
    """Decorator-like function to check authentication."""
    if not st.session_state.get('authenticated', False):
        login_form()
        return False
    return True


def is_admin() -> bool:
    """Check if current user is admin."""
    return st.session_state.get('user_role', 'customer') == 'admin'


def get_current_user_role() -> str:
    """Get current user's role."""
    return st.session_state.get('user_role', 'customer')
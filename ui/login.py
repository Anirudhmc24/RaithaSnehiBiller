# ui/login.py
import streamlit as st
from database.db_main import get_user, add_user
from utils.security import verify_password

def page_login():
    """
    Renders a premium fullscreen login and registration page.
    Hides the sidebar navigation until the user is authenticated.
    """
    # CSS to hide the Streamlit sidebar and header for unauthenticated sessions
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        header {
            visibility: hidden !important;
        }
        .login-container {
            max-width: 440px;
            margin: 60px auto;
            padding: 36px;
            background: #ffffff;
            border-radius: 16px;
            border: 1px solid rgba(226,232,240,0.8);
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
        }
        .login-title {
            text-align: center;
            font-size: 1.7rem;
            font-weight: 800;
            color: #1b5e20;
            margin: 0 0 6px 0;
            letter-spacing: -0.5px;
        }
        .login-subtitle {
            text-align: center;
            font-size: 0.85rem;
            color: #64748b;
            margin: 0 0 24px 0;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    if st.session_state.auth_mode == "login":
        st.markdown('<h1 class="login-title">🌱 Raitha Snehi Biller</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Fertilizer & Pesticide Management Gateway</p>', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Username", label_visibility="visible").strip()
            password = st.text_input("Password", type="password", placeholder="Password", label_visibility="visible")
            submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("Enter both username and password.")
                else:
                    user = get_user(username)
                    if user:
                        if user["status"] == "pending":
                            st.warning("⏳ Access Pending: Registration awaits administrator approval.")
                        elif user["status"] == "disabled":
                            st.error("🚫 Access Revoked: Account has been disabled. Contact admin.")
                        elif verify_password(password, user["password_hash"], user["salt"]):
                            st.session_state.authenticated = True
                            st.session_state.username = user["username"]
                            st.session_state.user_role = user["role"]
                            st.toast(f"Welcome back, {user['username']}!", icon="👋")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials: Incorrect username or password.")
                    else:
                        st.error("❌ Invalid credentials: Incorrect username or password.")

        st.markdown("<div style='text-align:center;margin-top:20px;'>", unsafe_allow_html=True)
        if st.button("Don't have an account? Request access", key="go_to_register"):
            st.session_state.auth_mode = "register"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown('<h1 class="login-title">🌱 Request Access</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Submit credentials for admin approval</p>', unsafe_allow_html=True)

        with st.form("register_form", clear_on_submit=False):
            new_username = st.text_input("Choose Username *", placeholder="e.g. staff_name").strip()
            new_password = st.text_input("Choose Password *", type="password", placeholder="Minimum 6 characters")
            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Retype password")
            submit_reg = st.form_submit_button("Register Account", type="primary", use_container_width=True)

            if submit_reg:
                if not new_username or not new_password or not confirm_password:
                    st.error("Please fill all marked (*) fields.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif not new_username.replace("_", "").replace(".", "").isalnum():
                    st.error("Username must be alphanumeric (underscores/dots allowed).")
                else:
                    success = add_user(new_username, new_password, role='user', status='pending')
                    if success:
                        st.success("✅ Account registration requested!")
                        st.info("An administrator must approve your account before you can log in.")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error("❌ Username already taken. Please choose another name.")

        st.markdown("<div style='text-align:center;margin-top:20px;'>", unsafe_allow_html=True)
        if st.button("Already have an account? Back to Login", key="go_to_login"):
            st.session_state.auth_mode = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

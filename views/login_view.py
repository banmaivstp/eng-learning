import streamlit as st
import logging
from config import oauth2

# Khai báo bộ logger định danh riêng cho giao diện đăng nhập
logger = logging.getLogger("views.login_view")

def render_login_form():
    """Renders the single-touch Google OAuth login UI components."""
    # Log ở cấp độ DEBUG để theo dõi số lần giao diện login được ép vẽ lại (Re-render)
    logger.debug("🖥️ Rendering single-touch Google OAuth login form interface.")
    
    st.title("⚡ Hệ thống Học tiếng Anh Edu-Stay AI")
    st.caption("Vui lòng xác thực tài khoản để bắt đầu bài học nghe hiểu.")
    
    # result = oauth2.authorize_button(
        # name="🔑 Đăng nhập bằng Gmail để bắt đầu học",
        # redirect_uri=st.secrets["REDIRECT_URI"],
        # scope="openid email profile",
        # key="google_auth"
    # )
# result = oauth2.authorize_button(
    # name="🔑 Đăng nhập bằng Gmail để bắt đầu học",
    # redirect_uri=st.secrets["REDIRECT_URI"],
    # scope="openid email profile",
    # key="google_auth",

    # extras_params={
        # "prompt": "select_account"
    # }
    
  
#)
    result = oauth2.authorize_button(
        name="🔑 Đăng nhập bằng Gmail để bắt đầu học",
        redirect_uri=st.secrets["REDIRECT_URI"],
        scope="openid email profile",
        key="google_auth",

        pkce="S256",

        extras_params={
            "prompt": "select_account",
            "access_type": "offline"
        }
    )
 
    return result
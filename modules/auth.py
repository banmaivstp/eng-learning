import streamlit as st
import jwt
from config import oauth2
from modules.database import upsert_user_profile

def render_login_screen():
    """Hiển thị màn hình đăng nhập ban đầu"""
    st.title("⚡ Hệ thống Học tiếng Anh Edu-Stay AI")
    st.caption("Vui lòng xác thực tài khoản để bắt đầu bài học nghe hiểu.")
    # 2. In log ra console (Terminal) để bạn kiểm tra
    print("👉 Debug local - redirect_uri hiện tại: " + st.secrets["REDIRECT_URI"])
    
    result = oauth2.authorize_button(
        name="🔑 Đăng nhập bằng Gmail để bắt đầu học",
        #redirect_uri="https://eng-learning.streamlit.app/",
        # Lấy redirect_uri động theo môi trường hiện tại
        redirect_uri = st.secrets["REDIRECT_URI"],
        scope="openid email profile",
        key="google_auth"
    )
    
    if result and "token" in result:
        st.session_state["auth"] = result
        
        # Giải mã lấy thông tin Profile an toàn qua thư viện PyJWT
        id_token = result["token"]["id_token"]
        payload = jwt.decode(id_token, options={"verify_signature": False})
        
        user_data = {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "full_name": payload.get("name"),
            "avatar_url": payload.get("picture")
        }
        
        # Đồng bộ trực tiếp vào database
        upsert_user_profile(user_data)
        st.rerun()

def render_sidebar_profile():
    """Hiển thị thông tin học viên ở góc màn hình sau khi login"""
    id_token = st.session_state["auth"]["token"]["id_token"]
    user_profile = jwt.decode(id_token, options={"verify_signature": False})
    
    st.sidebar.image(user_profile.get("picture", ""), width=60)
    st.sidebar.markdown(f"Học viên: **{user_profile.get('name')}**")
    st.sidebar.caption(f"Email: {user_profile.get('email')}")
   
    
    if st.sidebar.button("🚪 Đăng xuất"):
        del st.session_state["auth"]
        # Hãy xóa các session_state cũ về bài học tại đây nếu cần dọn dẹp bộ nhớ
        st.rerun()
import streamlit as st
import jwt
from config import oauth2
from modules.database import upsert_user_profile

def render_login_screen():
    """Hiển thị màn hình đăng nhập ban đầu"""
    st.title("⚡ Hệ thống Học tiếng Anh Edu-Stay AI")
    st.caption("Vui lòng xác thực tài khoản để bắt đầu bài học nghe hiểu.")
    
    result = oauth2.authorize_button(
        name="🔑 Đăng nhập bằng Gmail để bắt đầu học",
        redirect_uri=st.secrets["REDIRECT_URI"],
        scope="openid email profile",
        key="google_auth"
    )
    
    if result and "token" in result:
        st.session_state["auth"] = result
        
        # Cơ chế Safe-Fetch: Thích ứng linh hoạt với mọi phiên bản streamlit-oauth
        token_data = result.get("token", {})
        if isinstance(token_data, dict) and "id_token" in token_data:
            id_token = token_data["id_token"]
        else:
            id_token = result.get("id_token")
            
        if id_token:
            payload = jwt.decode(id_token, options={"verify_signature": False})
            user_data = {
                "id": payload.get("sub"), 
                "email": payload.get("email"),
                "full_name": payload.get("name"),
                "avatar_url": payload.get("picture")
            }
            upsert_user_profile(user_data)
            st.rerun()

def render_sidebar_profile():
    """Hiển thị thông tin học viên ở góc màn hình sau khi login và hiển thị Streak"""
    from config import supabase
    auth_data = st.session_state.get("auth", {})
    token_data = auth_data.get("token", {})
    
    if isinstance(token_data, dict) and "id_token" in token_data:
        id_token = token_data["id_token"]
    else:
        id_token = auth_data.get("id_token")
        
    if id_token:
        user_profile = jwt.decode(id_token, options={"verify_signature": False})
        st.sidebar.image(user_profile.get("picture", ""), width=60)
        st.sidebar.markdown(f"Học viên: **{user_profile.get('name')}**")
        st.sidebar.caption(f"Email: {user_profile.get('email')}")
        
        # Gọi bảng ngắn gọn (Đã được config định tuyến tự động)
        try:
            user_id = user_profile.get("sub")
            streak_res = supabase.table("user_streaks").select("current_streak").eq("user_id", user_id).execute()
            if streak_res.data:
                streak_num = streak_res.data[0].get("current_streak", 0)
                st.sidebar.markdown(f"🔥 Chuỗi ngày học: **{streak_num} ngày**")
            else:
                st.sidebar.markdown("🔥 Chuỗi ngày học: **0 ngày**")
        except Exception as e:
            st.sidebar.caption(f"⚠️ Chưa có dữ liệu chuỗi ngày học")
            
    if st.sidebar.button("🚪 Đăng xuất", key="logout_btn"):
        if "auth" in st.session_state:
            del st.session_state["auth"]
        st.rerun()
import streamlit as st
import jwt
import logging
from config import oauth2, supabase
from modules.database import upsert_user_profile
from views.login_view import render_login_form

# Định danh Logger riêng biệt cho module auth
logger = logging.getLogger("modules.auth")

def get_logged_in_user_id():
    """
    Core Logic: Extracts and safely decodes the user ID from current session context.
    Returns None if user is unauthenticated.
    """
    auth_data = st.session_state.get("auth", {})
    user_id = None
    
    if hasattr(auth_data, 'user') and auth_data.user:
        user_id = auth_data.user.id
    elif isinstance(auth_data, dict):
        user_id = auth_data.get("user", {}).get("id") or auth_data.get("id")
    
    if not user_id:
        token_data = auth_data.get("token", {}) if isinstance(auth_data, dict) else {}
        id_token = token_data.get("id_token") if isinstance(token_data, dict) else auth_data.get("id_token")
        if id_token:
            try:
                user_profile = jwt.decode(id_token, options={"verify_signature": False})
                user_id = user_profile.get("sub")
                logger.debug(f"Decoded User ID from ID Token: {user_id}")
            except Exception as jwt_err:
                logger.error(f"🚨 Error decoding token for analytical user mapping: {jwt_err}")
                pass
                
    return user_id

def render_sidebar_profile():
    """Hiển thị thông tin học viên ở góc màn hình sau khi login và hiển thị Streak"""
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
        
        try:
            user_id = user_profile.get("sub")
            logger.debug(f"Fetching streak for user_id: {user_id}")
            streak_res = supabase.table("user_streaks").select("current_streak").eq("user_id", user_id).execute()
            if streak_res.data:
                streak_num = streak_res.data[0].get("current_streak", 0)
                st.sidebar.markdown(f"🔥 Chuỗi ngày học: **{streak_num} ngày**")
            else:
                st.sidebar.markdown("🔥 Chuỗi ngày học: **0 ngày**")
        except Exception as e:
            logger.error(f"🚨 Supabase failure fetching sidebar streak: {e}")
            st.sidebar.caption("⚠️ Chưa có dữ liệu chuỗi ngày học")
        if st.sidebar.button("🚪 Đăng xuất"):
            st.session_state.clear()
            st.rerun()

def render_login_screen():
    """Điều hướng hiển thị biểu mẫu xác thực"""
    logger.debug("Navigating user into login view portal layer.")
    result = render_login_form()
    
    if result and "token" in result:
        st.session_state["auth"] = result
        logger.info("🔑 Authentication token captured from Google OAuth components wrapper.")
        
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
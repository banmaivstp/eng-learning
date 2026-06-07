# ==========================================
# FILE: modules/auth.py
# ==========================================
import streamlit as st
import jwt
import logging
from config import oauth2, supabase
from modules.database import upsert_user_profile
from views.login_view import render_login_form

# Định danh Logger riêng biệt cho module auth
logger = logging.getLogger("modules.auth")

def get_logged_in_user_id(auth_data=None):
    """
    Core Logic: Trích xuất và giải mã an toàn định danh user ID từ Session hiện tại.
    Trả về None nếu người dùng chưa xác thực (Unauthenticated).
    """
    if auth_data is None:
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

def process_user_login_data(oauth_result):
    """
    HÀM BỔ SUNG ĐỂ FIX LỖI IMPORTERROR:
    Core Logic: Nhận kết quả thô từ Google OAuth component, 
    giải mã JWT, đóng gói dữ liệu và đồng bộ xuông table users_profile trên Supabase.
    """
    if not oauth_result or "token" not in oauth_result:
        return None
        
    logger.info("🔑 Authentication token captured from Google OAuth components wrapper.")
    
    token_data = oauth_result.get("token", {})
    if isinstance(token_data, dict) and "id_token" in token_data:
        id_token = token_data["id_token"]
    else:
        id_token = oauth_result.get("id_token")
        
    if id_token:
        try:
            # Giải mã thông tin người dùng từ ID Token
            payload = jwt.decode(id_token, options={"verify_signature": False})
            user_data = {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "full_name": payload.get("name"),
                "avatar_url": payload.get("picture")
            }
            
            # Đồng bộ dữ liệu xuống database Supabase thông qua hàm có sẵn
            upsert_user_profile(user_data)
            logger.info(f"🎯 Sync core profile data into database successfully for: {user_data['email']}")
            
            # Trả về kết quả xác thực để lưu vào st.session_state["auth"] trong app.py
            return oauth_result
            
        except Exception as e:
            logger.error(f"🚨 Error processing login profile sync: {str(e)}")
            return None
    return None

def render_login_screen():
    """Điều hướng hiển thị biểu mẫu xác thực"""
    logger.debug("Navigating user into login view portal layer.")
    result = render_login_form()
    
    if result:
        auth_data = process_user_login_data(result)
        if auth_data:
            st.session_state["auth"] = auth_data
            st.toast("🎉 Đăng nhập thành công!", icon="🚀")
            st.rerun()
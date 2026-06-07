# ==========================================
# FILE: modules/auth.py
# ==========================================
import jwt
import logging
from config import oauth2, supabase
from modules.database import upsert_user_profile

# Định danh Logger riêng biệt cho module auth
logger = logging.getLogger("modules.auth")

def get_logged_in_user_id(auth_data=None):
    """
    Core Logic: Extracts and safely decodes the user ID from current session context.
    Returns None if user is unauthenticated.
    """
    # Nếu không truyền auth_data vào, tự động lấy từ session_state như cũ
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
            except Exception as e:
                logger.error(f"Failed decoding id_token in verification sub-step: {e}")
                
    return user_id

def calculate_user_streak(user_id):
    """
    Core Logic: Queries and calculates the consecutive study streak days for a specific profile.
    Returns 0 if any infrastructure error is encountered.
    """
    if not user_id:
        return 0
    try:
        res = supabase.table("user_profiles").select("current_streak").eq("id", user_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0].get("current_streak", 0)
    except Exception as e:
        logger.error(f"🚨 Supabase failure fetching sidebar streak: {e}")
    return 0

def process_user_login_data(oauth_result):
    """
    Core Logic: Nhận kết quả thô từ Google OAuth component, 
    giải mã JWT, đóng gói dữ liệu và đồng bộ vào Supabase.
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
            # Giải mã dữ liệu người dùng từ Google ID Token
            payload = jwt.decode(id_token, options={"verify_signature": False})
            user_data = {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "name": payload.get("name"),
                "avatar": payload.get("picture")
            }
            
            # Đồng bộ dữ liệu xuống database Supabase thông qua hàm có sẵn của bạn
            upsert_user_profile(user_data)
            logger.info(f"🎯 Sync core profile data into database successfully for: {user_data['email']}")
            
            # Đóng gói lại cấu trúc giống hệt session cũ để app.py lưu giữ
            return oauth_result
            
        except Exception as e:
            logger.error(f"🚨 Critical failure processing credentials: {str(e)}")
            return None
            
    return None
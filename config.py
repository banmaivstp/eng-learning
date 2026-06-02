import os
import logging
import streamlit as st
from groq import Groq
from supabase import create_client
from streamlit_oauth import OAuth2Component

# =====================================================
# CẤU HÌNH LOG LEVEL TẬP TRUNG
# =====================================================
LOG_LEVEL_STR = st.secrets.get("LOG_LEVEL") or os.environ.get("LOG_LEVEL") or "DEBUG"


def setup_global_logging():
    """Thiết lập cấu hình Logger chuẩn hóa cho toàn bộ các file trong hệ thống"""
    level = getattr(logging, LOG_LEVEL_STR.upper(), logging.INFO)
    
    # Định dạng Log bao gồm: Thời gian - Cấp độ - Định danh module - Thông điệp
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] (%(name)s): %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True  # Ghi đè các cấu hình logging mặc định cũ của Streamlit
    )
    
    init_logger = logging.getLogger("AppInit")
    init_logger.info(f"🚀 Hệ thống Logging đã kích hoạt ở chế độ: {LOG_LEVEL_STR.upper()}")

# Kích hoạt hệ thống Logger ngay khi import cấu hình config
setup_global_logging()

# Khởi tạo logger riêng cho file config
logger = logging.getLogger("config")

# =====================================================
# ĐỌC CẤU HÌNH BIẾN MÔI TRƯỜNG & SECRETS
# =====================================================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET")
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

logger.debug(f"Supabase URL: {SUPABASE_URL}")
logger.debug(f"Supabase Key Exists: {bool(SUPABASE_KEY)}")

# =====================================================
# KHỞI TẠO GROQ CLIENT (AI ENGINE)
# =====================================================
client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        logger.info("✅ Groq Client initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Lỗi khi khởi tạo Groq Client: {str(e)}")
else:
    logger.error("❌ Groq API Key missing! Vui lòng kiểm tra lại cấu hình secrets.")

# =====================================================
# KHỞI TẠO SUPABASE CLIENT (DATABASE LAYER)
# =====================================================
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase client initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Supabase init error: {str(e)}")
        supabase = None
else:
    logger.error("❌ Thiếu thông tin cấu hình SUPABASE_URL hoặc SUPABASE_KEY trong secrets.")

# =====================================================
# KHỞI TẠO GOOGLE OAUTH2 (Bản vá loại bỏ tham số revoke)
# =====================================================
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

oauth2 = None
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    try:
        # Khởi tạo chính xác với các tham số được hỗ trợ bởi streamlit-oauth 0.1.14
        oauth2 = OAuth2Component(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            authorize_endpoint=AUTHORIZE_URL,
            token_endpoint=TOKEN_URL,
            refresh_token_endpoint=TOKEN_URL
        )
        logger.info("✅ Google OAuth2 component initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Khởi tạo thành phần Google OAuth2 thất bại: {str(e)}")
else:
    logger.error("❌ Thiếu thông tin GOOGLE_CLIENT_ID hoặc GOOGLE_CLIENT_SECRET trong secrets!")
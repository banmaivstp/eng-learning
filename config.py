import os
import streamlit as st
from groq import Groq
from supabase import create_client, Client
from streamlit_oauth import OAuth2Component

# --- ĐỌC CẤU HÌNH TỪ SECRETS HOẶC BIẾN MÔI TRƯỜNG ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET")
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

# --- KHỞI TẠO CLIENTS ---
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None

# --- CẤU HÌNH GOOGLE OAUTH2 ---
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"

oauth2 = OAuth2Component(
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,
    AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, REVOKE_URL
)
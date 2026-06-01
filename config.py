import os
import streamlit as st
from groq import Groq
from supabase import create_client
from streamlit_oauth import OAuth2Component

# =====================================================
# ĐỌC CẤU HÌNH
# =====================================================

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET")

SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

print("SUPABASE_URL =", SUPABASE_URL)
print("SUPABASE_URL =", SUPABASE_URL)
print("SUPABASE_KEY exists =", bool(SUPABASE_KEY))

# =====================================================
# GROQ CLIENT
# =====================================================

client = None

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)

# =====================================================
# SUPABASE CLIENT
# =====================================================

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"❌ Supabase init error: {e}")
        supabase = None

# =====================================================
# GOOGLE OAUTH2
# =====================================================

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"

oauth2 = OAuth2Component(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    AUTHORIZE_URL,
    TOKEN_URL,
    TOKEN_URL,
    REVOKE_URL
)
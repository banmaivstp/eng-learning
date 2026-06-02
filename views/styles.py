import streamlit as st
import logging

# Khai báo bộ logger định danh riêng cho module thiết lập giao diện CSS
logger = logging.getLogger("views.styles")

def inject_global_css():
    """Injects global high-contrast CSS to improve readability and mobile display."""
    # Log ở cấp độ DEBUG để đảm bảo CSS được nhúng thành công mà không ghi đè block gây log rác ở chế độ INFO
    logger.debug("🎨 Injecting global high-contrast CSS design system into Streamlit layout.")
    
    st.markdown("""
    <style>
        /* Base Design System Theme */
        .stApp {
            background-color: #0D0D0D !important;
            color: #E0E0E0 !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 16px !important;
            padding: 24px !important;
            margin-bottom: 20px !important;
        }
        
        /* Streak Box Highlight Area */
        .streak-box-container {
            background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%) !important;
            border-radius: 16px !important;
            padding: 22px !important;
            text-align: center;
            color: #FFFFFF !important;
            box-shadow: 0 10px 30px rgba(255, 75, 43, 0.3) !important;
            margin-bottom: 25px !important;
        }
        
        /* Đèn hiệu Neon định hướng chuyển trạng thái */
        .neon-text-green { color: #2ecc71 !important; font-weight: 700; }
        .neon-text-cyan { color: #00F2FE !important; font-weight: 700; }
        .neon-text-red { color: #e74c3c !important; font-weight: 700; }

        /* FIX LỖI MỜ CHỮ TRÊN DI ĐỘNG & TĂNG TƯƠNG PHẢN CÁC KHỐI TAPPING */
        /* Định cấu hình các Tapping Options thành khối lớn, chữ đậm nét rõ ràng */
        div[data-testid="stRadio"] label {
            color: #FFFFFF !important; \
            font-weight: 600 !important;
            font-size: 15px !important;
            text-shadow: 0px 1px 2px rgba(0, 0, 0, 0.8) !important;
        }
        
        /* Tăng tương phản văn bản thuần của các câu hỏi radio button */
        div[data-testid="stRadio"] div[role="radiogroup"] {
            background: rgba(255, 255, 255, 0.02) !important;
            padding: 10px !important;
            border-radius: 8px !important;
        }

        /* Nút bấm của Streamlit hiển thị rõ nét chữ trên mọi độ phân giải di động */
        button[data-testid="baseButton-secondary"], button[data-testid="baseButton-primary"] {
            color: #FFFFFF !important;
            font-weight: 700 !important;
            background-color: #1A1A1A !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            transition: all 0.2s ease-in-out !important;
        }
        button[data-testid="baseButton-secondary"]:hover, button[data-testid="baseButton-primary"]:hover {
            border-color: #00F2FE !important;
            box-shadow: 0px 0px 10px rgba(0, 242, 254, 0.2) !important;
        }
    </style>
    """, unsafe_allow_html=True)
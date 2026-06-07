# ==========================================
# FILE: views/sidebar_css.py
# ==========================================
import streamlit as st

def inject_sidebar_css():
    """
    Nhúng CSS độc lập cho Sidebar.
    Giữ nguyên vẹn font chữ và không làm mất icon hay nội dung của radio button gốc.
    """
    st.markdown("""
    <style>
        /* Đảm bảo nền Sidebar đồng bộ màu tối huyền bí như bản gốc */
        [data-testid="stSidebar"] {
            background-color: #020617 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }
        
        /* Định dạng khối Text trong Sidebar gọn gàng hơn */
        [data-testid="stSidebar"] .stMarkdown p {
            font-size: 13.5px !important;
            line-height: 1.5 !important;
        }
        
        /* Tối ưu hiệu ứng hover nút bấm Đăng xuất và các nút chức năng phụ */
        [data-testid="stSidebar"] .stButton > button {
            border-radius: 10px !important;
            transition: all 0.2s ease !important;
        }
    </style>
    """, unsafe_allow_html=True)
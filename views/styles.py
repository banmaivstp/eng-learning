import streamlit as st

def inject_upgraded_design_system():
    st.markdown("""
    <style>
        /* Toàn bộ ứng dụng - Tăng kích thước font cơ bản lên 15px cho dễ đọc */
        .stApp {
            background-color: #0B0B0C !important;
            color: #E2E8F0 !important;
            font-family: 'Inter', system-ui, sans-serif !important;
            font-size: 15px !important;
        }
        
        /* Tối ưu lại Streak Box mỏng hơn, không chiếm quá nhiều chiều cao */
        .streak-box-mini {
            background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%) !important;
            border-radius: 12px !important;
            padding: 14px 20px !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 15px rgba(255, 75, 43, 0.25) !important;
            margin-bottom: 15px !important;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        /* Tăng mạnh độ tương phản cho Text câu hỏi và câu trả lời trắc nghiệm trên Mobile */
        .quiz-question-text {
            color: #00F2FE !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            margin-bottom: 10px;
        }
        
        /* Tùy biến lại các nhãn lựa chọn trắc nghiệm của Streamlit cho rõ nét */
        div[data-testid="stMarkdownContainer"] > p {
            color: #F8FAFC !important; /* Trắng sáng tinh khiết, chống mờ */
            font-weight: 500 !important;
        }
        
        /* Tối ưu khoảng cách cho gọn gàng */
        .glass-card-compact {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
            margin-bottom: 12px !important;
        }
        
        /* Định dạng hiển thị Badge dạng lưới nhỏ */
        .badge-grid-item {
            background: rgba(255, 215, 0, 0.04) !important;
            border: 1px solid rgba(255, 215, 0, 0.2) !important;
            border-radius: 10px !important;
            padding: 8px 12px !important;
            display: flex;
            align-items: center;
            gap: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import logging

logger = logging.getLogger("views.dashboard_view")

def render_dashboard_screen(user_analytics_data=None):
    """
    Render giao diện Dashboard độc lập, tối ưu hóa diện tích hiển thị (no-scroll).
    Phù hợp chuẩn hóa với cấu trúc trả về từ modules/database.py
    """
    logger.debug("📊 Rendering independent Dashboard screen.")
    
    # 1. Fallback dữ liệu mẫu nếu không load được từ Database (Bảo toàn cấu trúc của hệ thống)
    if not user_analytics_data:
        user_analytics_data = {
            "streak_count": 0,
            "total_episodes": 0,
            "total_hours": 0.0,
            "average_score": 0.0,
            "weekly_data": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        }

    # 2. VỊ TRÍ ĐẤT VÀNG: Hộp thông tin Streak 🔥 lên vị trí cao nhất
    streak = user_analytics_data.get("streak_count", 0)
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255, 75, 75, 0.15) 0%, rgba(255, 145, 0, 0.1) 100%);
                    padding: 12px 20px; 
                    border-radius: 12px; 
                    border: 1px solid rgba(255, 75, 75, 0.3); 
                    text-align: center; 
                    margin-bottom: 15px;">
            <span style="font-size: 20px; font-weight: 800; color: #FF4B4B; letter-spacing: 0.5px;">
                🔥 BẠN ĐÃ DUY TRÌ CHUỖI STREAK: {streak} NGÀY LIÊN TIẾP!
            </span>
            <br/>
            <span style="font-size: 12px; color: #94A3B8;">Hãy tiếp tục luyện nghe hôm nay để không làm tắt ngọn lửa học tập nhé.</span>
        </div>
    """, unsafe_allow_html=True)

    # 3. BỐ CỤC METRICS THU GỌN (Dàn hàng ngang dạng nén diện tích, tránh cuộn dọc)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.03); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); text-align: center;">
                <div style="font-size: 11px; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Tổng số bài</div>
                <div style="font-size: 22px; font-weight: 700; color: #00F2FE; margin-top: 2px;">{user_analytics_data.get("total_episodes", 0)}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.03); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); text-align: center;">
                <div style="font-size: 11px; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Thời gian nghe</div>
                <div style="font-size: 22px; font-weight: 700; color: #4FACFE; margin-top: 2px;">{user_analytics_data.get("total_hours", 0.0)}h</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.03); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); text-align: center;">
                <div style="font-size: 11px; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Điểm số TB</div>
                <div style="font-size: 22px; font-weight: 700; color: #00FF87; margin-top: 2px;">{user_analytics_data.get("average_score", 0.0)}/10</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("") # Khoảng đệm siêu nhỏ

    # 4. BIỂU ĐỒ CỘT TIẾN ĐỘ DẠNG NÈN DIỆN TÍCH (Giới hạn height=180px nghiêm ngặt)
    st.markdown('<div style="font-size: 13px; font-weight: 700; color: #F1F5F9; margin-bottom: 8px;">📊 TIẾN ĐỘ HỌC TẬP TUẦN NÀY (PHÚT)</div>', unsafe_allow_html=True)
    
    # Map mảng 7 phần từ của database.py tương ứng thứ 2 -> chủ nhật
    days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
    weekly_raw = user_analytics_data.get("weekly_data", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    
    # Đảm bảo mảng luôn có đủ dữ liệu vẽ chart
    if len(weekly_raw) < 7:
        weekly_raw += [0.0] * (7 - len(weekly_raw))
        
    chart_data = pd.DataFrame({
        'Ngày': days,
        'Thời gian (Phút)': weekly_raw[:7]
    }).set_index('Ngày')
    
    st.bar_chart(chart_data, height=180, use_container_width=True)
import streamlit as st
import pandas as pd
from modules.database import get_user_analytics, evaluate_user_badges

def render_dashboard_page(user_id):
    st.title("⚡ Kết Quả Học Tập")
    
    if not user_id:
        st.warning("Vui lòng đăng nhập để xem tiến độ.")
        return
        
    stats = get_user_analytics(user_id)
    badges = evaluate_user_badges(stats)
    
    # Hộp Streak mỏng theo hàng ngang (Row) cực gọn
    st.markdown(f"""
    <div class="streak-box-mini">
        <div>
            <span style="font-size: 12px; text-transform: uppercase; opacity: 0.8; font-weight:600;">Chuỗi học tập</span>
            <div style="font-size: 20px; font-weight: 800;">🔥 {stats['current_streak']} Ngày liên tiếp</div>
        </div>
        <div style="font-size: 13px; text-align: right; opacity: 0.8;">Kỷ lục: {stats['longest_streak']} ngày</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics nén không gian bằng 4 cột liền kề
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng bài", f"{stats['total_episodes']}")
    m2.metric("Thời gian", f"{stats['total_minutes']}m")
    m3.metric("Điểm TB", f"{stats['avg_score']}/10")
    m4.metric("Mới nhất", f"{stats['latest_score']}/10")
    
    st.write("")
    # Biểu đồ & Huy chương xếp chung hàng ngang để giảm scroll dọc
    col_chart, col_badges = st.columns([5, 4])
    with col_chart:
        st.caption("⏱️ Thời gian nghe tuần này (phút):")
        chart_df = pd.DataFrame({"Phút": stats["weekly_data"]}, index=["T2", "T3", "T4", "T5", "T6", "T7", "CN"])
        st.bar_chart(chart_df, color="#00F2FE", height=160)
        
    with col_badges:
        st.caption("🏅 Danh hiệu của bạn:")
        if badges:
            for b in badges[:3]: # Giới hạn hiển thị 3 huy chương cao nhất để tránh tràn khung
                st.markdown(f"""
                <div class="badge-grid-item">
                    <span style="font-size: 20px;">{b['icon']}</span>
                    <span style="font-weight: 700; color: #FFD700; font-size:12px;">{b['name']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("Chưa có huy chương.")
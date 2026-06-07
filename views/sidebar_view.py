# ==========================================
# FILE: views/sidebar_view.py
# ==========================================
import streamlit as st
import jwt
from views.sidebar_css import inject_sidebar_css

def render_sidebar_navigation(supabase):
    """
    VIEW SIDEBAR GỐC: Giữ nguyên 100% nội dung chữ, icon emoji và logic map trang.
    """
    # Nhúng CSS bổ trợ riêng cho Sidebar
    inject_sidebar_css()

    auth_data = st.session_state.get("auth", {})
    if not auth_data:
        return None
        
    token_data = auth_data.get("token", {}) if isinstance(auth_data, dict) else {}
    id_token = token_data.get("id_token") if isinstance(token_data, dict) else auth_data.get("id_token")
    
    if id_token:
        try:
            user_profile = jwt.decode(id_token, options={"verify_signature": False})
            
            # Khối Profile hàng ngang siêu gọn gốc (Tiết kiệm vùng đất vàng)
            col_av, col_txt = st.sidebar.columns([1, 3])
            with col_av:
                st.image(user_profile.get("picture", ""), width=38) # Thu nhỏ avatar tối đa
            with col_txt:
                st.markdown(f"**{user_profile.get('name')}**")
                
            # Lấy thông tin chuỗi ngày nhanh gọn gốc
            user_id = user_profile.get("sub")
            try:
                streak_res = supabase.table("user_streaks").select("current_streak").eq("user_id", user_id).execute()
                streak_num = streak_res.data[0].get("current_streak", 0) if streak_res.data else 0
                st.sidebar.markdown(f"🔥 Chuỗi hiện tại: **{streak_num} ngày**")
            except:
                pass
        except Exception:
            pass

    st.sidebar.write("---")
    
    # Menu điều hướng chính phân tách rõ ràng thành 3 tab/page gốc
    st.sidebar.markdown("🎯 **Menu ứng dụng**")
    page_selection = st.sidebar.radio(
        "Chọn màn hình làm việc:",
        ["📊 Bảng Tiến Độ", "📻 Tìm Bài Học Mới", "🎧 Phòng Học Thử Thách"],
        label_visibility="collapsed"
    )
    
    # Đồng bộ state với menu lựa chọn gốc
    page_map = {
        "📊 Bảng Tiến Độ": "dashboard",
        "📻 Tìm Bài Học Mới": "discover",
        "🎧 Phòng Học Thử Thách": "detail"
    }
    st.session_state['page'] = page_map[page_selection]
    
    st.sidebar.write("---")
    
    # Kiểm tra liên kết dữ liệu hệ thống phụ trợ gốc
    st.sidebar.markdown("⚙️ **Kết nối hệ thống:**")
    if supabase:
        try:
            st.sidebar.success("Supabase Kết Nối Tốt")
        except:
            st.sidebar.error("Supabase Lỗi Kết Nối")
    else:
        st.sidebar.error("Supabase Chưa Cấu Hình")
        
    st.sidebar.write("---")
    
    # Nút bấm Đăng xuất gốc
    if st.sidebar.button("🚪 Đăng xuất"):
        return "LOGOUT"
        
    return None